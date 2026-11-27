# Capability and evidence matrix

Status: **authoritative**. Statuses were assigned from source code, tests, and published evidence, not from descriptions. Status vocabulary: `IMPLEMENTED`, `VALIDATED`, `EXPERIMENTAL`, `PARTIALLY IMPLEMENTED`, `PLANNED`, `BLOCKED`, `NOT IMPLEMENTED`.

## Matrix

| Capability | Status | Source location | Test evidence | Execution evidence | Limitations |
|---|---|---|---|---|---|
| Runner reliability (staged execution, evidence capture) | VALIDATED | `scripts/run_baseline_orfs.sh`, `scripts/pnr_cli.py` | `tests/test_recovery_cli.py`, `tests/test_runner.sh` | Baseline runs including 1 ns control baseline PASS | Pinned ORFS/profile only; rc≠engineering pass |
| Preflight | VALIDATED | `scripts/manifest.py` (preflight path), runner | `tests/test_manifest.py` | Preflight records in run `evidence/` | Active profile only |
| Run isolation | VALIDATED | `scripts/pnr_cli.py` (`resume`), runner attempt dirs | `tests/test_recovery_cli.py` | Held-out recovery attempt dir; originals preserved | Local FS conventions, not a sandbox |
| Evidence collection | VALIDATED | `scripts/run_baseline_orfs.sh`, `scripts/evidence_package.py` | `tests/test_verify_run.py` | `evidence/run.json`, `stages.tsv`, logs, hashes | Curated evidence only; bulk DBs unpublished |
| Fingerprinting (manifest v2) | VALIDATED | `scripts/manifest.py`, `config/sattva_manifest.json` | `tests/test_manifest.py` | Canonical fingerprint in evidence; preflight fail-closed | Inactive profiles not validated for the control benchmark; explicitly selectable with `--profile` |
| Diagnosis — deterministic | VALIDATED | `scripts/diagnosis_agent.py` | `tests/test_diagnosis_agent.py`, `tests/test_evaluate_diagnosis_v2.py` | Controlled + held-out cases classified | Bounded family set; no cross-design generalization claim |
| Evidence references | VALIDATED | `scripts/diagnosis_agent.py` (`evidence_refs`), `scripts/verify_run.py` | `tests/test_diagnosis_agent.py`, `tests/test_verify_run.py` | Reviewable paths in diagnosis/verification records | Referential, not cryptographic proof |
| Proposal generation (bounded, unapplied) | VALIDATED | `scripts/diagnosis_agent.py` (`propose_patch`) | `tests/test_diagnosis_agent.py` | `approve-view` output; `PENDING_HUMAN` / `NO_PROPOSAL` | `NO_PROPOSAL` on no rule; no invented collateral |
| Patch validation | VALIDATED | `scripts/sattva_approval.py`, `state/approval_policy.json` | `tests/test_approval.py` | Exact-diff + hash-bound approvals | Integrity of hash, not engineering correctness |
| Approval integrity | VALIDATED | `scripts/sattva_approval.py` | `tests/test_approval.py` | Ledger, path safety, scope, expiry, reuse rejection | Self-declared approver; no signed identity |
| Recovery execution | VALIDATED | `scripts/remedy_engine.py`, `scripts/pnr_cli.py resume`, runner | `tests/test_recovery_cli.py`, `tests/test_remedy_engine.py` | `orfs_baseline_heldout_recovered_..._8250` rc=0; `verify_recovery` PASS | Deterministic, human-approved; no live-AI recovery |
| Stage-limited rerun | VALIDATED | `state/approval_policy.json`, approval `rerun_scope` | `tests/test_approval.py`, `tests/test_recovery_cli.py` | Recovery from earliest affected stage | Scope human-declared, validated for contiguity |
| Verification (report-level, fail-closed) | VALIDATED | `scripts/verify_run.py` | `tests/test_verify_run.py` | Baseline/1 ns/held-out verification PASS | Tool-level only; not signoff |
| Timing audit (schema v2) | VALIDATED | `scripts/timing_audit.py`, `scripts/audit_timing.tcl` | `tests/test_evidence_qualification.py` | Run-bound audits for clean 1 ns baseline and recovery | `update_timing` unsupported in pinned OpenROAD → `timing_update` UNKNOWN, never PASS; audits reject wrong-run/tampered artifacts |
| Reproducibility (manifest, pinned deps) | VALIDATED | `config/sattva_manifest.json`, `docs/REPRODUCIBILITY.md` | `tests/test_manifest.py` | Author-run clean-environment validation | **Not** tested by another engineer |
| Evaluation framework (diagnosis v2 frozen) | VALIDATED | `scripts/evaluate_diagnosis_v2.py`, `scripts/evidence_package.py` | `tests/test_evaluate_diagnosis_v2.py` | Held-out evaluation; historical `T1_*` reports | Small bundle set; v2 frozen |
| Timing qualification (v1) | VALIDATED | `scripts/timing_qualification.py`, `scripts/verify_run.py` | `tests/test_timing_qualification.py` | `evidence/verification/tq_recovery_comparison.json` (baseline PASS / recovery PASS / numeric comparison PASS) | Tool-level only; no signoff; unsupported capability remains UNKNOWN |
| Recovery evaluation | VALIDATED | `scripts/verify_run.py` | `tests/test_verify_run.py` | Held-out recovery verdict | Binary/limited metrics; no recovery-quality score |
| Knowledge base / remedy ledger | VALIDATED | `scripts/sattva_kb.py`, `scripts/remedy_kb.py` | `tests/test_kb.py`, `tests/test_remedy_kb.py` | Immutable/verifiable records in `knowledge/` | Historical knowledge, not general truth |
| AI integration (optional advisory) | PARTIALLY IMPLEMENTED | `scripts/live_diagnosis.py`, `scripts/pnr_cli.py live-diagnose` | `tests/test_live_diagnosis.py` | Advisory calls only; no patch/approval/execution | `SATTVA_MODEL_URL` unset → `SKIPPED_NO_CREDENTIALS`/`BLOCKED`; no live-AI recovery |
| Benchmark packaging | VALIDATED | `benchmark/design/nangate_macro_control/`, manifest | `tests/test_manifest.py` | Published control package + provenance | One benchmark; abstract macro |
| Signoff DRC/LVS | NOT IMPLEMENTED | — | — | — | Explicit non-goal |
| Functional correctness verification | NOT IMPLEMENTED | — | — | — | Timing ≠ function |
| Multi-corner / multi-mode timing | NOT IMPLEMENTED | — | — | — | Single typical corner |
| Autonomous production modification | NOT IMPLEMENTED | — | — | — | Explicit non-goal; human approval required |
| General cross-design diagnosis | PLANNED | — | — | — | Research direction only |

## Reading the matrix

- `VALIDATED` means source + tests + at least one execution artifact support the claim within the pinned benchmark.
- `IMPLEMENTED`/`PARTIALLY IMPLEMENTED` means code exists but validation or availability is limited.
- `PLANNED`/`NOT IMPLEMENTED` must never be presented as available.

## Related

`docs/reference/STATUS_CODES.md`, `docs/research/ROADMAP.md`, `docs/research/LIMITATIONS.md`, `docs/audit/CLAIM_EVIDENCE.md`.
