# SDC and timing constraints

Status: verified from tool evidence. Authoritative history: `docs/TIMING_AUDIT.md`. Preserved evidence: `evidence/timing/`.

## Units must be read, not assumed

OpenROAD `report_units` for the pinned run declares:

- time = **1 ns**
- capacitance = **1 fF**
- resistance = **1 kΩ**

The pinned Nangate45 Liberty declares `time_unit: 1ns` (corner `typical`, 1.1 V, 25 °C). The `fakeram45_64x32.lib` declares `time_unit 1ns` (`tt_1.0_25.0`). Therefore a bare clock period number is in nanoseconds.

## The historical 1000× discrepancy

- Historical `constraint.sdc` specified a period of **1000** (intended as 1 ns, but executed as **1000 ns**).
- Documentation and intent described a 1 ns clock.
- Tool evidence (`report_units`, Liberty) established the 1000× mismatch; it was not resolved by preference or by editing reports.
- Correction: `constraint_1ns.sdc` (period 1 ns) was explicitly approved and applied by repointing `config.mk`'s `SDC_FILE`.
- `constraint.sdc` is preserved verbatim; it is not active and its historical runs are not relabeled.
- New baseline `orfs_baseline_control_1ns_20261126T133241476241945Z_4600` PASS; `verify_run` PASS. The historical baseline at 1000 ns remains a historical record.

## Intermediate vs final constraints

`updated_clks.sdc` is an intermediate CTS artifact. It is not the constraint that was executed for the final run. Timing claims must reference the active `constraint_1ns.sdc` and the final reports (`6_finish.rpt`), not the CTS intermediate.

## Interpretation rules

- Read `report_units` before interpreting any period/slack number.
- Extracted timing uses `6_final.spef`; STA reports are only as good as extraction completeness (RCX-0045 count, unannotated drivers).
- Zero DRT violations and clean antenna do not prove timing closure.
- Timing numbers do not prove functional correctness.

## Verified usage

```
python3 scripts/timing_audit.py --run <run> --platform <orfs>/flow/platforms/nangate45 \
  --macro-lib fakeram45_64x32.lib --out <audit.json>
python3 scripts/verify_run.py --run <run> --audit <audit.json>
```

`timing_audit.py` is read-only; it does not change constraints.

## Related

`docs/TIMING_AUDIT.md`, `evidence/timing/`, `docs/engineering/VERIFICATION_BOUNDARIES.md`, `docs/reference/GLOSSARY.md`.
