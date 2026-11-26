#!/bin/bash
# =============================================================================
# SattvaRoute baseline PnR runner (FDE milestone 1).
#
# Executes ORFS stages one at a time from the LF execution mirror and captures
# per-stage evidence into a FRESH, collision-safe run directory. Previous runs
# are never overwritten.
#
# Reliability contract (D-007 is about engineering evidence, not exit codes):
#   * preflight failures BLOCK execution (no stage is launched);
#   * the process exit code equals the first non-zero stage rc (or 1 for
#     preflight/internal errors), so schedulers can trust $?;
#   * stage outcomes are ALSO written to stages.txt and run.json;
#   * executed binaries, inputs and the *patched* flow script are fingerprinted.
#
# All paths are parameterisable via environment variables so the script can be
# tested offline with stubs and run on another machine.
# =============================================================================
set -u

ROOT=${SATTVA_ROOT:-/mnt/d/SattvaRoute}
MIRROR=${SATTVA_MIRROR:-$ROOT/tools/OpenROAD-flow-scripts}
FLOW=$MIRROR/flow
DESIGN=${SATTVA_DESIGN:-$ROOT/benchmark/design/sattva_sram}
RUNS_ROOT=${SATTVA_RUNS:-$ROOT/runs}
CFG=$DESIGN/config.mk
OPENROAD_EXE=${OPENROAD_EXE:-/usr/local/bin/openroad}
YOSYS_EXE=${YOSYS_EXE:-/usr/bin/yosys}
RUN_TAG=${RUN_TAG:-}

# High-entropy ID + PID; atomic mkdir is the collision guard.
STAMP=$(date -u +%Y%m%dT%H%M%S%NZ)
if [ -n "$RUN_TAG" ]; then
  ID="orfs_baseline_${RUN_TAG}_${STAMP}_$$"
else
  ID="orfs_baseline_${STAMP}_$$"
fi
mkdir -p "$RUNS_ROOT" || { echo "FATAL: cannot create $RUNS_ROOT" >&2; exit 1; }
RUN=$RUNS_ROOT/$ID
if ! mkdir "$RUN" 2>/dev/null; then
  echo "FATAL: run directory already exists (collision): $RUN" >&2
  exit 1
fi
EV=$RUN/evidence
WORK=$RUN/work
mkdir -p "$EV" "$WORK" || { echo "FATAL: cannot create evidence/work dirs" >&2; exit 1; }
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
APPROVAL_TOOL=$SCRIPT_DIR/sattva_approval.py

# ---------------- optional approval gate (FDE-002) ---------------------------
# When any SATTVA_APPROVAL_* variable is supplied, ALL of them are mandatory.
# The guard validates/revalidates the exact patch and applies it narrowly
# before any stage is launched. Without these variables the runner is a plain
# baseline runner (no recovery action, no patch application).
APPROVAL=${SATTVA_APPROVAL:-}
PATCH_FILE=${SATTVA_PATCH:-}
POLICY=${SATTVA_POLICY:-}
SOURCE_RUN=${SATTVA_SOURCE_RUN:-}
SOURCE_RUN_ID=${SATTVA_SOURCE_RUN_ID:-}
DECISION_ID=${SATTVA_DECISION_ID:-}
APPROVAL_ACTIVE=0
JOB_TIMEOUT_SECS=${SATTVA_JOB_TIMEOUT_SECS:-0}
STAGES=(check-yosys check-openroad synth floorplan place cts route finish)

# The active design profile selects which collateral preflight checks and the
# shared manifest resolve. Infer it from the design path unless explicitly set.
if [ -z "${SATTVA_DESIGN_PROFILE:-}" ]; then
  case "$DESIGN" in
    *nangate_macro_control*) DESIGN_PROFILE=nangate_macro_control ;;
    *riscv32i*)              DESIGN_PROFILE=riscv32i_sattva ;;
    *)                       DESIGN_PROFILE=sattva_sram ;;
  esac
else
  DESIGN_PROFILE=$SATTVA_DESIGN_PROFILE
fi
PLATFORM_NG=$FLOW/platforms/nangate45
PLATFORM_ASAP7=$FLOW/platforms/asap7

