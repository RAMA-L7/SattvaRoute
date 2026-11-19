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

## 5. Approval service (implemented and offline-verified — FDE-002)

`scripts/sattva_approval.py` is a standard-library-only deterministic boundary:

- durable approval JSON binds approval ID, decision ID, source run ID, input fingerprint, exact patch SHA-256, target file + expected original hash, earliest affected stage, contiguous rerun scope, approver, `APPROVED`/`REJECTED`, timestamp and optional note;
- `validate` rejects missing/rejected/malformed records, unknown or altered patches, fingerprint/run/decision/scope/original-hash mismatches, and stale/reused approvals via an append-only JSONL ledger;
- `apply` accepts only targets inside `state/approval_policy.json`'s explicit `allowed_roots`, rejects traversal and symlinks, applies a strict single-target unified diff atomically, preserves a backup, writes before/after hashes and rollback evidence, and refuses concurrent modification via an exclusive lock;
- the runner calls `guard` before any patch application and again immediately before the affected stage(s); when an approval gate is configured it runs **only** the declared rerun scope after checking the source run's evidence-based input artifacts.

D-013 (failed) and D-014 (applied, partial) remain recorded in `docs/decisions/`. No real approval for a real patch was fabricated during FDE-002; all tests use temporary files.

## 6. Persistent run state (implemented, file-based + JSON)

`PROJECT_STATE.md`, `coordination/*`, `logs/*`, plus machine-readable per-run `evidence/preflight.json`, `evidence/run.json`, `evidence/approval_guard.json`, `evidence/approval_apply.json`, and the approval ledger under `state/`.

## 7. Not implemented in this release

`app/`, `configs/`, `artifacts/` and `experiments/` are empty placeholders in the local project. There is no backend, worker, persistent database service, or dashboard in this publication. `tests/` now contains two **offline** suites (`test_runner.sh`, `test_approval.py`) — these are not an EDA integration suite; no real flow run is executed by them.
