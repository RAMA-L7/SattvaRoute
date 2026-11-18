# Agent B — Net and Database Investigation: `zero_` net trace

- **Agent:** Agent B — Net and Database Investigation
- **Task:** T-M1-004, Milestone 1C-R (subagent assignment from orchestrator)
- **Start timestamp:** 2026-11-18T22:20:03.8725257+05:30
- **End timestamp:** 2026-11-18T22:23:22.8988295+05:30
- **Mode:** read-only investigation. No flow runs, no netlist/RTL/macro/SDC/config/PDN edits, no `write_db`. The only file written is this report.

## Initial project state

- Project root `D:\SattvaRoute` maps to WSL `/mnt/d/SattvaRoute`; `wsl -d Ubuntu-24.04` used for OpenROAD/Tcl DB inspection.
- Immutable baseline under investigation: `D:\SattvaRoute\runs\orfs_baseline_20261118T152845Z`.
- The baseline preserved 16 ODB databases under `work\results\asap7\sattva_sram\base\` (1 synth, 5 floorplan, 7 place, 2 CTS). **No `5_1_grt-failed.odb` (or any post-failure ODB) exists** — confirmed by recursive glob for `*grt*` and for all `*.odb` in the run. The global-route stage fails inside `pin_access` before any DB is written.
- `stage 5_1_grt` fails with `[ERROR DRT-0305] Net zero_ of signal type GROUND is not routable by TritonRoute. Move to special nets.`
- OpenROAD binary: `/usr/local/bin/openroad`, version banner `OpenROAD bazel-nostamp` (GUI/GPU disabled). Build is the LF execution mirror `D:\SattvaRoute\tools\OpenROAD-flow-scripts`.

---

## 1. Files inspected

### ODB databases (exact filenames, byte sizes, timestamps UTC)

Directory: `D:\SattvaRoute\runs\orfs_baseline_20261118T152845Z\work\results\asap7\sattva_sram\base\`

| Filename | Size (bytes) | LastWriteTimeUtc |
|---|---:|---|
| `1_synth.odb` | 635134 | 2026-11-18 15:28:56 |
| `2_1_floorplan.odb` | 641488 | 2026-11-18 15:29:03 |
| `2_2_floorplan_macro.odb` | 641550 | 2026-11-18 15:29:07 |
| `2_3_floorplan_tapcell.odb` | 690742 | 2026-11-18 15:29:13 |
| `2_4_floorplan_pdn.odb` | 856666 | 2026-11-18 15:29:17 |
| `2_floorplan.odb` | 856666 | 2026-11-18 15:29:18 |
| `3_1_place_gp_skip_io.odb` | 856666 | 2026-11-18 15:29:25 |
| `3_2_place_iop.odb` | 856858 | 2026-11-18 15:29:29 |
| `3_3_place_gp.odb` | 857904 | 2026-11-18 15:29:36 |
| `3_4_place_resized.odb` | 857904 | 2026-11-18 15:29:42 |
| `3_5_place_dp.odb` | 857904 | 2026-11-18 15:29:49 |
| `3_place.odb` | 857904 | 2026-11-18 15:29:50 |
| `4_1_cts.odb` | 861482 | 2026-11-18 15:30:01 |
| `4_cts.odb` | 861482 | 2026-11-18 15:30:02 |

Detailed net-level inspection was performed on: `1_synth.odb`, `2_1_floorplan.odb`, `2_2_floorplan_macro.odb`, `2_3_floorplan_tapcell.odb`, `2_4_floorplan_pdn.odb`, `2_floorplan.odb`, `3_place.odb`, `4_1_cts.odb`, `4_cts.odb`. A comparative read was also made of a later run's `4_cts.odb` (`runs/orfs_baseline_20261118T163553Z/.../4_cts.odb`).

### Other files

- `runs/orfs_baseline_20261118T152845Z/work/logs/asap7/sattva_sram/base/5_1_grt.log` (verbatim error excerpt below)
- `runs/orfs_baseline_20261118T152845Z/work/logs/asap7/sattva_sram/base/5_1_grt.json`
- `runs/orfs_baseline_20261118T152845Z/evidence/stage_route.log`
- `benchmark/design/sattva_sram/netlist/sattva_ctrl_synth.v`
- `benchmark/design/sattva_sram/rtl/sattva_ctrl.v`
- `benchmark/design/sattva_sram/rtl/sram_x4x4x1_bb.v`
- `benchmark/design/sattva_sram/macro/sram_x4x4x1.lef`
- `benchmark/design/sattva_sram/macro/sram_x4x4x1.lib`
- `benchmark/design/sattva_sram/pdn_sattva.tcl`
- `benchmark/design/sattva_sram/config.mk`
- `benchmark/design/sattva_sram/netlist/yosys_synth.log`

---

## 2. Exact commands executed (abridged to the decisive ones)

Environment / discovery (PowerShell on Windows, WSL for tools):

```powershell
Get-Date -Format o
Get-ChildItem -Recurse -File 'D:\SattvaRoute\runs\orfs_baseline_20261118T152845Z\work\results\asap7\sattva_sram\base' -Filter '*.odb' | Select-Object FullName,Length,LastWriteTimeUtc | Format-Table -AutoSize | Out-String -Width 300
Get-ChildItem -Recurse -File 'D:\SattvaRoute\runs' -Filter '*grt*' -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTimeUtc | Format-Table -AutoSize | Out-String -Width 300
wsl -d Ubuntu-24.04 -- bash -c 'which openroad; openroad -version 2>&1 | head -5'
```

Capability probe (OpenROAD Tcl via heredoc) — verbatim result:

```text
HELLO_FROM_OPENROAD
1
get_nets
```

Interpretation: `ord::get_db_block` exists (1 match); `get_nets` exists; `get_signal_type`, `get_special_nets`, `is_power`, `is_ground` returned **empty** (commands unavailable). Therefore all classification below uses the OpenROAD db/SWIG API (`dbNet` methods), not those convenience commands. `dbNet_setSpecial` global command also reported unavailable (`DBNET_HAS_SET_SPECIAL=0`) — no mutation was attempted in any case.

A first attempt at the detailed Tcl body failed because of my own two Tcl/bash quoting mistakes (`[$nm]` in Tcl is command substitution, not variable interpolation; and nested `[$inst getMaster getName]` is wrong arity). Those attempts produced errors, were corrected, and are marked as tooling errors below — not design findings.

Final inspection method: a PowerShell here-string Tcl body piped into a fresh `openroad -no_init` process per DB (fresh process required because `read_db` refuses a second DB in one process: `[ERROR ORD-0047] You can't load a new db file as the db is already populated`).

