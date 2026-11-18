#!/bin/bash
# =============================================================================
# T-M1-003 — Milestone 1 baseline PnR run (ORFS, ASAP7, sattva_sram).
#
# * Runs the flow stage-by-stage from the LF execution mirror (D-010) and
#   captures per-stage evidence into a FRESH timestamped run directory —
#   previous runs are never overwritten.
# * OPENROAD_EXE / YOSYS_EXE are passed explicitly: ORFS defaults point at
#   tools/install/ which does not exist in this environment.
# * WORK_HOME is overridden per run (config default stays pinned).
# * Exit code of this script is NOT success evidence (D-007): Phase D reviews
#   the captured artifacts/reports regardless of rc.
# =============================================================================
set -u

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
MIRROR=/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts
FLOW=$MIRROR/flow
DESIGN=/mnt/d/SattvaRoute/benchmark/design/sattva_sram
CFG=$DESIGN/config.mk
RUN=/mnt/d/SattvaRoute/runs/orfs_baseline_$STAMP
EV=$RUN/evidence
WORK=$RUN/work
mkdir -p "$EV"

OVERRIDES=(OPENROAD_EXE=/usr/local/bin/openroad YOSYS_EXE=/usr/bin/yosys "WORK_HOME=$WORK")

# ------------------------- preflight evidence --------------------------------
{
  echo "=== SattvaRoute baseline run preflight ==="
  echo "run_dir: $RUN"
  date -Iseconds
  echo "uname: $(uname -a)"
  echo "orfs_mirror_head: $(git -C "$MIRROR" rev-parse HEAD)"
  echo "orfs_source_head: $(git -C /mnt/d/tools/OpenROAD-flow-scripts rev-parse HEAD)"
  echo "orfs_mirror_status: [$(git -C "$MIRROR" status --porcelain | head -5)]"
  echo "--- tools ---"
  openroad -version 2>&1 | head -3
  yosys -V
  make -v | head -1
  echo -n "klayout: "; command -v klayout || echo "NOT FOUND (finish GDS step will fail)"
  echo -n "python3: "; python3 --version
  echo "--- system ---"
  free -h
  df -h /mnt/d | tail -1
  echo "--- input sha256 ---"
  sha256sum "$CFG" "$DESIGN/constraint.sdc" "$DESIGN/pdn_sattva.tcl" \
    "$DESIGN"/rtl/*.v "$DESIGN"/netlist/sattva_ctrl_synth.v \
    "$DESIGN"/macro/sram_x4x4x1.{lef,lib,gds}
} > "$EV/preflight.txt" 2>&1

# ------------------------- stage loop ----------------------------------------
# gates first (check-yosys/check-openroad), then the flow proper.
STAGES=(check-yosys check-openroad synth floorplan place cts route finish)
declare -a RESULTS=()
overall=0

for s in "${STAGES[@]}"; do
  t0=$(date -Iseconds)
  make -C "$FLOW" DESIGN_CONFIG="$CFG" "${OVERRIDES[@]}" "$s" \
    > "$EV/stage_$s.log" 2>&1
  rc=$?
  t1=$(date -Iseconds)
  RESULTS+=("$s rc=$rc start=$t0 end=$t1")
  echo "${RESULTS[-1]}" >> "$EV/stages.txt"
  if [ $rc -ne 0 ]; then
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

# sha256 of key products if they exist (evidence of real outputs, D-007)
{
  for f in \
    "$WORK"/results/asap7/sattva_sram/base/1_2_yosys.v \
    "$WORK"/results/asap7/sattva_sram/base/1_synth.odb \
    "$WORK"/results/asap7/sattva_sram/base/2_floorplan.odb \
    "$WORK"/results/asap7/sattva_sram/base/3_*place*.odb \
    "$WORK"/results/asap7/sattva_sram/base/4_*cts*.odb \
    "$WORK"/results/asap7/sattva_sram/base/5_*route*.odb \
    "$WORK"/results/asap7/sattva_sram/base/6_final.def \
    "$WORK"/results/asap7/sattva_sram/base/6_final.v \
    "$WORK"/results/asap7/sattva_sram/base/6_final.gds; do
    [ -f "$f" ] && sha256sum "$f"
  done
} > "$EV/artifact_sha256.txt" 2>&1

echo "RUN_DIR=$RUN" > "$EV/RUN_DIR.txt"
echo "OVERALL_RC=$overall" | tee -a "$EV/stages.txt"
echo "RUN_COMPLETE $RUN rc=$overall"