# Resolve the source-run results directory for the active profile instead of
# assuming the historical ASAP7 path.
RESULTS_ROOT=${SATTVA_RESULTS_ROOT:-}
if [ -z "$RESULTS_ROOT" ] && [ -n "$SOURCE_RUN" ] && [ -d "$SOURCE_RUN/work/results" ]; then
  RESULTS_ROOT=$(find "$SOURCE_RUN/work/results" -type d -name base 2>/dev/null | head -1)
fi
RESULTS_ROOT=${RESULTS_ROOT:-$SOURCE_RUN/work/results/asap7/sattva_sram/base}

if [ -n "$APPROVAL$PATCH_FILE$POLICY$SOURCE_RUN$SOURCE_RUN_ID$DECISION_ID" ]; then
  for pair in "approval:$APPROVAL" "patch:$PATCH_FILE" "policy:$POLICY" \
              "source_run:$SOURCE_RUN" "source_run_id:$SOURCE_RUN_ID" \
              "decision_id:$DECISION_ID"; do
    if [ -z "${pair#*:}" ]; then
      echo "FATAL: incomplete approval gate configuration ($pair missing)" >&2
      exit 1
    fi
  done
  # Guard is applied AFTER preflight (see below) so a failed preflight never
  # touches the execution mirror. Only completeness is checked here.
  APPROVAL_ACTIVE=1
fi

OVERRIDES=(OPENROAD_EXE="$OPENROAD_EXE" YOSYS_EXE="$YOSYS_EXE" "WORK_HOME=$WORK")

# ------------------------- preflight gate ------------------------------------
CHECKS="$EV/preflight_checks.tsv"
: > "$CHECKS"
required_fail=0
check_file() {
  local name=$1 path=$2 required=$3 status=OK
  [ -f "$path" ] || status=MISSING
  printf '%s\t%s\t%s\t%s\n' "$name" "$status" "$required" "$path" >> "$CHECKS"
  if [ "$status" = MISSING ] && [ "$required" = required ]; then required_fail=1; fi
}
check_dir() {
  local name=$1 path=$2 required=$3 status=OK
  [ -d "$path" ] || status=MISSING
  printf '%s\t%s\t%s\t%s\n' "$name" "$status" "$required" "$path" >> "$CHECKS"
  if [ "$status" = MISSING ] && [ "$required" = required ]; then required_fail=1; fi
}
check_cmd() {
  local name=$1 path=$2 required=$3 status=OK
  [ -x "$path" ] || status=MISSING
  printf '%s\t%s\t%s\t%s\n' "$name" "$status" "$required" "$path" >> "$CHECKS"
  if [ "$status" = MISSING ] && [ "$required" = required ]; then required_fail=1; fi
}