Decisive Tcl body (path substituted per DB):

```tcl
set dbpath "<DBPATH>"
puts "===BEGIN DB $dbpath==="
if {[catch {read_db $dbpath} err]} { puts "READ_DB_ERROR: $err"; puts "===END DB==="; exit }
set block [ord::get_db_block]
puts "BLOCK_NAME=[$block getName] TOTAL_NETS=[llength [$block getNets]]"
set allnets [$block getNets]
foreach net $allnets {
  set nm [$net getName]
  set low [string tolower $nm]
  set hit 0
  foreach key {zero gnd vss vdd} { if {[string first $key $low] >= 0} { set hit 1 } }
  if {!$hit} continue
  puts "NET $nm"
  puts "  sigType=[$net getSigType] isSpecial=[$net isSpecial]"
  puts "  bterms=[llength [$net getBTerms]] iterms=[llength [$net getITerms]] swires=[llength [$net getSWires]] wire=[$net getWire]"
  foreach bt [$net getBTerms] { puts "  BTERM [$bt getName]" }
  set cnt 0
  foreach it [$net getITerms] {
     set inst [$it getInst]; set instname "NULL"; if {$inst ne "NULL"} { set instname [$inst getName] }
     set mt [$it getMTerm]; set mtname "NULL"; if {$mt ne "NULL"} { set mtname [$mt getName] }
     puts "  ITERM inst=$instname pin=$mtname"
     incr cnt
     if {$cnt >= 20} { puts "  ...(ITerm output truncated at 20)"; break }
  }
  foreach it [$net getITerms] {
     set inst [$it getInst]
     if {$inst eq "NULL"} continue
     set master [$inst getMaster]
     if {$master eq "NULL"} continue
     set mname [$master getName]
     if {[string first "sram" [string tolower $mname]] >= 0} {
        set mt [$it getMTerm]; set mtname "NULL"; if {$mt ne "NULL"} { set mtname [$mt getName] }
        puts "  MACRO_CONN inst=[$inst getName] master=$mname pin=$mtname"
     }
  }
}
puts "===END DB==="
exit
```

