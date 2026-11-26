# Scope integrity record

Status: verified from `git status` and `git diff --stat` at milestone end. Branch `main`, base commit `783d7655af36b084fe958c216a54a0b7a58f58d8`.

## Working tree inventory

- Modified tracked files: **12** — `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CITATION.cff`, `THIRD_PARTY_NOTICES.md`, `docs/architecture.md`, `docs/recovery.md`, `docs/workflow.md`, `docs/REPRODUCIBILITY.md` (appended QA correction note only), plus appended outcome records in `PROJECT_STATE.md`, `coordination/TASK_BOARD.md`, `coordination/ACTIVE_WORK.md`.
- Untracked new files/directories: **15** root entries covering `CODE_OF_CONDUCT.md`, `SUPPORT.md`, `coordination/DOC_OVERHAUL_PLAN.md`, `docs/DOCUMENTATION_INDEX.md`, and 12 new documentation directories.
- New documentation files: **66** across `docs/product`, `docs/architecture`, `docs/engineering`, `docs/workflow`, `docs/security`, `docs/reproducibility`, `docs/reference`, `docs/governance`, `docs/research`, `docs/diagrams`, `docs/audit` (plus the root/index files above).

## Scope confirmations

| Item | Changed? | Evidence |
|---|---|---|
| Production source (`scripts/*.py`, `*.sh`, `.tcl`) | NO | No paths under `scripts/` in git status |
| Runner / approval / diagnosis / verifier | NO | No `scripts/` change |
| Benchmark RTL, `config.mk`, netlist, provenance | NO | No path under `benchmark/` |
| SDC (`constraint.sdc`, `constraint_1ns.sdc`) | NO | No SDC file changed |
| LEF / Liberty / platform collateral | NO | No LEF/Liberty file changed |
| Manifest / approval policy | NO | `config/`, `state/` unchanged |
| Historical evidence (`evidence/`, `runs/`, `logs/`, investigations) | NO | No path under those directories |
| Evaluation scores / approval records / patches | NO | No change under `knowledge/`, `proposals/`, `experiments/`, `state/` |
| LICENSE | NO | Not in modified list; only `THIRD_PARTY_NOTICES.md` supplemented |
| Git history / branches / PRs | NO | No commit, push, PR, merge, rebase, or force-push performed |
| New OpenROAD / ORFS experiments | NO | None run |
| New recovery attempts | NO | None run |
| DRT-0073 / OpenFinRAM | NO | Unresolved, preserved, excluded, not reopened |

## Modifications explained

- `README.md`: rewritten as product entry point; one link corrected during QA.
- `CONTRIBUTING.md`: rewritten to fix outdated "`tests/` is empty" claim.
- `SECURITY.md`: appended cross-references to new security docs; original policy text retained.
- `CITATION.cff`: title/abstract aligned with the authoritative product definition; AI advisory status explicit.
- `THIRD_PARTY_NOTICES.md`: appended Nangate45/FakeRAM rows and pointer to the full inventory; no attribution removed.
- `docs/architecture.md`, `docs/workflow.md`, `docs/recovery.md`: a single supersession header added above unchanged original text.

## Verdict

Documentation-only scope: **VERIFIED**. No engineering execution, collateral, history, or external publication action occurred.

## Related

`docs/audit/QA_FINAL.md`, `docs/governance/RELEASE.md`, `coordination/DOC_OVERHAUL_PLAN.md`.
