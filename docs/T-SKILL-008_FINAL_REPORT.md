# T-SKILL-008 — Prospective R2 Shadow Validation: Final Report

- **Date:** 2026-11-23
- **Status:** COMPLETE — R2 remains DRAFT/INACTIVE; no activation or further milestone.
- **Coordinator:** reconciled Agent A (R2 application), Agent B (blind validity), Agent C (usability).

## 1. New proposal selected

**P-SHADOW-002 — DRT-0419 pin-center causal diagnostic** (`docs/T-SKILL-008_SHADOW_PROPOSAL.md`,
SHA-256 `185ecee256385d5516fe2b829f0b7670eea585acf40f6c1f4f6497033ff0d3c9`). Genuinely new and
distinct from P-SHADOW-001: it targets the non-fatal DRT-0419 M3 D/Q pin-center advisory (8 warnings in
FDE-004), using a two-arm scratch placement contrast. No approval, no execution, no remedy.

## 2. R2 assessment

Dated immutable assessment: `docs/T-SKILL-008_SHADOW_ASSESSMENT.md`, SHA-256
`3b5625445ef04ab211b58d36d03f2d475b4a0ee162d3ca1e7e51b303b704b4b3`. R2 instrument:
`6900ebc8…cb9d` (unchanged).

Dispositions (A1–A17): **PASS 3** (A1, A2, A6) · **PARTIAL 9** (A3, A4, A5, A8, A9, A11, A12, A13,
A14) · **DEFERRED 1** (A10) · **DEFERRED-SHADOW 1** (A15) · **N/A 2** (A7, A16) · **UNKNOWN 1**
(A17 → STOP for dependents).

Class = `causal diagnostic`, so A3/A4/A6 apply and the A13 no-remedy exception was correctly denied.

## 3. Design weaknesses detected

Critical: A17 capability UNKNOWN (pin-center/bbox extraction unverified; historical tool aggregate-only).
Hard gate blockers: A3 control identity ambiguous (historical run named as concurrent control); A4
single-variable scope unproven (whole-macro move risk + "same ODB" contradiction); A13 missing cost cap;
A5/A8/A11/A12/A14 incomplete hashed nuisance table, bar, preflight fields, full hashes and toolchain
manifest; A8/A9/A10/A15 missing reviewer row, macro-edge/NOT_RUN labels and DEFERRED D-007 outcome.
Six actionable corrections are recorded in §3 of the assessment.

## 4. Independent review and disagreement reconciliation

Agent B reviewed blind and recommended **no execution and no approval**; its three disqualifying issues
(A17, A4, A3) are preserved in `docs/T-SKILL-008_INDEPENDENT_REVIEW.md`.

| Item | Agent A | Agent B (blind) | Agent C | Adjudication |
|---|---|---|---|---|
| A17 | UNKNOWN → STOP | UNKNOWN → STOP | highest-value catch | **UNKNOWN → STOP** (unanimous) |
| A3 | PARTIAL | PARTIAL/UNKNOWN | causal branch exercised | **PARTIAL**; FAIL/STOP if historical run reused |
| A4 | PARTIAL | UNKNOWN/PARTIAL | actionable | **PARTIAL**; digest required before execution |
| A7 | N/A | PARTIAL/conditional N/A | trigger ambiguous | **N/A** — no family *value* appears; field-name mention is not a family. Latent re-check if a value is named; R3 clarification recorded |
| A13 | PARTIAL | PARTIAL | exception correctly denied | **PARTIAL** — full cost cap required for causal diagnostic |
| A15/A10/A12(b)/A16 | DEFERRED-SHADOW / DEFERRED / N/A | same | stage handling correct | **agreed** — no false FAILs, no silent PASSes |

## 5. R2 effectiveness observations (single prospective shadow only)

**Material improvement demonstrated:** R2-J exposed the load-bearing A17 capability gap before
approval; R2-F drove a concrete A3 identity correction; R2-A/E avoided false FAILs for shadow-stage
reviewer/preflight; R2-D/K correctly denied the no-remedy cost-cap exception for a causal contrast;
R2-H produced an A7 N/A with a latent re-check obligation. Agent A quoted specific R2 wording mapped
to five concrete proposal corrections — guidance was actionable.

**Not demonstrated:** prevention of a real failure, readiness as a mandatory gate, or generalisability
beyond this one prospective shadow. Agent C verdict: acceptable as DRAFT/INACTIVE reference with
limitations; **not gate-ready**.

## 6. Remaining defects and recommended disposition

Remaining R2 defects (recommendations only, **no R3 revision made**): non-atomic DEFERRED can let
design-stage sub-checks escape (A11 probe naming, A12(b) full SHA); A7 trigger ambiguity (family value
vs schema field name); class distinction is an honour system without a self-consistency validator;
missing criteria for whole-macro vs per-pin placement scope, M3 track math, DRT-0419 bbox derivation,
D-014 parity, design-tree identity and KLayout trigger scope. Nine precise R3 recommendations are in
`T8_C_usability.md`. A second shadow would add value only on a causal variant that can reach an
approvable state.

**Disposition:** proposal is shadow-viable with one hard blocker (A17) and six design-stage corrections;
R2 is a useful DRAFT reference, not a gate.

## 7. Verification results

| Check | Actual |
|---|---|
| KB `verify` | PASS — 18 records, 18-link chain, 0 problems |
| `verify-immutable` | PASS — 9/9 protected artifacts, `changed=[]` |
| `.skills/validate_skills.py` | PASS=13 FAIL=0 |
| R2 checklist hash | `6900ebc8…cb9d` unchanged |
| EDA / experiment / approval / activation / install | none |
| Production, baseline, KB, approval, historical artifacts | unchanged |

## 8. Files created or modified

Created: `docs/T-SKILL-008_SHADOW_PROPOSAL.md`, `docs/T-SKILL-008_SHADOW_ASSESSMENT.md`,
`docs/T-SKILL-008_INDEPENDENT_REVIEW.md`, `docs/T-SKILL-008_FINAL_REPORT.md`; updated `PROJECT_STATE.md`,
`coordination/TASK_BOARD.md`, `coordination/ACTIVE_WORK.md`, logs and handoff.

## 9. Limitations

- One prospective shadow assessment; no experiment was run, so no preventive effectiveness is claimed.
- A17/A11/A12 UNKNOWNs reflect absent capability/probe records, not proven design failures.
- Agent B was blind to Agent A but both used the same proposal; independent validity methods still converged on the same three blockers.

## 10. Stop

T-SKILL-008 stops here. Explicit authorization is required for any EDA execution, R2 activation, R3
revision or subsequent milestone.
