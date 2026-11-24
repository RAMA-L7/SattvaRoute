# T-WORKFLOW-001 — Time-Budget Policy and Validation Contract

## 1. Budgets

| Stage | Default |
|---|---|
| Initial diagnosis | 15 min |
| KB + web research | 30 min |
| Candidate selection | 10 min (plus 5 min select gate) |
| Sandbox (first remedy attempt) | 45 min; first attempt within 60 min of failure registration |
| Validation | 30 min |
| Report + KB | 10 min |
| Common issue total | 120 min |
| Difficult issue total | 480 min (1 working day) |

Configurable at `config/remedy_budgets.json`. `BudgetTracker` records elapsed, budget, remaining and expired flags at every stage (injectable clock for deterministic tests).

## 2. Timeout semantics

Timeouts **never** produce a fix. They produce:
- `stop_condition = TIME_BUDGET_EXPIRED`;
- the failing stage and elapsed/budget checkpoints;
- an actionable research gap (what measurement or evidence is missing);
- an append-only low-maturity KB record on future execution.

## 3. Validation contract

Every executed candidate must have:
1. reproducible baseline (hash-identified ODB/LEF/DEF/binary);
2. pre-registered expected measurable outcome;
3. isolated scratch copies — no `write_db` to inputs;
4. minimum necessary single-variable change;
5. path-matched no-op control;
6. metrics: AP CREATE/ACCEPT/DROP, per-direction clean flags, marker census by type/layer/bbox/source, DRT-0073/0305/0419, all-pin AP, route DRC, extraction/timing, collateral;
7. abort conditions: protected hash change; DRT-0305 recurrence; multi-variable edit; no-op control delta; suppression presented as fix; resource/authority failure;
8. independent review.

## 4. Candidate loop

If a candidate fails, record `{candidate_id, outcome: FAIL, reason}` and automatically re-rank the remaining qualified candidates. Stop only on verified fix (`FIX_VERIFIED`), unverified PASS (`UNVERIFIED_PASS`), exhausted candidates, risk-policy violation, budget expiry, integrity failure, or unauthorized request. A PASS without `verified: true` and `independent_review: PASS` is never a fix; a timeout neutralises any PASS to `INCONCLUSIVE`.

## 5. R2 status

`EXPERIMENT_DESIGN_CHECKLIST.md` R2 remains DRAFT/INACTIVE. Its A7/A14/A17 discipline is reflected as requirements here but R2 itself was not activated or modified.
