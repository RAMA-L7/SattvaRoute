# T-SKILL-007 — Retrospective R2 Revalidation and R0/R1/R2 Comparison

- **Instrument scored:** R2 at `f81618a9a977c33deb938465178170da7cedeb9b904cfb6fe391ff0fd4863b31`
  (final hash after citation-only F1 fix: `6900ebc8b17821f7b1bb30f29224d0eb120042fd5e392dbbf42046877ba4cb9d`).
- **Corpus:** the same 8 historical experiments used in T-SKILL-004/005/006.
- **Framing:** R2 postdates every run and is DRAFT/INACTIVE. All results are retrospective
  counterfactuals; **no preventive effectiveness is claimed**.

## 1. Assessment stage rule

The counterfactual fills R2 out at each run's **`design` (pre-run) stage**. Under R2-A:
- A1–A9, A13, A14, A17 scored normally;
- A10 evaluated-pins record and A11 preflight are **DEFERRED to execution/post-run** (12 D cells);
- A12(b) post-run hash confirmation DEFERRED (cell remains PARTIAL on (a)/(c));
- A15 is **DEFERRED-SHADOW** for all 8 (observational assessment, no approval gate);
- A16 is N/A as a gate (demoted reference); A17 is UNKNOWN for all 8 (new item, no historical record).

## 2. R2 totals (verified against the scorecard)

| Disposition | Cells (136) | Gate-relevant (128) |
|---|---|---|
| PASS | 13 | 13 |
| PARTIAL | 51 | 51 |
| FAIL | 11 | 11 |
| UNKNOWN | 8 (all A17) | 8 |
| N/A | 33 (8 A16 + 25 class) | 25 |
| DEFERRED | 12 (A10×4, A11×8) | 12 |
| DEFERRED-SHADOW | 8 (A15×8) | 8 |
| **Sum** | **136** | **128** |

Assessable (P+Q+F) = **75 / 128 gate-relevant** (58.6%). Excluded by rule: 33 N/A + 20 DEFERRED + 8 UNKNOWN.
FAIL breakdown: A2×3, A3×3, A6×4, A7×1, **A11×0** (three blocked-build FAILs relocated to DEFERRED).

## 3. R0 / R1 / R2 comparison

| Anchor | R0 | R1 | R2 |
|---|---|---|---|
| Hash (scored) | `a445c7ae…` | `e6b2240b…` | `f81618a9…` |
| Items | A1–A12 | A1–A16 | A1–A17 |
| Cells | 96 | 128 | 136 |
| Gate-relevant | 96 | 120 | 128 |
| PASS | 23 | 13 | **13** |
| PARTIAL | 40 | 75 | **51** |
| FAIL | 16 | 15 | **11** |
| UNKNOWN | 3 | 3 | **8** |
| N/A | 14 | 22 | **33** |
| DEFERRED / DEFERRED-SHADOW | — | — | **12 / 8** |
| Assessable | 79/96 | 103/120 | **75/128** |

**PASS count did not rise** (R0 23 → R1 13 → R2 13). The apparently cleaner FAIL count (16 → 15 → 11)
and lower assessable share are **changed-rule effects** — stage-aware DEFERRED, class-model N/A and the
new no-data A17 — not evidence that historical designs improved.

**Comparability:** 97/136 cells are R1↔R2 comparable with identical dispositions; 39 are
non-comparable and individually listed by Agent C: A11×8, A15×8, A17×8, A3×4 (FDE-006/006R/006S/006T),
A4×3, A6×2, A10×6. R0 has no A13–A17 counterpart.

## 4. Genuine instrument improvements

Stage column + DEFERRED; DEFERRED-SHADOW; four-class model with no-remedy boundary; A3
modification-digest identity and instrumentation-neutrality ban; A4 instrumentation-factor rule;
A7 family-key check wherever the key appears; A14 GDS tooling/layer map; new A17 measurement-capability
preflight; merged reviewer evidence row; added §B evidence fields (per-marker provenance,
same-net-vs-foreign-net, out-of-scope record).

## 5. Changed-rule effects (not quality improvements)

- A11: R1's 3 blocked-build FAILs are **relabeled DEFERRED** (execution-stage relocation) — the
  infeasibility remains documented.
- A12(b): anachronistic "confirmed unchanged post-run" is now a properly deferred artifact; cell stays PARTIAL.
- A15: no reviewer COI/sign-off existed historically (APP-N/APP-W name a user as *approver*, not a
  disjoint reviewer); the rule no longer scores that as a gap, but the underlying absence is unchanged.
- A10/A3/A4/A6 class N/A: 13 cells removed from the assessable denominator; missing NOT_RUN labels,
  convenience order and blocked builds remain facts in the record.

**No historical FAIL was cured** by a checklist: A2 pseudoreplication ×3, A3 missing identity arms ×3
and A7 family repeat ×1 are retained on substance.

## 6. Limitations

- R2 is DRAFT/INACTIVE and postdates all runs; no shadow pilot of R2 has been performed.
- A17's 8 UNKNOWNs reflect absent historical capability records, not a judgment on those designs.
- All non-PASS cells carry exact file:line evidence in the Agent C report (`T7_C_revalidation.md`).
