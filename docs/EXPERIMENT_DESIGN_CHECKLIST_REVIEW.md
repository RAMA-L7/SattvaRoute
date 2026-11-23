# Checklist Review — `docs/EXPERIMENT_DESIGN_CHECKLIST.md` (A1–A12)

- **Task:** T-SKILL-004 · **Date:** 2026-11-23
- **Reviewed artifact:** DRAFT checklist, SHA-256 `a445c7ae48236456815e8ae2eb46faf48ad0784d2a0f83d2a77ffb58d9e0c091`
- **Disposition:** checklist **unchanged** by this milestone; all recommendations below are for the next
  revision. Do not activate or enforce it before revision and a shadow pilot.
- **Sources:** Agent B (FDE-006U/007 retrospective), Agent C (instrument evaluation), Agent A
  (FDE-005/006 retrospective), Agent D (integrity).

## 1. Executive assessment

The instrument is conceptually sound and has high **retrospective diagnostic** value: 10/12 items map
to documented historical failure modes. It is **not** yet safe as a pre-run gate: A3 is
self-contradictory and over-strict, A7 names the wrong concept and misses an existing mechanical check,
A8 applies a remedy bar to diagnostics, A12 contains a protected-path false positive, and several
failure modes are absent.

**Verdict: REVISE — then run one shadow/observational pilot before promoting to a gate.**

## 2. Per-item disposition

| Item | Classification | Action |
|---|---|---|
| A1 | COVERS; ambiguous | R1 — define unit vs sub-unit, claim scope, evidence vs response |
| A2 | COVERS; overlapping A1 | R2 — generalise rule, cross-reference A7 |
| A3 | COVERS; **self-contradictory, too restrictive** | **R3 (mandatory)** — identity-arm definition + diagnostic exemption |
| A4 | COVERS | R4 — scope to per-comparison delta; held-constant D-014 |
| A5 | COVERS; partial duplication | tighten with A14 toolchain identity |
| A6 | COVERS; misnamed, over-strict | R5 — "deterministic order", fixed-order exemption |
| A7 | COVERS; wrong key and wrong term | **R6 (mandatory)** — name `relationships.remedy_family`; retitle |
| A8 | COVERS; too broad | **R7 (mandatory)** — class-specific bar; narrowing clause |
| A9 | COVERS; provenance error | R8 — D-007 is project policy, not upstream wording |
| A10 | COVERS; ambiguous N/A | R11 — record evaluated pins; NOT_RUN for unevaluated |
| A11 | COVERS; "full rank" misapplied | **R9 (mandatory)** — feasibility + supervisor/timeout plan |
| A12 | COVERS; duplicates A11, false positive | **R10 (mandatory)** — split into three checks; fix `tools/` wording |
| — | Missing modes | A13–A16 |

## 3. Actionable revisions (exact wording)

### R1 — A1 (unit/response, claim scope)
> **INFERRED:** Question = the decision this run can change (mechanism attribution vs remedy validation
> vs baseline claim), stated explicitly. Unit = one isolated run with one fixed configuration and one run
> ID; a marker, AP candidate, pin, layer, corner or stage is a **sub-unit**, not a replicate. Response =
> the measured outcome (accepted AP count, sparse count, DRT-code census, stage rc). Hashes, logs,
> commands and error censuses are **evidence/control fields**, not response variables. Write all three
> before the run and state the intended claim scope.

### R2 — A2 (generalise + cross-reference)
> **INFERRED:** N = the number of distinct run IDs whose configuration differs only by the pre-registered
> factor levels. Every sub-unit sharing one run ID — AP candidate, DRC marker, pin, layer, corner, stage,
> log line — counts **once**. FDE-006U's 9 candidates / 107 markers are repeated measurements of ONE run.
> Two levels of one remedy family (A7) are two levels, **not** two replicates. **PASS:** N stated as a run
> count; no sub-unit or family-level variation counted as a replicate; inferential claim bounded to N.

