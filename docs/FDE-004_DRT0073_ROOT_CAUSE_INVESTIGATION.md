# FDE-004 — DRT-0073 Macro Pin-Access Root-Cause Investigation

- **Task:** T-FDE-004 (investigation only)
- **Date:** 2026-11-19
- **Coordinator:** orchestrator
- **Independent agents:** A (macro geometry/LEF/GDS), B (tracks/layers/vias), C (OpenROAD/FlexPA), D (placement/alignment)
- **Verdict category:** **ROOT CAUSE PROBABLE** — the failure class and mechanism are evidence-backed; the exact FlexPA filter stage that eliminated the last access-point candidate is **NOT EVALUATED**.
- **No fix was approved or applied. No second run was launched.**

## 1. Executive summary

`u_sram/clk` is a geometrically valid, correctly placed, exactly on-track single M4 pin. It was genuinely evaluated by FlexPA (sigtype CLOCK, non-special), and **zero access points survived** the access-point filter chain, causing fatal DRT-0073 inside `pin_access` before `global_route` ran.

The evidence convergently points to a **macro LEF pin-access geometry problem**: the `clk` pin is a very thin M4 stub (0.084 × 0.024 µm) whose only legal escape/via path requires M3/M5 metal that the macro's full-body OBS (M1–M5, no carve-outs) obstructs. Via enclosure and the thin stub compound the problem.

Explicitly ruled out by evidence: macro placement / exact placement / bypassed Snapper alignment; routing-grid misalignment; clock-layer or pin/net misclassification; D-014 / `zero_` / DRT-0305; PDN or macro PG connectivity; LEF-vs-GDS pin mismatch.

## 2. Verified baseline run and exact failure

- Primary evidence: `runs/orfs_baseline_20261119T131025284719666Z_9263` (FDE-003 validation run). synth/floorplan/place/cts rc=0; route rc=2; finish not launched.
- `5_1_grt.log:16` `pin_access`; `:25` `Reading design`; `:108` `[ERROR DRT-0073] No access point for u_sram/clk (sram_x4x4x1).`; stack `:109-124` → `drt::pin_access_cmd`. `Number of snets: 3` (`:33`), `Number of nets: 72` (`:34`), 8 × DRT-0419 (`:36-43`).
- `global_route` (line 76) never reached; no `5_1_grt.odb`, no `route.guide`, no detailed routing/extraction/timing.

## 3. Macro geometry (Agent A — HIGH confidence)

| Property | Value |
|---|---|
| Macro | `sram_x4x4x1`, CLASS BLOCK, SIZE 3.672 × 13.608 µm, SYMMETRY X Y |
| `clk` pin | DIRECTION INPUT, USE SIGNAL; Liberty `clock:true` → ODB sigtype CLOCK (not PG) |
| LEF RECT (local) | (3.534, 8.376)–(3.618, 8.400) µm = (3534,8376)–(3618,8400) DBU |
| Size | 0.084 × 0.024 µm = 84 × 24 DBU (height = M4 min width exactly) |
| Center (local) | (3.576, 8.388) µm |
| Placement | R0 at (1.230, 8.184) µm, LOCKED / `isFixed=1` |
| Absolute RECT | (4.764, 16.560)–(4.848, 16.584) µm = (4764,16560)–(4848,16584) DBU — matches ODB bit-for-bit |
| Net | `clknet_1_0__leaf_clk` |
| Shapes | exactly one M4 pin shape; nearest neighbor `ce_n` 0.168 µm away; M3 pins ≥1.3 µm in x |
| OBS | five full-macro rectangles (0,0)–(3.672,13.608) µm on M1–M5, **no carve-outs**; ODB confirms 5 obstructions |
| GDS | top cell `sram_x4x4x1`, 65 cells, dbu 0.00025 µm, bbox 3.672 × 13.652 µm, 27 layer/datatype combos; layer 40↔M4, 30↔M3; pin marker reproduces LEF RECT under the 0.054 µm FOREIGN offset |

LEF ↔ GDS ↔ Liberty ↔ ODB agree. NOT EVALUATED: complete GDS metal continuity under the pin marker; DRC legality.

## 4. Routing grid and via analysis (Agent B)

