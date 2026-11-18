# Implemented architecture

This document describes what exists in this release. Empty placeholder directories are identified as such.

## 1. Stage runner (implemented)

`scripts/run_baseline_orfs.sh` is the workflow controller:

- generates a UTC timestamp and a unique run directory `runs/orfs_baseline_<stamp>/`;
- records `preflight.txt` (tool versions, hashes, git state of the ORFS mirror);
- executes the fixed stage sequence `check-yosys → check-openroad → synth → floorplan → place → cts → route → finish`;
- captures each stage's stdout/stderr into `evidence/stage_<stage>.log`;
- stops at the first non-zero stage exit code and records `stages.txt` / `postflight.txt`;
- never overwrites a previous run.

Each stage delegates to ORFS `make`, which invokes a single OpenROAD process with the stage Tcl script. The fail-fast rule is execution control, not evidence of engineering success.

## 2. EDA execution and adapters (implemented)

- OpenROAD (`bazel-nostamp`) performs synthesis handoff, floorplan, placement, CTS, global routing and detailed routing.
- The ASAP7 platform provides technology, libraries and the baseline PDN strategy.
- Design-local adapters: `config.mk`, `constraint.sdc`, `pdn_sattva.tcl`, `macro_placement.tcl`.

## 3. Evidence collection (implemented)

Per run:

```
runs/<id>/evidence/   preflight.txt, postflight.txt, stages.txt, stage_*.log, artifact hashes
runs/<id>/work/       ORFS results/logs/databases scoped by per-run WORK_HOME
```

Immutable baseline: `orfs_baseline_20261118T152845Z` (6/7 stages pass, route rc=2 DRT-0305) is never modified. Full run directories are kept locally; this repository publishes curated summaries only.

## 4. Diagnosis layer (implemented as a documented process)

Investigations are performed by independent agents with disjoint read-only scopes. Each agent cites verbatim logs, exact ODB state, and installed tool source lines. Reports live in `docs/investigations/`. The orchestrator integrates and adjudicates; agents do not edit project-wide state.

## 5. Approval service (implemented as a documented process)

A change requires a decision record with: ID, root cause, exact diff, side effects, affected stages, rollback, verification plan, and explicit approval. D-013 and D-014 are recorded in `docs/decisions/`. No flow-script change is applied before approval.

## 6. Persistent run state (implemented, file-based)

`PROJECT_STATE.md` (single snapshot), `coordination/TASK_BOARD.md`, `coordination/ACTIVE_WORK.md`, `logs/DAILY_LOG.md`, `logs/AGENT_ACTIVITY.md`, `logs/REVIEW_LOG.md`, `logs/REPORT_LOG.md`, plus session handoffs under `logs/sessions/`.

## 7. Not implemented in this release

`app/`, `configs/`, `artifacts/`, `experiments/` and `tests/` are empty placeholders in the local project. There is no backend, worker, persistent database service, dashboard, or automated test suite in this publication. Do not assume these components exist.
