# Approval system

Status: implemented. Source: `scripts/sattva_approval.py`, `state/approval_policy.json`. Canonical diagram: `docs/diagrams/APPROVAL_LIFECYCLE.md`.

## Principle

No change is applied unless a human has explicitly created an approval record that binds the **exact patch hash**, the **target file**, the **decision ID**, the **source run ID**, the **rerun scope**, and the **earliest affected stage**. The CLI never manufactures an approval; `propose` and `approve-view` only display a pending proposal.

## Commands

| Command | Purpose |
|---|---|
| `create` | Human creates an approval with `--approval-id`, `--decision-id`, `--source-run-id`, `--patch`, `--target`, `--earliest-stage`, `--rerun-scope`, `--approver`, `--design-root`, `--policy`, `--out`; optional `--status APPROVED\|REJECTED`, `--candidate-id`, `--expected-final-hash`, `--expires-at`, `--profile`, `--note` |
| `validate` | Checks approval + `--patch` + `--policy` + `--design-root` + `--run-id` (+ optional `--decision-id`, `--for-apply`) before apply |
| `apply` | Applies an approved patch, with `--evidence-dir` capturing evidence |
| `guard` | Combined validation/applicability guard with `--evidence-dir` |
| `check-source-artifacts` | Checks source artifacts against an approval (`--source-work`, optional `--results-root`) |

## Policy constraints (`state/approval_policy.json`)

- `allowed_roots`: only ORFS `flow/scripts` under `SATTVA_ROOT` and `experiments/PNR-RECOVERY`. Patches outside allowed roots are not eligible.
- `stages`: the bounded stage set.
- `stage_inputs`: the artifact each stage consumes, used to derive invalidation.
- `ledger`: append-only JSONL at `state/approval_ledger.jsonl`.
- `recovery_profiles`: per-profile input files, absolute fingerprint files, and stage inputs.

## Integrity controls verified in source

- Patch hash is bound at create time and re-checked at validation/apply; a changed patch invalidates approval.
- Approval is bound to a source run ID and decision ID; cross-run reuse is rejected.
- `--expires-at` supports expiration where used; `--expected-final-hash` binds the expected resulting file.
- `validate` must succeed before `resume` invokes the runner (`pnr_cli.py` checks return code).
- Status may be `APPROVED` or `REJECTED`; rejected approvals do not authorize apply.

## What approval does not do

Approval authorizes a bounded attempt; it does not guarantee the change is correct, that the flow completes, that timing closes, or that signoff is achieved. Verification and engineering validation remain separate.

## Related

`docs/security/SAFETY.md`, `docs/architecture/PATCH_VALIDATION.md`, `docs/architecture/RECOVERY.md`.
