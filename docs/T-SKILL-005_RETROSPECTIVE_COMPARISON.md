# T-SKILL-005 — R0 vs R1 Retrospective Comparison

- **Date:** 2026-11-23
- **Scope:** same 8 historical experiments scored against R0 (A1–A12) and R1 (A1–A16).
- **Critical framing:** the checklist was created **after** every audited run and stayed **DRAFT /
  INACTIVE**. All results are retrospective counterfactuals. No historical run violated an active gate;
  no claim of preventive effectiveness is made.

## 1. Anchors and denominators

| Item | R0 | R1 |
|---|---|---|
| Checklist hash (scored) | `a445c7ae…e0c091` (preserved R0 snapshot) | `e6b2240b…775b3c` (pre-cleanup R1) |
| Final R1 hash after ED-1/ED-2 editorial cleanup | — | `286c7bbaa…2401` |
| Items | A1–A12 (12) | A1–A16 (16; A16 demoted to reference) |
| Cells for 8 cases | 96 | 128 total; **120 gate-relevant** (8 A16 cells N/A as gates) |
| Assessable (PASS+PARTIAL+FAIL) | 79 | 103 |
| UNKNOWN | 3 (separate) | 3 (separate) |
| N/A | 14 | 22 (8 demoted A16 + 14 class exclusions) |

The instruments are **not cell-for-cell comparable**: R1 adds A13–A15 (24 new cells, all PARTIAL
retrospectively), demotes A16, and rewrites PASS conditions for A3/A6/A7/A8/A10/A11/A12.

## 2. R1 scorecard (same 8 cases)

| Case | A1 | A2 | A3 | A4 | A5 | A6 | A7 | A8 | A9 | A10 | A11 | A12 | A13 | A14 | A15 | A16* |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FDE-005 (diagnostic) | Q | Q | **P** | **P** | Q | **F** | N | Q | **P** | Q | Q | Q | Q | Q | Q | N |
| FDE-006 (blocked) | Q | N | Q | Q | Q | ? | N | Q | **P** | Q | **F** | Q | Q | Q | Q | N |
| FDE-006R (blocked) | Q | N | ? | Q | Q | N | N | Q | **P** | N | **F** | Q | Q | Q | Q | N |
| FDE-006S (blocked) | Q | N | ? | Q | Q | N | N | Q | **P** | N | **F** | Q | Q | Q | Q | N |
| FDE-006T (diagnostic) | Q | Q | Q | Q | Q | **F** | N | Q | **P** | Q | Q | Q | Q | Q | Q | N |
| FDE-006U (causal A/B) | Q | **F** | **F** | **P** | Q | **F** | N | Q | **P** | Q | Q | Q | Q | Q | Q | N |
| FDE-007 R1-N (remedy) | Q | **F** | **F** | **P** | Q | **F** | N | Q | **P** | Q | Q | Q | Q | Q | Q | N |
| FDE-007 R1-N-W (remedy) | Q | **F** | **F** | **P** | Q | **F** | **F** | Q | **P** | Q | Q | Q | Q | Q | Q | N |

\* A16 = N/A as a gate for all 8 cases (demoted to reference).

Legend: P PASS · Q PARTIAL · F FAIL · ? UNKNOWN · N N/A. Every non-PASS cell in the Agent C
re-score (`T5_C_rescore.md`) carries exact `file:line` evidence from the T-SKILL-004 source set.

### R1 totals (verified against the table)

| Disposition | Cells (128) | Gate-relevant (120) |
|---|---|---|
| PASS | 13 | 13 |
| PARTIAL | 75 | 75 |
| FAIL | 15 | 15 |
| UNKNOWN | 3 | 3 |
| N/A | 22 | 14 |
| **Sum** | **128** | **120** |

Assessable denominator = 13 + 75 + 15 = **103 / 120 gate-relevant** (86%). UNKNOWNs are evidence
unavailability, not failures; N/As are class exclusions or the demoted A16 reference.

**Duplicate C-report reconciliation.** Two Agent C notifications reported different totals
(P13/Q75/F15/?3/N-A22 vs P10/Q79/F9/?2/N-A28). Only the report actually written to
`T5_C_rescore.md` was independently recounted cell-by-cell here and found internally consistent
(128 cells = 13+75+15+3+22). The conflicting notification had no reproducible table and is treated
as superseded; no effectiveness claim uses its numbers.

