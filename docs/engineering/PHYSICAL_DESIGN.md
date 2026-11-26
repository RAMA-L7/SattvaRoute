# Physical-design workflow context

Status: general engineering background, included only to orient readers. **SattvaRoute does not implement these stages**; it orchestrates ORFS/OpenROAD and reasons about their evidence. Implemented scope: `docs/architecture/`, `docs/reference/CAPABILITIES.md`.

## The flow stages

| Stage | Engineering role | Evidence SattvaRoute reads |
|---|---|---|
| Synthesis (`synth`) | RTL → gate-level netlist using Liberty cells | Stage log, resolved library/netlist variables, produced netlist |
| Floorplan | Die/core area, macro placement, PDN, I/O | Stage log, `1_synth.odb` input; macro placement reports |
| Placement (`place`) | Standard-cell placement, congestion | `2_floorplan.odb` input, placement/congestion reports |
| CTS | Clock tree synthesis, skew, insertion delay | `3_place.odb` input, clock reports; `updated_clks.sdc` is an **intermediate** artifact |
| Global/detail route | Global routing guides, detailed routing | `4_cts.odb` input, `route.guide`, `5_route.odb`, `DRT-0199` counts, `5_route_drc.rpt` |
| Extraction | Parasitics from geometry | `6_final.spef`, RCX-0045 counts, unannotated drivers |
| Timing (STA) | Setup/hold slack from extracted parasitics | `6_finish.rpt`, period/fmax, WNS/TNS, violation counts |
| Finish | Final outputs (DEF/GDS/verilog/SDC) | `6_final.def`, `6_final.gds`, `6_final.v`, `6_final.sdc` |

## How SattvaRoute relates to each stage

- It **launches** stages through the runner with a pinned ORFS revision and active profile.
- It **captures** logs and artifacts after each stage.
- It **classifies** failures by reading logs and resolved configuration (e.g. a missing `.lib` target at `synth`).
- It **derives** the earliest affected stage from declared `stage_inputs`, so recovery reruns only what must be rerun.
- It **verifies** endpoints and report signals independently.

## Important distinctions

- **Pin access** is a routing-era failure where a macro pin cannot be reached; the classifier emits `PIN_ACCESS` for `No access point` or `DRT-0073`, with LEF/Liberty pin geometry as supporting evidence. See `docs/engineering/MACRO_PIN_ACCESS.md`.
- **Macro collateral** (LEF, Liberty, optional GDS) must match the pinned platform and macro. The control benchmark uses an **abstract** `fakeram45_64x32`, not a characterized foundry SRAM. See `docs/engineering/CONFIG_COLLATERAL.md`.
- **Timing units** must be read from `report_units` and Liberty `time_unit` before interpreting bare periods. See `docs/engineering/SDC_TIMING.md`.
- **Verification boundaries** separate router-internal checks from signoff. See `docs/engineering/VERIFICATION_BOUNDARIES.md`.

## Supported workflow

The only validated end-to-end workflow is `nangate_macro_control` (Nangate45 + `fakeram45_64x32`) on the pinned ORFS revision with two declared local patches and pinned tool binaries. Historical ASAP7 / OpenFinRAM profiles are preserved but inactive and unresolved. See `docs/research/LIMITATIONS.md`.

## Related

`docs/engineering/FAILURE_TAXONOMY.md`, `docs/architecture/LIFECYCLE.md`, `docs/REPRODUCIBILITY.md`.
