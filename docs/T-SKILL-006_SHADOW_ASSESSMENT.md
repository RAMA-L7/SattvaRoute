# T-SKILL-006 — Dated Shadow-Pilot Assessment (IMMUTABLE RECORD)

- **Assessment date:** 2026-11-23
- **Status:** SHADOW ONLY — R1 is DRAFT/INACTIVE; nothing here approves, launches or enforces anything.
- **Target:** P-SHADOW-001 (`docs/T-SKILL-006_SHADOW_PROPOSAL.md`, SHA-256
  `d20230521dbeaa8b8d79ac04b1678dc012b516794bb84a52e4c6d89a7edb968c`) — unapproved, unexecuted.
- **Instrument:** R1 checklist (`docs/EXPERIMENT_DESIGN_CHECKLIST.md`, SHA-256
  `286c7bbaa53f2c936cc6bc2e87ddb34c9e640b80089051cb0be9d4bcf7b1fc4f`).
- **Methodology reference:** `experimental-design` (PS-001), RECOMMENDED only — not installed, not active.
- **Assessors:** Agent A (R1 application), Agent B (blind independent validity), Agent C (checklist
  usability); coordinator reconciled evidence and adjudicated.
- **Immutability:** this file is a dated record; do not edit it. Corrections must be appended in the
  final report or a new dated assessment.

## 1. Experiment class determination

P-SHADOW-001 is a **mechanism-only, multi-arm diagnostic**: no causal contrast is asserted, no remedy
geometry is proposed, and no baseline claim is made. It is nevertheless multi-arm (A/B/C) and
includes an all-pin AP survey, so A4/A6 and A10 apply. A3 is N/A-*eligible* and A7 is class-excluded,
but R1 requires written justification plus independent-reviewer concurrence for every N/A — neither
is available because A15 is unmet.

## 2. Final adjudicated A1–A16 dispositions

| Item | Class | Disposition | Evidence / basis | Coordinator note |
|---|---|---|---|---|
| A1 | diagnostic | **PASS** | Proposal §1 question/claim scope; §4 N=1 per arm and sub-units; §3 response metrics | A PASS; B PARTIAL (wants response vs evidence fields explicitly separated). Kept PASS: all R1 PASS elements are present, separation concern recorded as usability finding. |
| A2 | all | **PASS** | Proposal §4: AP candidates/DRC markers are sub-units, not replicates | A and B agree. State N=3 distinct run IDs and no claim beyond measurement completeness. |
| A3 | causal diagnostic / remedy — **not applicable as written** | **FAIL** | Proposal §2/§3 calls Arm B "instrumentation identity"; R1 A3 says instrumentation-neutrality is **not** a control. No formal N/A justification or concurrence (A15 unmet) | A scored PARTIAL (N/A-eligible, concurrence pending); B scored FAIL. **Adjudicated FAIL**: the proposal's own mislabeling violates R1; convertible to justified N/A only after renaming Arm B and recording reviewer concurrence. Any later causal/remedy claim → STOP. |
| A4 | multi-arm diagnostic | **PARTIAL** | A vs B single delta (script path); B vs C logging ON; no modification digest or approval IDs | A→C is a two-delta comparison not declared; D-014 held-constant not stated. |
| A5 | all | **PARTIAL** | ODB/config hash, scratch isolation, deterministic order recorded | Missing WSL memory/swap, supervisor mode, D-014 presence, time window, A14 cross-ref. |
| A6 | multi-arm diagnostic | **PARTIAL** | Deterministic rule `sha256(decision_id+run_tag)` recorded | Resulting order not fixed; rule depends on a `decision_id` that does not exist for an unapproved draft. |
| A7 | no remedy family named | **N/A** | Proposal §4: no family selected; FDE-007 R1-N/R1-N-W = one `M4_OBS_CORRIDOR` family | Class-excluded with written justification; concurrence pending A15. Future geometry needs `assess`/`duplicate_check` + `new_justification`. |
| A8 | all | **PARTIAL** | §3 pre-registered diagnostic bar, outcome labels, D-007 binding | Bar explicitly "draft, to be fixed"; no fixed hash list or quantified spacing/EOL mechanism criterion. |
| A9 | all | **PARTIAL** | D-007 invoked; rc≠PASS | No named reviewer, no scheduled review, §B evidence checklist not attached. |
| A10 | pin-access diagnostic | **PARTIAL** | All 12 pins, NOT_RUN for unreached pins, no cross-pin generalisation | No per-pin coordinates/layers/macro-edge table or blocking waiver concurrence. |
| A11 | all | **UNKNOWN** | Proposal §4 flags feasibility; `getSrcs()` availability NOT VERIFIED; historical build blocked then detached under ~2,640 s supervisor | A scored UNKNOWN (preflight unavailable), B scored FAIL. **Adjudicated UNKNOWN** per R1 A.1 ("preflight output unavailable"); if `getSrcs()` is confirmed unavailable it becomes FAIL/STOP. Top execution risk. |
| A12 | all (baseline sub-check class-excluded) | **PARTIAL** | Source ODB hash, scratch isolation, no-modification intent | No `verify-immutable` 9/9 result, scratch path, or `allowed_roots` D-014 mirror hash; post-run ODB check pending. B's "false positive" concern noted in §4. |
| A13 | all | **FAIL** | No max cost (wall-clock/build attempts/reruns), no escalation authoriser; only STOP conditions present | A scored PARTIAL but itself recommended escalation; R1 A.1 FAIL trigger "cost cap absent" is literally met. **Adjudicated FAIL.** |
| A14 | all | **PARTIAL** | Binary hashes "would be recorded per arm" | Two conflicting diagnostic binaries in history (`0d890431…`, `9c0ed727…`); no unified manifest, shims or supervisor mode. |
| A15 | all | **UNKNOWN** | Generic "named independent reviewer" for D-007 in §3, not a pre-run reviewer | A and B both note no identity/COI/sign-off. Per R1 A.1 "reviewer identity or sign-off records unavailable" → UNKNOWN; blocks all N/A concurrences. If the executor self-reviews, it becomes FAIL. |
| A16 | reference (demoted gate) | **N/A** | R1 demotes A16; proposal applies no patch and changes no production file | No `approval_apply.json` expected for a no-change diagnostic. |