Shape/width probe on `4_cts.odb` (separate run):

```tcl
read_db /mnt/d/SattvaRoute/runs/orfs_baseline_20261118T152845Z/work/results/asap7/sattva_sram/base/4_cts.odb
set block [ord::get_db_block]
foreach net [$block getNets] {
  if {[$net getName] ne "zero_" && [$net getName] ne "VSS"} continue
  puts "NET [$net getName] sigType=[$net getSigType] isSpecial=[$net isSpecial]"
  set sw [$net getSWires]
  puts "  swires=[llength $sw]"
  foreach s $sw {
    set boxes [$s getWires]
    puts "  swire boxes=[llength $boxes]"
    set i 0
    foreach b $boxes {
      puts "    box[$i] layer=[$b getTechLayer] dx=[$b getDX] dy=[$b getDY] xMin=[$b xMin] yMin=[$b yMin] xMax=[$b xMax] yMax=[$b yMax]"
      incr i
      if {$i >= 3} { puts "    ...(boxes truncated at 3)"; break }
    }
  }
  puts "  wire=[$net getWire]"
}
exit
```

---

## 3. Verbatim output excerpts

### 3.1 The DRT-0305 error and its input DB

`5_1_grt.log`, lines 12–17, 25–26 (verbatim):

```text
read_liberty /mnt/d/SattvaRoute/benchmark/design/sattva_sram/macro/sram_x4x4x1.lib
read_db /mnt/d/SattvaRoute/runs/orfs_baseline_20261118T152845Z/work/results/asap7/sattva_sram/base/4_cts.odb
read_sdc /mnt/d/SattvaRoute/runs/orfs_baseline_20261118T152845Z/work/results/asap7/sattva_sram/base/4_cts.sdc
source /mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow/platforms/asap7/setRC.tcl
pin_access
[INFO DRT-0149] Reading tech and libs.
...
[INFO DRT-0150] Reading design.
[ERROR DRT-0305] Net zero_ of signal type GROUND is not routable by TritonRoute. Move to special nets.
```

This proves global routing's input is exactly `4_cts.odb` — the same file inspected below. `5_1_grt.json`: `globalroute__flow__errors__count: 1`.

### 3.2 Synthesis DB `1_synth.odb` (verbatim)

```text
===BEGIN DB /mnt/d/SattvaRoute/runs/orfs_baseline_20261118T152845Z/work/results/asap7/sattva_sram/base/1_synth.odb===
BLOCK_NAME=sattva_ctrl TOTAL_NETS=63
NET zero_
  sigType=GROUND isSpecial=0
  bterms=0 iterms=6 swires=0 wire=NULL
  ITERM inst=u_sram pin=sdel[3]
  ITERM inst=u_sram pin=sdel[2]
  ITERM inst=u_sram pin=sdel[1]
  ITERM inst=u_sram pin=sdel[0]
  ITERM inst=u_sram pin=A[3]
  ITERM inst=u_sram pin=A[2]
  MACRO_CONN inst=u_sram master=sram_x4x4x1 pin=sdel[3]
  MACRO_CONN inst=u_sram master=sram_x4x4x1 pin=sdel[2]
  MACRO_CONN inst=u_sram master=sram_x4x4x1 pin=sdel[1]
  MACRO_CONN inst=u_sram master=sram_x4x4x1 pin=sdel[0]
  MACRO_CONN inst=u_sram master=sram_x4x4x1 pin=A[3]
  MACRO_CONN inst=u_sram master=sram_x4x4x1 pin=A[2]
===END DB===
```

