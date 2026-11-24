# T-ENGINEERING-013 — Directional Planar DRC Blocker Attribution: Final Report

- **Date:** 2026-11-24
- **Status:** COMPLETE. Stop at this milestone; no remedy or follow-up authorized.
- **Verdict:** westward blocker **CONFIRMED at shape level** — fixed M4 master-OBS rectangle `(4704,16560)-(4764,16584)`.

## 1. Evidence

- Log-only patch adds aggressor/victim rectangle and fixed flag to the existing provenance log; diff `8495405b…`, source `0815de7d…→797b282c…`, binary `7461d0d0…→db876fbf…`.
- Neutrality: debug-off identical except pre-existing sparse line; debug-on changes only PROV lines (107/107) by adding `rect=`/`fixed=`; all counts unchanged.
- Control ODB `662993ad…`: W `dir=3 clean=false` 9/9; blocker `Short` cid=0 rid=48 M4, aggressor `u_sram#3:292@L8`, `rect=(4704,16560,4764,16584)`, `fixed=1`; 9 CREATE / 0 ACCEPT / DRT-0073=2.
- Broad ODB `616e39f8…`: that west rectangle is carved out; W clean 3/3; 3 ACCEPT; DRT-0073=0; only E-side strip `(4880,16560,4902,16584)` remains.

## 2. Blocking object classification

Fixed M4 master obstruction (OBS), **not** a pin shape, not routing metal, not a rule-derived keepout alone. The EOL/spacing and via-stage M5 markers are non-binding (broad accepted x=4836 with them present). The instance-level `u_sram` label is an attribution artifact of `addTargetObj(inst)`; the stable evidence is layer + rectangle + fixed flag.

## 3. Independent review

Agent A source trace, Agent B instrumented replay, Agent C blind challenge. C's geometry prediction matched B's measured rectangle; all discrepancies reconciled in `ENG013_INDEPENDENT_REVIEW_AND_ADJUDICATION.md`.

## 4. Deliverables and integrity

Created `ENG013_DIRECTIONAL_PLANAR_DRC_REPORT.md`, `ENG013_PREDICATE_FAILURE_TRACE.md` (within directional report), `ENG013_BLOCKER_ATTRIBUTION.md`, `ENG013_GEOMETRY_CORRELATION.md` (within attribution), `ENG013_INSTRUMENTATION_NEUTRALITY.md` (within directional report), `ENG013_INDEPENDENT_REVIEW_AND_ADJUDICATION.md`, `ENG013_ROOT_CAUSE_MATRIX_UPDATE.md` (ENG012 hypothesis matrix updated), this report; state/logs/handoff updated. Scratch artifacts in `experiments/ENG013-BLOCKER/…`.

KB verify PASS (19/19), protected artifacts 9/9, validator 13/13, R2 unchanged/inactive, no production/geometry change.

## 5. Limitations / stop

Literal tech-LEF rule text for rid 48 UNKNOWN; all-pin AP and full-flow DRC/timing NOT EVALUATED. Do not initiate a remedy study, geometry modification, or follow-up experiment without explicit authorization.
