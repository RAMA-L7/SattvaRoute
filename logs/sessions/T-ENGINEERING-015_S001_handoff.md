# Session Handoff — T-ENGINEERING-015 S001

- **Task:** Evidence-driven research, remedy validation, and fix (T-ENGINEERING-015).
- **Date:** 2026-11-24
- **Agent:** orchestrator + Agents A/B/C (read-only research)
- **Safe for another agent to continue:** YES after lock release.

## Outcome
**NO-GO at Phase 2 research gate.** No credible research-supported candidate survives. No Phase 3 experiment, Phase 4 fix, source patch, geometry change, or production change was made.

## Key findings
- Failure is a true overlap Short against the target macro's own fixed M4 OBS; probe endpoint x4716 lies inside rect 4704–4764.
- Documented LEF/upstream fixes (OBS `SPACING 0` PR #10856, `USEMINSPACING OBS`, issue #1550) affect only abutment/prl spacing — source-proven inapplicable to this Short.
- No config knob creates AP 1; `set_ppl_mode` absent; `clk` exactly on M4 track #345 (PR #12162 inapplicable); no upstream backport after local `a77fc27`.
- Narrow carves fail due to 12 nm new-edge gap (< 24/25 nm); broad carve's 1986 nm clearance explains success but is physically illegal.
- Local macro generator hard-codes full-body M1–M5 OBS; no pin-aware configurability.

## Deliverables
`docs/ENG015_BASELINE_RECORD.md`, `_RESEARCH_REPORT.md`, `_CANDIDATE_COMPARISON.md`, `_RESEARCH_GATE.md`, `_INDEPENDENT_REVIEWS.md`, `_COORDINATOR_ADJUDICATION.md`, `_FINAL_REPORT.md`, updated `REPORT_INDEX.md`, state/task board/logs.

## Invariants
No EDA/source/geometry/ODB/LEF/DEF/GDS/config/production change. KB 19/19, protected 9/9, validator 13/13. R2 advisory/inactive.

## Next
Stop. Explicit authorization required for any future work.
