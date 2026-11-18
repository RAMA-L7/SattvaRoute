# Agent C — ORFS / TritonRoute Special-Net Mechanism & DRT-0305

- **Agent:** Agent C — ORFS and TritonRoute Special-Net Mechanism
- **Task:** T-M1-004 (Milestone 1C-R), assignment from orchestrator
- **Start timestamp:** 2026-11-18T16:50:50+00:00 (UTC; WSL `date --iso-8601=seconds`)
- **End timestamp:** 2026-11-18T17:06:16+00:00 (UTC)
- **Mode:** strictly read-only. No flow runs, no edits to scripts/configs/DBs/logs/state files. The only file written is this report.
- **Path mapping used:** `D:\SattvaRoute` = WSL `/mnt/d/SattvaRoute`; `D:\tools` = WSL `/mnt/d/tools`; OpenROAD source build tree = WSL `/mnt/d/tools/src/OpenROAD` (binary at `/mnt/d/tools/openroad/bin/openroad`, symlinked as `/usr/local/bin/openroad`).

---

## 0. Initial project state (as found, read-only)

From `D:\SattvaRoute\PROJECT_STATE.md` (lines 8, 55–56, 79):

> "Current status: DRT-0305 blocker investigated; D-013 set_special_nets verified by subagent (all 7 checks PASS) but does not complete routing through ORFS flow ..."

> "D-013: `set_special_nets [list zero_]` in `global_route.tcl` — verified by subagent all 7 checks PASS; ORFS flow execution model prevents command from taking effect on TritonRoute; same DRT-0305 error persists; original baseline preserved immutable"

From `D:\SattvaRoute\docs\DRT-0305_fix_proposal.md` (lines 24–34, 55–61) — the prior "fix proposal" that D-013 was based on:

> "Change location: After the `pin_access` command that triggers DRT-0305, add a `set_special_nets` command …"

> "The fix adds a `set_special_nets` Tcl command **after** the `pin_access` call in `global_route.tcl` …"

The failure under investigation (verbatim, `runs/orfs_baseline_20261118T152845Z/work/logs/asap7/sattva_sram/base/5_1_grt.log`, lines 16, 25–26, 29):

```
pin_access
[INFO DRT-0150] Reading design.
[ERROR DRT-0305] Net zero_ of signal type GROUND is not routable by TritonRoute. Move to special nets.
DRT-0305
"drt::pin_access_cmd $db_process_node  $via_access_layer $verbose $min_access_points  $via_in_pin_bottom_layer $via_in_pin_top_layer"
    (procedure "pin_access" line 65)
"pin_access"
"log_cmd pin_access {*}$additional_args"
```

This log also proves the runner uses the **LF execution mirror** (`D:\SattvaRoute\tools\OpenROAD-flow-scripts`), not the `D:\tools` global clone: line 165 of the same log sources `/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow/platforms/asap7/setRC.tcl`. (Consistent with D-010.)

Agent B's corroborating DB trace (`reports/agent_B_zero_net_database_trace.md`, §3.5, §4): in `4_cts.odb` the net `zero_` is `sigType=GROUND isSpecial=0`, while `VDD`/`VSS` are `POWER/GROUND, isSpecial=1`. `zero_` is a constant-zero tie net from RTL tie-offs, present since synthesis — **not** created by CTS (that prior claim is refuted).

---

## 1. Installed versions (verbatim outputs)