### 3.3 All net names per stage (verbatim excerpts)

`1_synth.odb` / `2_1_floorplan.odb` / `2_2_floorplan_macro.odb` / `2_3_floorplan_tapcell.odb` — 63 nets, ending:

```text
... | we_n | zero_
```

`2_4_floorplan_pdn.odb` and `2_floorplan.odb` — 65 nets, ending:

```text
... | we_n | zero_ | VDD | VSS
```

`3_place.odb` — 68 nets, ending:

```text
... | net1 | we_n | zero_ | VDD | VSS | rst_n | done | error
```

`4_1_cts.odb` / `4_cts.odb` — 75 nets, ending:

```text
... | VDD | VSS | rst_n | done | error | clk_regs | clknet_0_clk | clknet_1_0__leaf_clk | clknet_0_clk_regs | clknet_1_0__leaf_clk_regs | clknet_1_1__leaf_clk_regs | delaynet_0_clk
```

No `zero`, `ZERO`, `GND`, `gnd`, or standalone `vss` net name appears at any stage. The only case variants of the ground-like names are the net `zero_`, and the nets `VSS`/`VDD`.

### 3.4 PDN stage DB `2_4_floorplan_pdn.odb` (verbatim excerpts)

```text
BLOCK_NAME=sattva_ctrl TOTAL_NETS=65
NET zero_
  sigType=GROUND isSpecial=0
  bterms=0 iterms=6 swires=0 wire=NULL
  ...  (same 6 macro ITerms as synth: sdel[3:0], A[3], A[2]; same 6 MACRO_CONN lines)
NET VDD
  sigType=POWER isSpecial=1
  bterms=1 iterms=283 swires=1 wire=NULL
  BTERM VDD
  ITERM inst=u_sram pin=vdd
  ...
  MACRO_CONN inst=u_sram master=sram_x4x4x1 pin=vdd
NET VSS
  sigType=GROUND isSpecial=1
  bterms=1 iterms=283 swires=1 wire=NULL
  BTERM VSS
  ITERM inst=u_sram pin=vss
  ...
  MACRO_CONN inst=u_sram master=sram_x4x4x1 pin=vss
```

The same three records are byte-identical in `3_place.odb` and `4_cts.odb`.

### 3.5 CTS DB `4_cts.odb` — all POWER/GROUND nets (verbatim)

```text
PG NET zero_ sigType=GROUND isSpecial=0 iterms=6 bterms=0 swires=0
PG NET VDD sigType=POWER isSpecial=1 iterms=283 bterms=1 swires=1
PG NET VSS sigType=GROUND isSpecial=1 iterms=283 bterms=1 swires=1
TOTAL_NETS=75
```

Identical output was produced from later run `orfs_baseline_20261118T163553Z/.../4_cts.odb`, i.e. the condition is reproducible, not unique to the baseline run.

### 3.6 Shapes / widths (verbatim)

```text
NET zero_ sigType=GROUND isSpecial=0
  swires=0
  wire=NULL
NET VSS sigType=GROUND isSpecial=1
  swires=1
  swire boxes=1187
  box[0] layer=_c062de7fe0710000_p_odb__dbTechLayer dx=27810 dy=288 xMin=1080 yMin=28449 xMax=28890 yMax=28737
  box[1] layer=_c062de7fe0710000_p_odb__dbTechLayer dx=27810 dy=288 xMin=1080 yMin=23049 xMax=28890 yMax=23337
  box[2] layer=_c062de7fe0710000_p_odb__dbTechLayer dx=27810 dy=288 xMin=1080 yMin=17649 xMax=28890 yMax=17937
DBNET_HAS_SET_SPECIAL=0
```

(`getWidth`/`getShape` are not methods on `dbSBox` in this build — the method list exposed `getDX`, `getDY`, `getTechLayer`, `xMin`…; width was obtained as `dx`/`dy` in DBU. `zero_` has no shape at all, so there is no width attribute to report; the prior claim of "zero-width" is true only in the sense that the net has **no routing geometry whatsoever**.)