### R3 — A3 (identity arm; MANDATORY)
> **INFERRED:** For a remedy arm, plan an **identity (no-op) arm**: same binary SHA, same source ODB SHA,
> same config, same session, with the approved change replaced by its identity value (no OBS edit, no
> flag). The identity arm differs from the remedy arm **only by absence of the approved change**.
> Instrumentation-neutrality checks (FDE-006U §3 `prod == olddiag == newdiag_off`) verify that logging is
> behavior-neutral; they are **not** a control and must not be cited as one. A prior historical run is not
> a concurrent control. **PASS:** identity-arm modification digest equals the approved baseline digest;
> its run ID, binary/ODB/config hashes and execution window are recorded beside the remedy arm. **If
> absent:** record the gap; a mechanism-only diagnostic that asserts no causal contrast may mark A3 = N/A
> with written justification and independent reviewer concurrence; any causal/remedy claim is NO under
> the GATE RULE.

Rationale: FDE-005 had a genuine scoped no-flag control (PASS); FDE-006U/007 did not. A blanket STOP
would have blocked accepted work — class-aware disposition is required.

### R4 — A4 (per-comparison scoping)
> One approved delta **per arm-to-arm comparison**; no simultaneous LEF + config + binary + placement
> change within a comparison. Record the exact modification digest and the decision/approval IDs. A change
> replicated identically in all arms (e.g. D-014 `zero_ setSpecial`) is a held-constant, not a variable.
> A declared multi-factor/blocked design requires its model matrix and alias structure approved as a whole
> (cross-ref A7) and must not be described as "single variable".

### R5 — A6 (deterministic order, not "randomized")
> When ≥2 arms are planned, assign order with a pre-recorded deterministic rule (e.g. sort by
> `sha256(decision_id + run_tag)`), not convenience; "randomized" here means reproducible
> pseudo-randomisation. A fixed order is acceptable with a written justification that order-driven drift is
> impossible (hash-pinned binary, no shared mutable state, same session) plus reviewer concurrence. Record
> the rule and resulting order before execution.

### R6 — A7 (authoritative key; MANDATORY)
> **No aliasing of remedy families / parameter-variation repeats.** The authoritative key is
> `relationships.remedy_family` in `knowledge/kb_records.jsonl` (views: `by_remedy_family` and
> `repeated_families` in `knowledge/kb_manifest.json`). Variations within one family — FDE-007 R1-N
> (x3534–3672) and R1-N-W (x3474–3672), both `M4_OBS_CORRIDOR` — are one factor at two levels, never
> replicates or independent confirmations. Before approval run `sattva_kb.py` `assess`/`duplicate_check`
> for the proposed family, signature and design fingerprint; record prior outcomes and any
> `new_justification` for repeating a FAIL family. **PASS:** family key named verbatim, variations labelled
> levels, duplicate-check result attached.

### R7 — A8 (class-specific bar; MANDATORY)
> Before execution write the acceptance bar for **this experiment class**: (a) *diagnostic* — required
> measurement resolution and claim scope (candidate-level vs aggregate-only); (b) *remedy validation* —
> accepted-AP threshold, sparse threshold, required absent DRT codes, stage rc expectations, and
> DRC/extraction/timing disposition labels; (c) *baseline* — full D-007 report-level verification. Fix
> thresholds, outcome labels (PASS/FAIL/INCONCLUSIVE/BLOCKED/NOT_RUN) and hash list in the approval record.
> Post-hoc **broadening** is forbidden; post-hoc **narrowing** with recorded deviations and independent
> reviewer concurrence is permitted (FDE-006U §10). A8 fixes the bar; it never assigns PASS — D-007 remains
> binding.

### R8 — A9 (provenance)
> Verbatim principle: "Document the design, software versions, seed, and schedule." D-007 is project policy
> (`DECISIONS.md`), not upstream wording. **PASS:** the section B evidence checklist is present and the
> D-007 review is scheduled with a named reviewer; do not restate runner output already enforced by FDE-001.

