# Contributing to SattvaRoute

## Scope of this repository

SattvaRoute is a research-grade physical-design diagnosis and controlled recovery framework. Read `AGENTS.md`, `PROJECT_STATE.md`, `docs/status/STATUS.md`, and `docs/product/PRODUCT.md` before proposing a change. The authoritative product narrative and terminology live in `docs/product/PRODUCT.md` and `docs/reference/GLOSSARY.md`.

## Setup

1. Read `docs/workflow/GETTING_STARTED.md` for prerequisites, environment variables, and pinned dependency acquisition.
2. Obtain ORFS, OpenROAD, and Yosys externally at the pinned revisions/hashes in `config/sattva_manifest.json`. Nothing third-party is vendored.
3. Do not commit tool trees, PDKs, libraries, credentials, or full run databases.

## Branching

- Work on a feature branch; keep `main` publishable.
- One logical change per branch/commit.
- Only the owner pushes, opens PRs, merges, tags, or rewrites history.

## Tests (verified)

The offline suite exists and is runnable:

```
python3 -m unittest discover -s tests -p 'test_*.py'
```

The suite defines **157 test methods** across `tests/test_*.py` (counted in this milestone), covering approval integrity, diagnosis, manifest, recovery CLI, verification, knowledge base, remedy engine, and evaluation v2. Earlier notices that "`tests/` is empty" are superseded by this statement. Prior milestone records report the offline suites passing; the suite was not re-executed in this shell because no Python interpreter was available. No credentials or EDA flow run are required for these tests.

If you add tests, include the exact command and the result you actually observed. Never report a test as passing unless you ran it.

## Code and documentation style

- Shell: `bash`, explicit variables, fail-fast, no silent overwrites.
- Python: PEP 8, no credentials in source, no machine-specific absolute paths.
- Docs: professional engineering language; explicit status labels (`PASS / FAIL / BLOCKED / UNKNOWN / INCONCLUSIVE / NOT RUN / NOT EVALUATED`); UTC timestamps; link to authoritative sources instead of duplicating them.
- Commands and configuration keys in docs must be verified against source.

## Reporting issues

Include the run ID, stage, verbatim log excerpt, tool versions, exact command, and what evidence you inspected. Separate observed evidence from hypothesis. For security issues use `SECURITY.md` (private reporting), not a public issue.

## Pull requests

- Preserve failed experiments; never rewrite a failure to look successful.
- One change at a time; include a decision record with exact diff, rollback, and verification plan.
- State approval status if the change affects the PnR flow.
- Verify at report level — exit code 0 is not sufficient (D-007).
- Do not claim signoff, functional correctness, or quantified productivity/accuracy gains.
- Do not change `LICENSE` without explicit owner approval.

## Evidence requirements

Every engineering claim must cite a path and, where possible, a line number or hash. If evidence is unavailable, write `NOT EVALUATED`. Implemented, experimental, planned, and unavailable capabilities must be separated (`docs/reference/CAPABILITIES.md`).

## Related

`CODE_OF_CONDUCT.md`, `SUPPORT.md`, `SECURITY.md`, `docs/governance/GOVERNANCE.md`.
