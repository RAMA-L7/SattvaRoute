# T1 — Live AI Diagnosis Validation (T-PNR-001 failure evidence)

- **Date:** 2026-11-25
- **Status:** Implementation and offline evaluation PASS. **Live invocation BLOCKED** (no provider URL/credentials configured). No live-model acceptance claim is made.
- **Boundary:** diagnosis-only. No EDA, no patch application, no approval, no recovery, no benchmark/design change.

## 1. Current provider status

Audited (`T1_A_provider.md`): before T1 there was no real provider layer — only `diagnosis_agent.py:optional_model_note()`, one hard-coded OpenAI-compatible `urllib` call with a fixed 30 s timeout, zero retries, no structured output, no typed status, and unsanitized error text. `app/{backend,frontend,worker}` are empty; no SDK/service exists. Variables `SATTVA_MODEL_URL`, `SATTVA_MODEL_NAME`, `SATTVA_MODEL_KEY` and common provider keys are **unset** (presence-only checks; values never read).

T1 adds an isolated bounded provider layer without changing the verified deterministic/recovery path.

## 2. Implementation changes

| File | Change |
|---|---|
| `scripts/live_diagnosis.py` | NEW. OpenAI-compatible provider adapter with configurable URL/model/timeout (1–120 s), bounded retries (1–3), 429/Retry-After and 5xx handling, rate-limit/auth/transport/timeout/malformed status taxonomy, JSON-mode request, strict 14-field schema validation, evidence-reference resolution, credential redaction, sanitized errors, telemetry, and explicit `execution_kind` labeling. Advisory only: no execution, patch, or approval authority. |
| `scripts/evidence_package.py` | NEW. Builds a frozen model-input bundle `E01..E06` from the real T-PNR-001 failure and writes grader-only `gt.json` separately. Asserts ground-truth token deny-list absence from prompt. Failed config is sourced from a backup snapshot and presented under a neutral name. |
| `scripts/evaluate_diagnosis.py` | NEW. Deterministic rule-based diagnosis from the same bundle and a 12-metric ordinal rubric with hard gates (GT leak, fabricated refs, schema invalid). No aggregate accuracy percentage. |
| `scripts/pnr_cli.py` | Added `live-diagnose` command only; existing `diagnose`/`propose`/`resume` behavior unchanged. |
| `tests/test_live_diagnosis.py` | NEW. 21 offline tests with stub transport; no network or credentials. |

## 3. Provider configuration and credential setup

```
export SATTVA_MODEL_URL="https://provider.example/v1/chat/completions"   # required to enable
export SATTVA_MODEL_NAME="..."                                          # exact model id
export SATTVA_MODEL_KEY="..."                                           # optional Bearer token
export SATTVA_MODEL_PROVIDER="openai-compatible"                         # only supported wire shape
export SATTVA_MODEL_TIMEOUT_SECS=30                                      # capped 1..120
export SATTVA_MODEL_MAX_ATTEMPTS=1                                       # capped 1..3
export SATTVA_MODEL_MIN_INTERVAL_S=0                                     # capped 0..5
export SATTVA_MODEL_TEMPERATURE=0
export SATTVA_MODEL_MAX_TOKENS=1200
```

Run: `python3 scripts/pnr_cli.py live-diagnose --bundle experiments/T1-LIVE-DIAG/T-PNR-001/v1 --gt .../gt.json --out .../live_call.json`.

Credentials are read from the environment only, sent in an Authorization header, and never written to logs/artifacts (`record['credential_present']` is Boolean). Raw provider responses are stored redacted, without headers. No secondary/paid fallback exists; unset URL yields `SKIPPED_NO_CREDENTIALS` with zero requests.

## 4. Structured output schema

Required fields: `failure_class`, `failed_stage`, `primary_hypothesis`, `supporting_evidence`, `contradicting_evidence`, `alternative_hypotheses`, `confidence`, `proposed_action`, `patch_candidate`, `expected_effect`, `affected_stages`, `risk_assessment`, `verification_plan`, `missing_information`. Every evidence reference must be `E01..E06` with a verbatim excerpt whose hash matches the bundle. Fabricated IDs, paraphrased excerpts, malformed JSON and missing fields are rejected (`REF_FABRICATION`/`MALFORMED_RESPONSE`/`SCHEMA_INVALID`). Confidence alone never determines validity.

## 5. Evidence package and ground-truth isolation

