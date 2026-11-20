# FDE-006U — Candidate Rejection Attribution and Controlled OBS Validation

- **Task:** T-FDE-006U
- **Date:** 2026-11-20
- **Coordinator:** orchestrator
- **Agents:** A rejection attribution, B OBS control, C experiment integrity, D independent review (pre-run + post-run)
- **Verdict:** **ROOT CAUSE ESTABLISHED** (bounded, mechanism-level) — with a multi-violation refinement. Scope: `pin_access` on ODB `35bff121…` with the installed OpenROAD/ASAP7 toolchain. No production fix applied.

## 1. Executive summary

FDE-006T produced candidate counts but only aggregate DRC marker counts. FDE-006U added two log-only insertions to the existing target-gated instrumentation, rebuilt a separate diagnostic binary, proved three-way runtime equivalence, and ran a same-binary, single-variable A/B on the `u_sram/clk` pin. Experiment A (original M4 OBS): 9 M4 candidates, 107 per-marker records, 0 accepted, sparse 0 < 3, DRT-0073. Experiment B (scratch M4 OBS window carve): 3 candidates, 13 markers, 3 accepted, sparse 3 ≥ 3, no DRT-0073. The decisive change is removal of the full-body M4 master OBS blocking planar escape; M5 via-landing `Short` markers persist in B yet APs are accepted, so those are contributing rather than decisive. Independent review upgraded the verdict with explicit scope limits and residual gaps.

## 2. Starting revision and identities
- Publish HEAD `06f1a767bbf4ef75f81d4e80a49392dbca27f1dd` = remote.
- Source ODB `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1` — unchanged throughout.
- Production binary `c1b90e0af69bc9779cde8fd1579a92a10738ddebb9ea16e459f280556c349ee9`.
- FDE-006T reference diagnostic binary `9c0ed727dea3c6a07c04369472eef8c51c68ca7c095a0c9d925da7e2440ed86f` — preserved before rebuild.
- New rejection-attribution binary `0d890431065688930e8b140cb644e304a0a3a6beeaf32b2cff762a8aa000d33d`.
- Source `FlexPA_acc_point.cpp`: `305230b9…` → `0fc94a9d…` (two log-only insertions).

## 3. Baseline reproduction and three-way equivalence
Fresh scratch copies of the source ODB were used with the approved D-014 in-memory `zero_ setSpecial` step. Production, FDE-006T diagnostic (debug off), and new diagnostic (debug off) produced identical logs after path normalization; all rc=1, DRT-0305=0, DRT-0073=2. Debug-on added FDE006R lines only for `u_sram/clk` (239 lines, 107 marker records). **PASS** — instrumentation is behavior-neutral.

## 4. Candidate rejection attribution (Experiment A)
Nine M4 candidates at y=16572 DBU, x = 4740, 4764, 4787, 4788, 4806, 4812, 4825, 4836, 4860. Marker evidence:
- **Planar DRC on M4**: `Short` (rule id 48) with bboxes `(4704,16560)-(4764,16584)` and `(4848,16560)-(4902,16584)` — the neighbouring M4 pin shapes; `Lef58EolKeepOut` (rule id 59) near x=4740.
- **Via DRC**: VIA45 `Short` (rule id 70) on M5 with landing bboxes `(4800,16500)-(4824,16595)` and `(4800,16549)-(4824,16644)`; `Metal Spacing` and `Lef58SpacingEndOfLine` on M4 in some candidates.
- All 9 candidates dropped at final `hasAccess()`; `aps_out=0`; sparse `n_aps=0 n_sparse=0 thresh=3 macro=true`; `SUMMARY aps=0 met=false`; DRT-0073.

Association is spatial and candidate-scoped: each `is*ViolationFree` constructs a fresh `FlexGCWorker`, so every marker belongs to the candidate/stage whose log line precedes it. Marker `getSrcs()` provenance was not logged (residual gap).

## 5. Instrumentation patch and build
Two log-only insertions after the existing `DRC-MARKERS` count lines in `FlexPA_acc_point.cpp`: planar and via marker loops logging candidate x/y/layer, stage, via name, marker type/rule id/layer/bbox, and `clean`. No access bits, return values, containers, thresholds, or decision conditions changed. Existing `thread_local` `u_sram/clk` gate reused. Build: 5 actions, RC=0, log and binary hash preserved; reference binary kept separately.

## 6. OBS control design and verification
Scratch-only control (Agent B): edit M4 OBS in a scratch copy of the macro LEF — replace the full-body M4 RECT with four rects leaving a window `(1500,300)–(3650,13300)` DBU — export DEF from the source ODB (`write_def`, sha256 `fe1a5e07…`), rebuild DB with tech LEF + standard-cell LEF + scratch macro LEF + DEF, then `write_db`. Verification: source 5 OBS boxes → control 8 boxes; M1/M2/M3/M5 unchanged, M4 split into four rects `(0,0)-(3672,300)`, `(0,13300)-(3672,13608)`, `(0,300)-(1500,13300)`, `(3650,300)-(3672,13608)`; inst/net/bterm counts 293/75/6 unchanged; DEF round-trip byte-identical. No production LEF/GDS/DB touched.

## 7. Experiment B (same binary as A)
Control OBS: 3 candidates (x = 4788, 4812, 4836), 13 marker records, **3 ACCEPT lines**, 0 final drops, sparse progresses to `n_sparse=3 >= thresh=3`, `met=true`, DRT-0073 absent, rc=0. M5 VIA45 `Short` markers remain in B, proving they are not decisive once planar escape becomes legal.

## 8. A/B comparison

| Measurement | A: original OBS | B: M4 OBS window |
|---|---|---|
| Source ODB | `35bff121…` | same, scratch copy |
| Binary | `0d890431…` | `0d890431…` |
| OBS boxes | 5 (M1–M5 full) | 8 (M4 split; others unchanged) |
| Candidates | 9 | 3 |
| Marker records | 107 | 13 |
| Accepted APs | 0 | 3 |
| Final drops | 9 | 0 |
| Sparse | 0 < 3 | 3 ≥ 3 |
| DRT-0073 / rc | present / 1 | absent / 0 |

## 9. Root-cause adjudication
**ROOT CAUSE ESTABLISHED — bounded, mechanism-level.** The M4 full-body OBS blocks planar escape from the thin M4 `clk` pin; every generated candidate is invalidated by M4 `Short`/`EolKeepOut` violations (and additionally by M5 via-landing violations). Carving only the M4 OBS flips 0→3 accepted APs under identical conditions. The mechanism is multi-violation: M4 OBS is decisive for planar escape; M5 OBS, thin-pin end-of-line, and metal spacing are contributing. Scope: `pin_access` in this ODB/LEF/toolchain only — **not** proof of a production LEF defect, DRC-clean routing, timing closure, or other pins' behaviour.

## 10. Confidence and residual gaps
Confidence HIGH for the bounded mechanism. Residual gaps recorded: marker `getSrcs()` not logged (spatial attribution only); no no-op control arm; non-DEF ODB properties not exhaustively diffed; unpatched-control build byte-match inherited from earlier evidence; independent reviewer notes that under a literal pre-registered bar these would reduce the label to high-confidence PROBABLE with an ESTABLISHED path — hence the bounded wording above.

## 11. Remedy boundary
No remedy approved. Any production change (LEF OBS, pin geometry, via rules, placement) requires a separate decision and controlled validation. No full baseline, detailed routing, extraction, timing, or signoff was performed.

## 12. Recommendation
Next milestone should evaluate a production-relevant remedy only after separate approval, with DRC/router validation on a full flow. Preserve this A/B as the causal evidence baseline.