### 3.7 Netlist, RTL, macro views, PDN (verbatim excerpts)

`sattva_ctrl_synth.v` lines 356–365:

```verilog
  sram_x4x4x1 u_sram (
    .A({ 2'h0, \A[1] , \A[0]  }),
    .D({ \D[3] , \D[2] , \D[1] , \D[0]  }),
    .Q({ \Q[3] , \Q[2] , \Q[1] , \Q[0]  }),
    .ce_n(ce_n),
    .clk(clk),
    .oe_n(oe_n),
    .sdel(4'h0),
    .we_n(we_n)
  );
```

There is **no** net literally declared `zero_` in the Verilog (`grep` for `zero_|\bvss\b|\bVSS\b|\bVDD\b|\bvdd\b` returned "No matches found"). The six constant-zero bits (`2'h0` for `A[3:2]`, `4'h0` for `sdel`) become the OpenROAD-internal net `zero_` at netlist read/synthesis; this is confirmed by the DB connectivity (exactly those six pins).

`rtl/sattva_ctrl.v` lines 14, 48, 50:

```verilog
// - sdel tied to 0 (delay-select unused in benchmark; documented in macro doc).
    assign A    = (state == S_WR || state == S_RD || state == S_CAP) ? {2'b00, addr} : 4'b0000;
    assign sdel = 4'b0000;   // documented tie-off (macro doc)
```

`macro/sram_x4x4x1.lef` lines 12–27, 60–67:

```text
  PIN vdd
    DIRECTION INOUT ;
    USE POWER ;
    PORT
      LAYER M3 ;
        RECT 0.117000 11.151500 0.135000 11.421500 ;
  END vdd
  PIN vss
    DIRECTION INOUT ;
    USE GROUND ;
    PORT
      LAYER M3 ;
        RECT 0.153000 11.151500 0.171000 11.501500 ;
  END vss
...
  PIN sdel[0]
    DIRECTION INPUT ;
    USE SIGNAL ;
    PORT
      LAYER M4 ;
```

`macro/sram_x4x4x1.lib` lines 86–95:

```text
    pg_pin (vdd) {
      direction : inout;
      pg_type : primary_power;
      voltage_name : "VDD";
    }
    pg_pin (vss) {
      direction : inout;
      pg_type : primary_ground;
      voltage_name : "VSS";
    }
```

`rtl/sram_x4x4x1_bb.v` lines 3–4:

```verilog
// Supply pins vdd/vss are omitted per ORFS convention (see fakeram7_*.v);
// they exist in LEF (M3, POWER/GROUND) and are handled by PDN.
```

`pdn_sattva.tcl` lines 24–35 — the complete set of PDN global connections:

```tcl
add_global_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDD$} -power
add_global_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDDPE$}
add_global_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDDCE$}
add_global_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^vdd$} -power
add_global_connection -net {VSS} -inst_pattern {.*} -pin_pattern {^VSS$} -ground
add_global_connection -net {VSS} -inst_pattern {.*} -pin_pattern {^VSSE$}
add_global_connection -net {VSS} -inst_pattern {.*} -pin_pattern {^vss$} -ground
global_connect
set_voltage_domain -name {CORE} -power {VDD} -ground {VSS}
```

`config.mk` line 65: `export PDN_TCL = $(DESIGN_DIR)/pdn_sattva.tcl`.

---

## 4. Stage-by-stage trace table

