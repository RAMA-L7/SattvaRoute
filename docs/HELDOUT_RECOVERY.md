# Held-out recovery trial (Phase 8) — honest outcome

## Status

**Held-out failure is REAL and isolated. Deterministic diagnosis produced a
bounded proposal. NOTHING was applied without explicit user approval. The user
APPROVED the exact displayed single-target patch; it was applied via
scripts/sattva_approval.py; an isolated recovery rerun executed; independent
erify_recovery returned **PASS**. NO live-AI recovery is claimed (no model
credentials; deterministic result). Historical runs/originals preserved.**

## Frozen before the trial (no post-result tuning)

- Diagnosis implementation: `scripts/diagnosis_agent.py` (generalized; **not**
  hardcoded to any held-out name; no injected `missing_*` reliance).
- Prompt: "Propose a textual correction for review; do not execute or apply
  it."
- Evaluation rubric + implementation frozen: `scripts/evaluate_diagnosis_v2.py`
  (`t1_rubric/v2`). v1 preserved. Acceptance criteria fixed; not adjusted after
  seeing this case.
- Successful control baseline preserved untouched:
  `runs/orfs_baseline_nangate_macro_control_20261125T144339456871595Z_11464`.

## Selected case (materially different from `missing_fakeram`)

Attempt-local `ADDITIONAL_LEFS` referencing a **nonexistent macro LEF**.
- **Different variable** (`ADDITIONAL_LEFS`, not `ADDITIONAL_LIBS`/`LIB_FILES`).
- **Different declaration structure** (appended override in attempt-local
  `config.mk`; original `export ADDITIONAL_LEFS=$(PLATFORM_DIR)/lef/fakeram45_64x32.lef`
  also present; later wins in Make).
- **Different nonexistent name** (`no_such_macro_widget.lef`, unseen).
- **Different stage**: actual **`synth`**, not `missing_fakeram`'s synth-lib.
  (Checkpoint hypothesis said "floorplan"; direct evidence shows `synth`
  because ORFS adds `ADDITIONAL_LEFS` as a make prerequisite for `1_synth.odb`.
  Claims match demonstrated evidence.) 
- **Label**: within-family-adjacent generalization (not a new failure family).
  Historical `missing_fakeram45_64x32.lib`/`ADDITIONAL_LIBS` (T-PNR-001,
  `AP-PNR-003`) is separate historical evidence.
- **Not** a constraint change; **not** DRT-0073; **not** OpenFinRAM.

## Creation (isolated; originals untouched)

Attempt-local copy under `experiments/PNR-RECOVERY/heldout_additional_lefs_<ts>/design`;
pristine `config.mk` copied then ONE appended line injected:
`export ADDITIONAL_LEFS = <attempt>/lef/no_such_macro_widget.lef`. `constraint.sdc`,
`rtl`, `netlist` copied; benchmark originals unmodified; no useful preflight
check disabled.

## Real execution (actual runner)

`scripts/run_baseline_orfs.sh`, `SATTVA_DESIGN_PROFILE=nangate_macro_control`,
real ORFS pinned `25b6429c…`, local patches present.
- `check-yosys` rc=0, `check-openroad` rc=0, `synth` **rc=2**; stops.
- `make: *** No rule to make target '<attempt>/lef/no_such_macro_widget.lef',
  needed by '.../1_synth.odb'. Stop.`
- Run: `runs/orfs_baseline_heldout_additional_lefs_20261126T131626892892371Z_3737`
  (local; not published bulk; evidence preserved; original preserved).
- Failed-run evidence supplied to diagnosis **only**; no recovery answer,
  approval record, clean replacement diff, or grader ground truth was supplied.

## Diagnosis (deterministic; separate from model reasoning)

`scripts/diagnosis_agent.classify_failure`:
- `family = MISSING_MACRO_LEF`, `signature = missing macro LEF reference`
- `failed_stage = synth`, `failed_rc = 2`
- `missing_file = <attempt>/lef/no_such_macro_widget.lef`
- `missing_references = [...no_such_macro_widget.lef]`
- `source = deterministic_parser`

## Proposal (textual, for review; NOT applied)

`scripts/diagnosis_agent.propose_patch(..., baseline=nangate_macro_control,
mirror=...)`. Full record: `evidence/timing/heldout_proposal.json`.

- `status = proposal`, `applies = false`, `approval_status = PENDING`
- `note = Propose a textual correction for review; do not execute or apply it.`
- `family = MISSING_MACRO_LEF`, `variable = ADDITIONAL_LEFS`
- `target_file = <attempt>/design/config.mk`
- `current_resolved_value = [ $(PLATFORM_DIR)/lef/fakeram45_64x32.lef,
  <attempt>/design/lef/no_such_macro_widget.lef ]`; effective = injected.
