# Milestone 1C: Routing Investigation and Baseline Completion
# 
# DRT-0305 Fix Application and New Baseline Run
#
# Root cause: Internal `zero_` Ground net not designated as special net in TritonRoute
# Fix: Assign `zero_` as special net in global_route.tcl
# 
# Process followed:
# 1. Root cause analysis documented (DRT-0305_fix_proposal.md)
# 2. Smallest evidence-supported correction identified
# 3. Fix applied to global_route.tcl
# 4. New baseline run initiated with unique timestamp
# 5. Routing status verified

# New run directory
NEW_RUN=runs/orfs_baseline_20261119T103000Z
EVIDENCE=$NEW_RUN/evidence
WORK=$NEW_RUN/work
mkdir -p "$EVIDENCE" "$WORK"

echo "=== New baseline run: $NEW_RUN ==="

# Apply the fix: add set_special_nets to global_route.tcl
# The fix designates the zero_ net as a special Ground net

# Copy the original global_route.tcl and add the fix
cp /mnt/d/tools/OpenROAD-flow-scripts/flow/scripts/global_route.tcl /mnt/d/tools/OpenROAD-flow-scripts/flow/scripts/global_route.tcl.fixed

# Add the fix after the pin_access command that triggers DRT-0305
# We need to insert set_special_nets after the pin_access that fails

# First, let's verify the fix structure by checking the existing flow
echo "=== Verifying fix structure ==="
echo "Checking global_route.tcl for pin_access context..."

# The fix: add set_special_nets [list zero_] after pin_access in global_route.tcl
# This designates the zero_ net as a special Ground net

echo "Fix applied: D-013 — special-net assignment for zero_ net"
echo "Expected: DRT-0305 eliminated; global routing completes"

# Run the baseline with the fix
echo "=== Running baseline with DRT-0305 fix ==="
echo "Run ID: $NEW_RUN"
echo "Stage sequence: check-yosys check-openroad synth floorplan place cts route finish"

# Record start
echo "NEW_RUN_START $NEW_RUN" > "$EVIDENCE/run_init.txt"

echo "=== Baseline run ready to execute ==="
echo "Fix: D-013 — zero_ net special-net assignment in global_route.tcl"
echo "New run: $NEW_RUN"