### R9 — A11 (feasibility and supervision; MANDATORY)
> **Feasibility (model rank applies only to a declared multi-factor design).** Attach FDE-001 runner
> preflight output: disk/RAM, unique run ID, isolated scratch directory, no protected-path write. Record
> expected wall-clock ceiling, execution mode (supervised vs detached) and timeout/escalation plan
> (FDE-006S/006T). **PASS:** preflight PASS attached; no protected path in the run plan; NA recorded for
> "model rank" on single-arm runs. Do not duplicate A12's scratch/immutability text.

### R10 — A12 (split; fix `tools/` false positive; MANDATORY)
> (a) *Protected artifacts:* `sattva_kb.py verify-immutable` PASS (9/9 in
> `knowledge/kb_immutable_manifest.json` — note this set includes the production LEF/GDS, config.mk, SDC,
> runner and approval policy but **not** the baseline ODB). (b) *Design baseline:* name the reference run
> and ODB (e.g. FDE-003 `4_cts.odb` `35bff121…`), record its SHA-256 and confirm unchanged after the run.
> (c) *Isolation:* scratch path declared under `experiments/.../scratch_design`. Barred writes are
> `benchmark/`, `runs/`, production LEF/GDS and `D:\tools` **except through the approval gate's
> `allowed_roots`** (`/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow/scripts`), which is the sanctioned
> D-014 mirror path and must itself be hashed. **PASS:** (a)+(b)+(c) recorded with hashes.

### R11 — A10 (meaningful N/A)
> Record the pins actually evaluated with coordinates/layers and macro-edge position; pins not evaluated
> because the tool aborts on the first failing term must be labelled NOT_RUN, and no claim may generalise
> from one pin to all pins. If pin-row/edge-strip blocking is impossible, state why and record the reviewer's
> concurrence instead of a bare "not applicable".

### R12 — section A general (applicability column)
> Add an applicability column (`diagnostic` / `remedy validation` / `baseline`) so A3/A6/A8/A10 can be N/A
> with justification rather than silently NO; keep the GATE RULE but define NO vs N/A explicitly.

## 4. Proposed new items

- **A13 — Cost and stopping rule:** "State the decision this experiment will change, the maximum
  acceptable cost (wall-clock, build attempts, reruns) and the stopping/escalation rule; record who may
  authorise one further iteration."
- **A14 — Toolchain identity manifest:** "Record production **and diagnostic** binary SHA-256s, ORFS/OpenROAD
  commit, Yosys and ABC versions, shims (D-005/D-009), WSL build and supervisor mode; attach the manifest
  to both arms."
- **A15 — Independent pre-run reviewer:** "Name a reviewer disjoint from the experiment executor, record
  conflict-of-interest status and sign-off on A1–A12 before approval."
- **A16 — Rollback/restoration:** "Record how an approved patch is rolled back and how post-run restoration
  (mirror git-clean, source hashes unchanged) will be verified; attach the approval gate's rollback evidence."
  If judged already covered by FDE-002, demote to a reference line rather than a new gate.

## 5. Priority and adoption path

1. **Mandatory before any pilot:** R3, R6, R7, R9, R10 (these remove self-contradiction, wrong keys,
   over-breadth, false positives and missing failure modes).
2. **Strongly recommended:** R1, R2, R4, R5, R11, R12, A13, A14, A15.
3. **Optional/reference:** R8, A16.
4. Then run **one shadow/observational pilot** on the next FDE proposal: record A1–A12 answers without
   enforcing the GATE RULE; compare against reviewer judgment; only then consider promotion to a gate.

## 6. Non-changes and governance

This review changed no checklist content, no historical FDE report, no KB record, no protected artifact
and no skill status. All five catalog entries remain RECOMMENDED; installation gate remains enforced;
the checklist remains DRAFT and inactive. The separate metadata drift in `.skills/PROJECT_SKILLS.json`
(counts vs entries) is a documentation inconsistency to correct in a future catalog update, not a
status upgrade.