- Bundle ID `T-PNR-001-v1`, `bundle_sha256=c0cb248b…`, `prompt_sha256=5f39a656…`, `gt_sha256=063b7833…`.
- Model input: E01 run rc/stage, E02 stage table, E03 exact make error, E04 failed config lines, E05 earlier macro-lib declaration in the same failed config, E06 declared flow stage order.
- Excluded: `proposal.json`, `recovery.patch`, `approval*.json`, `comparison.json`, recovered/baseline runs, current recovered config, clean benchmark config content, approval ledger/policy, and diagnosis.json (contains deterministic answer).
- `gt.json` is grader-only (mode 0600) and contains the known correction, affected stages, and verified recovery outcome; the prompt builder never reads it.
- Original failed config bytes are preserved in a backup snapshot (sha `91e88105…`) and presented under the neutral name `design/config.mk`; the on-disk config is the recovered version and is not used as model input.

## 6. Deterministic diagnosis (Mode D)

`experiments/T1-LIVE-DIAG/T-PNR-001/v1/deterministic_output.json` — derived only from E01..E06. Stage `synth`, missing macro Liberty reference, exact make-path failure, attempt-local config divergence, patch candidate restoring the pinned platform Liberty path, stages `synth…finish`, risks and explicit unknowns.

Evaluation (`deterministic_eval.json`): diagnosis_accepted PASS; all 12 metrics CORRECT; hard gates GT_LEAK=false, REF_FABRICATION=false, SCHEMA_INVALID=false. Ordinal vector uses CORRECT=3, PARTIAL=2, INCORRECT=1, UNSUPPORTED=0; no accuracy percentage is claimed.

## 7. Live model diagnosis (Mode L)

`live_call.json`: `provider_status=SKIPPED_NO_CREDENTIALS`, `status=BLOCKED`, `execution_kind` recorded, zero requests attempted, `token_usage=null`, no parsed output, no evaluation. **No live model invocation occurred; no fixture or replay is presented as one.**

## 8. Side-by-side evaluation

| Criterion | Deterministic (D) | Live (L) |
|---|---|---|
| Same frozen bundle/prompt | YES | YES (would use same paths) |
| Actual invocation | rule-based, 0 network | NOT RUN — BLOCKED |
| Structured output parsed | PASS | N/A |
| Evidence refs resolved | E01–E05 verbatim | N/A |
| Ground truth hidden | VERIFIED | VERIFIED by construction |
| 12-metric rubric | all CORRECT | NOT RUN |
| Live acceptance | — | BLOCKED |

## 9. Independent review

Reviewer Agent D assessed the bundle, GT isolation, deterministic grading, live block state, safety and reproducibility. Findings and coordinator resolution are recorded in `T1_ADJUDICATION.md`.

## 10. Tests

- `python3 -m unittest discover -s tests -p 'test_live_diagnosis.py' -v` — **21 PASS** (offline, stub transport; includes missing credentials, timeout, bounded retries, rate limit, connection failure, malformed JSON, missing fields, fabricated IDs in all evidence fields, grader hard gates, excerpt mismatch, redaction, labeling, prompt-hash stability, GT isolation, reproducibility, no execution authority).
- Existing offline regression: approval 30 PASS, remedy 33 PASS, KB 21 PASS, recovery-CLI 5 PASS, runner 14 PASS.
- Stub-provider integration tests are labeled `execution_kind=stub`; no live-provider or live-evaluation test was run.

## 11. Model latency and usage

No live call → latency/tokens/cost are `null`. Telemetry schema includes them for a future real call; cost is computed only with a matching reliable price table, never guessed.

## 12. Evidence locations

All artifacts under `experiments/T1-LIVE-DIAG/T-PNR-001/v1/`. Source failure `runs/orfs_baseline_failure_20261125T145821Z_20261125T145821234238490Z_20208/`. Original T-PNR-001 evidence unchanged.

## 13. Acceptance matrix

| # | Criterion | Status |
|---|---|---|
| 1 | Provider path audited | PASS |
| 2 | Real provider configured | BLOCKED (URL/key unset) |
| 3 | Genuine model invocation observed | BLOCKED / NOT RUN |
| 4 | Actual T-PNR-001 failure evidence used | PASS |
| 5 | Ground truth hidden from model input | PASS |
| 6 | Structured output parsed and validated | PASS (deterministic); live NOT RUN |
| 7 | Evidence references verified | PASS |
| 8 | Deterministic diagnosis evaluated | PASS |
| 9 | Live diagnosis evaluated | BLOCKED |
| 10 | Independent comparison vs ground truth | BLOCKED for live side |
| 11 | Independent review complete | SEE T1_ADJUDICATION.md |
| 12 | Offline regression passes | PASS |
| 13 | Live results and limitations documented | PASS |
| 14 | No recovery/protected design changes | PASS |

## 14. Limitations and next milestone

No live model was invoked; live-mode acceptance remains BLOCKED until a real provider URL/model (and key if required) is supplied. Single-item ordinal grading is a gate aid, not a population accuracy measurement. External signoff remains out of scope. Next milestone: repeat `live-diagnose` with a configured provider and grade its real response; no patch application or recovery is implied.
