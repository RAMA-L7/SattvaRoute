# T-ENGINEERING-009 — Independent Agent Findings and Coordinator Adjudication

- **Session:** 2026-11-23/24
- **Agents:** A geometry, B OpenROAD mechanism, C flow/configuration, D independent challenge.

## 1. Workstream findings (evidence-backed)

| Agent | Core finding | Key evidence |
|---|---|---|
| A — Geometry | `clk` pin and OBS geometry hash-pinned; placement/grid causes ELIMINATED; broad M4 OBS carve sufficient only in FDE-006U scratch; narrow corridors weakened by ±24 nm y margin vs ~48 nm EOL/corner keepout; provenance missing | `FDE007_A_geometry.md`, LEF `f1c18877…`, GDS `12c56777…`, ODB `35bff121…`, tech LEF `d6361434…` |
| B — Mechanism | Full code path traced; `frAccessPoint` has no rejection-reason field; instrumented binary `0d890431…` present; `getSrcs()` API exists but uncollected; sparse threshold downstream; DRT-0419 distinct | `FlexPA_acc_point.cpp:1514-1535,1318-1331,1215-1252`; `frMarker.h:67,73,80` (verified directly); `io_parser_helper.cpp:926-929` |
| C — Flow/Config | All config hashes parity with FDE-003; D-014 present in mirror `cd86b587…` only; config-induced causes ELIMINATED; no config-only fix; via-in-pin no-op not to repeat; DRT-0419 decoupled | config.mk `63481bef…`, SDC `7b12de64…`, PDN `dec2ffed…`, placement `fc79c4fd…`, runner `0c790cc9…`, `D:\tools` `3968898c…` |
| D — Independent challenge | ACCEPT WITH LIMITATIONS but five blocking issues in the initial proposal: unmeasurable equivalence criterion, semantic A3 dodge, vague attribution/sliver rules, over-stated y-envelope conclusion, and risk of post-hoc geometry green-lighting | `ENG009_D_challenge.md` |

Two Agent C sessions were run (original and fresh after non-response); both agreed on config parity, elimination of config causes, no config-only fix, and DRT-0419 separation. They differed only in ranking config-only flag enumeration first (original) versus provenance first (fresh); coordinator selected provenance because it is cross-cutting and config-only diagnostics have low causal gain.

## 2. Coordinator adjudication of Agent D blockers

| ID | Agent D finding | Resolution in proposal |
|---|---|---|
| B1 | Three-way equivalence demanded per-marker census from production binary that emits none | Criterion 1 rewritten: Arm A vs B full per-marker equivalence; production binary aggregate-level only; smoke test first |
| B2 | `mechanism-only` class and A3 N/A was a semantic dodge around a genuine one-variable contrast | Reclassified `causal diagnostic` (instrumentation behavior only); Arm A is a digest-backed concurrent identity arm; A3 PASS with explicit note that the physical no-op-control gap remains open; cost cap added |
| B3 | ≥90% "resolvable" and sliver classification vague/assertion-satisfiable | Operational definitions added: source object or OBS-box id; artifact-vs-metal decision rule using GDS census; disagreement reported, not resolved by assertion |
| B4 | y-envelope conclusion INFERRED beyond evidence; no test in DIAG-001 | Relabelled INFERRED; rank-2/3 static pre-work made mandatory before rebuild; stop/redirect rule added |
| B5 | Results could be used post-hoc to green-light another rejected corridor variant | New classification-only/no-geometry gate added (§9); any future geometry needs a separate decision, full envelope, provenance, zero foreign metal, no-op control, full-flow plan |

Non-blocking Agent D concerns addressed: getSrcs not uniquely highest information (static ranks 2–3 now mandatory first); R2 shadow A8/A13/A17 corrected (A17 PARTIAL pending smoke test); DRT-0419 separation described as diagnostically solid but D/Q AP status UNTESTED; absent approval ledger recorded.

## 3. Accepted interpretations

- Root cause **CONFIRMED bounded**: full-body M4 master OBS blocks planar escape in the FDE-006U scratch DB; contributing factors thin-pin EOL/spacing and M5 via landing.
- Mechanism for narrow-corridor failure is **INFERRED**: y margin below EOL/corner keepout reach; not proven and not a license for a new geometry.
- DRT-0419 **does not share** DRT-0073's mechanism; D/Q AP status remains UNTESTED and must be a separate investigation.
- No previous remedy variant is repeated; all five catalog entries remain RECOMMENDED and no skill was installed or activated.

## 4. Independent review verdict after fixes

Agent D's conditional ACCEPT is satisfied by the five revisions above. Proposal remains **NOT AUTHORIZED**; the coordinator does not execute it.
