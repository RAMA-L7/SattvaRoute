# SattvaRoute — Current Architecture (T-PNR-001)

## Control boundary

AI never controls the PnR flow directly. Python controls stage execution; OpenROAD executes; parsers extract evidence; the diagnosis interface classifies/proposes; an approval service authorizes; deterministic code applies approved patches and resumes. Engineering PASS is a report-level verdict, never a return code.

## Components (verified present)

| Layer | File | Role |
|---|---|---|
| Runner | `scripts/run_baseline_orfs.sh` | Collision-safe isolated run dirs; preflight; manifest check; stage loop with timeout/cancellation/job ledger; approval guard after preflight; evidence hashes; `run.json` |
| Approval | `scripts/sattva_approval.py`, `state/approval_policy.json` | Validate/apply exact patches; approval ID, source run ID, input fingerprint, patch hash, expected original/final hash, candidate ID, profile, expiry, rerun scope; ledger reuse rejection; env-expanded paths |
| Shared manifest | `config/sattva_manifest.json`, `scripts/manifest.py` | One authoritative dependency list for preflight, fingerprinting, resume compatibility, final evidence bundle |
| Diagnosis | `scripts/diagnosis_agent.py` | Deterministic evidence parsing/classification; bounded exact patch proposal (unverified live note path remains untouched) |
| Live diagnosis (T1) | `scripts/live_diagnosis.py`, `scripts/evidence_package.py`, `scripts/evaluate_diagnosis.py` | Advisory-only bounded provider call, frozen GT-free evidence bundle, structured output validation, ordinal rubric; no execution/approval authority |
| CLI | `scripts/pnr_cli.py` | baseline, failure-demo, diagnose, propose, approve-view, resume |
| Workflow controller | `scripts/remedy_engine.py` | Stage/total clocks, transitions, terminal guards, expiry/cancellation, approval-bound execution, evidence-based verification, KB write-back |
| KB | `scripts/sattva_kb.py` (19 records), `scripts/remedy_kb.py` (22 hashed sidecar records) | Append-only ledgers, hash chains (integrity, not immutability), locked write transactions, context-scoped refutations, reconsideration |
| Budgets | `config/remedy_budgets.json` | Configurable stage/total budgets, weights, thresholds, stop conditions |
| Tests | `tests/test_*.py`, `tests/test_runner.sh` | Offline unit/integration suites |

## Separation of concerns (required by the task)

- **Execution status:** stage RC, jobs.jsonl, timeout/cancellation records, run directory.
- **Engineering verdict:** report-level review of artifacts/metrics/violations; `NOT EVALUATED` until review.
- **Approval status:** PENDING until exact human approval; enforced by `sattva_approval.py`.
- **Evidence completeness:** preflight/manifest hashes, artifact_sha256.txt, source-run identity, proposal/diagnosis refs.
- **Recovery outcome:** baseline vs failed attempt vs recovered attempt comparison.

## UI

`app/backend`, `app/frontend`, `app/worker` are placeholders (empty). The usable entry point for this milestone is the CLI (`scripts/pnr_cli.py`); no decorative web UI or broad dashboard work was added.

## Boundaries

- OpenFinRAM/SattvaRoute macro case stays unresolved (DRT-0073) as a regression/research case.
- R2 experiment checklist remains DRAFT/INACTIVE.
- GDS export and external DRC/LVS signoff are outside scope.
- Local CLI approval is single-user only; no enterprise identity verification is implied.
