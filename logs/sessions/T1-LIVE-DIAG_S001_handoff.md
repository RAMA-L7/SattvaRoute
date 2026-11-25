# Session Handoff — T1-LIVE-DIAG S001

- **Task:** Live AI diagnosis validation against real T-PNR-001 failure evidence.
- **Date:** 2026-11-25
- **Agent:** implementation engineer + Agents A/B/C/D.
- **Safe to continue:** YES after lock release.

## Completed
- Provider path audited; no real provider existed previously.
- New isolated advisory provider `scripts/live_diagnosis.py` with bounded timeout/retries, status taxonomy, redaction, schema/ref validation, telemetry, no execution authority.
- Frozen GT-free evidence bundle `experiments/T1-LIVE-DIAG/T-PNR-001/v1/`; grader-only `gt.json` (0600).
- Deterministic mode + 12-metric ordinal rubric; deterministic diagnosis accepted (all 12 CORRECT).
- 21 offline tests PASS; existing regression suites PASS.

## Outcome
Live provider URL/credentials unset → `SKIPPED_NO_CREDENTIALS`, status BLOCKED, no model call, no tokens/latency/cost, no live acceptance claim. No fixture or replay labeled live. No recovery, patch application, approval, EDA, or design/protected change.

## T1-LIVE update
Genuine local Ollama call completed through `scripts/run_t1_live.py` + narrow PowerShell forwarder: HTTP 200, `qwen2.5:7b-instruct`, 805/508/1313 tokens, 141,518 ms. Response `SCHEMA_INVALID` (three fields as strings) and evidence IDs cited only as unstructured strings; `refs_valid=false` after validator fix; `diagnosis_accepted=false`. Preserved failed attempts in `v1_live_attempt1/` and `v1_live_attempt2/`. Independent review found two grader bugs (string-length inflation, vacuous refs) and an out-of-band evaluation provenance gap — all fixed without changing rubric thresholds. `run_t1_live.py --grade-only` reproduces `live_eval.json`. 23 offline tests PASS.

## Open
Schema-conformant live re-run required. External signoff remains out of scope.

## Stop
No further milestone, remedy, experiment, or production change without explicit authorization.
