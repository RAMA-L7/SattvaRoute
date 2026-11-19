# Implemented architecture

This document describes what exists in this release. Empty placeholder directories are identified as such.

## 1. Stage runner (implemented)

`scripts/run_baseline_orfs.sh` is the workflow controller:

- generates a nanosecond UTC stamp + PID and atomically creates `runs/orfs_baseline_<stamp>_<pid>/` (collision-safe);
- runs required preflight checks and **blocks execution** if any required tool/input is missing; KLayout is optional/warned;
- records `preflight.txt`, machine-readable `preflight.json`, and the exact `mirror.patch` diff; hashes inputs, the executed binaries, the runner and the patched `global_route.tcl`;
- executes the fixed stage sequence `check-yosys → check-openroad → synth → floorplan → place → cts → route → finish`;
- captures each stage's stdout/stderr into `evidence/stage_<stage>.log`;
- stops at the first non-zero stage exit code and records `stages.txt`, `stages.tsv`, machine-readable `run.json`, and `postflight.txt`; hashes all produced artifacts/reports;
- exits with the failed stage's return code (or 1 for preflight failure), so schedulers can trust `$?`;
- never overwrites a previous run. Paths are parameterised via `SATTVA_*` / `OPENROAD_EXE` / `YOSYS_EXE` environment variables.

Each stage delegates to ORFS `make`, which invokes a single OpenROAD process with the stage Tcl script. The fail-fast rule is execution control, not evidence of engineering success.

## 2. EDA execution and adapters (implemented)

- OpenROAD (`bazel-nostamp`) performs synthesis handoff, floorplan, placement, CTS, global routing and detailed routing.
- The ASAP7 platform provides technology, libraries and the baseline PDN strategy.
- Design-local adapters: `config.mk`, `constraint.sdc`, `pdn_sattva.tcl`, `macro_placement.tcl`.

## 3. Evidence collection (implemented)

Per run:

```
runs/<id>/evidence/   preflight.txt/json, mirror.patch, stages.txt/tsv, run.json,
                      stage_*.log, artifact_sha256.txt (all produced files)
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
