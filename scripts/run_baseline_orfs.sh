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
check_file constraint             "$DESIGN/constraint.sdc"                 required
check_file pdn                    "$DESIGN/pdn_sattva.tcl"                  required
check_file netlist                "$DESIGN/netlist/sattva_ctrl_synth.v"     required
check_file rtl_controller         "$DESIGN/rtl/sattva_ctrl.v"               required
check_file macro_lef              "$DESIGN/macro/sram_x4x4x1.lef"           required
check_file macro_lib              "$DESIGN/macro/sram_x4x4x1.lib"           required
check_file macro_gds              "$DESIGN/macro/sram_x4x4x1.gds"           optional
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
  echo "--- input + patch sha256 ---"
  sha256sum "$CFG" "$DESIGN/constraint.sdc" "$DESIGN/pdn_sattva.tcl" \
    "$DESIGN"/rtl/*.v "$DESIGN"/netlist/sattva_ctrl_synth.v \
    "$DESIGN"/macro/sram_x4x4x1.lef "$DESIGN"/macro/sram_x4x4x1.lib 2>&1
  sha256sum "$MIRROR/flow/scripts/global_route.tcl" "$0" 2>&1
  [ -x "$OPENROAD_EXE" ] && sha256sum "$OPENROAD_EXE" 2>&1 || true
  [ -x "$YOSYS_EXE" ] && sha256sum "$YOSYS_EXE" 2>&1 || true
} > "$EV/preflight.txt" 2>&1

git -C "$MIRROR" diff --binary > "$EV/mirror.patch" 2>/dev/null || true
MIRROR_SHA=$(sha256sum "$MIRROR/flow/scripts/global_route.tcl" 2>/dev/null | awk '{print $1}')
RUNNER_SHA=$(sha256sum "$0" | awk '{print $1}')

python3 - "$CHECKS" "$EV/preflight.json" "$ID" "$MIRROR_SHA" "$RUNNER_SHA" "$required_fail" <<'PY'
import json, sys
checks_path, out, run_id, mirror_sha, runner_sha, fail = sys.argv[1:7]
checks = []
with open(checks_path) as fh:
    for line in fh:
        parts = line.rstrip("\n").split("\t")
        if len(parts) == 4:
            checks.append(dict(name=parts[0], status=parts[1], required=parts[2], path=parts[3]))
doc = dict(run_id=run_id, required_ok=(fail == "0"), checks=checks,
           mirror_global_route_sha256=mirror_sha, runner_sha256=runner_sha,
           first_failed_stage=None)
with open(out, "w") as fh:
    json.dump(doc, fh, indent=2)
    fh.write("\n")
PY

if [ "$required_fail" -ne 0 ]; then
  echo "PREFLIGHT FAILED: required checks missing; no EDA stage was launched. See $EV/preflight.txt" >&2
  echo "$ID" > "$EV/RUN_DIR_ID.txt"
  exit 1
fi

# ------------------------- stage loop ----------------------------------------
STAGES=(check-yosys check-openroad synth floorplan place cts route finish)
STAGE_TSV="$EV/stages.tsv"
: > "$STAGE_TSV"
overall=0

for s in "${STAGES[@]}"; do
  t0=$(date -Iseconds)
  make -C "$FLOW" DESIGN_CONFIG="$CFG" "${OVERRIDES[@]}" "$s" \
    > "$EV/stage_$s.log" 2>&1
  rc=$?
  t1=$(date -Iseconds)
  printf '%s\t%s\t%s\t%s\n' "$s" "$rc" "$t0" "$t1" >> "$STAGE_TSV"
  printf '%s rc=%s start=%s end=%s\n' "$s" "$rc" "$t0" "$t1" >> "$EV/stages.txt"
  if [ "$rc" -ne 0 ]; then
    overall=$rc
    echo "STAGE FAILED: $s (rc=$rc) — stopping (later stages depend on it)" | tee -a "$EV/stages.txt"
    break
  fi
done

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

python3 - "$STAGE_TSV" "$EV/run.json" "$ID" "$overall" "$RUN" "$MIRROR_SHA" "$RUNNER_SHA" <<'PY'
import json, sys
tsv, out, run_id, rc, run_dir, mirror_sha, runner_sha = sys.argv[1:8]
stages = []
with open(tsv) as fh:
    for line in fh:
        parts = line.rstrip("\n").split("\t")
        if len(parts) == 4:
            stages.append(dict(stage=parts[0], rc=int(parts[1]), start=parts[2], end=parts[3]))
failed = next((s["stage"] for s in stages if s["rc"] != 0), None)
doc = dict(run_id=run_id, run_dir=run_dir, overall_rc=int(rc),
           first_failed_stage=failed, mirror_global_route_sha256=mirror_sha,
           runner_sha256=runner_sha, stages=stages,
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
