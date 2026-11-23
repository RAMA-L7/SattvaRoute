# T-SKILL-004 — Retrospective Experimental Design Validation

- **Date:** 2026-11-23
- **Type:** read-only retrospective audit of an inactive DRAFT checklist
- **Verdict:** **REVISE** (retain the instrument, fix it before any controlled pilot; do not activate)
- **Agents:** A (FDE-005/006), B (FDE-006U/007), C (checklist coverage), D (evidence integrity)

## 1. Scope and methodology

The DRAFT `docs/EXPERIMENT_DESIGN_CHECKLIST.md` (A1–A12, SHA-256
`a445c7ae48236456815e8ae2eb46faf48ad0784d2a0f83d2a77ffb58d9e0c091`) was assessed against historical
FDE experiments using PASS / FAIL / PARTIAL / NOT APPLICABLE / UNKNOWN. Evidence was taken only from
existing reports, experiment manifests, approval records, decision index and review logs. No EDA, no
new experiment, no checklist activation, no historical rewrite.

**Critical framing:** the checklist was created on 2026-11-23 (D-027), 2–3 days **after** the audited
runs (2026-11-19/20/21). It states it is "not an installed skill and not an active project gate".
Therefore every result is a **retrospective counterfactual**: no historical run violated a gate that
did not exist. Gates added later (A12's `verify-immutable`, KB family dedup) are marked PARTIAL or
anachronistic rather than contemporary failures.

## 2. Historical cases evaluated

| Case | Nature | Key historical outcome |
|---|---|---|
| FDE-005 | A/B via-in-pin config diagnostic | Null result; DRT-0073 persists; root cause stays PROBABLE (D-016) |
| FDE-006 | Instrumented AP diagnostic (Gate 2 blocked) | Offline Bazel deps unavailable; no binary; BLOCKED (D-017) |
| FDE-006R | Dependency recovery/build | drvfs + WSL spawn failure; BLOCKED (D-018) |
| FDE-006S | Native build | SIGKILL RC=137 at link; BLOCKED (D-019) |
| FDE-006T | Build + candidate diagnostic | 9 candidates all rejected; equivalence PASS; Experiment B blocked (D-020) |
| FDE-006U | Controlled M4 OBS A/B (same binary) | 0→3 accepted APs, DRT-0073 gone in B; mechanism ESTABLISHED (bounded) (D-021) |
| FDE-007 | R1-N and R1-N-W full-flow remedies | Both rc=2 DRT-0073 / 0 APs; both REJECT; one family (D-022/D-023) |

## 3. A1–A12 scorecard

Legend: **P** PASS · **F** FAIL · **Q** PARTIAL · **N/A** not applicable · **?** UNKNOWN.
Anachronistic items are marked PARTIAL rather than treated as historical violations.

| FDE / Experiment | A1 | A2 | A3 | A4 | A5 | A6 | A7 | A8 | A9 | A10 | A11 | A12 | Major design weakness | Would checklist catch it? | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FDE-005 | Q | Q | P* | P | P | **F** | N/A | Q | P | Q | P | P* | Fixed "A then B" order; no single pre-run unit/response + numeric bar | Yes — A6; A1/A2/A8 form issues | FDE-005 §7–19; `EXPERIMENT_GO.md:33`; R-005; D-016 |
| FDE-006 (blocked) | Q | N/A | Q | P | Q | ? | N/A | Q | P | Q | **F** | P* | Offline build infeasible | Yes — A11 | FDE-006 §5–11; R-006; D-017 |
| FDE-006R | Q | N/A | ? | P | Q | N/A | N/A | Q | P | N/A | **F** | P* | drvfs/WSL process failure | Yes — A11 | FDE-006R §3–6; R-007; D-018 |
| FDE-006S | Q | N/A | ? | P | Q | N/A | N/A | Q | P | N/A | **F** | P* | SIGKILL at link | Yes — A11 | FDE-006S §3–7; R-008; D-019 |
| FDE-006T | Q | Q | **F**† | P | Q | **F** | N/A | Q | P | Q | Q | Q | No OBS no-op arm (Exp B blocked); fixed order; 9 candidates within one run | Yes — A3 (causal claim), A6 | FDE-006T §3–13; R-009; D-020 |
| FDE-006U | Q | **F** | **F** | P | Q | **F** | N/A | Q | P | Q | Q | Q* | 9 APs/107 markers treated as rich evidence but N=1; no concurrent no-op arm; convenience order | Yes — A2, A3, A6 | FDE-006U §3–10; `prod/olddiag/newdiag_off`; R-010; D-021 |
| FDE-007 (R1-N) | Q | **F** | **F** | P | Q | **F** | N/A | Q | P | Q | Q | Q* | Historical baseline + DRT-0419 "parity" instead of concurrent arm; 12 corridors changed but only clk diagnosed | Yes — A2, A3, A6 | FDE-007 addendum; run `…_97829`; R-011; D-022 |
| FDE-007 (R1-N-W) | Q | **F** | **F** | P | Q | **F** | **F** | Q | P | Q | Q | Q* | Same family at new level treated as a new attempt; residual 2 nm sliver INCONCLUSIVE | Yes — A2, A3, A6, **A7** | FDE-007 addendum; run `…_99729`; KB family `M4_OBS_CORRIDOR`; R-011; D-023 |

\* PASS on the substance available at the time, but the explicit checklist artifact did not exist.
† Three-way equivalence is an **instrumentation-neutrality** check, not a no-op control; the report itself says Experiment B was blocked.

### Coverage accounting (applicable and assessable items only)

- **Applicable/assessable assessments:** 79 (PASS + PARTIAL + FAIL; N/A and UNKNOWN excluded from the denominator).
- **PASS:** 23 · **PARTIAL:** 40 · **FAIL:** 16 · **UNKNOWN:** 3 · **NOT APPLICABLE:** 14.
  (96 cells total = 23 + 40 + 16 + 3 + 14.)
- **UNKNOWNs** (FDE-006 A6, FDE-006R A3, FDE-006S A3) arise because no comparative arm ran; they are not failures.
- **Real FAIL modes detected:** A6 (5 cases), A11 (3 blocked builds), A3 (3 causal-control cases), A2 (3 pseudoreplication cases), A7 (1 family-aliasing case).
- Effectiveness is reported **only** over assessable items; unavailable evidence is not counted as PASS or FAIL.

## 4. Historical weaknesses detected

1. **Missing genuine concurrent no-op control (A3).** FDE-006U §10 verbatim: **"no no-op control arm"**. The
   `prod == olddiag == newdiag_off` three-way equivalence verifies that instrumentation is
   behavior-neutral (all arms kept the original OBS). FDE-007 used a historical baseline plus
   DRT-0419 parity rather than a concurrent identity arm. Consequence: confidence labels had to be
   bounded; outcomes themselves were unchanged (0→3 flip observed; DRT-0073 persisted).
2. **Pseudoreplication / unit confusion (A2).** N=1 run per arm. 9 AP candidates, 107 marker records,
   12 pin corridors and 2 nm sliver measurements are repeated measurements of one run. FDE-007 changed
   all 12 corridors but diagnosed only `clk`, so "all pins" claims were never supported.
3. **Remedy-family aliasing (A7).** `KNOWLEDGE_BASE.md:155–157` and `kb_manifest.json` record R1-N and
   R1-N-W as two parameter variations of one family `M4_OBS_CORRIDOR`. The KB had to encode this
   retrospectively. Verdict was unchanged because both failed (latent, not realized, harm).
4. **Convenience ordering (A6).** FDE-005's gate fixes "Experiment A, then Experiment B"; FDE-006T
   similarly. No recorded deterministic order rule. This is a documentation/planning defect, not a
   demonstrated confound (binaries/ODBs were hash-identical).
5. **Feasibility (A11).** FDE-006/006R/006S failed before execution due to offline deps, drvfs and
   SIGKILL. A pre-run feasibility probe would have surfaced these earlier.
6. **Pre-registration form (A1/A8).** Thresholds such as sparse ≥3 were inherited knowledge, but no
   single approval record fixed the numeric bar, required absent DRT codes, disposition labels and
   hash list. FDE-006U §10 concedes a literal pre-registered bar would have lowered the label to
   high-confidence PROBABLE.

## 5. Missed weaknesses / false positives / limitations

- **FDE-005 is a genuine PASS on A3**, not a failure: it had a concurrent no-flag arm and one changed
  variable. A blanket A3 STOP would have blocked an accepted, well-controlled null experiment.
- **A12's phrase "never write to `tools/`" is a false positive** against the sanctioned D-014
  execution mirror (`D:\SattvaRoute\tools\OpenROAD-flow-scripts`). The real rule is "no unapproved
  production write".
- **A7 mislabels the failure as "aliasing"** (in DOE, aliasing = fractional-factorial confounding).
  The actual failure is repeated-family confirmation / pseudoreplication, and the authoritative key
  is `relationships.remedy_family` with an existing mechanical check in `sattva_kb.py duplicate_check()`.
- **A8 as written applies a remedy bar to diagnostics** and would forbid the reviewer-narrowing that
  FDE-006U §10 legitimately adopted.
- **A3 is self-contradictory**: an identity arm cannot both "differ only in the intended variable" and
  be identical to baseline; what is meant is "differs only by absence of the approved change".
- **Anachronism**: A12's `verify-immutable` and KB family checks post-date these runs.
- **Coverage gaps (not in A1–A12):** stop/cost rules, diagnostic vs production binary identity,
  independent pre-run reviewer, supervisor/timeout plan, rollback evidence, claim-scope labels,
  KB suppression check.

## 6. Checklist effectiveness

- **Retrospective diagnostic: high.** 10/12 items cover real documented failure modes; the instrument
  names exactly the defects that made FDE-006U bounded and FDE-007 BLOCKED.
- **Preventive value: unproven.** The checklist was never active; it cannot be credited with preventing
  anything. Its own GATE RULE would have STOPped FDE-006U and FDE-007 on A3 alone, and FDE-005 on A6.
- **Applicability:** 9/12 items are ambiguous, 6/12 too restrictive, 5/12 duplicate existing governance.
  All require some engineering judgment; none are purely non-pre-run-evaluable.
- **No item is redundant enough to delete**; several need scoping (diagnostic vs remedy vs baseline).

## 7. Proposed revisions

See `docs/EXPERIMENT_DESIGN_CHECKLIST_REVIEW.md` for R1–R12 and proposed A13–A15. Minimum before any
pilot: **R3** (A3 identity-arm definition + diagnostic exemption), **R6** (A7 authoritative key),
**R7** (A8 class scoping), **R9/R10** (A11/A12 feasibility and protected-path wording).

## 8. Integrity verification (actual)

| Check | Actual result |
|---|---|
| `sattva_kb.py verify` | PASS — 18 records, 18-link chain, 0 problems |
| `sattva_kb.py verify-immutable` | PASS — 9/9 protected artifacts OK, `changed=[]` |
| Checklist SHA-256 before/after mission | `a445c7ae…d9e0c091` unchanged |
| FDE-005/006U/007 sources + sampled evidence | all present and readable |
| Skill statuses | unchanged; 0 INSTALLED, 0 ACTIVE |

Disclosed limitations: `verify-provenance` reports DRIFT on `docs/decisions/DECISIONS.md` (legitimate
D-024 append; documented in `knowledge/PROVENANCE_DRIFT.md`); `.skills/PROJECT_SKILLS.json` counts
metadata drifts from its own entries (6 RECOMMENDED / 6 EVALUATED / 3 REJECTED vs declared 8/5) —
a documentation inconsistency, not a status upgrade; `state/approval_ledger.jsonl` is absent (FDE-007
approvals rest on per-run `APPROVAL.md`). These are pre-existing and were not modified.

## 9. Final verdict

**REVISE.** The checklist is a useful retrospective diagnostic and should be retained as DRAFT, but it
is **not ready for a controlled pilot as a gating instrument** until R3/R6/R7/R9/R10 are applied and
A13–A15 are considered. After revision, run **one shadow/observational pilot** on a future FDE
proposal — record A1–A12 answers without enforcing the GATE RULE — before promoting it to a gate.

No checklist content, historical report, KB record, protected artifact or skill status was changed by
this milestone. No EDA was run. No activation of the checklist occurred.
