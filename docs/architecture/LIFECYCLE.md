# Execution lifecycle

Status: implemented. Related: `docs/diagrams/RECOVERY_LIFECYCLE.md`, `docs/architecture/ARCHITECTURE.md`.

## Stages

The pinned ORFS stages, in order, are declared in `state/approval_policy.json`:

`check-yosys` → `check-openroad` → `synth` → `floorplan` → `place` → `cts` → `route` → `finish`

Stage inputs used for invalidation (from the flow Makefile do-step rules):

| Stage | Declared input |
|---|---|
| floorplan | `1_synth.odb` |
| place | `2_floorplan.odb` |
| cts | `3_place.odb` |
| route | `4_cts.odb` |
| finish | `5_route.odb` |

`synth`, `check-yosys`, and `check-openroad` declare no stage input. These facts are what make stage-limited rerun bounded: an approved change declares an `earliest-stage`, and only that stage and downstream stages are invalidated.

## Baseline lifecycle

1. `pnr_cli.py baseline` invokes `run_baseline_orfs.sh` with `SATTVA_DESIGN`, `SATTVA_DESIGN_PROFILE`, `SATTVA_ROOT`, and a tag.
2. Runner performs manifest preflight (profile-scoped): revision, local patches, collateral hashes, tool hashes.
3. Runner executes stages, capturing `evidence/run.json`, `stages.tsv`, `stage_*.log`, `preflight`, `manifest.json`, `mirror.patch`, artifact hashes, `postflight`.
4. CLI reports `status` from the process return code but explicitly sets `engineering_verdict: NOT EVALUATED - inspect reports`.
5. `verify_run.py` must be run separately to produce a report-level verdict.

## Failure lifecycle

A failed run is produced either by a real implementation failure or by a declared `failure-demo` fixture. The fixture is attempt-local: it copies only the needed control collateral and adds one omitted macro Liberty reference to its own `config.mk`. The original control design is never modified.

## Recovery lifecycle

1. `diagnose` reads evidence → classification + mechanism + earliest affected stage.
2. `propose` builds a bounded textual patch (or `insufficient_evidence`).
3. `approve-view` displays the exact diff, hashes, risks, and verification criteria.
4. A human creates an approval record with `sattva_approval.py create`; `validate` checks it before any apply.
5. `resume` invokes the runner with approval/patch/policy/source-run/decision; the runner applies the approved op and reruns from the earliest affected stage.
6. `verify_run.py --baseline B --failure F --recovery R` produces the independent recovery verdict.

## Failure-state handling

- Preflight mismatch → `FAIL`, run does not proceed.
- Approval validation failure → `FAIL`, no apply.
- Missing evidence → `UNKNOWN` or `FAIL` in verification, never `PASS`.
- Insufficient evidence for a proposal → `NO_PROPOSAL` / `insufficient_evidence`, no approval requested.

## Related

`docs/workflow/WORKFLOW.md`, `docs/architecture/RECOVERY.md`, `docs/reference/STATUS_CODES.md`.
