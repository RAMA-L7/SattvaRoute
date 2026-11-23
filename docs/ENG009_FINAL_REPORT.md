# T-ENGINEERING-009 — DRT-0073 Root-Cause Investigation and Engineering Recovery: Final Report

- **Session:** 2026-11-23/24
- **Status:** COMPLETE at the diagnostic decision boundary. No experiment executed, no remedy applied, no production change.
- **Verdict:** one major uncertainty narrowed with concrete evidence; next diagnostic technically justified and independently challenged.

## 1. Executive summary

The investigation reconciled FDE-003–007 without duplication. The bounded root cause remains: the full-body M4 master OBS blocks planar escape of the thin M4 `clk` pin in the FDE-006U scratch DB (0→3 accepted APs when the broad window was removed). Two physically narrower corridor variants failed, and the failure mechanism is now better characterised: the ±24 nm y margin is smaller than the ~48 nm M4 EOL/corner-keepout envelope, so residual OBS bands generate spacing/EOL markers; M5 via-landing shorts are contributing but not decisive. The decisive remaining uncertainty is **marker provenance** — `getSrcs()` is API-available but was never logged, leaving the 2 nm sliver INCONCLUSIVE.

DRT-0419 was investigated separately and is **not** a shared mechanism with DRT-0073 (different code, phase, severity, pins/layer; count invariant at 8; persists where DRT-0073 was removed). D/Q pin AP status remains UNTESTED.

## 2. Deliverables

- `ENG009_CURRENT_STATE_AUDIT.md` — verified repository/tool/KB state and FDE lineage.
- `ENG009_DRT_FAILURE_INVENTORY.md` — DRT-0305 / 0073 / 0419 / MPL-0005 inventory.
- `ENG009_HYPOTHESIS_MATRIX.md` — 18 hypotheses classified CONFIRMED / SUPPORTED / WEAKENED / ELIMINATED / UNTESTED.
- `ENG009_MEASUREMENT_CAPABILITY_REPORT.md` — available, partly available and missing measurements.
- `ENG009_PRIOR_EXPERIMENT_REVIEW.md` — lessons and unknowns from FDE-005/006T/006U/007.
- `ENG009_NEXT_STEP_PLAN.md` — ranked diagnostics by information gain, cost, risk, reproducibility.
- `ENG009_PROPOSED_DIAGNOSTIC_EXPERIMENT.md` — ENG009-DIAG-001 technical design with R2 advisory shadow assessment.
- `ENG009_AGENT_FINDINGS_AND_ADJUDICATION.md` — Agents A/B/C/D and resolution of five blocking findings.
- This final report; project state, coordination and logs updated.

## 3. Major uncertainty narrowed

- **Before:** narrow-corridor failure was attributed partly to a 2 nm boundary sliver of unknown origin.
- **Now:** the sliver is known to be boundary-correlated; `getSrcs()` is directly verified present in the instrumented source (`frMarker.h:67/73/80`), and the instrumented binary `0d890431…` is verified on disk. The missing measurement is feasible at low cost.
- **Still unknown:** actual source object per marker; whether the sliver is artifact or real metal; all-pin AP status; full-flow DRC/extraction/timing.

## 4. Next experiment (proposed, not authorized)

**ENG009-DIAG-001 — marker provenance and keepout-envelope diagnostic**, class `causal diagnostic` for instrumentation behavior only. Arm A = concurrent identity replay with existing instrumented binary; Arm B = same build with log-only `getSrcs()`/`getVictims()`/`getAggressors()` additions. One variable, frozen ODB, no geometry change. Pre-registered criteria include Arm A/B equivalence (production binary compared at aggregate level only), ≥90% operationally-defined marker attribution, GDS-backed sliver classification, mandatory static EOL/GDS pre-work, cost cap, and abort conditions. R2 applied advisory shadow only; no activation.

Independent Agent D initially found five blocking issues — unmeasurable equivalence, semantic A3 dodge, vague attribution rules, over-stated y-envelope inference, and post-hoc geometry risk. All five were resolved in the revised proposal (see adjudication doc). Agent D's conditional ACCEPT now holds; the proposal remains **not authorized**.

## 5. Verification results

| Check | Actual |
|---|---|
| KB `verify` | PASS — 18 records, 18-link chain, 0 problems |
| `verify-immutable` | PASS — 9/9 protected artifacts, `changed=[]` |
| `.skills/validate_skills.py` | PASS=13 FAIL=0 |
| R2 checklist hash | `6900ebc8…cb9d` unchanged, DRAFT/INACTIVE |
| Instrumented binary | `0d890431…` verified present |
| `getSrcs()` API | verified at `frMarker.h:67` (plus victims/aggressors) |
| EDA / experiment / approval / production change | none |

## 6. Files changed

Created the eight `ENG009_*.md` deliverables listed above; updated `PROJECT_STATE.md`, `coordination/TASK_BOARD.md`, `coordination/ACTIVE_WORK.md`, logs and handoff. No historical FDE report, KB record, approval control, baseline, production artifact or skill status changed.

## 7. Limitations

- Static/source evidence only; no new measurement was collected by executing a tool.
- y-envelope account is INFERRED, not experimentally tested.
- DRT-0419 D/Q AP status remains UNTESTED.
- One prospective diagnostic proposal; no effectiveness or preventive claim.

## 8. Stop condition

Stop at the diagnostic decision boundary. Explicit authorization is required before rebuilding the instrumented binary, replaying ODB, launching any flow, applying a remedy, or starting another milestone.
