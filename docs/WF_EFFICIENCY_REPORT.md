# T-WORKFLOW-001 — Before/After Workflow Comparison and Engineering Efficiency

## 1. Before (historical, VERIFIED from dated reports)

| Metric | Observation |
|---|---|
| DRT-0073 elapsed | ~6 calendar days (2026-11-18 → 11-24) |
| Milestones | FDE-004…007, ENG009…015 (11+ milestones) |
| Agents per milestone | 3–4, plus independent reviewers and adjudication |
| Diagnostic build blockers | 3 sessions lost (FDE-006/006R/006S) |
| Machine-readable refutations | none; ENG011–015 refutations prose-only |
| Resolution controller | none; runner enforced verification only |
| R2 checklist | DRAFT/INACTIVE |
| Refuted remedies re-evaluated | yes (narrow carve family repeated across FDE-007, ENG011, ENG014, ENG015) |

## 2. After (implemented this milestone)

| Metric | Observation |
|---|---|
| Diagnosis reuse | automatic via 21-record hashed remedy ledger + existing KB |
| Research sources | 5 cited URLs with evidence grade and applicability predicate |
| Refutation registry | 10 refuted families machine-readable; 8/10 demo candidates auto-eliminated |
| Ranking | deterministic weighted score with component traceability |
| Time budgets | configurable, injected clock, stage checkpoints, unresolved on expiry |
| Legality gate | blocks top-ranked candidate with explicit prerequisites |
| Failed-attempt loop | automatic advance to next qualified candidate |
| Tests | 24 new offline tests; all existing suites still PASS |
| EDA/production change | none |

## 3. Measured demonstration result

Using the old workflow, DRT-0073 required multiple approvals, repeated narrow-carve experiments and three diagnostic-build sessions before reaching a NO-GO gate (ENG015). Using the new engine, the same case reached an actionable NO-GO (`RISK_EXCEEDS_POLICY` with four named prerequisites) from stored evidence in a single reproducible offline run (`scripts/run_remedy_demo.py`, seconds of CPU time).

**Important limitation:** this is a workflow demonstration, not a resolution. No fix exists for DRT-0073 under current evidence, so "time to fix" remains unbounded by design. The efficiency gain is in time-to-decision, not time-to-fix. Exact historical hours-per-stage were not recorded, so a numeric hours-saved figure is UNKNOWN.

## 4. Efficiency principles realized

1. Retrieve before researching; research before ranking; rank before testing.
2. Eliminate refuted families before spending any sandbox budget.
3. Pre-register expected outcome and abort conditions; a no-op control is mandatory.
4. Timeouts produce useful unresolved reports, not endless investigation.
5. Verified fix requires measurable delta plus collateral checks plus independent review.
6. Negative results become reusable memory immediately.

## 5. Remaining inefficiency

Real EDA execution remains gated by explicit approval and an external harness; the engine deliberately does not own that boundary. Research fetch is agent-driven because the websearch integration returned HTTP 402. These are documented gaps, not hidden assumptions.