**Disposition totals (16 items):** PASS 2 · FAIL 2 (A3, A13) · PARTIAL 8 · UNKNOWN 2 (A11, A15) · N/A 2 (A7, A16).
No applicable item beyond A1/A2 is a clean PASS. This is a shadow design-quality verdict, **not** a gate action.

## 3. Design weaknesses detected

1. **Control mislabeling (A3).** Arm B is a logging-neutrality check, not an identity/no-op control; citing it as one would invite a disguised causal claim.
2. **Logging-ON arm C unguarded.** A≡B says nothing about C; C's non-provenance outputs (DRT census, AP counts, marker bboxes, rc) must match A, excluding added provenance lines.
3. **`getSrcs()` hard dependency (A11).** Primary response unavailable if the installed build lacks it; history shows instrumented builds blocked and only completed detached under a supervisor kill.
4. **Confounders (A5/A14).** Binary/build mode, D-014 presence, supervisor mode, shared scratch directory and run-order inputs unspecified.
5. **Pseudoreplication handled but unquantified (A2).** N=3 run IDs should be stated; markers/APs are sub-units.
6. **Remedy-family discipline (A7).** No family selected (correct); any future geometry must not be a third `M4_OBS_CORRIDOR` variant without `new_justification`.
7. **Acceptance and cost (A8/A13).** Draft bar with no fixed hash list/quantified mechanism; no cost cap or authoriser.
8. **Independence (A15).** No pre-run reviewer → all N/A concurrences and D-007 sign-off unavailable.

## 4. Corrections proposed to the PROPOSAL (not to R1)

1. Rename Arm B "instrumentation-neutrality check (production vs diagnostic, logging OFF)"; never cite as control; mark A3 N/A with written justification + reviewer concurrence.
2. Require C's non-provenance outputs to match A; verify `getSrcs()` availability in the exact binary before approval.
3. Attach FDE-001 preflight, wall-clock ceiling, detached execution mode and timeout/escalation plan; record model rank N/A.
4. Add a unified toolchain identity manifest (production + diagnostic binaries, commit, Yosys/ABC, shims, supervisor mode) and per-arm hashes.
5. Add nuisance-factor table (D-014 held constant, WSL memory/swap, scratch path, time window) and fix concrete run order.
6. Finalise §3 bar (remove "draft"), fix hash list and quantified spacing/EOL criterion; add cost cap + single escalation authoriser.
7. Name an independent pre-run reviewer (disjoint, COI recorded, A1–A15 sign-off) and schedule D-007 review.
8. Add per-pin coordinate/layer/edge table; cover FDE-007's omitted "foreign-metal-free justification" and draft (not execute) a full-flow plan.

## 5. Checklist usability findings (Agent C)

- Worked well: A1, A2, A5, A6, A8, A9, A10, A14, A16; R12 class column and ED-1/ED-2 wording held up.
- **False-positive risk:** A11/A12(b) and A15 demand execution/post-run artifacts from a *pre-run* checklist; A13 cost caps can be manufactured on a no-remedy diagnostic. A strict reader can inflate FAILs on otherwise sound diagnostics.
- **Missing criteria:** `getSrcs()` API availability (M1), KLayout version + layer/datatype map (M2), detached-build contingency (M3), explicit no-remedy boundary (M4), per-marker/same-net-vs-foreign-net evidence fields (M5), KB family check when family is a non-goal (M6).
- **Consistency defect:** §B row 104 still says A15 sign-off "on A1–A12" while §A.1 A15 says A1–A15.
- Proposed R2 directions: a **Stage column** (`design` / `execution` / `post-run` + DEFERRED), a new **A17 measurement-capability preflight**, a four-class model adding `mechanism-only diagnostic`, and wording fixes R2-A…R2-L. No R1 edit was made.

## 6. Shadow outcome

R1 successfully identified the real weaknesses before approval: control mislabeling, missing feasibility gate, draft bar, missing cost cap and absent independent reviewer. It also produced some manufactured/ill-timed gaps (A11/A12(b)/A15) that a Stage column would resolve. **No preventive effectiveness is claimed** — this was one shadow application of a DRAFT/INACTIVE instrument.

No experiment was executed or approved; no production, baseline, KB, approval-control or historical FDE report was changed; no skill was installed; R1 was not modified or activated.
