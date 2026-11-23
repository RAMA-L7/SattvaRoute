# Session Handoff — T-SKILL-005 S001

- **Task:** Experimental Design Checklist revision (R1) and retrospective re-scoring.
- **Date:** 2026-11-23
- **Agent:** orchestrator + Agents A/B/C/D
- **Safe for another agent to continue:** YES after lock release.

## Deliverables
- `docs/EXPERIMENT_DESIGN_CHECKLIST.md` — R1, final SHA-256 `286c7bbaa53f2c936cc6bc2e87ddb34c9e640b80089051cb0be9d4bcf7b1fc4f`.
- `docs/EXPERIMENT_DESIGN_CHECKLIST_R0.md` — preserved R0, SHA-256 `a445c7ae48236456815e8ae2eb46faf48ad0784d2a0f83d2a77ffb58d9e0c091`.
- `docs/T-SKILL-005_CHECKLIST_REVISION_REPORT.md`, `docs/T-SKILL-005_RETROSPECTIVE_COMPARISON.md`.

## Key results
- R1–R12 + A13–A16 applied; A16 demoted to reference. A3/A7/A8/A12 defects resolved.
- Agent B ACCEPT WITH LIMITATIONS; no blocking findings; ED-1/ED-2 minor wording fixes applied.
- R1 re-score of same 8 cases: P13 / Q75 / F15 / UNKNOWN3 / N-A22 = 128 cells (120 gate-relevant, assessable 103). R0: P23/Q40/F16/?3/N-A14 = 96 (assessable 79). Denominators not directly comparable.
- Two conflicting Agent C notifications reconciled: only the on-disk report table recounts to the stated totals; the conflicting numbers were superseded.

## Invariants
Checklist still DRAFT/INACTIVE; no EDA, no activation, no production/baseline/KB/approval/history change;
no skill installed or status change; KB verify 18/18 + chain PASS; immutable 9/9 PASS; validator 13/13 PASS.

## Next
Explicit authorization required before a shadow/observational pilot or activation. Do not start another milestone.