| Command | Verbatim output |
|---|---|
| `git -C /mnt/d/tools/OpenROAD-flow-scripts rev-parse HEAD` | `25b6429c1644a8682852646bebf19ff164402c76` |
| `git -C /mnt/d/tools/OpenROAD-flow-scripts log -1 --format="%H%n%ad%n%s" --date=iso-strict` | `25b6429c1644a8682852646bebf19ff164402c76` / `2026-09-27T18:19:53+00:00` / `Merge pull request #4570 from The-OpenROAD-Project-staging/tighten-gt2n` |
| `git -C /mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts rev-parse HEAD` | `25b6429c1644a8682852646bebf19ff164402c76` (mirror identical to global clone) |
| `git -C /mnt/d/tools/src/OpenROAD rev-parse HEAD` | `629aa76b94ae420170d18692016a7be9101a53e7` |
| `git -C /mnt/d/tools/src/OpenROAD log -1 --oneline` | `629aa76 Merge pull request #12205 from The-OpenROAD-Project-staging/fix-12049-hier-inst-name` (2026-11-11T12:54:56+00:00) |
| `which openroad` | `/usr/local/bin/openroad` → `/mnt/d/tools/openroad/bin/openroad` |
| `openroad --version` | `OpenROAD bazel-nostamp` then `Features included (+) or not (-): -GPU -GUI` + full usage block. Matches `README.md` of the binary install: "Source-built OpenROAD, built 2026-11-11 from `D:\tools\src\OpenROAD` @ `629aa76` with Bazel … `bazel-nostamp`." |
| `yosys -V` | `Yosys 0.33 (git sha1 2584903a060)` |

**Result: PASS.** ORFS commit is exactly `25b6429` in both trees; OpenROAD is the `bazel-nostamp` build from source commit `629aa76`; Yosys 0.33. All version claims in PROJECT_STATE.md are confirmed.

---

## 2. Where DRT-0305 is raised, and under what condition

### 2.1 Source of the message

Built-in `grep` for the message text across `D:\tools\src\OpenROAD\src` found exactly one functional match:

```
D:\tools\src\OpenROAD\src\drt\src\io\io.cpp:
  Line 1043:                    "Net {} of signal type {} is not routable by TritonRoute. "
  Line 1044:                    "Move to special nets.",
```

### 2.2 Exact condition (verbatim source, `io.cpp` lines 1031–1070)

```cpp
1031: frNet* io::Parser::addNet(odb::dbNet* db_net)
1032: {
1033:   auto existing_net = getBlock()->findNet(db_net->getName());
1034:   if (existing_net != nullptr) {
1035:     return existing_net;
1036:   }
1037:   bool is_special = db_net->isSpecial();
1038:   bool has_jumpers = db_net->hasJumpers();
1039:   bool is_abuted = db_net->isConnectedByAbutment();
1040:   if (!is_special && db_net->getSigType().isSupply()) {
1041:     logger_->error(DRT,
1042:                    305,
1043:                    "Net {} of signal type {} is not routable by TritonRoute. "
1044:                    "Move to special nets.",
1045:                    db_net->getName(),
1046:                    db_net->getSigType().getString());
1047:   }
...
1057:   if (is_special) {
1058:     net_in->setIsSpecial(true);
1059:   }
...
1066:   if (is_special) {
1067:     getBlock()->addSNet(std::move(net_in));
1068:   } else {
1069:     getBlock()->addNet(std::move(net_in));
1070:   }
```

`isSupply()` is defined in `odb\src\db\dbTypes.cpp` lines 392–397 and returns `true` for **POWER and GROUND**:

```cpp
392: bool dbSigType::isSupply() const
393: {
394:   switch (value_) {
395:     case POWER:
396:     case GROUND:
397:       return true;
```

**Interpretation (evidence-backed):** DRT-0305 is a guard in the **TritonRoute database importer** (`io::Parser::addNet`, called from `setNets()` at `io.cpp:1024–1029`, called from `readDesign()` at `io.cpp:1438`). It fires when an OpenDB net has a **supply signal type (POWER or GROUND) but `dbNet::isSpecial() == false`**. The message does **not** mean "TritonRoute lacks an algorithm for ground nets" — it means "the database handed to TritonRoute contains a supply-class net that was never designated special; fix the DB before importing." GROUND nets that *are* special are accepted and are placed into the special-net container (`addSNet`, line 1067) so they are preserved, not signal-routed.

### 2.3 Why it fires at stage 5_1_grt (global route) even though DRT is the detail router

- `global_route` itself isimplemented in `grt` (`grt/src/GlobalRouter.tcl:143–189`), not DRT.
- However, ORFS `flow/scripts/global_route.tcl:66` runs `log_cmd pin_access ...` **before** `global_route`. `pin_access` is a **DRT** command (`drt/src/TritonRoute.tcl:266–281`).
- `TritonRoute::pinAccess()` calls `initDesign()` (`drt/src/TritonRoute.cpp:1116–1119`); `initDesign()` calls `parser.readDesign(db_)` (`TritonRoute.cpp:590–597`) → `setNets()` → `addNet()` → DRT-0305.
- The log stack trace confirms exactly this path (`drt::pin_access_cmd` → `pin_access` → `log_cmd pin_access`).