- `current_bad_reference = <attempt>/design/lef/no_such_macro_widget.lef`
- `intended_value = $(PLATFORM_DIR)/lef/fakeram45_64x32.lef`
- `intended_value_resolved = .../flow/platforms/nangate45/lef/fakeram45_64x32.lef`
  (exists; compatible pinned macro; **no different macro/corner**; `intended_value_source`
  = compatible baseline `nangate_macro_control/config.mk`)
- `earliest_affected_stage = synth`; `downstream_invalidation = synth..finish`
- `patch_sha256 = 66d13d49529f374b6a8e2eff60d505e346d72d5c4f1bc22b1dcd816ae9428984`
- `target_original_hash = addb5ef67bea8e5953f1d6ca828628689f781505c81fa4137175022ece7ae7b1`

### Exact diff (attempt-local `config.mk` only)

```diff
--- <attempt>/design/config.mk
+++ <attempt>/design/config.mk
@@ -27,4 +27,6 @@
 
 # HELD-OUT injected fault (attempt-local only; originals untouched):
 # ADDITIONAL_LEFS references a nonexistent macro LEF -> fails at floorplan.
-export ADDITIONAL_LEFS = <attempt>/design/lef/no_such_macro_widget.lef
+
+# recovery: restore compatible pinned reference
+export ADDITIONAL_LEFS = $(PLATFORM_DIR)/lef/fakeram45_64x32.lef
```

(The `-> fails at floorplan` text is the injected attempt-local comment, not a
SattvaRoute claim; actual stage is `synth`.)

### Risks / verification (not filler)

- restoring collateral doesn't guarantee timing closure / DRC=0
- macro/corner identity must remain pinned; no corner substitution
- downstream synth→finish invalidated; must rerun or be validly reused
- `scripts/evaluate_diagnosis_v2.py` `_scratch_test` applies diff to scratch
  copy only; rejects unrelated change, broad deletion, corner change,
  constraint relaxation; `apply_unified_diff` re-applied. (v2 separately
  reports schema/reference validity vs engineering correctness.)
- apply via `scripts/sattva_approval.py` (single-target exact patch); allowed
  roots include `experiments/PNR-RECOVERY`; revalidate deps + source run.

## Live model

`optional_model_note` / `live_diagnosis`: **no model credentials**
(`SATTVA_MODEL_URL` unset) → available=false / `SKIPPED_NO_CREDENTIALS`. **No
genuine live-AI proposal obtained; not counted as successful live-AI recovery.**
Deterministic result retained. **Live acceptance item OPEN.**

## Evaluation (v2, frozen)

`scripts/evaluate_diagnosis_v2.py`. This trial does not tune thresholds. The
deterministic `propose_patch` output is not the model `REQUIRED_FIELDS` schema;
reported accordingly, not as a live-AI result. No hard-coded held-out name in
implementation. 

## Recovery gate (STOP — request explicit approval)

Per `scripts/sattva_approval.py`, before any mutation the user must approve the
**exact displayed diff**. Required to proceed would be:
1. human creates/approves an approval record bound to `target_file`,
   `expected_original_hash`, `patch_sha256`, `input_fingerprint`,
   `earliest_affected_stage`, `rerun_scope` (contiguous, `synth..finish`);
2. revalidate dependencies + source-run identity;
3. apply only this operation to `<attempt>/design/config.mk`;
4. invalidate affected outputs; resume `synth..finish`; 
5. `scripts/verify_run.py --baseline B --failure F --recovery R
   --approval-apply A --targeted-marker no_such_macro_widget`; confirm approved
   change reached executed config, targeted failure cleared, downstream reran,
   no collateral regression vs frozen baseline; baseline≠PASS⇒FAIL.

**Approval AP-HELDOUT-LEFS-001 created by the user decision; exact patch
applied via scripts/sattva_approval.py apply (phase=verified,
efore_sha256=addb5ef…, fter_sha256=83c2d7a…, backup retained;
pproval_apply.json/pproval_guard.json). Recovery run
orfs_baseline_heldout_recovered_20261126T135313595854554Z_8250 (rc=0; 6
affected stages). erify_recovery: baseline PASS / failure FAIL / recovery
PASS -> **PASS**; pproved_change_reached, 	arget_failure_cleared,
downstream_scope, collateral_regression, ailure_is_real. Evidence
evidence/verification/heldout_recovery_verify.json. Originals/history
preserved. Not live-AI.**

## Historical

T-PNR-001 `AP-PNR-003`/`RESTORE_MACRO_LIB` (`missing_fakeram45_64x32.lib` /
`ADDITIONAL_LIBS`) is historical evidence only; not this case; not reopened.
T1-LIVE-R2 historical; not modified. DRT-0073 unresolved; not reopened.
