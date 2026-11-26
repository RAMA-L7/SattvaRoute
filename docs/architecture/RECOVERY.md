# Recovery system

Status: implemented (deterministic, approval-gated). Canonical diagram: `docs/diagrams/RECOVERY_LIFECYCLE.md`. Evidence: `docs/HELDOUT_RECOVERY.md`, `docs/RECOVERY_WORKFLOW.md`.

## Definition

A recovery attempt is an **isolated run** that applies a human-approved, exact-hash-bound patch and reruns only from the earliest affected stage. It is not a rerun of the whole flow against the original collateral, and it is not an autonomous fix.

## Sequence

1. Approved correction exists (see `docs/architecture/APPROVAL.md`).
2. Input fingerprint validation: manifest preflight checks profile-scoped dependencies, collateral hashes, tool hashes, ORFS revision and declared local patches. A stale fingerprint blocks the attempt.
3. Stage selection: `earliest-stage` from the diagnosis/policy drives invalidation; downstream stages are rerun.
4. Execution: `pnr_cli.py resume` validates approval first, then invokes `run_baseline_orfs.sh` with the approved patch and source-run binding.
5. Result collection: the attempt directory captures its own evidence independently of the baseline.
6. Independent verification: `verify_run.py --baseline B --failure F --recovery R` compares report-level checks and flags regressions.
7. Recovery verdict: fixed / regressed / inconclusive / blocked, based on verification — not on the runner return code.

## Isolation properties

- Attempt directory is separate (`experiments/PNR-RECOVERY/...`); original control design and baseline are preserved.
- Original `constraint.sdc` preserved; `constraint_1ns.sdc` is a separate approved file.
- Blackbox/LEF/Liberty collateral is not edited in place; pinned files are fingerprinted.
- Approval records are append-only; no history rewrite.

## Verified recovery evidence

- Held-out missing-LEF case: real failure at synthesis → approved patch `AP-HELDOUT-LEFS-001` → recovery run `orfs_baseline_heldout_recovered_..._8250` rc=0 → `verify_recovery` PASS. The diagnosis and correction were **deterministic**, not live-AI.
- 1 ns SDC correction: explicitly approved, applied to `config.mk`, new baseline PASS, `verify_run` PASS; original SDC preserved.

## Non-claims

- No claim of general recovery success, signoff, timing closure, or functional correctness.
- No new recovery attempts are part of the documentation milestone.

## Related

`docs/architecture/VERIFICATION.md`, `docs/workflow/WORKFLOW.md`, `docs/research/LIMITATIONS.md`.