check_dir  mirror_flow            "$FLOW"                                  required
check_file mirror_makefile        "$FLOW/Makefile"                         required
check_file patched_flow_script    "$MIRROR/flow/scripts/global_route.tcl"   required
check_file design_config          "$CFG"                                   required
case "$DESIGN_PROFILE" in
  nangate_macro_control)
    check_file constraint          "$DESIGN/constraint.sdc"                 required
    check_file prepared_netlist    "$DESIGN/netlist/sattva_macro_top_synth.v" required
    check_file rtl_top             "$DESIGN/rtl/sattva_macro_top.v"         required
    check_file rtl_blackbox        "$DESIGN/rtl/fakeram45_64x32_bb.v"       required
    check_file tech_lef            "$PLATFORM_NG/lef/NangateOpenCellLibrary.tech.lef" required
    check_file sc_lef              "$PLATFORM_NG/lef/NangateOpenCellLibrary.macro.mod.lef" required
    check_file sc_lib              "$PLATFORM_NG/lib/NangateOpenCellLibrary_typical.lib" required
    check_file macro_lef           "$PLATFORM_NG/lef/fakeram45_64x32.lef"   required
    check_file macro_lib           "$PLATFORM_NG/lib/fakeram45_64x32.lib"   required
    check_file rcx_rules           "$PLATFORM_NG/rcx_patterns.rules"        required
    check_file rc_setup            "$PLATFORM_NG/setRC.tcl"                 required
    ;;
  riscv32i_sattva)
    # Upstream-style config: all collateral lives in the pinned ORFS tree and
    # is fingerprinted by the shared manifest.
    check_dir upstream_rtl         "$FLOW/designs/src/riscv32i"             required
    check_file upstream_sdc        "$FLOW/designs/asap7/riscv32i/constraint.sdc" required
    check_file platform_macro_lef  "$PLATFORM_ASAP7/lef/fakeram7_256x32.lef" required
    check_file platform_macro_lib  "$PLATFORM_ASAP7/lib/NLDM/fakeram7_256x32.lib" required
    ;;
  *)
    # Historical sattva_sram profile (ASAP7 + project-owned SRAM macro).
    check_file constraint          "$DESIGN/constraint.sdc"                 required
    check_file pdn                 "$DESIGN/pdn_sattva.tcl"                 required
    check_file netlist             "$DESIGN/netlist/sattva_ctrl_synth.v"    required
    check_file rtl_controller      "$DESIGN/rtl/sattva_ctrl.v"              required
    check_file macro_lef           "$DESIGN/macro/sram_x4x4x1.lef"          required
    check_file macro_lib           "$DESIGN/macro/sram_x4x4x1.lib"          required
    check_file macro_gds           "$DESIGN/macro/sram_x4x4x1.gds"          optional
    ;;
esac
check_cmd  openroad               "$OPENROAD_EXE"                           required
check_cmd  yosys                  "$YOSYS_EXE"                              required
check_cmd  make                   "$(command -v make || echo /nonexistent)" required
check_cmd  python3                "$(command -v python3 || echo /nonexistent)" required
check_cmd  klayout                "$(command -v klayout || echo /nonexistent)" optional

