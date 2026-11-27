# Release and publication policy

Status: policy statement; no publication action in this milestone.

## Authority

Only the project owner may push, open a PR, merge, tag, release, force-push, or rewrite history. Documentation work on `main` remains local and uncommitted unless the owner directs otherwise.

## Published state (verified)

- Publication state: `PUBLISHED_REMOTE`.
- PR #1: `PR_MERGED_VERIFIED`, merged into `main` via squash as `783d7655af36b084fe958c216a54a0b7a58f58d8`.
- PR URL: `https://github.com/RAMA-L7/SattvaRoute/pull/1`.

## What is publishable

Original source/docs/config/curated evidence. Not published: tool trees, PDKs, licensed collateral, credentials, full run databases, machine-specific paths in evidence/logs. The published `config.mk` now uses portable defaults for `WORK_HOME`/`KLAYOUT_CMD`; curated evidence records may still contain absolute provenance paths identifying the executed run. See `docs/governance/THIRD_PARTY.md`, `docs/REPRODUCIBILITY.md`.

## Release discipline

- One logical change per branch/commit; `main` kept publishable.
- Evidence-backed claims only; no fabricated results.
- Historical failures and evaluations preserved verbatim.
- Report-level verification required; `rc=0` is not acceptance.
- No signoff/functional-correctness claims in release notes.

## Documentation-only milestone boundary

No push, PR, merge, force-push, rebase, or history rewrite. No new experiments, recovery attempts, or production changes.

## Related

`docs/governance/GOVERNANCE.md`, `PROJECT_STATE.md`, `CONTRIBUTING.md`.
