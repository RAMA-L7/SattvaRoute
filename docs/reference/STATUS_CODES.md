# Status codes and verdicts

Status: authoritative vocabulary. Source: `scripts/verify_run.py`, approval/diagnosis/recovery tooling.

## Result statuses

| Status | Meaning |
|---|---|
| `PASS` | The specific check succeeded with complete evidence |
| `FAIL` | The check failed, or evidence is missing where presence is required |
| `BLOCKED` | A prerequisite (approval, credential, preflight, policy) prevented progress |
| `UNKNOWN` | The check could not be determined from available evidence |
| `INCONCLUSIVE` | Evidence is conflicting or insufficient to choose between mechanisms |
| `NOT RUN` | The step was not executed |
| `NOT EVALUATED` | Deliberately not assessed (e.g. signoff, functional correctness) |

`verify_run.py` internally uses `PASS`, `FAIL`, `UNKNOWN`, `NOT_EVALUATED`; aggregation: any `FAIL` → fail, else any `UNKNOWN` → unknown, all `PASS` → pass. Missing evidence is never `PASS`.

## CLI return statuses (selected)

- `baseline`: `PASS` if runner rc=0 else `FAIL`; always sets `engineering_verdict: NOT EVALUATED - inspect reports`.
- `failure-demo`: `PASS` if run failed as expected, `UNEXPECTED_PASS` otherwise.
- `propose`: `NO_PROPOSAL` / `insufficient_evidence` with exit 1 when no bounded rule applies.
- `live-diagnose`: `PASS` if provider OK, `BLOCKED` otherwise; `SKIPPED_NO_CREDENTIALS` when unconfigured.
- `resume`: `FAIL` if approval validation fails; otherwise runner rc-based status.
- Approval validation raises errors on REJECTED status, hash mismatch, stale fingerprint, path/scope violations, ledger reuse, expiry.

## Capability statuses

`IMPLEMENTED`, `VALIDATED`, `EXPERIMENTAL`, `PARTIALLY IMPLEMENTED`, `PLANNED`, `BLOCKED`, `NOT IMPLEMENTED`. See `docs/reference/CAPABILITIES.md`.

## Evidence/watch-out rules

- Empty report ≠ clean unless the log shows completion with zero violations.
- Take the **last** DRT-0199 count, not the first.
- `rc=0` ≠ engineering pass.
- Flow completion ≠ timing closure ≠ coverage ≠ characterized timing ≠ signoff.
- Router DRC=0 ≠ foundry DRC; timing ≠ functional correctness.

## Historical statuses

Historical results and verdicts (including `REJECTED` live-AI evaluations and unresolved `DRT-0073`) are preserved verbatim and must not be relabeled to match current documentation.

## Related

`docs/reference/GLOSSARY.md`, `docs/architecture/FAILURE_STATES.md`, `docs/engineering/VERIFICATION_BOUNDARIES.md`.
