# Contributing to SattvaRoute

## Setup

1. Read `AGENTS.md`, `PROJECT_STATE.md`, and `docs/status/STATUS.md`.
2. Obtain ORFS and OpenROAD externally; configure `scripts/run_baseline_orfs.sh` for your machine.
3. Do not commit third-party tool trees, PDKs, libraries, credentials, or full run databases.

## Branching

- Work on a feature branch; keep `main` publishable.
- One logical change per branch/commit.

## Tests

- `tests/` is currently empty; there is no automated suite to claim as passing.
- If you add tests, include exact commands and verified results in the PR.
- Never report a test as passing unless you executed it.

## Code style

- Shell: `bash`, explicit variables, fail-fast, no silent overwrites.
- Python: PEP 8, no credentials in source, no machine-specific absolute paths.
- Docs: explicit `PASS / FAIL / BLOCKED / NOT EVALUATED` labels; timestamp with timezone.

## Reporting issues

Include the run ID, stage, verbatim log excerpt, tool versions, and what evidence you inspected. Separate observed evidence from hypothesis.

## Pull requests

- Preserve failed experiments; never rewrite a failure to look successful.
- One change at a time; include a decision record with exact diff, rollback, and verification plan.
- State the approval status if the change affects the PnR flow.
- Verify at report level — exit code 0 is not sufficient (D-007).

## Evidence requirements

Every engineering claim must cite a path and, where possible, a line number or hash. If evidence is unavailable, write `NOT EVALUATED`.
