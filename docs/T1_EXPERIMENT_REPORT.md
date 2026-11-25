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

## 7. Live model diagnosis (Mode L — T1-LIVE)

A genuine local provider was made reachable through a narrow PowerShell forwarder (`scripts/t1_ollama_forward.ps1`, `scripts/run_t1_live.py`) because WSL cannot reach the Windows-loopback Ollama endpoint. Two transport attempts failed and are preserved under `v1_live_attempt1/` and `v1_live_attempt2/`. The third attempt produced a real response:

- Provider/model: local Ollama OpenAI-compatible endpoint, `qwen2.5:7b-instruct`.
- HTTP 200, `execution_kind=live_api`, latency 141,518 ms, prompt tokens 805, completion tokens 508, total 1,313.
- `status=SCHEMA_INVALID`: `contradicting_evidence`, `risk_assessment` and `verification_plan` were returned as strings instead of lists. `refs_valid=true` is vacuous because the supporting-evidence items were plain strings, not `{ref, excerpt}` objects.
- No ground-truth leak; no patch, approval, EDA, or design change.

This is a **genuine live invocation** but **not a valid structured diagnosis**; hard gate `SCHEMA_INVALID=true` prevents acceptance.

## 8. Side-by-side evaluation

| Criterion | Deterministic (D) | Live (L) |
|---|---|---|
| Same frozen bundle/prompt | YES | YES (identical frozen paths) |
| Actual invocation | rule-based, 0 network | **GENUINE HTTP 200**, local Ollama `qwen2.5:7b-instruct` |
| Structured output parsed | PASS | **FAIL** — `SCHEMA_INVALID` (3 fields returned as strings) |
| Evidence refs resolved | E01–E05 verbatim | **FAIL** — IDs present only as unstructured strings; `refs_valid=false` after validator fix |
| Ground truth hidden | VERIFIED | VERIFIED |
| 12-metric rubric | all CORRECT | diagnostic only: stage PARTIAL, signature CORRECT, root cause PARTIAL, patch INCORRECT, scope INCORRECT, stages PARTIAL, alternatives/evidence/risk UNSUPPORTED; hard gate blocks acceptance |
| Live acceptance | — | **BLOCKED** (invocation achieved, diagnosis not accepted) |

## 9. Independent review and adjudication

Agent D (`T1LIVE_D_review.md`, did not implement the provider) confirmed: genuine HTTP 200 call with real tokens/timestamps; no GT leak; no patch/approval/EDA/config change; frozen hashes intact. It found two evaluator implementation bugs (`refs_valid=true` was vacuous; `len()` on string fields inflated `risk_identification` and `contradiction_handling`) and an out-of-band evaluation provenance gap. **Coordinator resolution:** rubric thresholds were NOT changed; `validate_refs()` now rejects unstructured string-only evidence IDs, list-type checks are enforced for risks/contradictions, and `run_t1_live.py --grade-only` reproduces `live_eval.json` from the preserved call. Corrected live metrics: contradiction_handling UNSUPPORTED, risk_identification UNSUPPORTED, refs_valid false; `diagnosis_accepted=false`. Reviewer verdict: **BLOCKED** — genuine invocation achieved, but no accepted live diagnosis until a schema-conformant re-run.

## 10. Tests

- `python3 -m unittest discover -s tests -p 'test_live_diagnosis.py' -v` — **23 PASS** (offline, stub transport; includes the two reviewer-found grader regressions, missing credentials, timeout, bounded retries, rate limit, connection failure, malformed JSON, missing fields, fabricated IDs, redaction, labeling, prompt-hash stability, GT isolation, reproducibility, no execution authority).
- `python3 scripts/run_t1_live.py --grade-only` — PASS (reproducible evaluation of the preserved live call, no new provider request).
- Existing offline regression: approval 30 PASS, remedy 33 PASS, KB 21 PASS, recovery-CLI 5 PASS, runner 14 PASS.
- Stub-provider integration tests are labeled `execution_kind=stub`; no live-provider or live-evaluation test was run.

## 11. Model latency and usage

Genuine call: latency 141,518 ms; prompt tokens 805 (804 cached), completion tokens 508, total 1,313; retries 0; HTTP 200. Cost `null` (local Ollama, no reliable price table). Failed transport attempts: `MALFORMED_RESPONSE` 122,890 ms (BOM decoding), `HTTP_ERROR 502` 123,311 ms (forwarder timeout) — preserved separately, not counted as accepted calls.

## 12. Evidence locations

All artifacts under `experiments/T1-LIVE-DIAG/T-PNR-001/v1/`. Source failure `runs/orfs_baseline_failure_20261125T145821Z_20261125T145821234238490Z_20208/`. Original T-PNR-001 evidence unchanged.

## 13. Acceptance matrix

| # | Criterion | Status |
|---|---|---|
| 1 | Provider path audited | PASS |
| 2 | Real provider configured | PASS (local Ollama endpoint via narrow forwarder) |
| 3 | Genuine model invocation observed | PASS (HTTP 200, real tokens; artifacts in `v1_live/`) |
| 4 | Actual T-PNR-001 failure evidence used | PASS |
| 5 | Ground truth hidden from model input | PASS |
| 6 | Structured output parsed and validated | PASS (deterministic); **FAIL** (live `SCHEMA_INVALID`) |
| 7 | Evidence references verified | PASS (deterministic); **FAIL** (live unstructured refs) |
| 8 | Deterministic diagnosis evaluated | PASS |
| 9 | Live diagnosis evaluated | **BLOCKED** (graded diagnostic-only; hard gate rejects) |
| 10 | Independent comparison vs ground truth | PASS (both modes compared; live not accepted) |
| 11 | Independent review complete | SEE T1_ADJUDICATION.md |
| 12 | Offline regression passes | PASS |
| 13 | Live results and limitations documented | PASS |
| 14 | No recovery/protected design changes | PASS |

## 14. Limitations and next milestone

A genuine live call was made, but the model returned three fields with wrong types and cited evidence only as unstructured strings; live acceptance remains BLOCKED until a schema-conformant response is produced. The local provider is a free on-machine model reached via a narrow forwarder, not an external hosted service; no cost claim is made. Single-item ordinal grading is a gate aid, not a population accuracy measurement. External signoff remains out of scope. Next milestone: one conformant re-run using the same frozen bundle; grade with the corrected evaluator; no patch application or recovery is implied.
