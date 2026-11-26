# Safety principles, approval model, and patch policy

Status: safety documentation. Implementation detail: `docs/architecture/APPROVAL.md`, `docs/architecture/PATCH_VALIDATION.md`, `docs/architecture/FAILURE_STATES.md`.

## Safety principles

1. **Human control** — no change is applied without explicit human approval of the exact diff.
2. **Preserve originals** — baseline, collateral, historical evidence, and approval records are preserved; recovery is isolated.
3. **Bounded scope** — one mechanism, one target variable, one contiguous rerun scope starting at the earliest affected stage.
4. **Fail closed** — preflight mismatch, approval-validation failure, missing evidence, or unsafe patch → stop, never continue on an invalid premise.
5. **Separation of duties** — propose, approve, apply, execute, and verify are distinct.
6. **Honest reporting** — `PASS`/`FAIL`/`BLOCKED`/`UNKNOWN`/`INCONCLUSIVE`/`NOT RUN`/`NOT EVALUATED`; missing data is never success.
7. **No silent rule changes** — no constraint relaxation, corner swap, technology change, or invented collateral.

## Approval model (verified controls)

- Approval records created by `sattva_approval.py create` contain `approval_id`, `decision_id`, `source_run_id`, `input_fingerprint`, `patch_sha256`, `target_file`, `expected_original_hash`, `earliest_affected_stage`, `rerun_scope`, `status`, `approver`, `timestamp`, and `operation_id`; optional `note`, `candidate_id`, `expected_final_hash`, `expires_at`, `profile`. `--design-root`, `--policy`, and `--out` are CLI arguments, not fields stored in the record.
- `status` is `APPROVED` or `REJECTED`; `REJECTED` cannot validate.
- Validation re-hashes the patch and the target original, checks run/decision IDs, rejects reuse through the ledger, enforces `expires_at` when present, and validates that rerun scope is known, duplicate-free, contiguous, and starts at the earliest affected stage.
- `check_path_safety` rejects relative paths, `..`, symlinks in any component, and targets outside `allowed_roots`.
- Apply is atomic with a 0600 temporary file, a backup, and rollback if post-apply hash verification fails.

## Patch policy

| Rule | Enforcement |
|---|---|
| Exact patch hash bound | create + validate + apply |
| Allowed targets only | `allowed_roots` in `state/approval_policy.json` |
| Bounded rerun | `validate_scope` |
| No reuse | append-only ledger |
| No stale inputs | manifest fingerprint + input-file hash binding |
| Auditable | evidence dir records `approval_apply.json` / `approval_guard.json`; ledger appended |
| No fabrication | `NO_PROPOSAL` / `insufficient_evidence` when no bounded rule applies |

## Failure-safe behavior

| Failure | Safe response |
|---|---|
| Preflight mismatch | Stop (`FAIL`) |
| Approval invalid | Stop (`FAIL`), no apply |
| Insufficient evidence | Abstain (`insufficient_evidence`) |
| Post-apply hash mismatch | Restore original, report error |
| Verification regression | Verdict not "fixed" |
| Model unavailable | Advisory `BLOCKED`; deterministic path unaffected |

## Limitations

Controls are local and convention-based (append-only by file mode/behavior, self-declared approver, no authenticated identity, no sandbox). Do not describe SattvaRoute as a security-hardened or multi-tenant system.

## Related

`docs/security/THREAT_MODEL.md`, `docs/security/TRUST_BOUNDARIES.md`, `docs/security/INPUT_AND_AI_RISKS.md`.
