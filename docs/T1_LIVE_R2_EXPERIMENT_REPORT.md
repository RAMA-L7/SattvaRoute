# T1-LIVE-R2 — Conformant Diagnosis Rerun

- **Date:** 2026-11-25
- **Final verdict:** **REJECTED** — one genuine live invocation completed, output is schema-conformant and evidence-resolved, but the diagnosis fails the existing acceptance criteria. No integrity, safety, or execution defect.
- **Boundary:** diagnosis-only. No patch, approval, EDA, recovery, or production change.

## 1. Live invocation record

- Experiment: `T-PNR-001/v1_live_r2` (`experiments/T1-LIVE-DIAG/T-PNR-001/v1_live_r2/`).
- Provider/model: local Ollama OpenAI-compatible endpoint, `qwen2.5:7b-instruct`.
- Invocation: exactly one; HTTP 200, `execution_kind=live_api`, `status=OK`, retries 0.
- UTC: start `2026-11-25T18:00:49Z`, completion `2026-11-25T18:03:28Z`; latency 158,030 ms.
- Tokens: prompt 920, completion 524, total 1,444; cost `null` (local model, no reliable price table).
- Prompt: `v1/prompt_r2.txt`, `prompt_sha256=3b2ae9ad…f4`, version `t1_diag_prompt/v2_minimal_types`. Only structural type/evidence-shape wording changed from v1; evidence bundle untouched.
- POST body reproduced by reviewer equals `prompt_r2.txt`; raw response OpenAI-shaped (`chatcmpl-677`, `system_fingerprint=fp_ollama`), not stub/replay.

## 2. Frozen evidence and isolation

- `bundle_sha256=c0cb248b…5cbc`, original `prompt_sha256=5f39a656…a979`, `gt_sha256=063b7833…73a4` — all recomputed exactly.
- E04/E05 derive from failed snapshot `91e88105…`, not recovered config `453c5728…`.
- No forbidden tokens in model-visible files or model output: `RESTORE_MACRO_LIB`, approval IDs, proposal/recovery/comparison paths, recovered run, correction text, or patched hash.
- `gt.json` remains grader-only and separate; previous attempts `v1_live/`, `v1_live_attempt1/`, `v1_live_attempt2/` preserved.

## 3. Parsed model output (summary)

Correct stage `synth` and generic "missing macro library file" hypothesis. Copied E03/E04/E05 verbatim as structured `{ref, excerpt}` objects. However: `patch_candidate="None proposed"`, `proposed_action` generic, `affected_stages=["synth"]` only, one evidence-free alternative, one risk, and E05 (the correct declaration) mislabeled as contradicting evidence.

## 4. Twelve-metric evaluation (unmodified rubric `t1_rubric/v1`)

| Metric | Result | Note |
|---|---|---|
| Failure-stage accuracy | CORRECT | `synth` from E01/E02 |
| Failure-signature accuracy | CORRECT | Token match from copied E03/E04 text; "Configuration Error" is not GT phrasing |
| Root-cause accuracy | PARTIAL | Generic missing file; no attempt-local `ADDITIONAL_LIBS` override mechanism |
| Evidence precision | PARTIAL | 3 resolved refs, no fabrication; grader denominator quirk noted by reviewer, no acceptance impact |
| Evidence completeness | INCORRECT | E01/E02/E06 omitted (3/5) |
| Contradiction handling | PARTIAL | E05 misclassified; no precheck caveat |
| Alternative quality | UNSUPPORTED | One bare-string, evidence-free alternative |
| Patch correctness | INCORRECT | `patch_candidate="None proposed"` |
| Patch scope | INCORRECT | No patch/scope |
| Stage selection | PARTIAL | `["synth"]` only; omits five downstream stages |
| Risk identification | PARTIAL | One risk |
| Unsupported claims | CORRECT | No fabricated refs; explicit missing_information |

`diagnosis_accepted=false`. Acceptance fails solely on `patch_correctness=INCORRECT` in the existing four-metric conjunction; all other acceptance-linked metrics are at least PARTIAL. No threshold or gate was changed.

## 5. Hard gates and evidence validation

`GT_LEAK=false`, `REF_FABRICATION=false`, `SCHEMA_INVALID=false`. All 14 required fields present with correct types. `E03`, `E04`, `E05` resolve with verbatim excerpts and matching excerpt hashes; `fabricated=[]`, `distinct_valid=3`, `refs_valid=true`. R1's vacuous-refs defect is cured.

## 6. Grade-only reproducibility

`python3 scripts/run_t1_live.py --grade-only --out-dir experiments/T1-LIVE-DIAG/T-PNR-001/v1_live_r2` → `diagnosis_accepted=false`, same 12 scores and gates. Reviewer independently recomputed `grade()` and in-memory grade-only with zero diffs.

## 7. Independent review

Agent D (`T1R2_D_review.md`, did not execute or implement the provider) verified: genuine call; frozen hashes; GT isolation; 14/14 schema; real ref resolution; evaluator and grade-only reproducibility; unmodified hard gates; no patch/approval/EDA/recovery; 23/23 live tests and 14/14 runner checks. It labeled the result BLOCKED using an older project convention. **Coordinator adjudication:** under this task's explicit definitions, genuine response evaluated but failing acceptance is **REJECTED**, not BLOCKED; execution/evaluation completed reliably. Reviewer disagreements recorded without rubric changes: `evidence_precision=PARTIAL` is mechanically defensible but semantically understated; `signature=CORRECT` rests on copied evidence; `patch_correctness=INCORRECT` is rubric-correct though the "do not propose applying a patch" prompt wording may have discouraged a text candidate. No change made — post-result grading adjustments are prohibited.

## 8. Regression tests

- `tests/test_live_diagnosis.py`: 23 PASS.
- `tests/test_runner.sh`: PASS=14 FAIL=0.
- Existing suites from T1/T-PNR-001 remain PASS (remedy 33, approval 30, KB 21, recovery-CLI 5).
- Grade-only reproduction PASS. No live-provider test counted from stubs.

## 9. Acceptance matrix

| Criterion | Status |
|---|---|
| Exactly one genuine live invocation | PASS |
| Same frozen bundle and verified hashes | PASS |
| Ground truth isolated | PASS |
| Schema-conformant output | PASS |
| All evidence references resolve | PASS |
| Corrected evaluator grades actual response | PASS |
| All 12 metrics reported | PASS |
| Hard gates enforced unmodified | PASS |
| Independent review completed | PASS |
| Grade-only reproduces results | PASS |
| Existing regressions pass | PASS |
| No unauthorized engineering/recovery | PASS |
| Clean repo, published commit, released locks | PASS |
| Overall diagnosis acceptance | **REJECTED** |

## 10. Limitations and stop

The model produced valid structure but shallow synthesis; no accepted live diagnosis exists. A future re-run would require fresh authorization and must not tune the rubric. No further milestone, benchmark, recovery, or production change in this session.
