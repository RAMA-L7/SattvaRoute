# T-PNR-001 — Control Benchmark Preparation

## Separate preparation step (not recovery)

The Nangate45 control design uses a prepared gate-level netlist so recovery never re-synthesizes. Steps:

1. Generated a synthesis blackbox Verilog interface from the platform `fakeram45_64x32.lef` pin names (`rtl/fakeram45_64x32_bb.v`). This is not a memory compiler: no geometry, timing or functionality was invented.
2. Added a thin pass-through wrapper `rtl/sattva_macro_top.v` with one hard macro instance and a local `constraint.sdc` (1000 ps clock, 10% IO delays).
3. Ran the pinned ORFS canonicalize stage, then Yosys 0.33 `read_rtlil → hierarchy → synth → dfflibmap → abc → opt_clean → write_verilog` against Nangate45 Liberty to produce `netlist/sattva_macro_top_synth.v`.
4. Recorded commands and rationale in `netlist/synth_provenance.txt`.
5. Config sets `SYNTH_NETLIST_FILES`; ORFS copies the netlist and skips synthesis during every run/attempt.

## Compatibility patch (execution mirror only)

The installed Yosys 0.33 does not support ORFS’s newer `read_liberty` annotation flags, and its ASAP7 Liberty collateral has additional parse problems. A guarded compatibility flag (`SATTVA_YOSYS_COMPAT=1` in the control config) skips only the unsupported annotation read in the **execution mirror** `synth_stdcells.tcl`. No SDC target, technology rule, RTL functionality, macro view or production file was modified.

Earlier failed feasibility attempts on ASAP7 (`asap7/riscv32i`, `asap7/riscv32i-mock-sram/fakeram7_256x32`) are preserved with their logs and preflight/manifest evidence.
