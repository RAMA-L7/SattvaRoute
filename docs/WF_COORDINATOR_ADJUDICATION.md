# T-WORKFLOW-001 — Coordinator Adjudication

## 1. Conflicts resolved

| Conflict | Adjudication |
|---|---|
| Agent A ranked LEF OBS `SPACING` / `USEMINSPACING OBS` as top candidates vs Agent B's source proof that they only affect abutment/prl | **B adopted** — wrong-predicate candidates are auto-refuted and stored as `OBS_SPACING_SEMANTICS` refuted family |
| Agent C: no implementable fix credible vs potential generator path in A | **C adopted**, reinforced by coordinator's direct read of `lef_extractor.cpp:285-292` (hard-coded full-body OBS) |
| Reviewers demanded executable harness vs milestone constraint (no EDA) | **Constraint upheld** — controller layer only; `execute` callback and `authorized` flag are explicit handoff points, not implicit execution |

## 2. Implementation acceptance

Both post-implementation reviewers returned ACCEPT WITH FIXES. All major and medium findings were fixed and re-tested (documented in `WF_INDEPENDENT_REVIEWS.md`). No finding was rejected without justification. Final offline test count: 24 PASS; KB verify 19/19; sidecar verify 22 records PASS; immutable 9/9; validator 13/13.

## 3. What this milestone did and did not do

**Did:** audit architecture; add remedy-first controller, structured memory sidecar, ranking, time budgets, legality gate, failed-attempt advance, report+KB write-back, tests, and an honest DRT-0073 demonstration that stops with actionable prerequisites.

**Did not:** run EDA; design geometry; execute a remedy; modify production/design/config/baseline; activate R2; rewrite historical reports; claim a fix for DRT-0073.

## 4. Authoritative decision record

D-028 records the workflow addition as ACTIVE. DRT-0073 remains unresolved (ENG015 NO-GO); this milestone does not reopen or override it. The workflow's output for DRT-0073 is `RISK_EXCEEDS_POLICY` with named prerequisites — a useful unresolved state, not a fix.

## 5. Stop

Milestone boundary reached. No further milestone, remedy, experiment, implementation, or production change without explicit user authorization.
