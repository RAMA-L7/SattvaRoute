# T-SKILL-006 — Experimental Design Checklist Shadow Pilot: Final Report

- **Date:** 2026-11-23
- **Status:** COMPLETE — shadow assessment only; R1 remains DRAFT/INACTIVE.
- **Agents:** A (R1 application), B (blind independent validity), C (checklist usability); coordinator
  reconciled and adjudicated.

## 1. Selected proposal

**P-SHADOW-001 — Controlled DRT-0073 evidence-completeness diagnostic** (`docs/T-SKILL-006_SHADOW_PROPOSAL.md`,
SHA-256 `d20230521dbeaa8b8d79ac04b1678dc012b516794bb84a52e4c6d89a7edb968c`). It was reconstructed from
already-documented, unexecuted next-step requirements in `docs/FDE-007_REMEDY_EVALUATION.md` §33 and
`logs/sessions/FDE-007_S001_handoff.md` §Next: `getSrcs()` marker provenance, GDS census at the sliver
and spacing bands, all-pin AP survey, canonical DB diff + no-op control, spacing/EOL mechanism and a
full-flow plan.

**Not approved, not executed, not authorized.** It proposes no remedy geometry and no causal contrast.
It was chosen precisely because it is an upcoming but unexecuted proposal, satisfying the shadow-pilot
objective without launching an experiment.

## 2. Instrument and immutable record

- R1 checklist: `docs/EXPERIMENT_DESIGN_CHECKLIST.md`, SHA-256
  `286c7bbaa53f2c936cc6bc2e87ddb34c9e640b80089051cb0be9d4bcf7b1fc4f` — unchanged by this milestone.
- Dated immutable assessment: `docs/T-SKILL-006_SHADOW_ASSESSMENT.md`, SHA-256
  `4a9145d8d03e512582372a76bdab18cb0c418df3af8dbc66d90ebf71274bc6bb`.
- Source traces: FDE-007 evaluation/handoff, FDE-006T build/supervisor history, R1 §A.1 dispositions.

## 3. Checklist results (adjudicated)

Full A1–A16 table with evidence is in the immutable assessment. Totals: **PASS 2 · FAIL 2 · PARTIAL 8 ·
UNKNOWN 2 · N/A 2**. No applicable item beyond A1/A2 is a clean PASS.

- **PASS:** A1 (question/unit/response/claim scope), A2 (N=1 per arm; markers/APs are sub-units — Agent A and B agreed).
- **FAIL:** A3 (Arm B mislabeled "instrumentation identity" when R1 says instrumentation-neutrality is not a control; no justified N/A or concurrence), A13 (no cost cap/escalation authoriser).
- **UNKNOWN:** A11 (no preflight; `getSrcs()` availability unverified — top risk), A15 (no named pre-run reviewer/COI/sign-off; blocks all N/A concurrences).
- **N/A:** A7 (no remedy family named), A16 (demoted reference line).
- **PARTIAL:** A4, A5, A6, A8, A9, A10, A12, A14.

UNKNOWNs are separated from FAILs: A11 becomes FAIL/STOP only if `getSrcs()` is confirmed unavailable; A15
becomes FAIL if the executor self-reviews.

## 4. Design weaknesses detected

Control mislabeling (A3); unguarded logging-ON arm C; `getSrcs()` hard dependency (A11); confounders
(binary/build mode, D-014 presence, supervisor mode, scratch sharing, order inputs); pseudoreplication
handled but N unquantified; remedy-family discipline currently correct but fragile; draft acceptance bar
with no fixed hash list or quantified spacing/EOL criterion; no cost cap; absent independent reviewer.
Eight concrete corrections to the proposal are recorded in §4 of the immutable assessment.

## 5. Independent review and disagreement reconciliation

Agent B reviewed **blind** — it did not read Agent A's assessment. Key reconciliations:

