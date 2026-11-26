# Failure-state handling

Status: implemented behavior; see `docs/reference/STATUS_CODES.md` for the full status vocabulary.

## Principles

- Stop on safety failure; do not continue with an invalid premise.
- Missing evidence is not success.
- Historical failures are preserved, not rewritten.
- A failure in one stage invalidates dependent downstream work; it does not silently invalidate unrelated profiles or the baseline.

## States and responses

| Condition | Response |
|---|---|
| Manifest preflight mismatch (revision, patch set, hash, tool) | `FAIL`; runner does not proceed |
| Approval validation failure | `FAIL`; `resume` returns before invoking runner |
| No bounded correction applies | `NO_PROPOSAL` / `insufficient_evidence`; no approval requested |
| Stage log missing / unreadable | `FAIL` or `UNKNOWN` in verification; never `PASS` |
| Empty report with no completion evidence | `FAIL` (not "clean") |
| Intermediate DRT count only | `UNKNOWN`/`FAIL` depending on evidence; last count required |
| Recovery regression vs baseline | Flagged by verification; verdict not "fixed" |
| DRT-0073 / OpenFinRAM | `UNRESOLVED_DRT0073_PRESERVED`; excluded; not reopened |
| Live model unavailable | `SKIPPED_NO_CREDENTIALS` / `BLOCKED`; advisory only |
| Inactive profile | Declared but not checked; no claim about it |

## Escalation

When evidence is insufficient, the correct outcome is `insufficient_evidence`, a request for more data, or a human decision — not a guessed cause, a relaxed constraint, or invented collateral. Engineering issues found during documentation are recorded as recommendations, never silently fixed in this milestone.

## Related

`docs/architecture/VERIFICATION.md`, `docs/security/SAFETY.md`, `docs/product/NON_GOALS.md`.