{
  echo "=== SattvaRoute baseline run preflight ==="
  echo "run_dir: $RUN"
  echo "run_id: $ID"
  date -Iseconds
  echo "uname: $(uname -a)"
  echo "orfs_mirror_head: $(git -C "$MIRROR" rev-parse HEAD 2>/dev/null || echo UNKNOWN)"
  echo "orfs_mirror_status: [$(git -C "$MIRROR" status --porcelain 2>/dev/null | tr '\n' ' ')]"
  echo "--- tool identity (exact executed binaries) ---"
  echo "OPENROAD_EXE=$OPENROAD_EXE"
  "$OPENROAD_EXE" -version 2>&1 | head -3 || true
  echo "YOSYS_EXE=$YOSYS_EXE"
  "$YOSYS_EXE" -V 2>&1 || true
  make -v 2>&1 | head -1 || true
  python3 --version 2>&1 || true
  echo "PATH_openroad=$(command -v openroad || echo NOT_FOUND)"
  echo "PATH_yosys=$(command -v yosys || echo NOT_FOUND)"
  echo "--- checks ---"
  column -t -s $'\t' "$CHECKS" 2>/dev/null || cat "$CHECKS"
  echo "--- system ---"
  free -h
  df -h "$ROOT" | tail -1
  echo "--- profile ---"
  echo "SATTVA_DESIGN_PROFILE=$DESIGN_PROFILE"
  echo "--- input + patch sha256 ---"
  case "$DESIGN_PROFILE" in
    nangate_macro_control)
      sha256sum "$CFG" "$DESIGN/constraint.sdc" \
        "$DESIGN"/rtl/sattva_macro_top.v "$DESIGN"/rtl/fakeram45_64x32_bb.v \
        "$DESIGN"/netlist/sattva_macro_top_synth.v \
        "$PLATFORM_NG"/lef/fakeram45_64x32.lef \
        "$PLATFORM_NG"/lib/fakeram45_64x32.lib \
        "$PLATFORM_NG"/lib/NangateOpenCellLibrary_typical.lib \
        "$PLATFORM_NG"/lef/NangateOpenCellLibrary.tech.lef \
        "$PLATFORM_NG"/lef/NangateOpenCellLibrary.macro.mod.lef \
        "$PLATFORM_NG"/rcx_patterns.rules "$PLATFORM_NG"/setRC.tcl 2>&1
      ;;
    riscv32i_sattva)
      sha256sum "$CFG" "$PLATFORM_ASAP7"/lef/fakeram7_256x32.lef \
        "$PLATFORM_ASAP7"/lib/NLDM/fakeram7_256x32.lib 2>&1
      ;;
    *)
      sha256sum "$CFG" "$DESIGN/constraint.sdc" "$DESIGN/pdn_sattva.tcl" \
        "$DESIGN"/rtl/*.v "$DESIGN"/netlist/sattva_ctrl_synth.v \
        "$DESIGN"/macro/sram_x4x4x1.lef "$DESIGN"/macro/sram_x4x4x1.lib 2>&1
      ;;
  esac
  sha256sum "$MIRROR/flow/scripts/global_route.tcl" "$0" 2>&1
  [ -x "$OPENROAD_EXE" ] && sha256sum "$OPENROAD_EXE" 2>&1 || true
  [ -x "$YOSYS_EXE" ] && sha256sum "$YOSYS_EXE" 2>&1 || true
} > "$EV/preflight.txt" 2>&1

git -C "$MIRROR" diff --binary > "$EV/mirror.patch" 2>/dev/null || true
MIRROR_SHA=$(sha256sum "$MIRROR/flow/scripts/global_route.tcl" 2>/dev/null | awk '{print $1}')
RUNNER_SHA=$(sha256sum "$0" | awk '{print $1}')
MANIFEST=${SATTVA_MANIFEST:-$ROOT/config/sattva_manifest.json}
MANIFEST_SHA=$(sha256sum "$MANIFEST" 2>/dev/null | awk '{print $1}')
if [ -f "$MANIFEST" ] && [ "${SATTVA_MANIFEST_CHECK:-1}" != "0" ]; then
  if ! python3 "$SCRIPT_DIR/manifest.py" --manifest "$MANIFEST" --check \
      --profile "$DESIGN_PROFILE" --mirror "$MIRROR" --design-root "$DESIGN" \
      > "$EV/manifest.json" 2>&1; then
    required_fail=1
    echo "MANIFEST CHECK FAILED (profile $DESIGN_PROFILE); see $EV/manifest.json" >> "$EV/preflight.txt"
  fi
else
  echo '{"status":"SKIPPED","reason":"manifest absent or check disabled"}' > "$EV/manifest.json"
fi

python3 - "$CHECKS" "$EV/preflight.json" "$ID" "$MIRROR_SHA" "$RUNNER_SHA" "$required_fail" "$MANIFEST_SHA" <<'PY'
import json, sys
checks_path, out, run_id, mirror_sha, runner_sha, fail, manifest_sha = sys.argv[1:8]
checks = []
with open(checks_path) as fh:
    for line in fh:
        parts = line.rstrip("\n").split("\t")
        if len(parts) == 4:
            checks.append(dict(name=parts[0], status=parts[1], required=parts[2], path=parts[3]))
doc = dict(run_id=run_id, required_ok=(fail == "0"), checks=checks,
           mirror_global_route_sha256=mirror_sha, runner_sha256=runner_sha,
           manifest_sha256=manifest_sha, first_failed_stage=None)
with open(out, "w") as fh:
    json.dump(doc, fh, indent=2)
    fh.write("\n")
PY

if [ "$required_fail" -ne 0 ]; then
  echo "PREFLIGHT FAILED: required checks missing; no EDA stage was launched. See $EV/preflight.txt" >&2
  echo "$ID" > "$EV/RUN_DIR_ID.txt"
  exit 1
fi

# Patch application only now: preflight has passed, so no stage-less mirror edit.
if [ "$APPROVAL_ACTIVE" -eq 1 ]; then
  # Carry an already-applied approval state into this isolated attempt so the
  # guard recognises a resumed operation instead of attempting a second apply.
  APPROVAL_STATE_RUN=${SATTVA_APPROVAL_STATE_RUN:-}
  if [ -n "$APPROVAL_STATE_RUN" ] && [ -f "$APPROVAL_STATE_RUN/evidence/approval_apply.json" ]; then
    cp "$APPROVAL_STATE_RUN/evidence/approval_apply.json" "$EV/approval_apply.json"
  fi
  python3 "$APPROVAL_TOOL" guard \
    --approval "$APPROVAL" --patch "$PATCH_FILE" --policy "$POLICY" \
    --design-root "$DESIGN" --run-id "$SOURCE_RUN_ID" \
    --decision-id "$DECISION_ID" --evidence-dir "$EV" || exit 1
fi

# ------------- rerun scope enforcement + second revalidation ------------------
if [ "$APPROVAL_ACTIVE" -eq 1 ]; then
  # Verify SOURCE_RUN really is the run named by the approval.
  if [ -f "$SOURCE_RUN/evidence/run.json" ]; then
    python3 - "$SOURCE_RUN/evidence/run.json" "$SOURCE_RUN_ID" <<'PY'
import json, sys
doc = json.load(open(sys.argv[1]))
if doc.get("run_id") != sys.argv[2]:
    raise SystemExit(f"source run identity mismatch: {doc.get('run_id')} != {sys.argv[2]}")
PY
    [ $? -eq 0 ] || exit 1
  fi
  python3 "$APPROVAL_TOOL" check-source-artifacts \
    --approval "$APPROVAL" --policy "$POLICY" --source-work "$SOURCE_RUN/work" \
    --results-root "$RESULTS_ROOT" || exit 1
  # Resume only the declared affected stages; prerequisite products come from
  # the immutable source run, never from an inferred dependency graph.
  # A failure at the first stage may have produced no reusable results;
  # absence is valid, so do not fail the recovery.
  if [ -d "$SOURCE_RUN/work/results" ]; then
    cp -a "$SOURCE_RUN/work/results" "$WORK/" || exit 1
  fi
  mapfile -t STAGES < <(python3 -c \
    'import json,sys; print("\n".join(json.load(open(sys.argv[1]))["rerun_scope"]))' \
    "$EV/approval_guard.json")
  [ "${#STAGES[@]}" -gt 0 ] || { echo "FATAL: empty rerun scope" >&2; exit 1; }
  # Revalidate immediately before the affected stage execution.
  python3 "$APPROVAL_TOOL" guard \
    --approval "$APPROVAL" --patch "$PATCH_FILE" --policy "$POLICY" \
    --design-root "$DESIGN" --run-id "$SOURCE_RUN_ID" \
    --decision-id "$DECISION_ID" --evidence-dir "$EV" || exit 1
fi

# ------------------------- stage loop ----------------------------------------
STAGE_TSV="$EV/stages.tsv"
JOBS="$EV/jobs.jsonl"
: > "$STAGE_TSV"
: > "$JOBS"
overall=0
active_pid=""

# Reconcile an interrupted/prior run without launching duplicate jobs.
start_index=0
if [ -n "${SATTVA_RESUME_DIR:-}" ] && [ -f "$SATTVA_RESUME_DIR/evidence/stages.tsv" ]; then
  cp -a "$SATTVA_RESUME_DIR/work/results" "$WORK/" 2>/dev/null || true
  while read -r s rc _ _; do
    if [ "$rc" = "0" ] && [ "$start_index" -lt "${#STAGES[@]}" ]; then
      printf '%s\t0\tRESUMED\tRESUMED\n' "$s" >> "$STAGE_TSV"
      printf '%s rc=0 RESUMED (no duplicate job)\n' "$s" >> "$EV/stages.txt"
      start_index=$((start_index + 1))
    else
      break
    fi
  done < "$SATTVA_RESUME_DIR/evidence/stages.tsv"
fi

on_signal() {
  echo "CANCELLED $(date -Iseconds) active_pid=${active_pid:-none}" > "$EV/cancellation.json"
  if [ -n "$active_pid" ]; then kill -TERM "$active_pid" 2>/dev/null || true; fi
  echo "RUN_CANCELLED rc=143" | tee -a "$EV/stages.txt"
  exit 143
}
trap on_signal INT TERM

idx=0
for s in "${STAGES[@]}"; do
  if [ "$idx" -lt "$start_index" ]; then idx=$((idx + 1)); continue; fi
  t0=$(date -Iseconds)
  printf '{"stage":"%s","phase":"starting","pid":null,"start":"%s"}\n' "$s" "$t0" >> "$JOBS"
  if [ "$JOB_TIMEOUT_SECS" -gt 0 ] && command -v timeout >/dev/null 2>&1; then
    timeout --signal=TERM --kill-after=30 "${JOB_TIMEOUT_SECS}s" \
      make -C "$FLOW" DESIGN_CONFIG="$CFG" "${OVERRIDES[@]}" "$s" \
      > "$EV/stage_$s.log" 2>&1 &
  else
    make -C "$FLOW" DESIGN_CONFIG="$CFG" "${OVERRIDES[@]}" "$s" \
      > "$EV/stage_$s.log" 2>&1 &
  fi
  active_pid=$!
  stage_pid=$active_pid
  wait "$active_pid"; rc=$?
  active_pid=""
  t1=$(date -Iseconds)
  printf '{"stage":"%s","phase":"finished","pid":%s,"end":"%s","rc":%s}\n' \
    "$s" "$stage_pid" "$t1" "$rc" >> "$JOBS"
  printf '%s\t%s\t%s\t%s\n' "$s" "$rc" "$t0" "$t1" >> "$STAGE_TSV"
  printf '%s rc=%s start=%s end=%s\n' "$s" "$rc" "$t0" "$t1" >> "$EV/stages.txt"
  if [ "$rc" -eq 124 ] || [ "$rc" -eq 137 ]; then
    printf '{"stage":"%s","phase":"timeout","rc":%s}\n' "$s" "$rc" >> "$JOBS"
    echo "STAGE TIMEOUT: $s (rc=$rc) — evidence preserved" | tee -a "$EV/stages.txt"
  fi
  if [ "$rc" -ne 0 ]; then
    overall=$rc
    echo "STAGE FAILED: $s (rc=$rc) — stopping (later stages depend on it)" | tee -a "$EV/stages.txt"
    break
  fi
  idx=$((idx + 1))
done
trap - INT TERM

# ------------------------- postflight evidence --------------------------------
{
  echo "=== postflight $(date -Iseconds) ==="
  echo "--- stage results ---"
  cat "$EV/stages.txt" 2>/dev/null
  echo "--- work tree files ---"
  find "$WORK" -type f 2>/dev/null | sort
} > "$EV/postflight.txt" 2>&1

# Hash every produced artifact and report, not just a whitelist.
find "$WORK" -type f -print0 2>/dev/null | xargs -0 -r sha256sum > "$EV/artifact_sha256.txt" 2>/dev/null

python3 - "$STAGE_TSV" "$EV/run.json" "$ID" "$overall" "$RUN" "$MIRROR_SHA" "$RUNNER_SHA" "$MANIFEST_SHA" <<'PY'
import json, sys
tsv, out, run_id, rc, run_dir, mirror_sha, runner_sha, manifest_sha = sys.argv[1:9]
stages = []
with open(tsv) as fh:
    for line in fh:
        parts = line.rstrip("\n").split("\t")
        if len(parts) == 4:
            stages.append(dict(stage=parts[0], rc=int(parts[1]), start=parts[2], end=parts[3]))
failed = next((s["stage"] for s in stages if s["rc"] != 0), None)
doc = dict(run_id=run_id, run_dir=run_dir, overall_rc=int(rc),
           first_failed_stage=failed, mirror_global_route_sha256=mirror_sha,
           runner_sha256=runner_sha, manifest_sha256=manifest_sha, stages=stages,
           engineering_verdict="NOT EVALUATED — report-level review required (D-007)")
with open(out, "w") as fh:
    json.dump(doc, fh, indent=2)
    fh.write("\n")
PY

echo "RUN_DIR=$RUN" > "$EV/RUN_DIR.txt"
echo "$ID" > "$EV/RUN_DIR_ID.txt"
echo "OVERALL_RC=$overall" | tee -a "$EV/stages.txt"
echo "RUN_COMPLETE $RUN rc=$overall"
exit "$overall"
