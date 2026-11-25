# T-PNR-001 — Frozen Acceptance Criteria (before any treatment)

Recorded 2026-11-25 after baseline artifact review and before failure injection. These thresholds are not changed after seeing treatment results.

## Control baseline (reference)

- Run: `orfs_baseline_nangate_macro_control_20261125T144339456871595Z_11464`
- All 8 stages rc=0; `overall_rc=0`.
- Required artifacts present: `5_route.odb`, `route.guide`, `6_final.odb`, `6_final.spef`, `6_final.def`, `6_final.gds`, `6_finish.rpt`, `5_route_drc.rpt`.
- `5_route_drc.rpt` has 0 reported violations; `6_finish.rpt`: setup violation count 0, hold violation count 0, max slew/fanout/cap violation counts 0; worst setup slack 899.75 ns at 1000 ps target.
- Engineering verdict: BASELINE ACCEPTED as control reference (separate from RC).

## Required recovery outcome

1. Failure attempt must fail in a real ORFS stage with evidence (stage log, stages.tsv, run.json), not by a simulated response or preflight-only trick.
2. Exact injected change is recorded and confined to an attempt-local config copy; original benchmark config/RTL/SDC/macro views/technology data unchanged.
3. Agent proposal is evidence-grounded, reviewable, exact (unified diff + SHA-256), and PENDING human approval. No patch applied before that approval.
4. After approval, only the approved patch is applied through `sattva_approval.py`; runner revalidates source-run identity, fingerprints and rerun scope immediately before execution.
5. Recovered attempt must reach the same endpoint with rc=0 and all required artifacts present.
6. Recovered `5_route_drc.rpt` must report 0 violations; `6_finish.rpt` must report setup/hold/slew/fanout/cap violation counts 0.
7. No protected artifact hash changes; OpenFinRAM case remains unresolved; R2 remains advisory/inactive.
8. Baseline, failure and recovery are compared from structured evidence (`run.json`, `stages.tsv`, reports, artifact hashes).

## Stop conditions

Stop and leave acceptance open on: model credentials unavailable for live-model item; physical legality uncertain; new collateral violations; baseline/protected integrity failure; no explicit approval at the gate.
