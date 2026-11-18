# Failure Case 1: Missing macro timing-view configuration
#
# Problem: The ORFS flow references a macro Liberty file that is absent or
# incompatible. OpenROAD reports errors like:
#   "Cannot read Liberty file" or "No lib file found for macro"
#   during the floorplan/placement stages.
#
# Evidence collection:
#   - Check the floorplan log for Liberty-read errors
#   - Verify the ADDITIONAL_LEFS and ADDITIONAL_LIBS variables in config.mk
#   - Confirm the file path exists on the filesystem
#
# Likely cause:
#   - ADDITIONAL_LIBS points to a .lib file that was moved, deleted, or never
#     copied into the design directory
#   - The .lib filename doesn't match the macro's LEF-defined cell name
#   - The VT (voltage/temperature) tag is incorrect for the chosen CORNER
#
# Proposed patch (requires approval):
#   1. Restore the correct .lib path in ADDITIONAL_LIBS in config.mk
#   2. Or copy the required .lib file into benchmark/design/sattva_sram/macro/
#   3. Re-run the floorplan stage
#
# Expected effect:
#   - Floorplan stage completes successfully after the Liberty file is available
#   - Downstream stages (place, cts, route) become reachable
#
# Earliest stage requiring rerun:
#   floorplan (stage 2_1_floorplan) — after lib is restored, re-run from this stage
#
# Verification criteria:
#   - `check -assert` 0 problems after floorplan
#   - Macro sram_x4x4x1 appears in the placed design without timing warnings
#   - Downstream stages proceed past floorplan

# Run revision and patch identity:
#   Baseline run: runs/orfs_baseline_20261118T152845Z
#   Patch: D-013 — restore missing .lib file reference