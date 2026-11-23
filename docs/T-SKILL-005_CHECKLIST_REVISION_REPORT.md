# T-SKILL-005 — Experimental Design Checklist Revision Report

- **Date:** 2026-11-23
- **Task:** T-SKILL-005 — revise the DRAFT checklist using T-SKILL-004 findings, then re-score.
- **Status:** revision complete; checklist remains **DRAFT / INACTIVE / not an installed skill or active gate**.

## 1. Versions and provenance

| Version | Path | SHA-256 |
|---|---|---|
| R0 (pre-revision) | `docs/EXPERIMENT_DESIGN_CHECKLIST_R0.md` | `a445c7ae48236456815e8ae2eb46faf48ad0784d2a0f83d2a77ffb58d9e0c091` |
| R1 (re-score basis) | working copy at re-score time | `e6b2240b25844b0cef9a5c246fd74fc636993803f4251f0094596eca6a775b3c` |
| R1 final (post editorial cleanup) | `docs/EXPERIMENT_DESIGN_CHECKLIST.md` | `286c7bbaa53f2c936cc6bc2e87ddb34c9e640b80089051cb0be9d4bcf7b1fc4f` |

R0 was preserved byte-for-byte before revision; its hash matches the value cited in T-SKILL-004.
Source of truth for the revision: `docs/EXPERIMENT_DESIGN_CHECKLIST_REVIEW.md` (R1–R12 exact wording,
A13–A16 proposals) and `docs/T-SKILL-004_RETROSPECTIVE_VALIDATION.md` (defects to fix).

## 2. Revisions applied (Agent A)

| Revision | Target | Application |
|---|---|---|
| R1 | A1 | Unit (one run ID) vs sub-unit; response vs evidence fields; claim scope |
| R2 | A2 | Generalised N rule; cross-reference A7 |
| R3 (mandatory) | A3 | Identity (no-op) arm definition; instrumentation-neutrality warning; diagnostic N/A exemption |
| R4 | A4 | Per-comparison single delta; D-014 held-constant rule |
| R5 | A6 | "Deterministic order" + fixed-order exemption with concurrence |
| R6 (mandatory) | A7 | Authoritative key `relationships.remedy_family`; existing `sattva_kb.py duplicate_check()`; retitled away from "aliasing" |
| R7 (mandatory) | A8 | Class-specific bar (diagnostic / remedy / baseline); post-hoc narrowing allowed, broadening forbidden; D-007 binding |
| R8 | A9 | Provenance corrected: D-007 is project policy, not upstream wording |
| R9 (mandatory) | A11 | Feasibility + supervisor/timeout plan; "model rank" N/A only on single-arm |
| R10 (mandatory) | A12 | Split into protected artifacts / baseline ODB / isolation; `tools/` false positive removed via approval-policy `allowed_roots` exception |
| R11 | A10 | Meaningful N/A; unevaluated pins NOT_RUN; no one-pin-to-all-pins generalisation |
| R12 | § A | Applicability column + class-aware NO vs N/A GATE RULE |
| A13 | new | Cost and stopping rule |
| A14 | new | Toolchain identity manifest (production + diagnostic binaries) |
| A15 | new | Independent pre-run reviewer with COI status and sign-off |
| A16 | new → reference | Rollback/restoration wording retained but **demoted to reference, not a gate** (FDE-002 `apply_patch()` + D-014 preflight + A12 already cover it) |

Additionally, explicit PASS / FAIL / PARTIAL / UNKNOWN / N/A definitions were added for every item
A1–A16 (§ A.1), and sections B–E (evidence fields, anti-patterns, exclusions, usage) were updated.

## 3. Agent B independent review (ACCEPT WITH LIMITATIONS)

- All 16 revisions traced verbatim; four R0 defects (A3 self-contradiction, A7 wrong key/term,
  A8 over-breadth, A12 false positive/duplication) genuinely resolved; A9 provenance corrected.
- Governance intact: DRAFT/INACTIVE, no install/activation, D-007 binding, R0 hash unchanged,
  A16 demotion justified against actual `apply_patch()` code.
- Verdicts: A1/A3/A4/A6/A7/A8/A9/A11/A13 CLEAR+TESTABLE; A2/A5/A14 NEEDS CLARIFICATION (minor);
  A10/A12(b) NOT PRE-RUN TESTABLE (full PASS needs post-run evidence); A16 N/A as gate.
- **Three minor non-blocking findings were fixed** before publication:
  - **ED-1:** N/A now permitted for class exclusions **or** named structurally-impossible sub-checks,
    but not for a whole applicable item; A14 single-arm case is a **modified PASS**, not N/A.
  - **ED-2:** A15 sign-off scope corrected from A1–A12 to **A1–A15** (A16 is a reference line).
  - A revision-ledger note records that the R1 re-score used hash `e6b2240b…`, while these editorial
    changes do not alter any applicability class, PASS condition or disposition.

## 4. Agent D integrity audit (ACCEPT WITH LIMITATIONS)

- KB `verify`: 18 records / 18-link chain / 0 problems.
- `verify-immutable`: 9/9 OK, `changed=[]`.
- Validator: `PASS=13 FAIL=0`.
- R0/R1 hashes matched at audit time; KB ledger, protected artifacts, approval controls, FDE reports
  and skill statuses unchanged; checklist DRAFT/INACTIVE; 0 skills installed/active.
- R0 scorecard arithmetic independently verified: P23/Q40/F16/?3/N-A14 = 96, assessable 79.
- Findings addressed: the two required T-SKILL-005 reports were created (this file and the comparison);
  the stale "a445c7ae… is current" citation is explained above as the R0 snapshot; the T-SKILL-004
  "A3 (3 cases)" undercount is annotated in the comparison report rather than rewriting that document.

## 5. Verification results (final)

| Check | Actual |
|---|---|
| KB `verify` | PASS — 18 records, 18-link chain, 0 problems |
| `verify-immutable` | PASS — 9/9 protected artifacts, `changed=[]` |
| `.skills/validate_skills.py` | PASS=13 FAIL=0 |
| R0 snapshot SHA-256 | `a445c7ae…e0c091` unchanged |
| R1 final SHA-256 | `286c7bbaa…2401` |
| EDA / new experiment | none |
| Activation / install / status change | none |

## 6. Remaining weaknesses

- A10 and A12(b) cannot reach full PASS pre-run; post-run evidence is required for pin disposition and
  restored-state confirmation. They remain PARTIAL retrospectively and must be accepted as bounded
  deviations in a shadow pilot.
- A13–A15 are now present but historically unverifiable (no cost caps, toolchain manifests or
  independent reviewer COI/sign-off records on the audited runs); all score PARTIAL.
- A16 is a reference line, not a gate; uneven historical evidence does not affect scoring.
- No shadow/observational pilot has been run. **No preventive effectiveness is claimed.**

## 7. Governance

`experimental-design` (PS-001) remains **RECOMMENDED — methodology reference only**, not installed,
not active. The checklist remains DRAFT and INACTIVE. No EDA, production, baseline, KB, approval-control,
historical FDE report or protected artifact was changed. Explicit authorization is required before any
shadow pilot or activation.
