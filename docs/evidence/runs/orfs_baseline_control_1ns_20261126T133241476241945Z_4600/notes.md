# Run notes — `orfs_baseline_control_1ns_20261126T133241476241945Z_4600`

## Scope

Five images were rendered from five saved databases of this single run: `2_floorplan.odb`, `3_place.odb`, `4_cts.odb`, `5_route.odb`, `6_final.odb`. Raw full-view captures are preserved under `original/`; display-only crops are under `presentation/`. All source databases were read-only during capture; post-capture hashes matched pre-capture hashes.

## Capture method

The installed OpenROAD reports `-GUI`, so `save_image` is unavailable. The OpenROAD **web viewer** loaded each saved ODB and its matching `constraint_1ns.sdc`; a browser captured the layout pane. The load-only script is [`capture_stage.tcl`](capture_stage.tcl) and invokes only `read_db` and `read_sdc`. No synthesis, floorplanning, placement, CTS, routing, recovery, or flow-stage command was executed.

The viewer's WebSocket connection failed, producing a transient "disconnected" banner. Static layout tiles had already been rendered from the loaded database; the banner and viewer side panels were hidden for the capture. No design geometry was altered.

## Presentation derivatives

All five raw captures were cropped 1:1 to `(x=10, y=48, width=800, height=694)` from the 1012×751 source canvas. This removes unused black margin and the viewer tab bar while retaining the die, macro, scale bar and stage detail. Crops were saved as PNG via `System.Drawing` with nearest-neighbour interpolation; no recoloring, redrawing, or enhancement was applied. Derivative filenames and hashes are recorded separately in [`manifest.json`](manifest.json).

### Engineering-detail views

Three additional views were rendered **directly from the saved ODBs** with OpenROAD's headless `save_image -web` facility, not from the screenshots. Stage-specific micron areas (recorded in `manifest.json`) place the active design region at a much larger scale: floorplan `{2 8 32 75}`, placement `{0 2 42 79}`, routing `{0 2 39 78}`; output width 1200 px. Display options selected the relevant layers (macro/blockage, standard cells, routing segments/vias); instance-name labels were disabled in the routing view to avoid clutter. PNGs were composited onto opaque black to match the full-die gallery.

- `presentation/detail/floorplan_detail.png` — macro geometry, blockage and power straps.
- `presentation/detail/placement_detail.png` — standard-cell clusters beside and around the macro.
- `presentation/detail/routing_detail.png` — routed segments and vias in the active region.

**CTS:** a detail render was attempted from `4_cts.odb` with clock-net and routing visibility enabled. No distinct clock trunk, spine or buffer chain appears; the difference from placement is isolated cell-level pixels (2,451 pixels, 0.71% of the die rectangle by exact-colour comparison). Publishing it would overstate CTS evidence, so no `cts_detail.png` is included and the full-die CTS view is retained with this limitation.

**Final:** no detail image is included because it would duplicate the routing detail; the final ODB differs only subtly after routing. The full-die final view remains available.

## Stage observations

- **Floorplan:** macro blockage and power straps are clearly visible. The macro is the ORFS abstract `fakeram45_64x32`, not a foundry SRAM.
- **Placement:** standard cells are concentrated near the macro; the design is deliberately small, so the view is sparse. The placement log reports INFO-level weighted congestion 1.5015 with "could not reach target" despite `rc=0`.
- **CTS:** visually almost identical to placement at this zoom (2,451 pixels differ inside the die, 0.71% by exact-colour comparison). No legible clock tree is claimed. `4_cts_final.rpt` reports "No launch/capture paths found". A read-only investigation of a clock-only view (`save_clocktree_image -clock clk`) failed with `GUI-0001: Command save_clocktree_image is not usable in non-GUI mode`; no better visualization is available from the existing saved database without rebuilding the tool, so the original CTS view is retained with this limitation.
- **Routing:** routed nets appear across the macro region. The routing log records DRT-0199 counts `[159, 37, 32, 6, 6, 0]`, final 0. `5_route_drc.rpt` is 0 bytes; the verifier ties this to the final zero count.
- **Final:** final tool-generated implementation detail from `6_final.odb`. It is not signoff.

## Viewer artefact

The routing image scale bar reads `100 μm` while the other four read `20 μm`, although the die footprint occupies the same pixel rectangle in every image. This is a viewer artefact, not a zoom change; no physical distance is inferred from these bars in captions.

## Source reports

`2_floorplan_final.rpt`, `3_detailed_place.rpt`, `4_cts_final.rpt`, `5_global_route.rpt`, `5_route_drc.rpt` (0 bytes), `6_finish.rpt` (TNS 0.00, WNS 0.00, worst slack 0.64 at 1 ns). Congestion and DRT counts are traceable to `evidence/stage_place.log` and `evidence/stage_route.log`. Independent verification: `baseline_1ns_verify.json` — overall `PASS`, tool-level only.

## Limitations

- Router DRC = 0 is not foundry DRC. No DRC/LVS signoff, functional verification, or characterized multi-corner timing is claimed.
- The run's `engineering_verdict` remains `NOT EVALUATED — report-level review required (D-007)`; a tool return code is not engineering acceptance.
- No SattvaRoute source commit SHA was recorded for the run (`NOT_AVAILABLE`).
- `evidence/manifest.json` records a digest that differs from the file's own on-disk hash; this is disclosed as UNKNOWN in `manifest.json` and was not resolved here.
- Capture method details are self-declared; the published load-only script and unmodified source hashes are the verifiable anchors.

## Provenance pointer

Per-image source ODB paths and SHA-256 hashes, raw image hashes, derivative hashes, capture timestamps, tool hashes and report paths are in [`manifest.json`](manifest.json).
