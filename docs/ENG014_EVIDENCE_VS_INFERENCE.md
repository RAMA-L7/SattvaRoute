# T-ENGINEERING-014 — Evidence vs Inference Table

Labels: **PROVEN** (direct measurement/read from preserved artifact) · **INFERRED** (reasoned from proven facts) · **UNKNOWN** (not established).

| # | Statement | Status | Basis / limitation |
|---|---|---|---|
| 1 | West planar AP for `u_sram/clk` is the gate; `getMarkers().empty()` decisive | PROVEN | ENG013 source trace + replay |
| 2 | Failing check is `Short`, cid=0, rid=48, `checkMetalSpacing_short`, M4 | PROVEN | ENG013-B marker line + source |
| 3 | Blocking rect is fixed M4 OBS abs `(4704,16560)-(4764,16584)` | PROVEN | instrumented aggressor tuple `rect=…, fixed=1`; matches master geometry; stable across 9 candidates |
| 4 | Aggressor instance suffix `:56`/`:292` identifies the blocking object | **REJECTED** | provenance artifact of `addTargetObj(inst)`; numeric id unstable |
| 5 | Aggressor object class is a master `dbBox` OBS (not pin stub / routed wire) | **INFERRED → UNKNOWN** | geometry/fixedness PROVEN; object type/net never emitted |
| 6 | Literal tech-LEF rule text for rid=48 | UNKNOWN | no constraint-ID→rule dump |
| 7 | Broad carve removes the west strip and restores W access + 3 accepted APs | PROVEN | ODB hash `616e39f8…`, replay CREATE=3/ACCEPT=3/DROP=0, DRT-0073=0 |
| 8 | Broad carve is a legitimate production remedy | **REJECTED** | frees 120 `M4/0` + 92 `M4/251` real shapes; explicitly rejected in FDE-007 D-022 |
| 9 | Minimal west-strip carve would restore `clk` W access | INFERRED (high) | strip is exactly the proven blocker rect; E-side markers non-binding |
| 10 | Minimal west-strip carve would pass whole `pin_access` | **UNSUPPORTED** | other 11 pins unchanged; `clk`-local carve shifted failure to `ce_n` |
| 11 | The strip is free of real SRAM metal over its full bbox | UNKNOWN | GDS census covered only a 2 nm sliver |
| 12 | Pin-geometry adjustment would fix the blocker | UNSUPPORTED | M4 OBS removal alone sufficed; LEF↔GDS mismatch; no LVS/PEX |
| 13 | Placement/alignment adjustment would fix the blocker | **REFUTED** | relative pin↔OBS geometry invariant under rigid translation; FDE-004-D |
| 14 | A config flag would create the first AP | **REFUTED** | via-in-pin tested no-op; threshold flags cannot create AP 1; 0-AP fatal |
| 15 | Generator-level OBS regeneration would give an all-pin fix | UNKNOWN / speculative | no configurability or defect evidence; largest scope |
| 16 | Full-flow (route/DRC/timing) correctness of any geometry | UNKNOWN | no flow beyond `pin_access` was run for any carve |

## 2. Reproducibility caveats found by Agent C (recorded here, historical reports preserved)

| Caveat | Status | Consequence |
|---|---|---|
| `ENG012_BROAD_CARVE_PROVENANCE.md` records `4e8a85dc…36fdea` as a "SHA-256" but it is 46 hex chars and is not a prefix of the actual file hash (`4E8A85DC…FDEA`) | PROVEN (C recomputed) | log content still matches line-for-line; the recorded string is **not** a usable verification key. Historical report is preserved, not edited. |
| ENG012 replay used binary `7461d0d0…` while original FDE-006U Experiment B used `0d890431…` | PROVEN | replay is "same counts on an equivalent binary" (ENG010 equivalence PASS), not same binary |
| Broad-carve generating LEF/script was never located | PROVEN | artifact replayable only from preserved ODB; no full source→artifact reproduction |
| No byte-level canonical ODB diff; selected-field dump only | PROVEN | collateral-delta claim is bounded |
| `ENG012_HYPOTHESIS_UPDATE.md` row 5 says all 9 candidates survive sparse; contradicts generation matrix (only 3 generated) | PROVEN | "all 9 survive" is REJECTED; historical report preserved |
| FDE-006U §6 right-bar rect differs from dump (`…13608` vs `…13300` + separate top band) | PROVEN | `clk` band geometry unaffected |

## Rule for the decision

Only PROVEN statements may be used as decision premises. INFERRED statements may motivate a *bounded, authorized diagnostic*, never a production change. UNKNOWN / REJECTED / UNSUPPORTED statements must not be quoted as justification for implementing a remedy.
