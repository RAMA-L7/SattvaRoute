#!/bin/bash
# Offline, credential-free tests for scripts/run_baseline_orfs.sh.
# No EDA flow is executed: `make`, openroad and yosys are stubs in a temp sandbox.
set -u

RUNNER=$(cd "$(dirname "$0")/.." && pwd)/scripts/run_baseline_orfs.sh
SANDBOX=$(mktemp -d)
trap 'rm -rf "$SANDBOX"' EXIT
ROOT=$SANDBOX/project
RUNS=$ROOT/runs
DESIGN=$ROOT/benchmark/design/sattva_sram
MIRROR=$ROOT/tools/OpenROAD-flow-scripts
BIN=$SANDBOX/bin
mkdir -p "$RUNS" "$DESIGN/netlist" "$DESIGN/rtl" "$DESIGN/macro" \
         "$MIRROR/flow/scripts" "$BIN"

for f in config.mk constraint.sdc pdn_sattva.tcl; do echo "stub" > "$DESIGN/$f"; done
echo "stub" > "$DESIGN/netlist/sattva_ctrl_synth.v"
echo "stub" > "$DESIGN/rtl/sattva_ctrl.v"
echo "stub" > "$DESIGN/macro/sram_x4x4x1.lef"
echo "stub" > "$DESIGN/macro/sram_x4x4x1.lib"
echo "stub" > "$DESIGN/macro/sram_x4x4x1.gds"
echo "all:" > "$MIRROR/flow/Makefile"
echo "# stub patched flow script" > "$MIRROR/flow/scripts/global_route.tcl"

cat > "$BIN/make" <<'EOF'
#!/bin/bash
if [ "${1:-}" = "-v" ]; then echo "GNU Make 4.3 (stub)"; exit 0; fi
exit "${STUB_RC:-0}"
EOF
cat > "$BIN/openroad" <<'EOF'
#!/bin/bash
echo "OpenROAD stub (test build)"
EOF
cat > "$BIN/yosys" <<'EOF'
#!/bin/bash
echo "Yosys 0.33 (stub)"
EOF
chmod +x "$BIN/make" "$BIN/openroad" "$BIN/yosys"

export PATH="$BIN:$PATH"
export SATTVA_ROOT="$ROOT"
export SATTVA_MIRROR="$MIRROR"
export SATTVA_DESIGN="$DESIGN"
export SATTVA_RUNS="$RUNS"
export OPENROAD_EXE="$BIN/openroad"
export YOSYS_EXE="$BIN/yosys"
unset RUN_TAG

PASS=0
FAIL=0
check() {
  local label=$1 actual=$2 expected=$3
  if [ "$actual" = "$expected" ]; then
    echo "PASS $label"
    PASS=$((PASS + 1))
  else
    echo "FAIL $label (actual='$actual' expected='$expected')"
    FAIL=$((FAIL + 1))
  fi
}
last_run_dir() {
  ls -dt "$RUNS"/*/ | head -1
}

# --- test 1: failed stage propagates as process exit code -------------------
export STUB_RC=7
bash "$RUNNER" > "$SANDBOX/out1.txt" 2>&1
rc=$?
check "failed-stage process rc" "$rc" "7"
R1=$(last_run_dir)
check "stages.txt OVERALL_RC" "$(grep -c 'OVERALL_RC=7' "$R1/evidence/stages.txt")" "1"
check "run.json overall_rc" "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["overall_rc"])' "$R1/evidence/run.json")" "7"
check "run.json first_failed_stage" "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["first_failed_stage"])' "$R1/evidence/run.json")" "check-yosys"
check "preflight required_ok" "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["required_ok"])' "$R1/evidence/preflight.json")" "True"

# --- test 2: success propagates as zero, all stages recorded ----------------
export STUB_RC=0
bash "$RUNNER" > "$SANDBOX/out2.txt" 2>&1
rc=$?
check "success process rc" "$rc" "0"
R2=$(last_run_dir)
check "all 8 stages recorded" "$(wc -l < "$R2/evidence/stages.tsv")" "8"
check "run.json overall_rc success" "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["overall_rc"])' "$R2/evidence/run.json")" "0"

# --- test 3: concurrent-style launches get distinct directories ------------
STUB_RC=0
ID1=$(bash "$RUNNER" >/dev/null 2>&1; cat "$(last_run_dir)evidence/RUN_DIR_ID.txt")
ID2=$(bash "$RUNNER" >/dev/null 2>&1; cat "$(last_run_dir)evidence/RUN_DIR_ID.txt")
if [ "$ID1" != "$ID2" ]; then check "unique run ids" "distinct" "distinct"; else check "unique run ids" "$ID1" "distinct"; fi
check "distinct run directories" "$(find "$RUNS" -mindepth 1 -maxdepth 1 -type d | wc -l)" "4"

# --- test 4: preflight failure blocks all stages ---------------------------
mv "$DESIGN/constraint.sdc" "$DESIGN/constraint.sdc.hidden"
export STUB_RC=0
bash "$RUNNER" > "$SANDBOX/out4.txt" 2>&1
rc=$?
check "preflight-failure process rc" "$rc" "1"
R4=$(last_run_dir)
check "no stages started" "$([ -f "$R4/evidence/stages.txt" ] && echo yes || echo no)" "no"
check "preflight required_ok false" "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["required_ok"])' "$R4/evidence/preflight.json")" "False"
mv "$DESIGN/constraint.sdc.hidden" "$DESIGN/constraint.sdc"

# --- test 5: patched flow script is fingerprinted ---------------------------
EXPECT=$(sha256sum "$MIRROR/flow/scripts/global_route.tcl" | awk '{print $1}')
check "patch hash recorded" "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["mirror_global_route_sha256"])' "$R2/evidence/preflight.json")" "$EXPECT"

echo "RESULT: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ]