**Result: PASS.** The error is a DRT DB-import validation error triggered by `pin_access`, caused by `zero_` being GROUND-typed but non-special in `4_cts.odb`.

---

## 3. `set_special_nets` — is it even a real command in this build?

### 3.1 Searches performed (all read-only)

| Search | Command / tool | Result |
|---|---|---|
| OpenROAD C++/Tcl source | built-in `grep` pattern `set_special_nets`, path `D:\tools\src\OpenROAD` | **No matches found** |
| Entire ORFS tree | built-in `grep` pattern `set_special_nets`, path `D:\tools\OpenROAD-flow-scripts` | **No matches found** |
| Mirror ORFS tree | built-in `grep` pattern `set_special_nets`, path `D:\SattvaRoute\tools\OpenROAD-flow-scripts` | **No matches found** |
| Installed binary strings | `grep -a -c "set_special_nets" /mnt/d/tools/openroad/bin/openroad` | `0` (exit 1 = no match) |
| Both `global_route.tcl` copies | built-in `grep` pattern `set_special_nets` in `D:\tools\...` and `D:\SattvaRoute\tools\...` | **No matches found in either** (the D-013 patch is not currently present in either copy) |

Agent B independently probed the live Tcl command set (`reports/agent_B_zero_net_database_trace.md`, §2 lines 79, §6 line 426): `get_signal_type`, `get_special_nets`, `is_power`, `is_ground` all returned **empty** (unavailable), and the global command `dbNet_setSpecial` reported `DBNET_HAS_SET_SPECIAL=0`. A runtime `info commands *special*` probe by this agent via PowerShell→WSL was attempted but produced mangled quoting (PowerShell mishandled the `<(...)` process substitution); that specific dynamic probe is therefore **NOT EVALUATED**, but it is redundant given the source + binary-string evidence above.

### 3.2 Assessment

**`set_special_nets` is NOT a command in this OpenROAD build (`bazel-nostamp`, commit `629aa76`).** It does not exist in the source, in the ORFS scripts, or in the binary. Consequently:

- **D-013's premise is invalid (FAIL).** "Use `set_special_nets [list zero_]`" cannot work because the command does not exist. Even if it had, adding it **after** `pin_access` (as `docs/DRT-0305_fix_proposal.md:28,57` proposes) could not affect an error raised *by* `pin_access` — the ordering is backwards. And the patch was reportedly applied to the `D:\tools` copy (task background), while the runner uses the `D:\SattvaRoute\tools` mirror (D-010), so it would not have executed anyway.
- The prior subagent's "all 7 checks PASS" almost certainly verified only **static text presence** of the line in one copy, not command existence or runtime effect. That verification does not establish a working fix.

**Result: FAIL** (for the hypothesis "set_special_nets is the correct command in this build").

---

## 4. The mechanism this ORFS version actually expects

### 4.1 Command that marks nets special: `add_global_connection ... -power/-ground` + `global_connect`

Official in-tree documentation, `D:\tools\src\OpenROAD\src\README.md` lines 215–250:

> "The `add_global_connection` command is used to specify how to connect power and ground pins on design instances to the appropriate supplies."
>
> `add_global_connection -net net_name [-inst_pattern ...] -pin_pattern ... (-power|-ground) [-region ...]`
>
> Examples: `add_global_connection -net VDD -pin_pattern {^VDD$} -power` / `add_global_connection -net VSS -pin_pattern {^VSS$} -ground`

Implementation, `D:\tools\src\OpenROAD\src\OpenRoad.tcl` lines 367–413 (verbatim):

