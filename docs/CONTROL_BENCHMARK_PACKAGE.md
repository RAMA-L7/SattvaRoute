# Control benchmark package — T-PNR-001 `nangate_macro_control`

The selected reproducible control benchmark (Phase 1 + Phase 3).

## Selection

**Nangate45 + `fakeram45_64x32`**, ORFS `25b6429c…`, project-owned
`sattva_macro_top` wrapper + prepared gate-level netlist. Historical baseline
`orfs_baseline_nangate_macro_control_20261125T144339456871595Z_11464` (8 stages
rc=0, DRT-0199→0, SPEF 201261 B, RCX 209 nets) accepted from real artifacts.
ASAP7/riscv32i (`sattva_sram`, `riscv32i_sattva`) is historical/inactive;
**DRT-0073 remains unresolved and is not reopened**; OpenFinRAM evidence is
preserved and excluded. 

## Contents (`benchmark/design/nangate_macro_control/`)

See `docs/REPRODUCIBILITY.md`. config, `constraint.sdc` (preserved) +
`constraint_1ns.sdc` (applied; `SDC_FILE`→1 ns), wrapper RTL, macro blackbox,
prepared netlist + provenance. Not yet mirrored to public `origin/main` (see
publication status); not claimed published remotely.

## Timing

Executed **1000 ns** clock (1 MHz) in historical `...1144339456871595Z_11464`;
units **1ns**, `typical`, 1.1V, 25C, extracted post-route SPEF, coverage
complete, `setup=0 hold=0`. **1000× unit error vs documented 1 ns intent.**
**Approved applied** `constraint_1ns.sdc` (1 ns); new
`orfs_baseline_control_1ns_20261126T133241476241945Z_4600` PASS, `setup=0 hold=0`,
`worst slack≈0.64/0.08`, `period_min=0.36/fmax≈2760`, coverage complete.
`docs/TIMING_AUDIT.md`. **Not** timing-closure-representative; abstract
FakeRAM; no signoff.

## Recovery on this benchmark

Generalized bounded diagnosis (Phase 6) + frozen evaluation v2 (Phase 7) +
exact-patch approval (`scripts/sattva_approval.py`) + independent verification
(`scripts/verify_run.py`). Historical `T-PNR-001` `AP-PNR-003`/`RESTORE_MACRO_LIB`
on `missing_fakeram45_64x32.lib` is historical evidence only. One **new**
held-out case (attempt-local `ADDITIONAL_LEFS` → nonexistent macro LEF; floorplan;
within-family-adjacent) is the Phase-8 trial — see `docs/HELDOUT_RECOVERY.md`.
**Nothing applied without explicit approval.**

## Verification

`python3 -m unittest discover -s tests`. `scripts/verify_run.py`.
`scripts/manifest.py --check`. See `docs/VERIFICATION.md`.