| Item | Agent A | Agent B (blind) | Coordinator adjudication |
|---|---|---|---|
| A3 | PARTIAL (N/A-eligible, concurrence pending) | FAIL as written | **FAIL** — the proposal's mislabeling violates R1; convertible to justified N/A only after renaming and reviewer concurrence |
| A11 | UNKNOWN | FAIL | **UNKNOWN** — R1 A.1 defines absent preflight as UNKNOWN; FAIL only if `getSrcs()` confirmed unavailable |
| A15 | UNKNOWN | FAIL | **UNKNOWN** — no reviewer identity/sign-off records; FAIL if executor self-reviews |
| A13 | PARTIAL (recommended escalation) | PARTIAL | **FAIL** — R1 A.1 FAIL trigger "cost cap absent" is literally met |
| A1 | PASS | PARTIAL | **PASS** — all R1 PASS elements present; separation concern logged as usability finding |
| A2 / A7 / A16 | PASS / N/A / N/A | PASS / N/A / N/A | agreed |

Agent B independently recommended **no execution and no approval** in the proposal's current form.

## 6. R1 usability findings

Worked well: A1, A2, A5, A6, A8, A9, A10, A14, A16; R12 applicability classes and ED-1/ED-2 wording held.
Problems: A11/A12(b)/A15 demand execution/post-run artifacts from a *pre-run* checklist (manufactured
gaps); A13 cost caps can be manufactured on a no-remedy diagnostic; the class model conflates arm count
with causal intent, so a multi-arm non-causal diagnostic survives only via an ad-hoc GATE RULE exemption.
Missing criteria M1–M6: `getSrcs()` API availability, KLayout version/layer map, detached-build
contingency, explicit no-remedy boundary, same-net-vs-foreign-net evidence fields, KB family check when
family is a stated non-goal. One consistency defect: §B row 104 still says A15 sign-off "on A1–A12"
while §A.1 A15 says A1–A15. Proposed R2 directions (not applied): Stage column (`design`/`execution`/
`post-run`+DEFERRED), new A17 measurement-capability preflight, a four-class model adding
`mechanism-only diagnostic`, and wording fixes R2-A…R2-L.

**Verdict on R1:** useful shadow diagnostic; **not ready for a second shadow pilot unchanged** (Agent C).

## 7. Verification results

| Check | Actual |
|---|---|
| KB `verify` | PASS — 18 records, 18-link chain, 0 problems |
| `verify-immutable` | PASS — 9/9 protected artifacts, `changed=[]` |
| `.skills/validate_skills.py` | PASS=13 FAIL=0 |
| R1 checklist SHA-256 | `286c7cba…2401` unchanged |
| R0 snapshot SHA-256 | `a445c7ae…e0c091` unchanged |
| EDA / experiment execution | none |
| Approval / activation / R1 edit / install | none |

## 8. Files created or modified

Created: `docs/T-SKILL-006_SHADOW_PROPOSAL.md` (supporting, unapproved), `docs/T-SKILL-006_SHADOW_ASSESSMENT.md`
(immutable dated record), `docs/T-SKILL-006_SHADOW_PILOT_REPORT.md` (this report); updated
`PROJECT_STATE.md`, `coordination/TASK_BOARD.md`, `coordination/ACTIVE_WORK.md`, `logs/DAILY_LOG.md`,
`logs/AGENT_ACTIVITY.md`, `logs/REVIEW_LOG.md`, `logs/REPORT_LOG.md`, handoff and publish allowlist.

No historical FDE report, KB record, production artifact, baseline, approval control or skill status changed.

## 9. Limitations

- One shadow application of a DRAFT/INACTIVE checklist — **no preventive effectiveness is claimed**.
- The proposal is a reconstruction of documented requirements, not a user-authorized experiment design.
- A11/A15 gaps are evidence-unavailability (UNKNOWN), not proven failures.
- R1 usability findings are proposals only; R1 was not revised.

## 10. Final status

T-SKILL-006 complete. The checklist remains DRAFT/INACTIVE. Explicit authorization is required for any
experiment execution, checklist activation, R2 revision, or subsequent milestone. No further work started.
