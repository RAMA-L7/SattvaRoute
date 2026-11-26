# Claim-to-evidence verification

Status: independent mapping of major documentation claims to source/evidence. Verification performed by inspecting actual files, not by trusting other documents.

| Claim in documentation | Verified source / evidence | Verdict |
|---|---|---|
| CLI provides status/baseline/failure-demo/diagnose/live-diagnose/propose/approve-view/resume | `scripts/pnr_cli.py:207-243` argparse definitions | CONFIRMED |
| `baseline` returns process-level status and `engineering_verdict: NOT EVALUATED` | `scripts/pnr_cli.py:59-63` | CONFIRMED |
| Approval gate: `resume` validates before apply | `scripts/pnr_cli.py:184-204` | CONFIRMED |
| Patch hash binding, original hash, scope, ledger reuse, expiry, path safety | `scripts/sattva_approval.py:143-158,161-196,223-258,341-411`; `state/approval_policy.json` | CONFIRMED |
| Post-apply hash failure restores original | `scripts/sattva_approval.py:406-411` | CONFIRMED |
| Deterministic diagnosis families and `insufficient_evidence` | `scripts/diagnosis_agent.py:50-79,635-642` | CONFIRMED |
| Proposal is unapplied and `PENDING_HUMAN`; `NO_PROPOSAL` on no rule | `scripts/pnr_cli.py:137-151` | CONFIRMED |
| Verification uses last DRT-0199 count and missing≠pass | `scripts/verify_run.py:12-20,53,378-383` | CONFIRMED |
| Manifest v2 pins ORFS `25b6429c…`, two local patches, tool/collateral hashes | `config/sattva_manifest.json`, `docs/REPRODUCIBILITY.md:50-83` | CONFIRMED |
| Inactive profiles ASAP7 / `sattva_sram` unresolved; DRT-0073 preserved | `config/sattva_manifest.json:83-127` | CONFIRMED |
| Active SDC is `constraint_1ns.sdc`; historical 1000 ns preserved | `docs/REPRODUCIBILITY.md:9-15`, `docs/TIMING_AUDIT.md`, benchmark config | CONFIRMED |
| `report_units` 1 ns / 1 fF / 1 kΩ; Liberty `time_unit 1ns` | `docs/TIMING_AUDIT.md`, `evidence/timing/` | CONFIRMED (prior evidence) |
| Held-out missing-LEF recovery deterministic + human-approved + verified | `docs/HELDOUT_RECOVERY.md`, `AP-HELDOUT-LEFS-001`, recovery run record | CONFIRMED (prior evidence) |
| Live AI advisory only; no credentials → `SKIPPED_NO_CREDENTIALS` | `scripts/live_diagnosis.py`, `scripts/pnr_cli.py:110-134` | CONFIRMED |
| Evaluation v2 frozen | `scripts/evaluate_diagnosis_v2.py` exists and is referenced as frozen in `docs/REPRODUCIBILITY.md:134` | CONFIRMED |
| Offline test suite passes | Prior milestone records report suites passing; 157 `def test_` methods counted in `tests/*.py` during QA. Not re-executed here because Python is unavailable in this shell. An earlier "166" figure was not supported by the current file count and was corrected. | RECORD-BASED, not independently re-run |
| MIT covers original code/docs only | `LICENSE` header and scope paragraph | CONFIRMED |
| Nangate45/FakeRAM external, hash-pinned, not vendored | `config/sattva_manifest.json:71-81`, `docs/REPRODUCIBILITY.md:61-71` | CONFIRMED |
| PR #1 merged to main | `PROJECT_STATE.md`, commit `783d7655…` | CONFIRMED (prior evidence) |

## Unsupported claims deliberately absent

No signoff claim; no functional-correctness claim from timing; no AI-driven recovery claim; no quantified productivity/accuracy gain; no general cross-design validation; no external independent reproduction claim; no security-hardening claim beyond verified code.

## Related

`docs/reference/CAPABILITIES.md`, `docs/audit/QA_FINAL.md`, `docs/engineering/VERIFICATION_BOUNDARIES.md`.
