# T-WORKFLOW-001 — Independent Agent Reviews

## Phase 1 audits (read-only, blind)

| Role | Report | Contribution |
|---|---|---|
| Research Engineer | `WF_R_audit.md` | KB robust but stops at ENG010; refutations prose-only; `assess` needs caller justification; no web-source ledger. Designed 12-field query signature, 4-layer refutation detection, KB-compatible record shape, source tiers A–D, ≤6 queries/≤30 min/≤12 URLs. |
| EDA Source Engineer | `WF_S_audit.md` | Re-verified fail path (`FlexPA_acc_point.cpp:873`, `FlexGC_main.cpp:643-701/800-849`); `USEMINSPACING`/`SPACING 0` are prl/abutment-only — wrong-predicate candidates cost a review cycle. Designed tool/version→signature→mechanism index and 10 auto-reject rules. |
| Physical Design Engineer | `WF_P_audit.md` | Prior work checked mechanism, not legality. G1–G8 legality preconditions, R-A…R-G hard rejects, six weighted ranking factors, all-pin/collateral criteria; DRT-0073 candidates auto-eliminated, none promotable. |
| Validation Engineer | `WF_V_audit.md` | Framework is a verification boundary, not a resolution controller. Designed 8-state machine, budgets, controls/metrics/abort list, candidate cap, 40 proposed tests, and unresolved-report semantics. |

## Phase 2 post-implementation reviews

### REV1 — Implementation reviewer (`WF_REV1_impl.md`): ACCEPT WITH FIXES
- **MAJOR:** `selection` set before legality gate and not cleared → demo named `C-GEN` as selection while stop was `RISK_EXCEEDS_POLICY`.
- **MAJOR:** timeout did not neutralise a PASS (`TIME_BUDGET_EXPIRED` + `execution_state=PASS`).
- **MAJOR:** `FIX_VERIFIED` never emitted; PASS without evidence mislabelled.
- **MAJOR:** `INCONCLUSIVE` treated as refutation, over-eliminating families.
- MINOR: dead per-stage budget enforcement, caller-object mutation, no head check, append without chain check, missing execution-callback tests.

### REV2 — Workflow/evidence reviewer (`WF_REV2_design.md`): ACCEPT WITH FIXES
- F1: `workflow` claimed 8 stages but FAILURE was never appended and SANDBOX/VALIDATE were silently short-circuited.
- F2: REPORT+KB write-back not implemented.
- F3: `FIX_VERIFIED` unreachable.
- F4–F7: approval gate, EDA harness, automated legality gate, live web research are capability gaps; misleading selection on gated stop.

## Fixes applied by coordinator (all reviews resolved)

1. `selection` cleared on any gate rejection; gated candidate recorded as `evidence.gated_candidate` (REV1/REV2).
2. Timeout now neutralises PASS → `INCONCLUSIVE` with `timeout_neutralised_pass` evidence (REV1).
3. `FIX_VERIFIED` emitted only with `state=PASS`, `verified=true`, `independent_review=PASS`; otherwise `UNVERIFIED_PASS` (both reviewers).
4. `INCONCLUSIVE` removed from refutation outcomes in both engines (REV1).
5. FAILURE stage appended at init; SANDBOX/VALIDATE explicitly recorded as `SKIPPED` when no harness (REV2).
6. `report_kb()` appends an idempotent hashed `engineering_conclusion` record after chain verification (REV2).
7. Per-stage budgets enforced in `_stage`; family-alias normalisation added; candidates copied instead of mutated; stop conditions validated; sidecar `verify` supports `expected_head`; append refuses broken chain (reviewers' minor findings).
8. Added tests for execution callback, verified PASS, unverified PASS, timeout+PASS, unauthorized execution, INCONCLUSIVE handling, head check, broken-chain append. Total: 24 offline tests, all PASS.

## Residual gaps acknowledged

No EDA harness or approval-token integration is implemented (deliberate boundary); web research is static replay of ENG015 sources; legality evidence remains caller-supplied; R2 stays advisory/inactive. These are documented prerequisites, not hidden assumptions.