## 3. What R1 corrected in the instrument

| R0 defect | R1 resolution | Retrospective effect |
|---|---|---|
| A3 self-contradictory / blanket STOP | identity-arm definition, instrumentation-neutrality warning, bounded-diagnostic N/A exemption | FDE-006T A3 **F → Q**; FDE-006/006R/006S A3 become Q/? instead of F/?; FDE-005 A3 stays **P** (scoped, sequential within one session) |
| A7 wrong term/key | names `relationships.remedy_family`, `by_remedy_family`, `duplicate_check()`; retitled | FDE-007 R1-N-W A7 **F → Q** (family key now mechanically reachable) |
| A8 remedy bar applied to diagnostics | class-specific bar (a/b/c); narrowing with concurrence; D-007 binding | all A8 cells Q (bar partly documented), no false FAIL on diagnostics |
| A12 `tools/` false positive | split protected artifacts / baseline ODB / isolation; `allowed_roots` exception for sanctioned D-014 mirror | false FAIL removed; A12 remains PARTIAL for all 8 because `verify-immutable` postdates runs |
| A6 fixed-order over-strict | deterministic order + fixed-order exemption with justification | FDE-005/006T/006U A6 **F → Q**; FDE-007 A6 **Q → N** where class-exempt |
| A10 bare N/A | meaningful N/A; NOT_RUN pins; no one-pin generalisation | clearer Q/N dispositions |
| A13–A15 missing | new cost/stopping, toolchain identity, independent reviewer items | 24 new cells, all historically PARTIAL (no such records on the audited runs) |
| A16 added then demoted | reference line with justification (FDE-002/D-014/A12 cover rollback) | 8 N/A as gates; no score distortion |

## 4. What remains unresolved in the historical record

- **A2 pseudoreplication** (FDE-006U and both FDE-007 cases): 9 AP candidates, 107 markers, 12 pin
  corridors are sub-units of N=1 runs. R1 names this precisely but cannot retroactively create
  independent replicates.
- **A3 absent identity arms** (FDE-006U + both FDE-007 cases): FDE-006U §10 states "no no-op control
  arm"; FDE-007 used historical parity. These remain FAIL under R1's corrected definition.
- **A11 blocked builds** (FDE-006/006R/006S): infeasibility was real and stopped those lines honestly.
- **A13–A15** are present but all PARTIAL: no pre-registered cost caps, toolchain identity manifests
  or reviewer COI/sign-off records exist for the audited runs.
- **A12 anachronism:** `verify-immutable` did not exist when the runs happened, so no case can PASS
  A12 retrospectively. This is an evidence limitation, not a historical violation.

R1 FAIL modes: A6 ×5, A11 ×3, A3 ×3, A2 ×3, A7 ×1 = **15** (R0 had 16; the removed cell is
FDE-006T A3 under the bounded-diagnostic exemption). Agent D noted T-SKILL-004's "A3 (3 cases)"
breakdown undercounted its four A3 FAIL cells (sum 15 vs 16); that historical undercount is
annotated here rather than rewriting T-SKILL-004.

## 5. Effectiveness conclusion

- **Instrument quality:** R1 resolves the R0 contradictions, false positives and missing controls;
  it is internally consistent after ED-1/ED-2 and independently reviewed (Agent B ACCEPT WITH
  LIMITATIONS; no blocking findings).
- **Retrospective diagnostic value:** sharper — it names the same real weaknesses with corrected
  definitions and adds three previously missing capability areas.
- **Preventive value:** **not demonstrated and not claimed**. R1 postdates all eight runs, was never
  active, and no shadow pilot has occurred. "Catches" throughout this report means "retrospectively
  names a documented weakness", not "would have prevented the outcome".

## 6. Gate status

R1 is **DRAFT / INACTIVE**. A separate explicit authorization is required for a shadow/observational
pilot; promotion to a mandatory gate additionally requires pilot evidence, independent reviewer
sign-off and green integrity checks at pilot time. No skill was installed or activated.
