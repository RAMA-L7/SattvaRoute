# T-PNR-001 — PnR Orchestration Implementation and Recovery Gate

- **Date:** 2026-11-25
- **Status:** Implementation complete; control baseline accepted; controlled failure captured; human approval received; approved patch applied through existing enforcement boundary; recovery rerun rc=0 with endpoint artifacts verified.
- **No production/design/protected original changed.** The only recovery change is the approved patch to the attempt-local config.

## 1. Verified state at start

Publication HEAD `ac40255`, clean, equal to `origin/main`; KB 19/19, sidecar 22 records, immutable 9/9, validator 13/13; OpenFinRAM DRT-0073 case preserved as unresolved; R2 DRAFT/INACTIVE.

## 2. Corrections implemented

Twenty verified gaps closed: stage/total timing, hard expiry and cancellation, transitions/terminal states, approval binding, evidence-based verification, context-scoped refutations with reconsideration, locked KB transactions, shared dependency manifest, runner ordering/source-run identity/stale-output hashes, timeout/job ledger/resume dedup, CLI entry point, and a minimal diagnosis interface. Full list with file references: `IMPLEMENTATION_GAPS.md`.

## 3. Compatible control benchmark

Selected after preserving two failed ASAP7 feasibility attempts (Yosys 0.33 cannot read ASAP7 Liberty collateral): Nangate45 + platform `fakeram45_64x32` hard macro, at pinned ORFS `25b6429c1644a8682852646bebf19ff164402c76`. RTL wrapper and blackbox stub are synthesis placeholders only; a gate-level netlist was prepared in a separate step and PnR starts from it. Details: `CONTROL_BENCHMARK_SELECTION.md`, `BENCHMARK_PREPARATION.md`.

## 4. Baseline result (real artifacts, RC separate from verdict)

`runs/orfs_baseline_nangate_macro_control_20261125T144339456871595Z_11464`: all 8 stages rc=0. Routed ODB, guide, `6_final.odb/def/spef/gds`, `5_route_drc.rpt` (0 violations) and `6_finish.rpt` (setup/hold/slew/fanout/cap counts 0, TNS/WNs 0.00, worst slack 899.75 ns at 1000 ps) verified. Engineering verdict: BASELINE ACCEPTED. Acceptance criteria were frozen before treatment (`BASELINE_ACCEPTANCE_CRITERIA.md`).

## 5. Controlled failure and proposal

Fixture `experiments/PNR-RECOVERY/missing_macro_lib_20261125T145821Z/` changes only an attempt-local config: the macro Liberty reference points to a missing file. Real runner produced RC 2 at synth. Deterministic diagnosis classified `MISSING_MACRO_LIB`; optional model unavailable and explicitly labelled. Exact unified-diff proposal (`RESTORE_MACRO_LIB`, SHA-256 `8a7178f6…`) was presented and explicitly approved. Approval `AP-PNR-003` (operation `3205f326…`) was created/validated and the exact patch applied through `sattva_approval.py guard`. Recovered run `runs/orfs_baseline_recovered_final_20261125T152826305943439Z_27610`: rc=0 over the 6 approved stages (`synth…finish`, preflight/checks inherited from the baseline), routed ODB/SPEF/final reports present, `5_route_drc.rpt` empty (=0 violations; `DRT-0199 Number of violations = 0`), setup/hold/slew/fanout/cap counts 0. Three-way comparison in `experiments/PNR-RECOVERY/.../comparison.json`.

## 6. Tests and integrity

Offline: 33 remedy, 30 approval, 21 KB, 5 recovery-CLI, 14 runner checks — all PASS. Manifest PASS (28 hashed declarations). KB verify 19/19, sidecar 22/22 chain PASS, immutable 9/9, validator 13/13. Original macro LEF/GDS and ENG013/ENG014 docs unchanged byte-for-byte.

## 7. Open acceptance items

1. Live model diagnosis: `SATTVA_MODEL_URL` not configured; deterministic classification used, live-model item open.
2. External signoff DRC/LVS: outside milestone scope.
3. Live model acceptance remains open; the recovery diagnosis was deterministic and labelled.

## 8. Stop

The approved recovery is complete and verified from real artifacts. No further milestone, remedy, experiment, or production change without explicit authorization.
