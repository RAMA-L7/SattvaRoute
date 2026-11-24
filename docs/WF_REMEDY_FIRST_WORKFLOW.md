# T-WORKFLOW-001 — Remedy-First Workflow Design and Implementation

## 1. Pipeline

```
FAILURE → DIAGNOSIS → KB RETRIEVAL + WEB RESEARCH → REMEDY RANKING
        → CANDIDATE SELECTION → SANDBOX TEST → VALIDATION → REPORT + KB
```

Implemented as `scripts/remedy_engine.py` (decision layer, no EDA) with `scripts/remedy_kb.py` (append-only structured memory sidecar extending the existing KB).

## 2. Stage contracts

| Stage | Input | Action | Output |
|---|---|---|---|
| FAILURE | log/signature | register signature | failure record |
| DIAGNOSIS | existing reports/evidence | **reuse**; never re-run root cause unless new evidence | `diagnosis` evidence block |
| KB+WEB | signature | `remedy_kb.retrieve` + `refuted_families` + `sattva_kb.kb_refuted_families`; attach cited sources | candidates + refuted set |
| RANK | candidates + weights | deterministic weighted score + hard gates | ranked list with component breakdown |
| SELECT | ranked list | top eligible above threshold; legality gate | candidate or actionable stop |
| SANDBOX | candidate | delegated to approved isolated harness; no implicit execution | `NOT_RUN` or harness outcome |
| VALIDATE | outcome | baseline/treatment + collateral checks | PASS/FAIL/INCONCLUSIVE |
| REPORT+KB | all of above | JSON report + idempotent append of an `engineering_conclusion` record (`report_kb`) | usable resolved/unresolved report + hashed KB write |

## 3. Automatic elimination rules

A candidate is ineligible if any of:
- family is in the KB/sidecar refutation set (`refuted_families`, `kb_refuted_families`);
- `applicability == INCOMPATIBLE`;
- `legality == FAIL`;
- `evidence_strength == UNKNOWN` and applicability is not `EXACT`;
- score below `selection_min_score` (default 0.62);
- already attempted in this cycle.

Legality `UNKNOWN` marks the candidate ineligible with reason `legality unverified`; `rank_and_select` converts this into `RISK_EXCEEDS_POLICY` with the candidate's recorded prerequisites and clears `selection` to `null` (the gated candidate is recorded under `evidence.gated_candidate`). Execution requires `authorized=True` plus an explicit harness callback; otherwise SANDBOX/VALIDATE are recorded as explicitly skipped.

## 4. Ranking

`score = Σ(weight_i × component_i)`, weights summing to 1.0:
evidence 0.30, applicability 0.25, effectiveness 0.20, risk 0.15 (inverted), cost 0.05 (inverted), reversibility 0.05. Full detail in `WF_REMEDY_RANKING.md`. Sorting is deterministic: `(-score, candidate_id)`.

## 5. Time budgets

Defaults in `config/remedy_budgets.json`: diagnosis 15 min, research 30 min, rank 10 min, selection 5 min, sandbox 45 min, validate 30 min, report 10 min; first attempt within 60 min; common issue 120 min; difficult issue 480 min. `BudgetTracker` uses an injectable clock for deterministic tests. Expiry sets `TIME_BUDGET_EXPIRED` and an actionable unresolved gap — never a fix.

## 6. Stop conditions

`FIX_VERIFIED`, `CANDIDATES_EXHAUSTED`, `RISK_EXCEEDS_POLICY`, `UNVERIFIED_PASS`, `TIME_BUDGET_EXPIRED`, `BASELINE_INTEGRITY_FAIL`, `UNAUTHORIZED_EXECUTION_REQUESTED`. A PASS result without `verified: true` and `independent_review: PASS` is `UNVERIFIED_PASS`, never a fix; a timeout neutralises a PASS to `INCONCLUSIVE`.

On a failed attempt, `record_failure_and_advance()` records the outcome and re-runs ranking, automatically evaluating the next qualified candidate.

## 7. Validation policy (enforced by contract, not by this engine)

Execution requires: reproducible baseline; pre-registered expected measurable outcome; isolated scratch copies; minimum necessary change; path-matched no-op control; baseline/treatment comparison; collateral DRC/routing/timing/functional check; independent review. Success is never declared from error disappearance alone. See `WF_TIME_BUDGET_AND_VALIDATION.md`.

## 8. Files

- `scripts/remedy_engine.py` — controller, ranking, budgets, stop conditions.
- `scripts/remedy_kb.py` — append-only hashed sidecar (12 structured record types).
- `scripts/seed_remedy_kb.py` — idempotent seeding from `knowledge/remedy_seed.jsonl`.
- `scripts/run_remedy_demo.py` — DRT-0073 demonstration, no EDA.
- `config/remedy_budgets.json` — configurable policy.
- `tests/test_remedy_engine.py`, `tests/test_remedy_kb.py` — 24 offline tests.

## 9. Boundaries

No EDA, no production/design/config modification, no remedy execution, no unverified fix claim. R2 remains advisory/inactive. Existing KB chain and immutable manifest are untouched.
