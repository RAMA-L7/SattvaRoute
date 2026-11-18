#!/bin/bash
# SattvaRoute — OpenFinRAM macro generation recipe (Milestone 0)
# Generates a real ASAP7 SRAM macro (GDS + LEF + Liberty) with no Calibre.
#
# Prerequisites (installed 2026-11-18, see docs/milestone0-environment-audit.md):
#   - pip install --user --break-system-packages klayout yowasp-yosys
#   - OpenFinRAM built: cmake -S . -B build && make -j4
#   - the v2lvs patch in src/openroad_manager.cpp (fatal -> warning)
#
# Usage: wsl -d Ubuntu-24.04 -- bash /mnt/d/SattvaRoute/scripts/gen_sram_macro.sh
set -e

REPO=/mnt/d/SattvaRoute/benchmark/design/OpenFinRAM
NUM_WLS=${NUM_WLS:-2}
NUM_DATA_BITS=${NUM_DATA_BITS:-4}
NUM_BANKS=${NUM_BANKS:-1}

# Per-run PATH shim: bare `yosys` -> yowasp-yosys 0.71 (multi-dim packed array
# ports in sram_control.v need >=0.55; system yosys 0.33 left untouched).
SHIM_DIR=$(mktemp -d)
printf '#!/bin/bash\nexec /root/.local/bin/yowasp-yosys "$@"\n' > "$SHIM_DIR/yosys"
chmod +x "$SHIM_DIR/yosys"
export PATH="$SHIM_DIR:$PATH"

cd "$REPO"
./build/OpenFinRAM \
  --num-wls "$NUM_WLS" --num-data-bits "$NUM_DATA_BITS" --num-banks "$NUM_BANKS" \
  --single-port --openroad --skip-characterization \
  --openroad-path /usr/local/bin/openroad

echo "Done. Views in $REPO/results/ and $REPO/sram_*.lef|.lib"
