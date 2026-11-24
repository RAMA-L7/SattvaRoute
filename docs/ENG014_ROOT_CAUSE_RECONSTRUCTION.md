# T-ENGINEERING-014 — Confirmed Root Cause and Evidence Chain

> Reconstructed from already-published evidence only. No new execution, no geometry change.

## 1. Authoritative chain (all VERIFIED)

| # | Finding | Source |
|---|---|---|
| 1 | `u_sram/clk` has zero accepted APs at `pin_access` → DRT-0073 | baseline run `orfs_baseline_20261118T171712Z` |
| 2 | Nine M4 AP candidates are **generated** (x=4788/4812/4836 among them, y=16572); all are dropped at final `hasAccess()` | `ENG012_GENERATION_REJECTION_MATRIX.md` |
| 3 | Decisive predicate: `isPlanarViolationFree` → `getMarkers().empty()` false; `setAccess(W,false)`; sparse 0 < 3 is a downstream consequence, not a cause | `ENG013_PREDICATE_FAILURE_TRACE.md` |
| 4 | Failing sub-check: `checkMetalSpacing_short`, `Short`, cid=0, rid=48, M4 | `ENG013_BLOCKER_ATTRIBUTION.md` |
| 5 | Blocking object: **fixed M4 master OBS**, `fixed=1`; rect absolute `(4704,16560)-(4764,16584)` = master-local `(3474,8376)-(3534,8400)` | ENG013-B instrumented `rect=`/`fixed=` provenance; behavior-neutral patch `8495405b…`, binary `db876fbf…` |
| 6 | Rect is stable across all 9 control candidates; instance label `u_sram#3:56` vs `:292` is transient and **not authoritative** | ENG013-B/C |
| 7 | Broad-carve ODB `616e39f8…` removes that exact west rectangle; replay (same binary, same Tcl) gives W clean 3/3, CREATE 3 / ACCEPT 3 / DROP 0, DRT-0073=0, RC=0 | `ENG012_BROAD_CARVE_PROVENANCE.md`, `ENG013_DIRECTIONAL_PLANAR_DRC_REPORT.md` |
| 8 | Broad carve frees **120 `M4/0` + 92 `M4/251` real internal shapes** → physically illegitimate; diagnostic counterfactual only | `FDE-006U`, `ENG012_HYPOTHESIS_UPDATE.md` |
| 9 | Narrow variants (R1-N x3534–3672, R1-N-W x3474–3672 y±24; C1 y±48; C2 corner tab) all reached the DB but produced **0 accepted APs**; marker families shifted, no AP recovery | `FDE-007_REMEDY_EVALUATION.md`, `ENG011_DIAGNOSTIC_RESULTS.md` |
| 10 | Config-only `via_in_pin_bottom/top_layer M4` A/B was a no-op; placement/grid attempts refuted (relative pin↔OBS geometry invariant) | `FDE-005`, `FDE-004-D`, Agent A report |

## 2. Causal statement

DRT-0073 is caused by a **fixed M4 master-OBS strip immediately west of the `clk` pin**, overlapping the westward planar escape stub at y=16572. The DRC worker reports a geometric metal short between the own-net access stub and that fixed OBS. Removing the strip makes the west planar direction clean; because a macro pin needs only one clean planar direction, three candidates are then accepted and the sparse threshold (3) is met.

Contributing but **non-binding** marker families: `Metal Spacing`, `Lef58SpacingEndOfLine`, `Lef58EolKeepOut`, and VIA45 M5 landing `Short`s. These persist even in the accepted broad-carve replay (candidate x=4836 accepted with them present).

## 3. What the chain does *not* establish

- No proof that the aggressor object class is a master-OBS `dbBox` rather than a pin stub or routed wire — the `(layer, rect, fixed)` tuple is decisive geometrically but object-type/net fields were not emitted.
- No proof of physical vacancy of the strip in design-level GDS over its **full bbox** (prior census covered only a 2 nm sliver).
- No proof that other pins gain APs under any narrow carve; all-pin state is UNKNOWN and prior `clk`-local carving shifted failure to `ce_n`.
- No global/detailed route, DRC, LVS/PEX, SPEF, or timing evidence for any remedy geometry.
- No production authorization: broad-carve success is a diagnostic result, not a solution.
