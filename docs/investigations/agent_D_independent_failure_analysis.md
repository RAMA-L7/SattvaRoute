# Agent D — Independent Failure Analysis (T-M1-004)

## 0. Metadata and initial state

| Item | Value |
|---|---|
| Agent | **Agent D — Independent Failure Analysis** (subagent) |
| Task | T-M1-004, Milestone 1C-R; challenge the DRT-0305 root-cause hypothesis |
| Start timestamp | **2026-11-18T22:20:25+05:30** |
| End timestamp | **2026-11-18T22:26:02+05:30** |
| Mode | Read-only. No flow runs, no edits to scripts/configs/DBs/RTL/netlist/macro/SDC/logs/state files. Only this report was written. OpenROAD was used solely for in-memory, read-only DB introspection and command-existence queries (`-exit -no_init`, no `write_db`). |
| Hypothesis under test | “DRT-0305 occurs because internal Ground net `zero_` is not designated as a special net; fix = `set_special_nets [list zero_]` in `global_route.tcl`.” |

**Initial project state (verified at session start):**
- `D:\SattvaRoute\tools\OpenROAD-flow-scripts\flow\scripts\global_route.tcl` (LF execution mirror) and `D:\tools\OpenROAD-flow-scripts\flow\scripts\global_route.tcl` (read-only global clone) are **byte-identical** (`diff` exit 0), both 6110 bytes, and **both contain no `set_special_nets`**. The D-013 edit is not present anywhere at session start.
- `D:\SattvaRoute\reports\` was empty.
- Immutable baseline `runs/orfs_baseline_20261118T152845Z/` is intact; its route evidence log is 59 lines and contains DRT-0305 at line 39.
- Git status showed pre-existing modifications only (`PROJECT_STATE.md`, `coordination/*`, `docs/decisions/DECISIONS.md`, logs, untracked `benchmark/`, `runs/`, `tools/`, etc.); Agent D did not touch any of them.
- No run in `runs/` contains any routed DB (`find … -name '5_*.odb'` → no output). Global routing has never completed in any preserved run.

---

## 1. Files inspected

**Evidence/logs**
- `runs/orfs_baseline_20261118T152845Z/evidence/stage_route.log`
- `runs/orfs_baseline_20261118T152845Z/work/logs/asap7/sattva_sram/base/5_1_grt.log`, `3_4_place_resized.log`, `1_synth.log`, `2_1_floorplan.log`, `2_2_floorplan_macro.log`, `*.json`
- `runs/orfs_baseline_20261118T163746Z/evidence/stage_floorplan.log`
- All `runs/orfs_baseline_*/evidence/stage_route.log` and `work/logs/.../5_1_grt.log` for the DRT-0305 recurrence check
- `runs/orfs_baseline_d013_20261118T160213Z/` (empty evidence/ and work/ dirs)

**Design files**
- `benchmark/design/sattva_sram/config.mk`, `pdn_sattva.tcl`, `macro_placement.tcl`
- `benchmark/design/sattva_sram/rtl/sattva_ctrl.v`, `rtl/sram_x4x4x1_bb.v`
- `benchmark/design/sattva_sram/netlist/sattva_ctrl_synth.v`
- `benchmark/design/sattva_sram/macro/sram_x4x4x1.lef`, `macro/sram_x4x4x1.lib`
- `runs/.../work/results/asap7/sattva_sram/base/1_2_yosys.v`

**Flow scripts / DBs**
- `tools/OpenROAD-flow-scripts/flow/scripts/global_route.tcl`, `synth.tcl`, `synth_preamble.tcl`
- `tools/OpenROAD-flow-scripts/flow/platforms/asap7/config.mk`
- ODB files: `1_synth.odb`, `2_4_floorplan_pdn.odb`, `4_1_cts.odb`, `4_cts.odb`

**Existing investigation narrative (read for comparison only, not used as evidence)**
- `docs/DRT-0305_fix_proposal.md`
- `corouting/MILESTONE_1C_ROUTING_INVESTIGATION.md`
- `<temp>/opencode/T-M1-003_Execution_Report.md`
- `PROJECT_STATE.md`

---

## 2. Commands executed (abridged to exact, reproducible forms)

```
Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
git status --short
Get-ChildItem -Force D:\SattvaRoute\runs
wsl -d Ubuntu-24.04 -- bash -c 'diff /mnt/d/tools/.../global_route.tcl /mnt/d/SattvaRoute/tools/.../global_route.tcl'
wsl -d Ubuntu-24.04 -- bash -c 'cat /mnt/d/SattvaRoute/tools/.../global_route.tcl'
wsl -d Ubuntu-24.04 -- bash -c 'find /mnt/d/SattvaRoute/runs -iname "*route*log*" -o -iname "*grt*" | sort'
wsl -d Ubuntu-24.04 -- bash -c 'find /mnt/d/SattvaRoute/runs -type f -name "5_*.odb" | sort'
wsl -d Ubuntu-24.04 -- bash -c 'sha256sum .../4_1_cts.odb .../4_cts.odb'
wsl -d Ubuntu-24.04 -- bash -c 'grep -n -e h0 -e zero -e one .../1_2_yosys.v'
wsl -d Ubuntu-24.04 -- bash -c 'grep -rn -e zero -e const -e tie .../synth.tcl .../synth_preamble.tcl'
wsl -d Ubuntu-24.04 -- bash -c 'grep -n -e SYNTH_NETLIST_FILES -e exit .../synth_preamble.tcl'
wsl -d Ubuntu-24.04 -- bash -c 'grep -n -e sdel -e 2.h0 -e 4.h0 .../rtl/*.v'
wsl -d Ubuntu-24.04 -- bash -c 'grep -n -e vdd -e vss -e pg_pin .../sram_x4x4x1.lib'
```
Read-only OpenROAD introspection (temp Tcl scripts under `<temp>/opencode/`, no writes to project):

```
AGENTD_DB=<odb> openroad -exit -no_init agentD_inspect_db.tcl     # net sigType/isSpecial/connectivity
openroad -exit -no_init agentD_cmd_query.tcl                     # info commands *special*, set_special_nets
AGENTD_DB=<odb> openroad -exit -no_init agentD_cmd_query2.tcl    # read_db then invoke set_special_nets / assign_ground_net
AGENTD_DB=<odb> openroad -exit -no_init agentD_cmd_query3.tcl    # report_floating_nets
AGENTD_DB=<odb> openroad -exit -no_init agentD_floating.tcl      # driverless-net enumeration
```
Dedicated `grep`/`read` tools were used on Windows paths for all text files.

---

## 3. Verbatim evidence excerpts (paths + line numbers)

### 3.1 The failure is in `pin_access`, at design-read time — before routing geometry

`runs/orfs_baseline_20261118T152845Z/work/logs/asap7/sattva_sram/base/5_1_grt.log`:
```
13: read_db /mnt/d/SattvaRoute/runs/orfs_baseline_20261118T152845Z/work/results/asap7/sattva_sram/base/4_cts.odb
16: pin_access
17: [INFO DRT-0149] Reading tech and libs.
25: [INFO DRT-0150] Reading design.
26: [ERROR DRT-0305] Net zero_ of signal type GROUND is not routable by TritonRoute. Move to special nets.
27: DRT-0305
28:     while executing
29: "drt::pin_access_cmd $db_process_node  $via_access_layer $verbose $min_access_points  $via_in_pin_bottom_layer $via_in_pin_top_layer"
30:     (procedure "pin_access" line 65)
...
42:     (file "/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow/scripts/global_route.tcl" line 188)
```
`evidence/stage_route.log` lines 39–40 repeat the same error; line 1 confirms the runner uses `/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow` (the **mirror**), not `/mnt/d/tools/...`.

### 3.2 What `zero_` actually is — read-only ODB introspection

Command: `AGENTD_DB=.../1_synth.odb openroad -exit -no_init agentD_inspect_db.tcl`
```
AGENTD BLOCK: sattva_ctrl  NETS=63
AGENTD NET name=zero_ sigType=GROUND isSpecial=0 bterms=0 iterms=6 segs=0
AGENTD   ITERM inst=u_sram mterm=sdel[3]
AGENTD   ITERM inst=u_sram mterm=sdel[2]
AGENTD   ITERM inst=u_sram mterm=sdel[1]
AGENTD   ITERM inst=u_sram mterm=sdel[0]
AGENTD   ITERM inst=u_sram mterm=A[3]
AGENTD   ITERM inst=u_sram mterm=A[2]
```
Same result for `2_4_floorplan_pdn.odb` and `4_cts.odb` (`NETS=65` and `NETS=75` respectively), i.e. **classification never changes between stages**. In `4_cts.odb` / `2_4_floorplan_pdn.odb`:
```
AGENTD NET name=VDD sigType=POWER isSpecial=1 bterms=1 iterms=283 segs=0
AGENTD   BTERM VDD
AGENTD   ITERM inst=u_sram mterm=vdd        <-- macro PG pin correctly on VDD
...
AGENTD NET name=VSS sigType=GROUND isSpecial=1 bterms=1 iterms=283 segs=0
AGENTD   BTERM VSS
AGENTD   ITERM inst=u_sram mterm=vss        <-- macro PG pin correctly on VSS
...
```
Driverless-net enumeration on `4_cts.odb`:
```
AGENTD4 DRIVERLESS net=zero_ sigType=GROUND iterms=6 bterms=0 sinks=6
```
`report_floating_nets` on `4_cts.odb`:
```
[WARNING RSZ-0020] found 1 floating nets.
```
which matches `3_4_place_resized.log` lines 31–32:
```
31: Floating nets:
32: [WARNING RSZ-0020] found 1 floating nets.
```
No alternative driverless net exists — the single floating net is `zero_`.

### 3.3 Source of `zero_`: Verilog tie-off constants, not PDN

`benchmark/design/sattva_sram/netlist/sattva_ctrl_synth.v`:
```
357:     .A({ 2'h0, \A[1] , \A[0]  }),
363:     .sdel(4'h0),
```
`rtl/sattva_ctrl.v`:
```
14: // - sdel tied to 0 (delay-select unused in benchmark; documented in macro doc).
50:     assign sdel = 4'b0000;   // documented tie-off (macro doc)
103:        .sdel  (sdel),
```
`grep -n -e h0 .../1_2_yosys.v` (the DB input to stage 1) → only lines 357 and 363, i.e. the constants survive verbatim; there is no `zero_` string in the netlist text (the name is created by OpenROAD's Verilog reader for the constant-0 tie).

### 3.4 LEF/LIB prove those six pins are SIGNAL, and PG pins are separate and correct

`macro/sram_x4x4x1.lef`:
```
12:   PIN vdd
14:     USE POWER ;
16:       LAYER M3 ;
20:   PIN vss
22:     USE GROUND ;
24:       LAYER M3 ;
60:   PIN sdel[0]
61:     DIRECTION INPUT ;
62:     USE SIGNAL ;
64:       LAYER M4 ;
... (sdel[1..3] identical: DIRECTION INPUT / USE SIGNAL / M4)
108:   PIN A[2]       ... 109: DIRECTION INPUT ; 110: USE SIGNAL ; 112: LAYER M4 ;
116:   PIN A[3]       ... 117: DIRECTION INPUT ; 118: USE SIGNAL ; 120: LAYER M4 ;
```
`macro/sram_x4x4x1.lib`:
```
86:     pg_pin (vdd) {
88:       pg_type : primary_power;
91:     pg_pin (vss) {
93:       pg_type : primary_ground;
```

### 3.5 PDN is intact and explicitly handles lowercase macro PG pins

`pdn_sattva.tcl` (current, clean):
```
24: add_global_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDD$} -power
27: add_global_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^vdd$} -power
28: add_global_connection -net {VSS} -inst_pattern {.*} -pin_pattern {^VSS$} -ground
30: add_global_connection -net {VSS} -inst_pattern {.*} -pin_pattern {^vss$} -ground
31: global_connect
35: set_voltage_domain -name {CORE} -power {VDD} -ground {VSS}
```
ODB evidence (§3.2) confirms `u_sram.vdd`∈VDD and `u_sram.vss`∈VSS, `isSpecial=1` for both.

### 3.6 The proposed fix command does not exist in this OpenROAD build

`openroad -exit -no_init agentD_cmd_query.tcl` (before and after `read_db`):
```
AGENTD special_cmds:
AGENTD set_special_nets_exists: 0
AGENTD2 after_read set_special_nets=0
AGENTD2 all_special=
AGENTD2 net_cmds=set_nets_to_route report_victim_nets report_net assign_power_net ... assign_ground_net ... report_floating_nets ...
AGENTD2 invoke_set_special_nets rc=1 msg=invalid command name "set_special_nets"
AGENTD2 invoke_assign_ground_net rc=1 msg=ODB-0332
```
So `set_special_nets [list zero_]` would abort with a Tcl “invalid command name” error before TritonRoute ever sees it. (The related `assign_ground_net zero_` is present but rejected here with `ODB-0332`; root cause of that rejection NOT EVALUATED.)

### 3.7 Upstream cause: ORFS synthesis (incl. tie-cell mapping) is bypassed

`config.mk`:
```
9: # Netlist     : pre-synthesized in Phase A (task T-M1-001). SYNTH_NETLIST_FILES
10:#               short-circuits yosys inside ORFS (synth_preamble.tcl), while
35: export SYNTH_NETLIST_FILES = $(DESIGN_DIR)/netlist/sattva_ctrl_synth.v
65: export PDN_TCL = $(DESIGN_DIR)/pdn_sattva.tcl
```
`synth_preamble.tcl`:
```
17: if { [env_var_exists_and_non_empty SYNTH_NETLIST_FILES] } {
19:     log_cmd exec cp $::env(SYNTH_NETLIST_FILES) $::env(RESULTS_DIR)/1_2_yosys.v
34:   exit
35: }
```
`synth.tcl` — the step that would normally replace constant drivers with tie cells is skipped by that `exit`:
```
301: # Technology mapping of constant hi- and/or lo-drivers
302: hilomap -singleton \
303:   -hicell {*}$::env(TIEHI_CELL_AND_PORT) \
304:   -locell {*}$::env(TIELO_CELL_AND_PORT)
```
`platforms/asap7/config.mk`:
```
129: export TIELO_CELL_AND_PORT     ?= TIELOx1_ASAP7_75t_$(PRIMARY_VT_TAG) L
```
and the ASAP7 LEF defines `TIELOx1_ASAP7_75t_L` (`CLASS CORE TIELOW`, LEF line 18037–18038). The corresponding Yosys stage log confirms the plain copy:
```
1_1_yosys_canonicalize.log: exec cp .../sattva_ctrl_synth.v .../1_2_yosys.v
```

### 3.8 No stage warning anticipates the error; DBs are consistent

- `grep` over all baseline stage logs for `warn|special|unconnect|zero_|net type` produced only ODB-1220 LEF-grid rounding warnings, EST-0027, MPL-0074, RSZ-0020 (floating net), and DRT-0305 itself. **No warning about special nets, power nets, or net-type changes between stages.**
- `sha256sum` of `4_1_cts.odb` and `4_cts.odb` are identical: `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1…` for both; global routing reads `4_cts.odb` (log line 13), matching `load_design 4_cts.odb 4_cts.sdc` in `global_route.tcl`.

### 3.9 D-013 attempt evidence gap and an alternative failed edit

- `runs/orfs_baseline_d013_20261118T160213Z/evidence/` and `/work/` are **empty** — no preserved proof of the claimed D-013 execution.
- `runs/orfs_baseline_20261118T163746Z/evidence/stage_floorplan.log`:
```
164: [ERROR STA-0562] add_global_connection -net_type is not a known keyword or flag.
176: "add_global_connection -net {zero_} -net_type special -ground"
177:     (file "/mnt/d/SattvaRoute/benchmark/design/sattva_sram/pdn_sattva.tcl" line 32)
```
A different attempted PDN-side “special net” edit also failed (unsupported `-net_type` keyword), and the current `pdn_sattva.tcl` no longer contains it.

### 3.10 Existing narrative claims that conflict with measured reality

`<temp>/opencode/T-M1-003_Execution_Report.md`:
```
11:   - ✅ `set_special_nets` command valid in ORFS (error message "Move to special nets" confirms)
41: - **Key finding**: `set_special_nets` command is valid per ORFS (error message confirms) but ORFS execution model prevents the command from taking effect on TritonRoute routing
112: - **`set_special_nets` command**: Valid per ORFS error message but ORFS execution model prevents taking effect...
```
The DRT-0305 diagnostic text is not evidence of a Tcl command's existence; §3.6 directly disproves the claim.

`docs/DRT-0305_fix_proposal.md` lines 10–12 call `zero_` “an internal OpenROAD Ground net created during the CTS stage” and “a zero-width Ground net”. §3.2/§3.3 disprove both: it exists already in `1_synth.odb`, it is a constant tie net with six macro **signal** sinks, and its classification is unchanged by CTS.

---

## 4. Independent conclusions on the 7 challenges

**C1 — Should `zero_` be routed by TritonRoute at all; what is it?**
**Verdict: FAIL (hypothesis description is wrong).** `zero_` is the OpenROAD Verilog-reader artifact for the constant-0 tie in the netlist (`.A({2'h0,…})`, `.sdel(4'h0)`). It is **not** a real ground/PDN net and **not** created by CTS. It has zero BTerms, zero wire segments, six ITerms — all on macro `USE SIGNAL` input pins — and is the design's only driverless/floating net. Its LEF pins are signal inputs, so a correct physical implementation must drive them (through a tie-low cell tied to VSS or by connecting the tie net to VSS). It *should* be routed or otherwise physically connected; treating it as a non-routable special net would leave those six inputs open. Evidence: §3.2, §3.3, §3.4.

**C2 — Is the Ground classification correct, or is the net misclassified?**
**Verdict: FAIL for “correct classification” — strong evidence of MISCLASSIFICATION.** The net's only connectivity is to six `DIRECTION INPUT / USE SIGNAL` macro pins (§3.4); the macro's actual ground is the separate `vss` pin on net `VSS` (§3.2, §3.5). OpenROAD typed the constant-0 tie net GROUND by convention (constant 0 → GROUND), which is semantically wrong for a net driving digital inputs. DRT-0305 is thus a *symptom of a mislabeled tie net*, not proof that a legitimate ground net lacks a designation. Marking the mislabeled net “special” freezes the misclassification.

**C3 — Does the error originate from PDN connectivity or a separate logical ground net?**
**Verdict: PASS (for “separate logical net”); FAIL (for “PDN problem”).** The PDN is complete and consistent: `VDD`/`VSS` are POWER/GROUND, `isSpecial=1`, have BTerms and 283 ITerms each including `u_sram.vdd`/`u_sram.vss`; `pdn_sattva.tcl` explicitly global-connects both uppercase stdcell pins and lowercase macro pins. `zero_` is a **separate** GROUND-typed net with no PG pin, no BTerm, no geometry. Error is not a missing macro PG connection or unconnected ground pin. Evidence: §3.2, §3.5. (Lowercase-vs-uppercase pin naming is handled, not the fault.)

**C4 — Unsupported power-net representation?**
**Verdict: PARTIAL PASS — there is an unsupported *tie/constant* representation, not a power-net representation.** The design carries raw Verilog constants on macro pins because `SYNTH_NETLIST_FILES` short-circuits Yosys (`exit` at synth_preamble.tcl:34), so the normal `hilomap` tie-cell insertion (synth.tcl:301–304; ASAP7 `TIELOx1_ASAP7_75t_L`) never runs. The resulting driverless, GROUND-typed `zero_` net is a representation OpenROAD's DRT refuses. “Multiple ground nets not tied together” is literally true (VSS and zero_), but only because zero_ is a mislabeled tie net, not a second power domain. Evidence: §3.3, §3.7.

**C5 — Does routing receive a consistent database?**
**Verdict: PASS — no DB inconsistency found.** `global_route.tcl` loads `4_cts.odb`; the route log reads the same path; `4_1_cts.odb` and `4_cts.odb` are byte-identical (same sha256). `zero_` has the same name, sigType GROUND, isSpecial=0, and the same six macro ITerms in `1_synth.odb`, `2_4_floorplan_pdn.odb`, and `4_cts.odb`. No stage log warns about net-type changes. Evidence: §3.1, §3.2, §3.8.

**C6 — Could the macro/LEF/ASAP7 platform/ORFS integration be the cause instead?**
**Verdict: macro pin-access geometry and routing-layer setup — NOT EVALUATED as a route outcome (routing never started), but EXCLUDED as the trigger of DRT-0305.** DRT-0305 is raised at `drt::pin_access_cmd` during “Reading design”, before pin-access computation or track access; the failing entity is a net classification, not a pin-shape/R3/M3 access failure. `config.mk` sets no custom routing-layer overrides (platform defaults apply), and `macro_placement.tcl` uses `place_macro -exact` to place `u_sram` at (1.230, 8.184) R0. Platform integration *is* implicated indirectly through C4 (the bypassed synthesis/tie-cell step), not through M3 PG pin access. Evidence: §3.1, §3.7.

**C7 — If `zero_` were marked special, would DRT-0305 necessarily disappear?**
**Verdict: mechanically LIKELY YES, empirically NOT EVALUATED — and it would be a MASK, not a fix.** DRT-0305's printed condition is “signal type GROUND … not routable … Move to special nets”; the DB shows exactly `sigType=GROUND, isSpecial=0`, so flipping `isSpecial` would satisfy DRT's check. However: (a) I could not run a flow to prove it (hard constraint) — label **NOT EVALUATED**; (b) the proposed command does not exist in this build (§3.6), so D-013 could not have exercised it; (c) even if a working mechanism were used (e.g. `set_nets_to_route`, present but untested), the six macro signal inputs would remain physically undriven — the floating-net condition (RSZ-0020) and the misclassification would persist into detailed routing/DRC. I found **no** evidence that `zero_` has *both* GROUND and SIGNAL uses or that its ground semantics are legitimate; the evidence points the other way.

---

## 5. Agreement / disagreement with the current hypothesis

**PARTIAL AGREE (symptom level only).** The immediate trigger is correctly identified: a net named `zero_` with `sigType=GROUND` and `isSpecial=0` is rejected by TritonRoute during `drt::pin_access_cmd`. The DB and log agree with that narrow mechanical statement (§3.1, §3.2).

**DISAGREE (root cause and remedy), with evidence:**
1. **“Internal Ground net created during CTS” — false.** It is present in `1_synth.odb` already, created from Verilog constant ties in the pre-synthesized netlist (§3.2, §3.3).
2. **“Legitimate Ground net that merely needs designation” — false.** All six sinks are `USE SIGNAL` macro inputs; the real ground is `vss` on `VSS`, already special (§3.4, §3.5). This is misclassification, not a missing designation.
3. **“`set_special_nets` is a valid command; error message confirms it” — false.** Direct query: `invalid command name "set_special_nets"`; `info commands *special*` empty (§3.6). The prior report's inference from the DRT text is circular and contradicted by measurement.
4. **“Infrastructure-only fix; no design change needed” — misleading.** The upstream defect is a design-integration choice: `SYNTH_NETLIST_FILES` bypasses `hilomap`, leaving a driverless constant net (§3.7, RSZ-0020). A durable fix belongs at the netlist/tie-cell or net-classification level, not in global_route.tcl special-net bookkeeping.
5. **“D-013 failed because the ORFS execution model prevents the command from taking effect” — unsupported.** There are two simpler, evidence-backed explanations: the command is invalid in this OpenROAD build (§3.6), and the edit was applied to `/mnt/d/tools/...` while the runner executes the mirror `/mnt/d/SattvaRoute/tools/...` (§3.1, stage_route.log:1). The D-013 run directory is empty, so the claimed execution is not independently verifiable (§3.9).

---

## 6. Alternative root-cause candidates, ranked by evidence support

| # | Candidate | Support / evidence | Confidence |
|---|---|---|---|
| 1 | **Misclassified constant tie net from a pre-synthesized netlist that bypasses ORFS tie-cell insertion.** Raw `2'h0`/`4'h0` → OpenROAD creates driverless, GROUND-typed `zero_` → DRT refuses it at design read. | §3.2, §3.3, §3.4, §3.7; RSZ-0020 floating net; `hilomap` skipped by `exit` at synth_preamble.tcl:34 | **HIGH** |
| 2 | **Proposed remedy is not executable in this toolchain** (`set_special_nets` absent; Tcl error on invoke). Explains D-013 non-effect directly. | §3.6 direct query | **HIGH** (for D-013 failure; not the original DRT cause) |
| 3 | **Wrong-path edit / no preserved D-013 execution evidence** (edit in `/mnt/d/tools`, runner uses mirror; empty D-013 run). | stage_route.log:1; `diff` clean; empty `runs/orfs_baseline_d013_20261118T160213Z` | **MEDIUM–HIGH** (for D-013 failure) |
| 4 | **PDN/macro PG connectivity defect (lowercase vdd/vss, missing ground connection).** | Disproven: §3.2 ODB shows `u_sram.vdd/vss` on special VDD/VSS; §3.5 PDN script | **LOW** (ruled out) |
| 5 | **DB rewritten between CTS and route changing net classification.** | Disproven: byte-identical CTS DBs; classification constant across 1_synth→4_cts; §3.8 | **LOW** (ruled out) |
| 6 | **Macro M3 PG pin access / pin-shape / routing-layer failure.** | Error precedes geometry processing; no custom layer overrides; §3.1, §3.6 note | **LOW** for DRT-0305 trigger; **NOT EVALUATED** as a downstream route risk |
| 7 | **A GROUND net with genuine SIGNAL uses in the same net / two ground domains shorted.** | `zero_` has only signal-input sinks and no ground pin; VSS is separate and special. §3.2, §3.4 | **LOW** as stated; the *semantic* version (“GROUND-typed net driving signal pins”) is the actual mechanism in #1 |
| 8 | **PDN-side `add_global_connection -net_type special` attempt.** | Failed earlier at floorplan with STA-0562; §3.9 | **MEDIUM** as a failed attempt, not a root cause |

---

## 7. Handoff, remaining uncertainty, and labels

**Handoff to orchestrator.** The current hypothesis is correct only about the *immediate DRT check condition* and wrong about the *nature of `zero_`* and the *proposed mechanism*. Recommend: (a) stop treating `set_special_nets` as the fix — it is not a command in this OpenROAD build; (b) re-frame the defect as a misclassified, driverless constant-tie net originating from the `SYNTH_NETLIST_FILES` synthesis bypass; (c) evaluate fixes at the correct layer: regenerate/upgrade the pre-synthesized netlist so constants are tied via `TIELOx1_ASAP7_75t_*` cells to VSS (or otherwise connect `zero_` to VSS / reclassify it as SIGNAL with a driver), and verify no other tool-visible constant nets remain; (d) before any new run, ensure the edited script is in the **mirror** tree the runner actually sources and preserve the run's evidence logs. Do not claim routing, extraction, timing, or signoff success — no `5_*.odb` exists in any run.

**Remaining uncertainty / NOT EVALUATED items:**
- Empirical proof that any special-net designation suppresses DRT-0305 (no flow run permitted; mechanically likely only).
- Whether `assign_ground_net zero_` / `set_nets_to_route` / an OpenDB `setSigType SIGNAL` API can implement the correct reclassification (commands exist; `assign_ground_net` returned `ODB-0332`; not pursued further).
- Whether the ASAP7 M3/M4 macro pin-access geometry or M3 PG taps would pass once routing starts.
- Exact semantics of `ODB-0332`; content of the empty D-013 run; whether any un-preserved run ever applied the D-013 edit.
- Downstream DRC/open pins if `zero_` were special-cased (no routed DB to inspect).

**Explicit labels**

| Claim / check | Label |
|---|---|
| Hypothesis: `zero_` is a genuine internal Ground net created at CTS | **FAIL** |
| Hypothesis: root cause is a missing special-net designation | **FAIL** (as root cause); mechanism of DRT check **PASS** |
| Hypothesis: fix = `set_special_nets [list zero_]` in global_route.tcl | **FAIL** (command absent; path mismatch; masking risk) |
| `zero_` is a misclassified, driverless constant-tie net driving six macro SIGNAL pins | **PASS** |
| PDN / macro `vdd`/`vss` connectivity is correct and complete | **PASS** |
| CTS → global-route DB consistency | **PASS** |
| Special/power/net-type warnings between stages | **PASS** (none found) |
| D-013 static “7/7 checks PASS” claim that `set_special_nets` is valid | **FAIL** |
| D-013 executed in the runner's tree with preserved evidence | **NOT EVALUATED** (no artifacts; empty run dir) |
| Would special-net designation suppress DRT-0305 empirically | **NOT EVALUATED** (mechanically likely) |
| Macro pin access / routing-layer feasibility in actual routing | **NOT EVALUATED** |
| Detailed routing / extraction / timing / signoff | **NOT EVALUATED** (never reached) |
| Agent D modified only its assigned report | **PASS** |

— End of Agent D report.
