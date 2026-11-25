# T1 — Coordinator Adjudication of Independent Review

Reviewer: Agent D (`T1_D_review.md`), did not implement the provider. Verdict: **ACCEPT WITH FIXES, no blocker**.

## Findings and resolution

| Reviewer finding | Resolution |
|---|---|
| Fabricated refs in `contradicting_evidence` were not checked | **FIXED** — `validate_refs()` now walks all evidence-bearing fields; added regression test. |
| `execution_kind=live_api` when no request was made | **FIXED** — skip path emits `not_invoked`; candidate path emits `live_api_candidate`; stub remains explicit for injected test transports. `live_call.json` regenerated showing `not_invoked`. |
| `GT_LEAK` / `SCHEMA_INVALID` gates were constants in grader | **FIXED** — grader now computes both from output tokens and `validate_schema()`; added regression test. |
| GT file mode 0600 ineffective on WSL 9p `drvfs` (reports 777) | **DOCUMENTED LIMITATION** — GT is logically isolated (separate file, never read by prompt/builder); no OS-level restriction is claimed on this mount. If strict filesystem isolation is required, store GT outside the 9p mount or apply Windows ACLs. |
| Benign `PNR-RECOVERY` path string inside verbatim make-error excerpt | **ACCEPTED** — it is part of the real failure log, not a recovery outcome or approval. Explicit allow-case; deny-list covers leak tokens that matter (`RESTORE_MACRO_LIB`, approval IDs, patch hash, recovered run, `comparison.json`). |
| Theoretical prompt-injection surface from verbatim evidence | **ACCEPTED with mitigation** — model has no execution/patch/approval authority; output is validated and advisory. No injection present in this run. |
| All other checks (GT exclusion, E04/E05 provenance, deterministic scoring, no live call, safety, reproducibility) | **VERIFIED** — no correction required. |

## Authoritative conclusion

- Provider path audited; advisory-only bounded provider implemented without touching the verified recovery engine.
- Deterministic diagnosis accepted (12/12 ordinal CORRECT, hard gates clear).
- Live model **NOT RUN** because URL/credentials are unset; `SKIPPED_NO_CREDENTIALS`, no HTTP, no tokens/latency/cost. No fixture or replay was presented as live.
- Offline suite: **21 tests PASS** in `test_live_diagnosis.py`; existing regression suites pass.
- Acceptance remains BLOCKED only on real provider configuration; no recovery, patch, approval, EDA, or design/protected change occurred.

## Stop

No further milestone, remedy, experiment, or production change without explicit authorization.