| Stage / DB | Net present? | sigType | `isSpecial` | BTerms / ITerms / SWires / wire | Macro connections | PDN membership |
|---|---|---|---|---|---|---|
| Synth — `1_synth.odb` | **YES** (earliest preserved) | `GROUND` | `0` (NO) | 0 / 6 / 0 / NULL | `u_sram` (`sram_x4x4x1`): `sdel[3]`,`sdel[2]`,`sdel[1]`,`sdel[0]`,`A[3]`,`A[2]` | No — `VDD`/`VSS` nets do not exist yet at this stage |
| Floorplan pre-PDN — `2_1_floorplan.odb`, `2_2_floorplan_macro.odb`, `2_3_floorplan_tapcell.odb` | YES (63 nets) | `GROUND` | `0` | 0 / 6 / 0 / NULL | Same 6 macro ITerms (detailed ITerm dump for these sub-stages BLOCKED by Tcl arity error; net record verbatim confirmed) | No |
| Floorplan post-PDN — `2_4_floorplan_pdn.odb`, `2_floorplan.odb` | YES (65 nets) | `GROUND` | `0` | 0 / 6 / 0 / NULL | Same 6 macro ITerms | **No.** PDN creates separate `VDD` (POWER, special=1, 283 ITerms, 1 bterm, 1 swire) and `VSS` (GROUND, special=1, 283 ITerms, 1 bterm, 1 swire), with macro pins `vdd`/`vss` respectively |
| Place — `3_place.odb` | YES (68 nets) | `GROUND` | `0` | 0 / 6 / 0 / NULL | Same 6 macro ITerms | No — unchanged |
| CTS — `4_1_cts.odb`, `4_cts.odb` | YES (75 nets) | `GROUND` | `0` | 0 / 6 / 0 / NULL | Same 6 macro ITerms | No — unchanged |
| **Global route (failure)** — no `5_1_grt-failed.odb` exists; failure occurred reading `4_cts.odb` | YES — the error names it | `GROUND` (per DRT-0305) | `0` in the input DB | 0 / 6 / 0 / NULL in the input DB | Same 6 macro ITerms in the input DB | No — see `5_1_grt.log` |

Net count trajectory: 63 (synth, pre-PDN floorplan) → 65 (after PDN adds `VDD`,`VSS`) → 68 (place adds `net1`/`net2`/`net3`) → 75 (CTS adds clock nets). `zero_` is present from the very first preserved DB and its own record never changes.

---

## 5. Explicit answers

**Q1. Is the `zero_` net in CTS the same net that global routing rejects?**
**YES.** `5_1_grt.log` line 13 shows global routing loads exactly `4_cts.odb`, the file inspected. That DB contains exactly one net named `zero_`, with `sigType=GROUND`, `isSpecial=0`, 6 ITerms, 0 BTerms, 0 SWires, `wire=NULL`. There is no `zero` alias or any other net with a conflicting name/classification. The DRT-0305 message (`Net zero_ of signal type GROUND`) matches that single net exactly. It is the same net object, unchanged since synthesis.

**Q2. What is its ground classification and connectivity?**
`dbNet::getSigType` returns `GROUND`; `isSpecial` returns `0`. It has **0 BTerms**, **6 ITerms**, all on the single macro instance `u_sram` of master `sram_x4x4x1`, pins `sdel[3]`, `sdel[2]`, `sdel[1]`, `sdel[0]`, `A[3]`, `A[2]`. It has **no routing geometry at all** (`swires=0`, `getWire=NULL`), i.e. "zero-width" only in the sense of having no shapes/physical width. The macro's actual ground pin is `vss` (LEF `USE GROUND`, LIB `pg_pin` `primary_ground`, `voltage_name "VSS"`) and is **not** connected to `zero_`; `vss` is on net `VSS`. `sdel` and `A` are LEF `USE SIGNAL` / `DIRECTION INPUT` pins. So `zero_` is a **logical constant-zero tie net mis-tagged as GROUND**, not a supply net.

**Q3. Are prior claims verified?**
- *"`zero_` is an internal Ground net created during CTS"* — **PARTIALLY FALSE / REFUTED on origin.** It is a GROUND-typed internal net, but it is present already in `1_synth.odb`, the earliest preserved DB, and in the synthesized netlist as six constant-zero literal connections. It is **not created during CTS**; CTS only adds unrelated clock nets.
- *"zero-width"* — **SUBSTANTIATED with qualification:** no SWires and no wire (no shapes at all); no literal width field exists because there is no geometry.
- *"not designated special"* — **CONFIRMED:** `isSpecial=0` at every stage, while the real supply nets `VDD`/`VSS` are `isSpecial=1`. This is precisely why `pin_access` rejects it.