- Platform `asap7_tech_1x_201209.lef`; `make_tracks.tcl:5-7`: M4 `y = 0.012 + n·0.048` (horizontal), M3 `x = 0.009 + m·0.036` (vertical), M5 `x = 0.012 + k·0.048`. `Number of track patterns: 32` = 16 track statements × 2 directions. No design-level routing-layer / via-in-pin overrides.
- `clk` center y 16.572 µm → `(16.572−0.012)/0.048 = 345` exactly: **center-to-M4-track = 0 DBU**; pin edges ±12 DBU from center.
- M3 vertical tracks at x 4.797 / 4.833 µm cross the pin shape; nearest to center is 9 DBU off-center.
- VIA34 (M3↔M4, V3 cut 18×24 DBU) needs 11 DBU M4 side enclosure / 5 DBU M3 end-of-line; VIA45 (M4↔M5, V4 cut 24×24) needs 11 DBU on M4/M5. Only **one** grid x (4.797 µm) geometrically fits both vias inside the pin — `[GEOMETRIC CANDIDATE]`, **not** tool-confirmed legal. The M3/M5 halves lie inside the full-macro OBS.
- Grid misalignment and wrong clock layer are **refuted** as causes.

## 5. FlexPA diagnostics (Agent C)

- `FlexPA::genInstAccessPoints` (`FlexPA_acc_point.cpp:1514–1535`) raises DRT-0073 when a non-skipped instance term yields zero surviving APs. `clk` sigtype CLOCK, `isSpecial=0` → not skipped → genuinely evaluated.
- Source filter chain: `genAPsFromPinShapes` → `createAPsFromLayerToRectCoordsMap` → `validateAPForPlanarAccess` → `filterMultipleAPAccesses` → `hasAccess()`. All candidates were eliminated. **Which specific stage fired is NOT EVALUATED** — logs contain no candidate-level coordinates or rejection reasons.
- `pin_access` uses `verbose=1` default; `set_debug_level DRT pin_access 1` would add sparse-AP threshold output but not per-candidate rejection reasons without source instrumentation.
- DRT-0419 (`io_parser_helper.cpp:926–929`) is a non-fatal center-track advisory on M3 D/Q pins; never emitted for `clk` (M4); different mechanism from DRT-0073. D/Q AP success is unproven because the tool aborts at the first zero-access term.

## 6. Macro placement / `-exact` analysis (Agent D)

- `macro_placement.tcl` uses `place_macro -exact`, which skips Snapper (`rtl_mp.cpp:106-108`); macro LOCKED in ODB; logs show MPL-0035/0062/0017/0013, **no MPL-0005**.
- Snapper validates exact pin-*center* == track equality on RIGHTWAYONGRIDONLY layers (`snapper.cpp:282-289`, fatal). D/Q centers are 3–4 DBU off M3 tracks, so non-exact placement would analytically have hit MPL-0005 (predicted, not tested).
- All 12 M4 pin centers land **exactly** on M4 tracks, including `clk`; `check_placement` reported zero violations; legalizer converged 0/0/0. **Snapper compliance cannot explain a failure on the on-track `clk` pin; placement is not the cause.**

## 7. D-014 / constant-tie status (kept separate)

D-014 patch hash `cd86b587…` present in the mirror, `D:\tools` copy `3968898c…` unpatched. DRT-0305 absent from the FDE-003 run, present in 11 earlier runs. `zero_` is GROUND, non-special in the persistent ODB, with six driverless macro signal sinks; D-014 toggles an in-memory SPECIAL bit only. No evidence links `zero_` to the `clk` (CLOCK/M4) access failure. Physical tie correctness remains unresolved and **not part of this root cause**.

## 8. Agent findings summary

| Agent | Core finding | Confidence |
|---|---|---|
| A | Geometry valid, LEF/GDS/ODB agree, OBS full-body no carve-out | HIGH |
| B | Grid aligned; one geometric via candidate; OBS blocks M3/M5 halves | MEDIUM-HIGH (~0.75) |
| C | FlexPA did evaluate `clk`; all APs filtered; exact stage unknown | HIGH for evaluation, LOW for exact stage |
| D | Placement legal, `-exact`/Snapper irrelevant | HIGH |

No conflicts between agents; all four independently rejected placement/grid/classification causes.

## 9. Hypothesis matrix

| Hypothesis | Supporting | Contradicting | Confidence | Discriminating test | Risk | Remedy class |
|---|---|---|---|---|---|---|
| H1: Full-macro M3/M5 OBS blocks legal via-in-pin / escape for `clk` | LEF OBS lines 188-199; B geometric candidate inside OBS; D handoff | No tool-level candidate dump yet | MEDIUM-HIGH | Scratch-copy `pin_access` with via-in-pin layers / trimmed OBS control | Low if on copy, medium if on real design | LEF/OBS or via-access config |
| H2: 0.024 µm M4 stub too thin for legal via enclosure | A: height = M4 min width; B: 11 DBU enclosure vs 24 DBU height | One geometric candidate fits VIA34/VIA45 | MEDIUM | Legal-translation sweep of AP generation with verbose diagnostics | Low on copy | Pin geometry / access config |
| H3: Placement offset / bypassed Snapper | historical `-exact` note | D: centers on track, legal, no MPL-0005, clk center exact | LOW (refuted) | (none needed) | — | Placement adjustment (not indicated) |
| H4: Grid pitch/orientation mismatch | prior DRT-0419 concern | B/A/D: center-to-track 0 DBU; D/Q warnings are advisory | LOW (refuted) | — | — | Grid change (not indicated) |
| H5: Pin/net misclassification or D-014/`zero_` | historical DRT-0305 | C: clk CLOCK non-special; DRT-0305 absent; unrelated nets | LOW (refuted) | — | — | Net classification (not indicated) |
| H6: FlexPA limitation / filter-stage behavior (e.g. sparse-AP threshold) | C: zero APs after filter chain; no candidate data | no evidence of tool bug | LOW–MEDIUM | `set_debug_level DRT pin_access 1`, optional source instrumentation | Low on copy | Flow infrastructure / tool version |

