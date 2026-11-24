# T-WORKFLOW-001 — Remedy Ranking Methodology

## 1. Score

`score = Σ wᵢ · cᵢ` with `w = {evidence: 0.30, applicability: 0.25, effectiveness: 0.20, risk: 0.15, cost: 0.05, reversibility: 0.05}` (sum = 1.0, enforced by `load_budgets`).

| Component | Mapping |
|---|---|
| evidence | DIRECT_FIX 1.0; DOCUMENTED_FIX 0.9; SOURCE_VERIFIED 0.85; PAPER/DIRECT_EXPERIENCE 0.6; ANECDOTE 0.4; INFERENCE 0.2; UNKNOWN 0 |
| applicability | EXACT 1.0; HIGH 0.8; PARTIAL 0.5; INCOMPATIBLE/UNKNOWN 0 |
| effectiveness | caller-supplied predicted effectiveness ∈ [0,1] |
| risk | `1 − risk ∈ [0,1]` |
| cost | `max(0, 1 − cost_minutes / COMMON_ISSUE_TOTAL)` |
| reversibility | FULL 1.0; PARTIAL 0.5; NONE 0 |

## 2. Hard gates (applied before score is considered)

1. refuted family (KB sidecar or existing KB ledger) → ineligible;
2. applicability INCOMPATIBLE → ineligible;
3. legality FAIL or UNKNOWN → ineligible (`physical legality failed` / `legality unverified`); sets `RISK_EXCEEDS_POLICY` with prerequisites if no legal candidate remains;
4. evidence UNKNOWN with non-EXACT applicability → ineligible;
5. score < `selection_min_score` (0.62) → not selected;
6. already attempted this cycle → skipped.

## 3. Tie-break

Descending score, then ascending `candidate_id` — deterministic across runs.

## 4. Evidence grading policy

- Tier A: LEF/DEF spec, upstream merged fix, tool source code.
- Tier B: maintainer issue report, peer-reviewed paper, established industry practice.
- Tier C: unmerged PR, community discussion, teaching material.
- Tier D: inference from prior local evidence.
- A grade-A source that proves **predicate mismatch** (e.g., abutment-only fix vs true-overlap Short) is a `REFUTES` veto, not a positive score.

## 5. Legality gate (before TESTABLE)

Required prerequisites: full-region GDS foreign-net census; rule-envelope proof; all-pin AP survey; no-op-controlled single-variable A/B; collateral DRC/route/timing plan; fresh decision approval. `UNKNOWN` legality does not authorize testing.

## 6. Verified fix criteria

A fix is VERIFIED only when: baseline/treatment delta is measured; original error is gone; no new DRT codes; all-pin AP preserved/improved; collateral DRC/routing/timing/functional checks pass; independent review recorded; protected hashes unchanged. Otherwise at most PROVISIONAL.
