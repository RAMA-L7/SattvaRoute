#!/bin/bash
# Standalone synthesis of the SattvaRoute benchmark (T-M1-001, Phase A).
# Runs system Yosys 0.33 in WSL against the ORFS ASAP7 TT/RVT NLDM libs.
# Produces: benchmark/design/sattva_sram/netlist/{sattva_ctrl_synth.v,synth_provenance.txt,synth_stat.txt}
# NEVER modifies D:\tools — libs are read-only inputs.
set -euo pipefail

PROJ=/mnt/d/SattvaRoute
ORFS=/mnt/d/tools/OpenROAD-flow-scripts
RTL=$PROJ/benchmark/design/sattva_sram/rtl
OUT=$PROJ/benchmark/design/sattva_sram/netlist
LIB=$ORFS/flow/platforms/asap7/lib/NLDM
SCRIPTS=$ORFS/flow/scripts

mkdir -p "$OUT"

# --- inputs (RVT primary VT, TT corner for mapping; documented decision D-009) ---
SEQ_LIB=$LIB/asap7sc7p5t_SEQ_RVT_TT_nldm_220123.lib
COMB_LIBS="$LIB/asap7sc7p5t_AO_RVT_TT_nldm_211120.lib.gz \
           $LIB/asap7sc7p5t_INVBUF_RVT_TT_nldm_220122.lib.gz \
           $LIB/asap7sc7p5t_OA_RVT_TT_nldm_211120.lib.gz \
           $LIB/asap7sc7p5t_SIMPLE_RVT_TT_nldm_211120.lib.gz"

for f in "$SEQ_LIB" $COMB_LIBS "$RTL/sattva_ctrl.v" "$RTL/sram_x4x4x1_bb.v" "$PROJ/scripts/abc_map_sattva.script"; do
  [ -f "$f" ] || { echo "MISSING INPUT: $f" >&2; exit 2; }
done

TS=$(date -Iseconds)

{
  echo "=== SattvaRoute synthesis provenance ==="
  echo "timestamp: $TS"
  echo "host: $(uname -a)"
  echo "yosys: $(yosys -V)"
  echo "abc: (bundled with yosys 0.33)"
  echo "top: sattva_ctrl"
  echo "clock_period_abc_D: 950 ps"
  echo "corner: TT (TC) · primary VT: RVT"
  echo "inputs (sha256):"
  sha256sum "$RTL/sattva_ctrl.v" "$RTL/sram_x4x4x1_bb.v" "$SEQ_LIB" $COMB_LIBS "$PROJ/scripts/abc_map_sattva.script"
} > "$OUT/synth_provenance.txt"

# abc's read_lib cannot parse .lib.gz (yosys 0.33 abc crashed, rc 134) —
# decompress TT comb libs to /tmp (C-free, ephemeral) and pass plain .lib.
WORK=$(mktemp -d /tmp/ofr_synth_XXXXXX)
COMB_PLAIN=""
for f in $COMB_LIBS; do
  base=$(basename "$f" .lib.gz)
  gunzip -c "$f" > "$WORK/$base.lib"
  COMB_PLAIN="$COMB_PLAIN $WORK/$base.lib"
done

LIBERTY_ARGS=""
for f in $COMB_PLAIN; do LIBERTY_ARGS="$LIBERTY_ARGS -liberty $f"; done

yosys -p "
# Load cell definitions first so port directions are known — otherwise
# check reports false 'no driver' warnings on QN/Y outputs (verified).
read_liberty -lib $SEQ_LIB
read_liberty -lib $WORK/asap7sc7p5t_AO_RVT_TT_nldm_211120.lib
read_liberty -lib $WORK/asap7sc7p5t_INVBUF_RVT_TT_nldm_220122.lib
read_liberty -lib $WORK/asap7sc7p5t_OA_RVT_TT_nldm_211120.lib
read_liberty -lib $WORK/asap7sc7p5t_SIMPLE_RVT_TT_nldm_211120.lib
read_verilog $RTL/sram_x4x4x1_bb.v
read_verilog $RTL/sattva_ctrl.v
hierarchy -check -top sattva_ctrl
synth -top sattva_ctrl -noabc
dfflibmap -liberty $SEQ_LIB
abc -script /mnt/d/SattvaRoute/scripts/abc_map_sattva.script $LIBERTY_ARGS
opt -purge
splitnets
opt_clean -purge
check -assert
tee -o $OUT/synth_stat.txt stat -liberty $SEQ_LIB $LIBERTY_ARGS
write_verilog -noattr -noexpr $OUT/sattva_ctrl_synth.v
" 2>&1 | tee "$OUT/yosys_synth.log"

echo "SYNTH_EXIT=$?"

# --- post-checks: netlist must be real gate-level with the macro instance ---
echo "=== post-checks ===" | tee -a "$OUT/synth_provenance.txt"
grep -c "sram_x4x4x1 u_sram" "$OUT/sattva_ctrl_synth.v" | tee -a "$OUT/synth_provenance.txt"
if grep -qE '\\\$(dff|mux|alu|add|sub|eq|ne)' "$OUT/sattva_ctrl_synth.v"; then
  echo "POSTCHECK FAIL: internal \$ cells remain" | tee -a "$OUT/synth_provenance.txt"; exit 3
fi
CELLS=$(grep -oE '^[[:space:]]*[A-Za-z0-9_]+_ASAP7_75t_[A-Z0-9]+ ' "$OUT/sattva_ctrl_synth.v" | wc -l)
echo "asap7_stdcell_instances: $CELLS" | tee -a "$OUT/synth_provenance.txt"
sha256sum "$OUT/sattva_ctrl_synth.v" | tee -a "$OUT/synth_provenance.txt"
echo "POSTCHECK PASS" | tee -a "$OUT/synth_provenance.txt"