```tcl
367: sta::define_cmd_args "add_global_connection" {[-net net_name] \
368:                                               [-inst_pattern inst_name_pattern] \
369:                                               [-pin_pattern pin_name_pattern] \
370:                                               [(-power|-ground)] \
371:                                               [-region region_name] \
372:                                               [-defer_connection]
373: }
...
398:   set net [[ord::get_db_block] findNet $keys(-net)]
399:   if { $net == "NULL" } {
400:     set net [odb::dbNet_create [ord::get_db_block] $keys(-net)]
...
407:   if { [info exists flags(-power)] } {
408:     $net setSpecial
409:     $net setSigType POWER
410:   } elseif { [info exists flags(-ground)] } {
411:     $net setSpecial
412:     $net setSigType GROUND
413:   }
```

And `global_connect` (OpenRoad.tcl lines 347–355) calls `[ord::get_db_block] globalConnect ...`; the C++ `dbGlobalConnect.cpp:354–357` connects ITerms and calls `iterm->setSpecial()` when the net is special. So the supported, documented way to make a supply net SPECIAL is `add_global_connection <net> ... -power|-ground`, which performs **both** `setSpecial()` and `setSigType()`.

### 4.2 Where ORFS invokes this: the PDN stage (`pdn.tcl`), via `PDN_TCL`

`D:\SattvaRoute\tools\OpenROAD-flow-scripts\flow\scripts\pdn.tcl` lines 1–24 (verbatim excerpt):

```tcl
1: source $::env(SCRIPTS_DIR)/load.tcl
2: erase_non_stage_variables floorplan
3: load_design 2_3_floorplan_tapcell.odb 2_1_floorplan.sdc
4: source_step_tcl PRE PDN
6: source $::env(PDN_TCL)
7: pdngen
...
24: orfs_write_db $::env(RESULTS_DIR)/2_4_floorplan_pdn.odb
```

`flow/platforms/asap7/config.mk:39–44`:
```
39: # Define default PDN config
40: ifeq ($(BLOCKS),)
41:    export PDN_TCL ?= $(PLATFORM_DIR)/openRoad/pdn/grid_strategy-M1-M2-M5-M6.tcl
```

`flow/platforms/asap7/openRoad/pdn/grid_strategy-M1-M2-M5-M6.tcl:1–13` (verbatim):
```tcl
4: add_global_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDD$} -power
5: add_global_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDDPE$}
6: add_global_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDDCE$}
7: add_global_connection -net {VSS} -inst_pattern {.*} -pin_pattern {^VSS$} -ground
8: add_global_connection -net {VSS} -inst_pattern {.*} -pin_pattern {^VSSE$}
9: global_connect
13: set_voltage_domain -name {CORE} -power {VDD} -ground {VSS}
```

The design override `benchmark/design/sattva_sram/pdn_sattva.tcl:24–31` adds lowercase `vdd`/`vss` global connections (for the macro) and `global_connect`; it declares **only VDD and VSS** as supplies. This is why `VDD`/`VSS` are `isSpecial=1` while `zero_` is not (Agent B, §3.4–3.5).

### 4.3 Variables that are NOT special-net mechanisms

