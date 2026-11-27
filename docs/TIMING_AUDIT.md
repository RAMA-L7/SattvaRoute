# Timing-unit and constraint audit (SattvaRoute)

This records **what the pinned tool actually does**, not what the documentation
claims. Evidence is captured with `scripts/audit_timing.tcl` (read-only) and
summarized by `scripts/timing_audit.py`. Machine-readable record:
[`evidence/timing/timing_audit.json`](../evidence/timing/timing_audit.json);
raw tool output: [`evidence/timing/timing_audit.raw.txt`](../evidence/timing/timing_audit.raw.txt).

## Status separation (read first)

Five independent facts. A "PASS" on one is not a "PASS" on another:

1. **Flow completed** — every declared stage rc=0 and endpoint artifacts exist.
2. **Reported timing checks passed at the executed target** — `setup=0`,
   `hold=0`, `worst slack ≥ 0`, `tns/wns = 0` at the executed clock period.
3. **Timing coverage complete** — no unconstrained endpoints (`check_setup`
   empty), no unannotated drivers, no missing timing arcs/blackboxes.
4. **Characterized physical timing established** — corner/PVT, RC corner,
   propagated clock, extracted parasitics. This benchmark uses an **abstract
   FakeRAM** model (see *FakeRAM scope* below); it is not foundry-characterized
   SRAM.
5. **Signoff performed** — NOT performed. No foundry DRC/LVS, no power, no IR
   drop, no antenna, no electromigration, no SDF/functional signoff. The router
   "DRC=0" is OpenROAD-internal routing DRC, not foundry DRC.

**Timing checks do not imply functional correctness.**

## Tool and unit evidence (captured, not asserted)

From the pinned OpenROAD `bazel-nostamp` at ORFS `25b6429c…`, executed with the
local patches recorded in `evidence/mirror.patch` / the manifest, on the
accepted baseline `orfs_baseline_nangate_macro_control_20261125T144339456871595Z_11464`:

- `report_units`: **time 1ns, capacitance 1fF, resistance 1kohm**, voltage 1v,
  current 1mA, power 1nW, distance 1um. (Captured; `scripts/timing_audit.py`.)
- Liberty `time_unit: "1ns"`, `voltage_unit: "1V"`, capacitance unit per the
  pinned Nangate/FakeRAM files. Both standard-cell and macro Liberty use **1ns**.
- No time-unit conversion is performed by ORFS; the SDC numeric value is in
  tool time units (nanoseconds). ORFS only *extracts* a numeric `clock_period`
  (`clock_period.txt`) for synthesis `abc -D`, and propagates constraints via
  `read_sdc`; it does not rescale the period.
- `set_propagated_clock [all_clocks]` is applied in `final_connect.tcl`.
- Post-route analysis reads extracted parasitics: `final_outputs.tcl` runs
  `set_extraction_rules_file $::env(RCX_RULES)`, `extract_parasitics`,
  `write_spef …/6_final.spef`, then `read_spef …/6_final.spef`, then reports.
- `6_report.log` shows `read_spef 6_final.spef`. `report_parasitic_annotation`
  reports `Found 0 unannotated drivers`, `Found 0 partially unannotated drivers`.
- RCX evidence: `[INFO RCX-0045] Extract 209 nets, 677 rsegs, 677 caps, 1998 ccs`.
  RCX rules `flow/platforms/nangate45/rcx_patterns.rules`; RC setup
  `setRC.tcl`; `set_wire_rc -signal -layer metal3`, `set_wire_rc -clock -layer
  metal5`.
- SPEF `6_final.spef` (201,261 bytes) present and non-empty.

## Corner / PVT / library set

- Operating corner: Liberty `default_operating_conditions` **typical** (Nangate
  `typical`, FakeRAM `tt_1.0_25.0`); `nom_process 1`, `nom_temperature 25`,
  `nom_voltage 1.1`. No temperature/voltage scaling, no derating
  (`set_timing_derate` not called; no OCV/AOCV). 
- Platform `PROCESS = 45`. `PWR_NETS_VOLTAGES 1.1`.
- Library set (`flow/platforms/nangate45/config.mk`): standard cells
  `lib/NangateOpenCellLibrary_typical.lib`, macro `lib/fakeram45_64x32.lib`
  (added via `ADDITIONAL_LIBS`), tech `lef/NangateOpenCellLibrary.tech.lef`,
  SC LEF `lef/NangateOpenCellLibrary.macro.mod.lef`, macro LEF
  `lef/fakeram45_64x32.lef`. Single corner. (Hashes in
  `config/sattva_manifest.json`.)
- Only `typical` Nangate is used; no `ff`/`ss`. Not multi-corner signoff.

## Clock

- `create_clock -name clk -period 1000 [get_ports clk]`, waveform `0.00 500.00`
  (from `constraint.sdc`, `report_clock_properties`, `1_2_yosys.sdc`,
  `6_final.sdc`, `clock_period.txt=1000`).
- **Executed period = 1000 ns (1 MHz).** `clock propagation`: propagated
  (`set_propagated_clock`); `report_clock_skew` reports no launch/capture paths
  (no register-to-register paths in this pass-through design).
- IO delays: `set_input_delay`/`set_output_delay` = `clk_period * clk_io_pct`
  = `1000 * 0.1` = **100 ns** on `all_inputs`/`all_outputs`, clock `clk`. These
  are part of the executed constraint, not a separate tool convention.
- Normalized: period 1000 ns = 1e-6 s; **frequency `f = 1/1e-6 = 1e6 Hz = 1 MHz`.**
  Executed target = 1 MHz, not 1 GHz.

