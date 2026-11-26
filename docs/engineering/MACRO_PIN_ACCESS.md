# Macro and pin-access issues

Status: engineering background plus implemented evidence handling. Historical investigations preserved in `docs/` (`ENG*`, `FDE-*`) and indexed in `docs/REPORT_INDEX.md`; this page does not rewrite them.

## Why macros matter

A macro in physical design is a hard block (e.g. SRAM) with abstract views: LEF (geometry, pins, blockages), Liberty (timing), and optionally GDS. If the macro views are inconsistent with the netlist instance, or if a pin cannot be reached by the router, implementation fails late and is expensive to diagnose.

## The control benchmark macro

`fakeram45_64x32` is an **abstract** macro supplied by the pinned ORFS Nangate45 platform. It is not a foundry-characterized SRAM and has no bit-cell geometry here. The netlist contains one instance; the synthesis blackbox (`rtl/fakeram45_64x32_bb.v`) is a synthesis-only interface stub. Macro interface consistency (cell name and pins such as `clk`, `we_in`, `ce_in`, `addr_in[5:0]`, `w_mask_in[31:0]`, `rd_out[31:0]`, `wd_in[31:0]`) was observed across netlist ↔ LEF ↔ Liberty during benchmark preparation and is recorded in `docs/REPRODUCIBILITY.md`; no automated checker implements this as a capability.

## Implemented failure handling

- **Missing macro Liberty** (`ADDITIONAL_LIBS` target): classified `MISSING_MACRO_LIB`; controlled failure fixture is attempt-local. Bounded correction targets that variable only.
- **Missing macro LEF** (`ADDITIONAL_LEFS` target): held-out case failed at `synth`; deterministic diagnosis; human-approved patch (`AP-HELDOUT-LEFS-001`); isolated recovery verified PASS. See `docs/HELDOUT_RECOVERY.md`.
- **Pin access** (`PIN_ACCESS` family): emitted for `No access point` or `DRT-0073` hits; LEF/Liberty pin geometry is supporting evidence, not a blanket rule for all DRT codes. The historical DRT-0305 case was a **net-classification** failure (`zero_` constant net typed GROUND, not routable by TritonRoute), not a pin-access failure; its declared local patch (`global_route.tcl`: mark `zero_` net SPECIAL before the first TritonRoute call) is recorded in the manifest with its hash. DRT-0073 / OpenFinRAM remains **unresolved and not reopened**; the classifier can still report a `DRT-0073` hit as `PIN_ACCESS`.

## Boundaries

- No claim of general macro/pin-access diagnosis across arbitrary macros or PDKs.
- No foundry macro characterization or signoff.
- Historical verdicts are not relabeled; DRT-0073 is not reopened.

## Related

`docs/engineering/CONFIG_COLLATERAL.md`, `docs/architecture/DIAGNOSIS.md`, `docs/research/LIMITATIONS.md`.