- `PWR_NETS_VOLTAGES` / `GND_NETS_VOLTAGES` (`asap7/config.mk:213–214`: `VDD $(VOLTAGE)` / `VSS 0.0`) are used **only** for IR-drop analysis in `flow/scripts/final_outputs.tcl:40–56` and `save_images.tcl:44`. They do not mark nets special.
- There is **no** `SPECIAL_NETS` or `PDN_NETS` variable anywhere in the ORFS `flow/` tree (verified by grep). (Uppercase `PDN_NETS` appears only as an unrelated internal identifier in the `pdn` module's source, not as a flow control.)

### 4.4 Alternate path: DEF `SPECIALNETS`

Nets present in the DEF `SPECIALNETS` section are marked special on import: `odb\src\defin\definSNet.cpp:37` `_cur_net->setSpecial();`. Conversely, `odb\src\defout\defout_impl.cpp:141` writes special nets to SPECIALNETS. So ODB↔DEF round-trips the special bit. This is how special status survives `write_db`/`read_db` between flow stages.

---

## 5. How `zero_` became GROUND-but-not-special (source-level root cause)

This closes the gap left by Agent B (who labeled the exact internal mechanism NOT EVALUATED):

1. The Verilog reader creates a net literally named `zero_` for constant-zero literals: `sta\verilog\VerilogReader.cc:117` `zero_net_name_("zero_")`, and `VerilogReader.cc:2019–2020`:
   ```cpp
   2019: if (net_str == zero_net_name_)
   2020:   network->addConstantNet(net, LogicValue::zero);
   ```
   (Constant-one uses `one_`.)
2. When the STA network is written into OpenDB, constant nets are given supply sigtypes but **are not** made special: `dbSta\src\dbReadVerilog.cc:768–773`:
   ```cpp
   768: if (network_->isPower(net)) {
   769:   db_net->setSigType(odb::dbSigType::POWER);
   770: }
   771: if (network_->isGround(net)) {
   772:   db_net->setSigType(odb::dbSigType::GROUND);
   773: }
   ```
   There is no `setSpecial()` call here. Result: `sigType=GROUND, isSpecial=0` — exactly what Agent B measured in `1_synth.odb` through `4_cts.odb`.
3. `zero_` connects only to constant-tied macro signal pins (`sdel[3:0]`, `A[3:2]`); it has no shapes and is not on the PDN. At `pin_access`, DRT's `addNet()` guard sees `isSupply()==true && isSpecial()==false` → DRT-0305.

This is a **tool-side misclassification**: a logical constant-tie net is typed as a physical supply net without the special designation that DRT requires. The PDN configuration for VDD/VSS is correct; the defect is the `zero_` net's class.

---

## 6. Answers to the five required questions

**Q1. What mechanism does this ORFS version EXPECT for special nets?**
✅ **PASS — identified with source evidence.** Supply nets are designated SPECIAL in the database by `add_global_connection -net <name> ... -power|-ground` (which calls `dbNet::setSpecial()` + `setSigType()`), followed by `global_connect`, inside the PDN TCL sourced at stage 2_4 (`pdn.tcl:6`, `PDN_TCL`). Equivalently, nets in the DEF `SPECIALNETS` section are marked special on import. There is no standalone `set_special_nets` command; `PWR_NETS_VOLTAGES`/`GND_NETS_VOLTAGES` are IR-drop-only.

**Q2. At what stage should ground nets be classified?**
✅ **PASS.** At **PDN generation (stage `2_4_floorplan_pdn`, `pdn.tcl`)** — i.e., before CTS and well before global routing. Practically, the classification must be present in `4_cts.odb` (the DB loaded by `5_1_grt`) before `pin_access` runs. Any later insertion at global-route time is too late for the DRT error, because `pin_access` is the first DRT call in that stage.

**Q3. Does ORFS generate, preserve, or overwrite special-net status?**
✅ **PASS.** ORFS **generates** special status at PDN (via `add_global_connection`), and **preserves** it thereafter: `global_route.tcl` and `detail_route.tcl` contain no special-net mutation, and status round-trips through ODB↔DEF SPECIALNETS (`definSNet.cpp:37`, `defout_impl.cpp:141`). ORFS does **not** overwrite it in later stages. It does **not** repair a net that was mis-classified at netlist import (like `zero_`).

**Q4. Does the global-routing invocation receive special-net information?**
✅ **PASS — with precise channel.** Not via command-line flags: `global_route` args (`grt/src/GlobalRouter.tcl:143–169`) and `detailed_route` args (`detail_route.tcl:45–50`) contain **no** special-net option. Special-net info reaches routing **inside the ODB** loaded by `load_design 4_cts.odb` (`global_route.tcl:4`). `pin_access`/DRT reads `dbNet::isSpecial()` from that DB (`io.cpp:1037`). `write_guides` (`global_route.tcl:182`) emits signal-net guides; DRT's special nets come from the DB, not the guide file.

**Q5. Is DRT-0305 a configuration problem, script-order issue, database issue, or tool limitation?**
✅ **PASS — primary classification: DATABASE issue with a contributing TOOL limitation.**
- It is a **database-state problem**: `zero_` has `sigType=GROUND` and `isSpecial=0` in the input DB. The DRT parser guard is working as designed.
- Underlying cause is a **tool limitation/bug in OpenROAD's netlist import**: the Verilog reader names constant-zero nets `zero_`, `dbReadVerilog` maps them to `GROUND` sigtype, but never sets the SPECIAL bit — so a non-supply tie net masquerades as a supply net (`§5`).
- It is **not** an ORFS PDN configuration problem: `VDD`/`VSS` are correctly declared special; the design's PDN override correctly covers the macro's `vdd`/`vss` pins.
- It is **not** fundamentally a script-order problem, although order matters for any fix: the special bit must be set in the DB *before* the first DRT call (`pin_access`). D-013's "add the command after pin_access" was doubly wrong (nonexistent command + wrong side of the failing call), and was targeted at the wrong checkout.

---

## 7. Handoff to orchestrator

- **Corrective direction:** Treat `set_special_nets` as a non-existent command in this build and retire D-013's premise (FAIL). If a targeted DB fix is desired, the supported primitive is `dbNet::setSpecial()` on the `zero_` net (exposed on the SWIG `dbNet` object, used internally by `OpenRoad.tcl:408/411`), or formally declaring `zero_` as a ground connection via `add_global_connection -net zero_ ... -ground` **in the PDN TCL (stage 2_4)**, before CTS. NOTE: marking a geometry-less tie net as a special/supply net may create new DRC/LVS/connectivity concerns; an arguably cleaner fix is to prevent the mis-tagging (e.g., tie constants to `VSS` through tie cells / keep `zero_` as SIGNAL). These are **design-time decisions for the orchestrator**; this agent performed no flow run and evaluated no fix.
- **Where to apply:** any DB mutation must run in the stage that owns the DB **and** in the checkout the runner actually uses (`D:\SattvaRoute\tools\OpenROAD-flow-scripts`, D-010). A patch to `D:\tools` will not be executed.
- **Timing:** must be before `pin_access` in `5_1_grt` (ideally at PDN, stage 2_4). Adding anything after `pin_access` cannot suppress DRT-0305.

### Remaining uncertainty / NOT EVALUATED
- **Web research on DRT-0305-specific official guidance:** `websearch` returned HTTP 402 (quota); direct doc URL guesses `openroad.readthedocs.io/en/latest/main/src/drt/README.html`, `.../src/pdn/README.html`, `.../main/messages.html`, `.../user/MessageReference.html` returned 404. Reaching the general OpenROAD docs landing page and ORFS UserGuide succeeded but contained no DRT-0305 or special-net guidance. **No official web statement about DRT-0305 was obtainable.** All authoritative findings here come from the *installed, exact-build* source and in-tree docs, which are stronger evidence than generic web docs for this version. URL attempts are cited above for reproducibility.
- **Runtime `info commands` enumeration** of the OpenROAD Tcl command set: attempted but defeated by PowerShell→WSL quoting; marked NOT EVALUATED (non-binding — source and binary-string searches are definitive for absence of `set_special_nets`).
- **Whether marking `zero_` special actually allows routing to complete** — NOT EVALUATED (no flow runs permitted by task constraints). This requires an orchestrator-approved rerun.
- **Full duplication of Agent B's DB trace** — not repeated; referenced by file/line and independently consistent with this agent's source findings.
- **Whether older/newer OpenROAD versions ever had a `set_special_nets` command** — NOT EVALUATED (web search unavailable); irrelevant to this installed build.

### Label summary
| Item | Label |
|---|---|
| Installed versions / commit IDs | **PASS** |
| DRT-0305 source location and trigger condition | **PASS** |
| Failure path traced to `pin_access` / DRT import | **PASS** |
| Supported ORFS special-net mechanism identified | **PASS** |
| `zero_` GROUND mis-tagging root cause (source) | **PASS** |
| `set_special_nets` is a real command in this build | **FAIL** (absent from source, ORFS, binary) |
| D-013 hypothesis / prior "all 7 checks PASS" fix | **FAIL** (wrong command, wrong order, wrong checkout) |
| Official web documentation for DRT-0305 | **NOT EVALUATED** (402 / 404; in-tree source/docs used instead) |
| Runtime `info commands *special*` enumeration | **NOT EVALUATED** (PowerShell quoting; redundant) |
| Efficacy of any candidate fix (flow rerun) | **NOT EVALUATED** (out of scope) |

- **Constraint compliance:** no flow run; no script/config/DB/log/state-file modification; web attempts documented with URLs; no fabrication — unavailable probes are explicitly labeled.