## Timing coverage

- 73 input ports, 32 output ports, 1 register (`u_macro`/`fakeram45_64x32`,
  `register_clock_pins=1`), 1 clock, `unconstrained_endpoints=0`.
- `check_setup -verbose` empty (no setup warnings). `report_checks
  -unconstrained` prints a macro→output path even though constrained; coverage
  is taken from `check_setup`, not that command.
- 0 unannotated drivers, 0 partially unannotated, no missing timing arcs, no
  blackboxes in timing. `report_check_types -violators`: no violators.

## Slack / period / fmax reconciliation (historical combination)

At executed 1000 ns, `clk_io_pct=0.1`, output delay 100 ns:

- `worst slack max = 899.75`. Reconciles as `1000 − 100 (output delay) −
  0.2511 (path) = 899.7489`; the register→output buffered path is 0.2511.
  (Recorded 899.75.) Not 899.75 with a different unit; it's ns.
- `worst slack min (hold) = 99.98`. 
- `setup violation count 0`, `hold violation count 0`, `tns max 0.00`,
  `wns max 0.00`.
- `clk period_min = 100.25 fmax = 9.97` is emitted **only** with
  `report_clock_min_period -include_port_paths`. The dominant min period comes
  from port-path constraints (`output_delay` 100 + path 0.2511), not a
  register-to-register requirement. `period_min=100.25` ns, `fmax≈9.97 MHz`.
- **Reg-to-reg `period_min = 0.00 fmax = inf`** (no register→register paths;
  the macro outputs are unconstrained register endpoints relative to `clk`
  arrival at the macro, and there are no downstream flops). 
- `updated_clks.sdc` (period 95.2596) is an ORFS-internal CTS artifact written
  during clock synthesis, **not** the executed final constraint. Final
  `6_final.sdc` / `6_1_fill.sdc` keep `create_clock -period 1000`.
- `clock_period.txt = 1000` feeds only `abc -D 1000`, not a reported slack.

## The 1000× unit error

Documented intent vs executed:

| | documented intent | executed |
|---|---|---|
| provenance comment | `constraint.sdc (1000 ps clock, 10% IO delays)` | `create_clock -period 1000` |
| period | 1000 ps = **1 ns** | **1000 ns** |
| frequency | 1 GHz | **1 MHz** |
| IO delay | 100 ps = 0.1 ns | **100 ns** |

Because Liberty/`report_units` are **1ns**, `1000` is 1000 ns, not 1000 ps.
No other documented unit convention explains the values. The `period_min=100.25`
and `fmax≈9.97` figures are *consequences* of the executed 1000 ns target, not
evidence of a 100 MHz/9.97 MHz design.

**APPLIED with explicit user approval.** See `proposals/sdc_1ns.patch`.
Add versioned `constraint_1ns.sdc` (period 1, `clk_period` 1, IO `0.1`), repoint
`config.mk` `SDC_FILE`, **preserve original `constraint.sdc`**, preserve
historical runs, run a new isolated baseline, re-audit, verify. **No silent
relaxation.** 
- New isolated baseline `orfs_baseline_control_1ns_20261126T133241476241945Z_4600`
  (8 stages rc=0): `report_units time=1ns`, `clock.period=1`, `clock_period.txt=1`,
  `6_final.sdc` period 1, Liberty unchanged, corner unchanged; `verify_run` **PASS**.
- `worst slack max≈0.64`, `min≈0.08` (2-dp `6_finish.rpt`; ≈0.6489/0.0788 pre-round);
  `setup=0 hold=0`. `period_min=0.36 fmax≈2760` (`-include_port_paths`); reg-to-reg
  `0/inf`. Recorded `evidence/timing/timing_audit_1ns.json`. **Not** a guarantee
  in general; timing may not close; would be reported. Target NOT adjusted to
  make reports pass.

## FakeRAM scope and limitations

`fakeram45_64x32` (Nangate45 platform abstract macro) is a **blackbox with
simplified Liberty**: scalar `cell_rise/cell_fall = 0.207`, scalar transition,
single `rising_edge`, setup/hold, `min_period 0.164`, no real memory
bit-cells, no read/write electrical detail, no power, no noise, no geometry
beyond LEF, not a foundry-characterized SRAM. **Not representative** of real
SRAM timing. `interface_timing : true`.

## This design is not a timing-closure benchmark

`sattva_macro_top` is a pass-through wrapper: one macro instance, no top-level
flops, no logic. Timing closure here is **trivial** and **not representative**
of real designs. The macro→output path dominates. Reg-to-reg checks are vacuous.
Documented limitation.

## Signoff scope

OpenROAD-internal routing DRC=0 + 0 DRT-0199 + clean antenna + extracted STA.
**Not** foundry DRC/LVS, **not** full signoff, **not** functional verification.
## Pinned-tool limitation: update_timing (2026-11-27)
- The pinned OpenROAD binary reports no `update_timing` command. Audit schema v2 records this as `SECTION_UNSUPPORTED` and `timing_update = UNKNOWN`. UNKNOWN is never converted to PASS.
- The 1 ns baseline and recovery passed every executable report check (execution, artifacts, freshness, routing, timing reports, coverage, extraction, approval/scope/same-target), but timing qualification is unresolved: collateral timing regression cannot be claimed.
- Recovery verdict therefore remains FAIL on `collateral_regression` in `evidence/verification/clean_1ns_recovery.json`. This is verifier integrity, not a timing failure; no signoff or functional-correctness claim is made.
- Potential resolution: obtain a compatible OpenROAD build with `update_timing`, then rerun baseline and recovery qualification. Out of scope for this milestone.
