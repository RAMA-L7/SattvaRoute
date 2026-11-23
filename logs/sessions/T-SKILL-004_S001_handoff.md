# Session Handoff — T-SKILL-004 S001

- **Task:** retrospective experimental design validation of the inactive DRAFT checklist.
- **Date:** 2026-11-23
- **Agent:** orchestrator + Agents A/B/C/D
- **Safe for another agent to continue:** YES after lock release.

## Deliverables
- `docs/T-SKILL-004_RETROSPECTIVE_VALIDATION.md` — scope, 8 FDE cases, A1–A12 scorecard, weaknesses,
  effectiveness, integrity verification and verdict **REVISE**.
- `docs/EXPERIMENT_DESIGN_CHECKLIST_REVIEW.md` — R1–R12 exact revisions + proposed A13–A16 and adoption path.

## Key findings
- Checklist created 2026-11-23, after all audited runs; all results are retrospective counterfactuals,
  not violations of an active gate.
- FDE-005 had a genuine scoped no-flag control (A3 PASS); FDE-006U §10 says "no no-op control arm";
  FDE-007 used historical parity, not a concurrent control.
- AP candidates/markers are sub-units (N=1 run per arm); R1-N/R1-N-W are one `M4_OBS_CORRIDOR`
  family at two levels.
- Instrument defects: A3 self-contradictory/over-strict, A7 wrong key and term, A8 too broad,
  A12 `tools/` false positive; missing cost/stopping, toolchain identity and independent reviewer gates.

## Verification
KB verify PASS (18/18 + chain); immutable 9/9 PASS; validator 13/13 PASS; checklist SHA-256
`a445c7ae…d9e0c091` unchanged; no EDA, no activation, no KB/approval/protected/skill-status change.
Scorecard arithmetic corrected to P23/Q40/F16/?3/N-A14 after Agent D review.

## Next
Await explicit authorization before revising the checklist or running a shadow pilot. Do not start
another milestone.
