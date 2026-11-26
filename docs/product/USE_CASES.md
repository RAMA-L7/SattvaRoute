# Use cases

All use cases below are framed around the implemented control benchmark and deterministic tooling. Model-assisted steps are advisory and optional. See `docs/reference/CAPABILITIES.md`.

## UC-1 — Diagnose a failed control run from preserved evidence

**Actor:** physical-design engineer. **Input:** a run directory with `evidence/`. **Flow:** `diagnose` → review classification, mechanism, `evidence_refs`, earliest affected stage → decide. **Output:** evidence-bound diagnosis or `insufficient_evidence`. The tool does not apply anything.

## UC-2 — Investigate a missing macro Liberty reference

A controlled failure fixture (`failure-demo`) omits the macro Liberty reference in an attempt-local config. Diagnosis identifies the missing `ADDITIONAL_LIBS` target from the Make error and logs, binds the claim to stage logs, and proposes a bounded correction to that variable only. Original control collateral is untouched.

## UC-3 — Investigate missing macro LEF inputs

A held-out case (`ADDITIONAL_LEFS`) fails at synthesis. The diagnosis is deterministic; a human-approved patch restores the pinned macro LEF reference. The recovery attempt is isolated and independently verified. See `docs/HELDOUT_RECOVERY.md`. This was **deterministic, not live-AI recovery**.

## UC-4 — Audit timing units and constrain a run correctly

Read `report_units`, Liberty `time_unit`, and the executed SDC. The historical 1000 ns / 1 ns 1000× discrepancy is reconciled from tool evidence; `constraint_1ns.sdc` was explicitly approved and applied while `constraint.sdc` was preserved. See `docs/engineering/SDC_TIMING.md`, `docs/TIMING_AUDIT.md`.

## UC-5 — Review a proposed correction before any change

`propose` emits a textual patch with exact diff, current/intended resolved values, original hash, patch hash, earliest affected stage, downstream invalidation, risks, and verification criteria. `approve-view` displays it. Nothing is applied until a human creates an approval record.

## UC-6 — Execute an approval-gated, stage-limited recovery

A human creates an approval via `sattva_approval.py create` binding the exact patch hash, decision, source run, and rerun scope. `resume` validates approval before invoking the runner; the runner applies only the approved op and reruns from the earliest affected stage.

## UC-7 — Independently verify an outcome

`verify_run.py` checks execution, artifacts, engineering report signals, evidence completeness, and recovery regression against the baseline. Missing evidence fails; a zero return code is not sufficient.

## UC-8 — Reproduce the benchmark from pinned inputs

Acquire the pinned ORFS revision, apply the two recorded local patches, build the pinned tool binaries, set `SATTVA_MIRROR`, and run the documented commands. See `docs/REPRODUCIBILITY.md`.

## UC-9 — Evaluate diagnosis quality in research

Use the frozen `evaluate_diagnosis_v2.py` rubric and held-out bundles. Live-AI calls are advisory and counted only with real credentials; without them the status is `BLOCKED`/`SKIPPED_NO_CREDENTIALS`. See `docs/reproducibility/EVALUATION.md`.

## Non-use cases

Not supported: signoff DRC/LVS, functional correctness, multi-corner timing, foundry macro characterization, autonomous production edits, reopening `DRT-0073`.