## 10. Root cause and confidence

**ROOT CAUSE PROBABLE.** The defensible root cause statement: *the pre-synthesized SRAM macro LEF gives `clk` a single, minimum-width M4 pin stub over a full-macro M1–M5 OBS; although the pin center is exactly on an M4 track, no access point survives FlexPA's legal-access filtering because the required M3/M5 via landing and escape are inside the obstruction, with the thin pin geometry compounding enclosure constraints.* Confidence HIGH that this is the failure class; MEDIUM-HIGH on the specific OBS/via mechanism; the exact filter stage is NOT EVALUATED.

## 11. Missing evidence

1. FlexPA per-candidate AP dump with rejection reasons for `u_sram/clk` (coordinates, via cuts, layers, DRC/enclosure outcome).
2. Macro OBS box dump from the executed ODB (pin vs obstruction intersection at the via site).
3. AP status of other `u_sram` pins (D/Q/ce_n) — the tool aborts at `clk`, so their success is unknown.
4. Controlled comparison with explicit via-in-pin layers or a scratch OBS change on a **copy** of `4_cts.odb`.
5. OpenROAD source-revision pinning (binary reports `bazel-nostamp`; hash-level identity only).

## 12. Remedy options (none approved)

| Option | Rationale / expected effect | Side effects / implications | Files | Rerun scope | Verification | Confidence |
|---|---|---|---|---|---|---|
| R1: Explicit via-in-pin access configuration for M4→M3 on `clk` | Could allow via landing inside the pin despite OBS | Via/enclosure DRC risk; may affect other pins | flow config (scratch first) | route (5_1_grt) | AP exists; DRT-0073 gone; DRC clean | MEDIUM |
| R2: Correct macro LEF OBS to carve out pin-access regions | Removes the obstruction at the via site | Requires proof LEF is wrong vs GDS; impacts all macro pins | macro LEF (only if proven wrong) | floorplan onward | LEF/GDS consistency; DRT-0073 gone; DRC clean | LOW–MEDIUM |
| R3: Adjust legal macro placement so `clk` escapes on a clear layer/track | Could avoid OBS-blocked region | Placement currently legal and on-track; may violate other constraints | macro_placement.tcl | floorplan onward | legal placement; AP exists; DRC clean | LOW |
| R4: Tool/flow investigation (via-access flags, FlexPA debug, version) | May reveal a configurable mechanism or tool limitation | No design change; may need newer build | flow infrastructure only | route | diagnostic output explains filter | MEDIUM |

No remedy is approved in FDE-004; no patch was created or applied.

## 13. Recommended next controlled experiment (requires separate approval)

On a **scratch copy** of the FDE-003 run's `4_cts.odb`, run read-only `pin_access` with `set_debug_level DRT pin_access 1` and an explicit via-in-pin control, capture per-pin AP counts and route-stage logs, and compare against the unmodified copy. Cost: one short pin-access invocation (no full flow). Risks: confined to copy; no design/config change. Coordinator approval and a new decision ID (e.g. D-015) required before execution.

## 14. Strict limitations

Investigation only. No RTL/netlist/SDC/LEF/GDS/Liberty/PDN/placement/layer/track/via/OpenROAD/ORFS/D-014 change. No recovery patch, no second baseline, no detailed routing, no expensive experiment, no signoff. All findings are from read-only inspection of the FDE-003 run and exact-build source; historical runs are labeled as such.

## 15. Files created / modified by this milestone

Created: this report, `logs/sessions/FDE-004_S001_handoff.md`. Updated: `PROJECT_STATE.md`, `coordination/TASK_BOARD.md`, `coordination/ACTIVE_WORK.md`, `logs/DAILY_LOG.md`, `logs/AGENT_ACTIVITY.md`, `logs/REVIEW_LOG.md`, `logs/REPORT_LOG.md`, `docs/decisions/DECISIONS.md` (D-015 finding record). No design or run artifact modified.