**Q4. Aliases / multiple ground representations?**
Three PG-relevant nets coexist at floorplan/place/CTS:
1. `VSS` — GROUND, special, BTerm `VSS`, 283 ITerms (incl. macro `u_sram/vss`), 1 SWire / 1187 shapes; this is the PDN ground.
2. `VDD` — POWER, special, BTerm `VDD`, 283 ITerms (incl. macro `u_sram/vdd`), 1 SWire; PDN power.
3. `zero_` — GROUND, **non-special**, no BTerm, 6 ITerms to macro `sdel`/`A` signal pins, no shapes; **not in the PDN**.

No `zero`, `ZERO`, `GND`, `gnd`, or separate `vss` net name exists. The lowercase `vdd`/`vss` names are **pin names** on the macro, connected to nets `VDD`/`VSS` by `pdn_sattva.tcl` global connections — not separate nets. There is no tie/connection between `zero_` and `VSS` in any DB; they are entirely separate nets.

**Q5. WHEN does `zero_` first appear?**
At the earliest available database, `1_synth.odb` (2026-11-18 15:28:56 UTC). Its origin is the constant-zero tie-offs in the RTL/ synthesized netlist (`2'h0` on macro `A[3:2]`, `4'h0` on `sdel`), materialized by the netlist reader as a GROUND net named `zero_`. It persists unchanged through floorplan, PDN insertion, placement, CTS, and into global routing.

**Q6. `5_1_grt-failed.odb` inspection — STATUS: BLOCKED / NOT EVALUATED.**
No such file exists in the baseline or in any run under `D:\SattvaRoute\runs`. Stage 5_1_grt aborts inside `pin_access` before emitting any ODB. The failure-moment database is therefore `4_cts.odb`, which was inspected in full (see §3.5).

**Q7. Other runs.** One alternate run (`orfs_baseline_20261118T163553Z`) was inspected at `4_cts.odb` and shows the identical three PG nets and identical `zero_` record — condition reproduced. Remaining runs NOT EVALUATED.

---

## 6. Handoff to orchestrator

- **Root-cause direction (database-backed):** DRT-0305 is not a CTS-created defect. A synthesized constant-zero tie net (`zero_`, GROUND, non-special, no shapes, connected only to `sram_x4x4x1` signal pins `sdel[3:0]` and `A[3:2]`) reaches TritonRoute as a routable-signal-class GROUND net. The real PDN ground `VSS` is special and routed; `zero_` is not, and is rejected.
- **Design-level source:** RTL tie-offs `assign sdel = 4'b0000;` and upper address bits `{2'b00, addr}` / `4'b0000` become a Yosys constant net that OpenROAD imports as GROUND-class `zero_`. Any fix should address the net's *logical* naming/classification (e.g., keep it a regular signal/tie net rather than GROUND, or formally designate it special/tied), not the PDN, which is correctly configured for `VDD`/`VSS` only.
- **Do not repeat the seven completed D-013 static checks** — this report adds no challenge to them.
- **Remaining uncertainty / NOT EVALUATED:**
  - No `5_1_grt-failed.odb` exists, so there is no post-failure DB snapshot; the failure-moment state is inferred from the stage log plus its documented input `4_cts.odb` (both quoted verbatim).
  - The exact OpenROAD internal mechanism that renames the Verilog constant to `zero_` and assigns `GROUND` sigType was not traced through source code (netlist + DB correlation only).
  - `get_signal_type`, `get_special_nets`, `is_power`, `is_ground`, and a public "set special" command are unavailable in this OpenROAD build; classification used `dbNet::getSigType`/`isSpecial` instead. No mutation was attempted.
  - Detailed per-pin ITerm dumps for the three pre-PDN floorplan sub-stage DBs were not captured (Tcl arity error); their net records (`GROUND`, `isSpecial=0`, 0/6/0/NULL) were captured verbatim.
  - Other non-baseline runs were not inspected except one comparative `4_cts.odb`.
- **Constraint compliance:** No `write_db`, no flow runs, no edits to any project/design/evidence/state file. Only this report was created.
