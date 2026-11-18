# Agent A — ORFS Execution-Path Investigation (T-M1-004 / Milestone 1C-R)

## 0. Metadata

| Item | Value |
|---|---|
| Agent | **Agent A — ORFS Execution-Path Investigation** (subagent) |
| Task | T-M1-004, Milestone 1C-R: determine exactly how `global_route.tcl` is executed in the failing run and whether D-013 (`set_special_nets [list zero_]`) ever affected the database or the routing invocation |
| Start timestamp | **2026-11-18T22:19:52+05:30** (2026-11-18T16:49:52Z) |
| End timestamp | **2026-11-18T22:31:16+05:30** (= 2026-11-18T17:01:16Z) |
| Mode | **Read-only.** No flow run, no edit to any flow file, script, config, netlist, RTL, macro, SDC, DB, log, or coordination/state file. Only this report was created. OpenROAD was used solely for in-memory read-only DB introspection and command-existence queries (`-no_init -exit`, no `write_db`, no DB save). |
| Constraint compliance | **PASS** — no `make` of a flow target, no `write_db`, no project file modified. |
| Deliverable | This report (`D:\SattvaRoute\reports\agent_A_orfs_execution_path.md`). |

### Initial project state (verified at start)

- `D:\SattvaRoute\runs\` held 15 run directories: 14 `orfs_baseline_*` + 1 `orfs_baseline_d013_20261118T160213Z`. Twelve had an `evidence/stage_route.log`; all twelve showed 6/7 stages passing and `rc=2` at route. No `5_*.odb` existed in any run (routing never completed anywhere).
- `orfs_baseline_d013_20261118T160213Z/evidence/` and `/work/` were **empty** — no preserved D-013 evidence.
- `orfs_baseline_20261118T163746Z` failed earlier (floorplan), so no route log.
- Both `global_route.tcl` copies were already clean: `grep set_special_nets` → no matches in either tree.
- `reports/` already contained `agent_D_independent_failure_analysis.md`; read for context only, not used as primary evidence.

---

## 1. Files inspected (exact paths)

**Runner / Makefile / variables**
- `D:\SattvaRoute\scripts\run_baseline_orfs.sh` (full, 100 lines)
- `D:\SattvaRoute\tools\OpenROAD-flow-scripts\flow\Makefile` (lines 149–154, 390–419, 601–631)
- `D:\SattvaRoute\tools\OpenROAD-flow-scripts\flow\scripts\variables.mk` (lines 6–17, 46–49, 83–115)
- `D:\SattvaRoute\tools\OpenROAD-flow-scripts\flow\scripts\flow.sh` (full, 26 lines)
- `D:\SattvaRoute\tools\OpenROAD-flow-scripts\flow\scripts\run_command.py` (full, 130 lines)
- `D:\SattvaRoute\tools\OpenROAD-flow-scripts\flow\scripts\noop.tcl` (1 empty line)

**Tcl scripts in the executed source chain**
- `D:\SattvaRoute\tools\OpenROAD-flow-scripts\flow\scripts\global_route.tcl` (full, 188 lines)
- `D:\SattvaRoute\tools\OpenROAD-flow-scripts\flow\scripts\load.tcl` (full, 58 lines)
- `D:\SattvaRoute\tools\OpenROAD-flow-scripts\flow\scripts\util.tcl` (lines 1–30, 200–224, 330–338)
- `D:\tools\OpenROAD-flow-scripts\flow\scripts\global_route.tcl` (hash/line comparison only)
- `D:\SattvaRoute\tools\OpenROAD-flow-scripts\flow\platforms\asap7\setRC.tcl` (grep: no `source`/`read_db`/`write_db`/`special`)

**Logs / evidence (verbatim quotes below)**
- `D:\SattvaRoute\runs\orfs_baseline_20261118T152845Z\evidence\stage_route.log` (full, 59 lines)
- `D:\SattvaRoute\runs\orfs_baseline_20261118T152845Z\work\logs\asap7\sattva_sram\base\5_1_grt.log` (full, 43 lines)
- `D:\SattvaRoute\runs\orfs_baseline_20261118T152845Z\evidence\preflight.txt`, `stages.txt`
- All 12 `runs\orfs_baseline_*\evidence\stage_route.log` and `preflight.txt` files (cross-run comparison)
- `D:\SattvaRoute\runs\orfs_baseline_20261118T163746Z\evidence\stage_floorplan.log` (failed alternate edit, context)

**Design / docs (context only)**
- `D:\SattvaRoute\benchmark\design\sattva_sram\config.mk`
- `D:\SattvaRoute\docs\DRT-0305_fix_proposal.md` (D-013 patch identity and stated edit location)
- `D:\SattvaRoute\scripts\routing_fix_demo.py`
- `D:\SattvaRoute\corouting\MILESTONE_1C_ROUTING_INVESTIGATION.md`
- `D:\SattvaRoute\runs\orfs_baseline_20261118T152845Z\work\results\asap7\sattva_sram\base\4_cts.odb` (**read-only** inspection)

---

## 2. Commands executed (with output excerpts)

### 2.1 Windows PowerShell
```
Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
Get-ChildItem -Path 'D:\SattvaRoute\runs' -Directory | ...   # inventory of stage_route.log / stages.txt
```
Excerpt:
```
orfs_baseline_20261118T152845Z  route=YES  OVERALL_RC=2
orfs_baseline_20261118T161543Z  route=YES  OVERALL_RC=2
...
orfs_baseline_20261118T163746Z  route=NO   OVERALL_RC=2
orfs_baseline_d013_20261118T160213Z  route=NO   (no stages.txt)
```

### 2.2 WSL (`wsl -d Ubuntu-24.04 -- bash -c '...'`)
```
sha256sum /mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow/scripts/global_route.tcl \
          /mnt/d/tools/OpenROAD-flow-scripts/flow/scripts/global_route.tcl
```
```
3968898c9abd8c0fd56c50d08bed6d3943bdc641f63c8674817449bbec2706ce  /mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow/scripts/global_route.tcl
3968898c9abd8c0fd56c50d08bed6d3943bdc641f63c8674817449bbec2706ce  /mnt/d/tools/OpenROAD-flow-scripts/flow/scripts/global_route.tcl
```
```
wc -l .../global_route.tcl (both)  -> 188 / 188
git -C ... status --porcelain -- flow/scripts/global_route.tcl  -> (empty for both)
git -C ... reflog --date=iso  ->  25b6429 HEAD@{2026-11-18 14:41:25 +0000}: clone: from /mnt/d/tools/OpenROAD-flow-scripts
grep -n -e pin_access -e global_route_helper .../global_route.tcl
```
```
8:proc global_route_helper { } {
66:  log_cmd pin_access {*}$additional_args
188:global_route_helper
```
```
sha256sum .../4_cts.odb .../flow.sh .../util.tcl
```
```
35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1  4_cts.odb
75a317153c67818f6d7189bfc8ff0a4f489d4baa136e36200b082c3f787bdb1f  flow.sh
e78048e8c9e0c45cada6ab09baf142780edd09f52f0e04e8fb5645e330d108d0  util.tcl
```
```
diff <(sed -E 's@orfs_baseline_[0-9TZ]+@RUN@g' <run A route.log>) <(same for run 163357Z)
```
Output: only three `Elapsed time:` lines differ (timings); all paths, commands, error text and line numbers identical.

```
grep -r -l -F set_special_nets /mnt/d/SattvaRoute /mnt/d/tools/OpenROAD-flow-scripts
```
→ matches **only** SattvaRoute docs/coordination files; **zero** matches under either `flow/` tree or any OpenROAD-flow-scripts file.

### 2.3 Tcl line-number rule validation (STATIC tool-behavior check)
Because the log reports proc-relative line numbers, the rule was validated with both `tclsh` and `openroad` using scripts piped through `/dev/stdin`:
```
printf '%s\n' '# comment' 'proc outer { } {' '  proc inner { } {' ... '  error boom' '}' 'outer' | tclsh /dev/stdin
```
```
    (procedure "outer" line 9)     # error at file line 10, proc starts at file line 2
```
**Rule:** reported proc line = file line − proc-definition line + 1 (verified identically in `tclsh` and `openroad bazel-nostamp`).

### 2.4 Read-only OpenROAD DB introspection (EXECUTION observation, no writes)
Tcl supplied via stdin to `openroad -no_init -exit /dev/stdin`:

```
set db [ord::get_db]
read_db /mnt/d/SattvaRoute/runs/orfs_baseline_20261118T152845Z/work/results/asap7/sattva_sram/base/4_cts.odb
set chip [$db getChip]; set block [$chip getBlock]; set nets [$block getNets]
puts "TOTAL_NETS=[llength $nets]"
... foreach n $nets { ... isSpecial / getSigType / getName ... }
```
```
TOTAL_NETS=75
MATCH name=zero_ special=0 sigtype=GROUND
SPECIAL_COUNT=2
```
```
NET name=clk special=0 sigtype=CLOCK
NET name=zero_ special=0 sigtype=GROUND
NET name=VDD special=1 sigtype=POWER
NET name=VSS special=1 sigtype=GROUND
NET name=clk_regs special=0 sigtype=CLOCK
...
```
Command-existence probe (before **and** after `read_db`):
```
BEFORE_READ_DB all-namespaced special commands:
AFTER_READ_DB all-namespaced special commands:
set_special_nets exists: 0
direct invocation test:
1
catch msg: invalid command name "set_special_nets"
```

---

## 3. Evidence tables

### 3.1 Runner environment (STATIC — `run_baseline_orfs.sh`)

| Item | Exact value / line |
|---|---|
| `STAMP` | `date -u +%Y%m%dT%H%M%SZ` (line 16) |
| `MIRROR` | `/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts` (line 17) |
| `FLOW` | `$MIRROR/flow` = `/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow` (line 18) |
| `DESIGN` / `CFG` | `/mnt/d/SattvaRoute/benchmark/design/sattva_sram` / `$DESIGN/config.mk` (lines 19–20) |
| `RUN` / `EV` / `WORK` | `/mnt/d/SattvaRoute/runs/orfs_baseline_$STAMP` / `$RUN/evidence` / `$RUN/work` (lines 21–23) |
| `OVERRIDES` | `OPENROAD_EXE=/usr/local/bin/openroad YOSYS_EXE=/usr/bin/yosys WORK_HOME=$WORK` (line 26) |
| `STAGES` | `check-yosys check-openroad synth floorplan place cts route finish` (line 54) |
| Per-stage command | `make -C "$FLOW" DESIGN_CONFIG="$CFG" "${OVERRIDES[@]}" "$s" > "$EV/stage_$s.log" 2>&1` (lines 60–61) |
| Stop rule | `if [ $rc -ne 0 ]; then overall=$rc; ... break; fi` (lines 66–70) |

Derived Make variables (`Flow_HOME`-relative, `variables.mk`): `FLOW_HOME=/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow` (Makefile:150), `SCRIPTS_DIR=$FLOW_HOME/scripts` (variables.mk:17), `UTILS_DIR=$FLOW_HOME/util` (:16), `RESULTS_DIR=$WORK_HOME/results/asap7/sattva_sram/base` (:49), `LOG_DIR=$WORK_HOME/logs/asap7/sattva_sram/base` (:46), `PLATFORM_DIR=$FLOW_HOME/platforms/asap7` (:31), `OPENROAD_EXE=/usr/local/bin/openroad`, `OPENROAD_ARGS=-no_init -threads 8 …` (:111), `OPENROAD_CMD=$OPENROAD_EXE -exit $OPENROAD_ARGS` (:112), `RUN_CMD=python3 $FLOW_HOME/scripts/run_command.py` (:86), `PYTHON_EXE=python3`.

### 3.2 Which script actually ran — EXECUTION evidence

| Evidence | Exact quote | Source | Line |
|---|---|---|---|
| make working directory | `make: Entering directory '/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow'` | `evidence/stage_route.log` | 1 |
| stage entry | `/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow/scripts/flow.sh 5_1_grt global_route` | `evidence/stage_route.log` | 17 |
| stage name echo | `Running global_route.tcl, stage 5_1_grt` | `evidence/stage_route.log` | 18 |
| platform libs from **mirror** | `source /mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow/platforms/asap7/liberty_suppressions.tcl` | `evidence/stage_route.log` | 19 |
| `setRC` from **mirror** | `source /mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow/platforms/asap7/setRC.tcl` | `evidence/stage_route.log` | 28 |
| **absolute executed script path in Tcl stack trace** | `(file "/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow/scripts/global_route.tcl" line 188)` | `evidence/stage_route.log` + `5_1_grt.log` | 55 / 42 |
| design read | `read_db /mnt/d/SattvaRoute/runs/orfs_baseline_20261118T152845Z/work/results/asap7/sattva_sram/base/4_cts.odb` | `5_1_grt.log` | 13 |
| no D-013 in executed command stream | Sequence `source liberty_suppressions → read_liberty ×6 → read_db → read_sdc → source setRC → pin_access`; **`set_special_nets` absent** | `5_1_grt.log` / `stage_route.log` | 6–16 / 19–29 |
| failure point | `[ERROR DRT-0305] Net zero_ of signal type GROUND is not routable by TritonRoute. Move to special nets.` | `5_1_grt.log` / `stage_route.log` | 26 / 39 |
| call chain at failure | `log_cmd pin_access {*}$additional_args` → `(procedure "global_route_helper" line 57)` → `global_route_helper` → `(file "...global_route.tcl" line 188)` | `5_1_grt.log` | 38–42 |
| make result | `make[1]: *** [Makefile:613: do-5_1_grt] Error 1` … `Error 2` | `stage_route.log` | 57–58 |
| run outcome | `route rc=2` / `STAGE FAILED: route (rc=2) — stopping` / `OVERALL_RC=2` | `stages.txt` | 7–9 |

**Cross-run:** all 12 `stage_route.log` files contain the same path `/mnt/d/SattvaRoute/tools/...`, the same line-188 stack frame, the same DRT-0305 at line 39, and no `set_special_nets`. Normalized diff against run `163357Z` differs only in three `Elapsed time:` lines.

**Preflight (EXECUTION snapshot at each run start):** every run with a `preflight.txt` records
```
orfs_mirror_head: 25b6429c1644a8682852646bebf19ff164402c76
orfs_mirror_status: []
```
i.e. the **executed mirror tree was git-clean at the start of every run**, including all D-013-era attempts (15:28Z–16:33Z). No run ever began with a patched mirror.

### 3.3 Source / execution order (STATIC structure + EXECUTION log)

| # | File : line | Statement | Evidence type |
|---|---|---|---|
| 1 | `Makefile:613` | `do-step,5_1_grt,$(RESULTS_DIR)/4_cts.odb …,global_route` | STATIC |
| 2 | `Makefile:408` | `$(SCRIPTS_DIR)/flow.sh $(1) $(3)` → `flow.sh 5_1_grt global_route` | STATIC + log:17 |
| 3 | `flow.sh:16` | throwaway `openroad … -exit noop.tcl` (empty script; separate short-lived process) | STATIC |
| 4 | `flow.sh:19–20` | `$RUN_CMD … -- $OPENROAD_CMD -no_splash "$SCRIPTS_DIR/$2.tcl" -metrics …` → **single** OpenROAD process with `global_route.tcl` as its script | STATIC |
| 5 | `global_route.tcl:1` | `utl::set_metrics_stage "globalroute__{}"` | STATIC |
| 6 | `global_route.tcl:2` | `source $::env(SCRIPTS_DIR)/load.tcl` | STATIC |
| 7 | `load.tcl:1` | `source $::env(SCRIPTS_DIR)/util.tcl` → defines `log_cmd` (util.tcl:6–28) | STATIC |
| 8 | `load.tcl:3` | `source $::env(SCRIPTS_DIR)/report_metrics.tcl` | STATIC |
| 9 | `load.tcl:5` | `proc load_design {design_file sdc_file}` | STATIC |
| 10 | `global_route.tcl:3–4` | `erase_non_stage_variables grt`; `load_design 4_cts.odb 4_cts.sdc` | STATIC |
| 11 | `load.tcl:36` | `log_cmd read_db …/4_cts.odb` | EXECUTION: `5_1_grt.log:13` |
| 12 | `load.tcl:42` | `log_cmd read_sdc …/4_cts.sdc` | EXECUTION: `5_1_grt.log:14` |
| 13 | `load.tcl:51` | `log_cmd source …/platforms/asap7/setRC.tcl` | EXECUTION: `5_1_grt.log:15` |
| 14 | `global_route.tcl:8` | `proc global_route_helper { } {` (definition only; body not yet executed) | STATIC |
| 15 | `global_route.tcl:188` | `global_route_helper` — **top-level call** | EXECUTION: stack frame `5_1_grt.log:42` |
| 16 | `global_route.tcl:9` | `source_step_tcl PRE GLOBAL_ROUTE` → `source_env_var_if_exists PRE_GLOBAL_ROUTE_TCL` (`util.tcl:335–338`, `:213–217`). **Not set** (no `source` line in log; no config.mk binding) ⇒ no hook script ran | STATIC + EXECUTION (absence) |
| 17 | `global_route.tcl:66` | `log_cmd pin_access {*}$additional_args` → `util.tcl:18 uplevel 1 [list $cmd {*}$args]` | EXECUTION: `5_1_grt.log:35–39`, failure at `:26` |
| 18 | `global_route.tcl:68` | `if { ![do_global_route …] }` → would call `log_cmd global_route` (`:34`) | **NEVER REACHED** |

### 3.4 Tcl scope / catch analysis (STATIC + stack-trace EXECUTION)

- `global_route.tcl` is sourced into the **same** OpenROAD process that later calls `pin_access`: `5_1_grt.log` contains exactly one tool banner (lines 1–4), then `read_db` (13), `read_sdc` (14), `setRC` (15), `pin_access` (16) — no second process banner and no reopening of the design. The stack trace (38–42) nests `pin_access` inside `log_cmd` inside `global_route_helper` invoked at top-level line 188 of that same file.
- `pin_access` is issued **inside `proc global_route_helper`**, i.e. a Tcl local scope, but OpenROAD DB commands act on the process-global design; scope is not the failure mechanism. A command placed before line 66 inside the proc would still mutate the same loaded DB.
- `log_cmd` (`util.tcl:6–28`) **prints** the command (`puts $log_cmd`, line 9) and executes it via `uplevel 1` (line 18) **without any `catch`**. DRT-0305 therefore propagates as a fatal Tcl error (confirmed by the stack trace). The only `catch` in the file is in `run_global_route_and_catch_failures` (`global_route.tcl:33–46`) which wraps `log_cmd global_route` — never reached because `pin_access` fails first.
- A `set_special_nets` inserted **after** `pin_access` (as `docs/DRT-0305_fix_proposal.md:28,57` prescribes) would be **dead code** in every run.

### 3.5 DB observations (EXECUTION — read-only OpenROAD, `4_cts.odb`)

| Observation | Value |
|---|---|
| `4_cts.odb` sha256 | `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1` |
| Total nets | 75 |
| `zero_` | `name=zero_ special=0 sigtype=GROUND` — **not** a special net |
| `VDD` | `special=1 sigtype=POWER` |
| `VSS` | `special=1 sigtype=GROUND` |
| Special-net count | 2 (VDD and VSS only; `zero_` excluded) |
| `set_special_nets` command | absent before and after `read_db`; invoking it → `invalid command name "set_special_nets"` |

Confirms the DB loaded by the failing router is exactly the state DRT-0305 reports (`GROUND` + non-special `zero_`). No DB rewrite occurs between `read_db` and `pin_access`: the only `write_db`-class calls in the executed chain are `global_route.tcl:38`/`:42` (failure/success paths of `global_route`, unreachable) and `:184` (`orfs_write_db` at the very end of the success path).

### 3.6 Hashes and identity

| File | sha256 | Note |
|---|---|---|
| mirror `…/flow/scripts/global_route.tcl` | `3968898c9abd8c0fd56c50d08bed6d3943bdc641f63c8674817449bbec2706ce` | 188 lines, git-clean, tracked `H`, working tree == HEAD |
| source `D:\tools\…\global_route.tcl` | `3968898c9abd8c0fd56c50d08bed6d3943bdc641f63c8674817449bbec2706ce` | byte-identical to mirror today; neither contains `set_special_nets` |
| `4_cts.odb` (baseline) | `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1` | DB actually read at route |
| `flow.sh` (mirror) | `75a317153c67818f6d7189bfc8ff0a4f489d4baa136e36200b082c3f787bdb1f` | |
| `util.tcl` (mirror) | `e78048e8c9e0c45cada6ab09baf142780edd09f52f0e04e8fb5645e330d108d0` | |

### 3.7 STATIC vs EXECUTION classification

| Claim | Type | Basis |
|---|---|---|
| Runner uses `$MIRROR/flow` and passes `WORK_HOME` override | STATIC | `run_baseline_orfs.sh:17–26,60` |
| `SCRIPTS_DIR`/`OPENROAD_CMD`/`RUN_CMD` values | STATIC | `Makefile:150`, `variables.mk:17,86,112` |
| Source order of `load.tcl`/`util.tcl`/`setRC.tcl` | STATIC + EXECUTION | script text + echoed `log_cmd` lines in `5_1_grt.log` |
| Executed script path = mirror | **EXECUTION** | `make: Entering directory …` (log:1) + Tcl stack frame absolute path (log:55/42) |
| No `set_special_nets` in executed command stream | **EXECUTION** | full command echo in `5_1_grt.log:6–16`, identical across 12 runs |
| Mirror git-clean at every run start | **EXECUTION** | `preflight.txt:7` in all runs |
| Failure at `pin_access` before `global_route` | **EXECUTION** | log:16/26 + stack trace + no further router calls |
| `zero_` is GROUND and non-special in the loaded DB | **EXECUTION** (read-only) | OpenROAD `read_db` introspection output |
| `set_special_nets` is not a command in this build | **EXECUTION** (read-only) | `info commands ::*special*` empty; direct `catch` → `invalid command name` |
| Proposed edit location (after `pin_access`) is unreachable | STATIC + EXECUTION | `docs/DRT-0305_fix_proposal.md:28,57` + failure at `pin_access` |

---

## 4. Findings

1. **The runner never executes anything from `D:\tools`.** `run_baseline_orfs.sh:17–18` pins `MIRROR=/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts`, and every stage uses `make -C $FLOW`. All 12 route logs confirm `make: Entering directory '/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow'`. The stack trace quotes the same mirror path for `global_route.tcl`. Editing `/mnt/d/tools/.../global_route.tcl` cannot influence this flow.

2. **D-013 was aimed at the wrong tree.** `docs/DRT-0305_fix_proposal.md:26` and `scripts/routing_fix_demo.py:27` explicitly name `/mnt/d/tools/OpenROAD-flow-scripts/flow/scripts/global_route.tcl` as the patch target — the read-only global clone, not the execution mirror. `orfs_baseline_d013_20261118T160213Z` has no evidence at all, so the claimed D-013 run is not independently verifiable.

3. **The mirror was clean at every run start.** `preflight.txt:7` = `orfs_mirror_status: []` for all 14 runs with preflight, including every D-013-era attempt. The executed tree never carried the patch at the moment a stage began.

4. **The executed command stream contains no D-013 command.** `5_1_grt.log` echoes every `log_cmd`-wrapped command; lines 6–16 run `source liberty_suppressions`, six `read_liberty`, `read_db`, `read_sdc`, `source setRC`, `pin_access` — no `set_special_nets`. All 12 route logs are identical modulo timing.

5. **The failure precedes the router's geometry phase and precedes every `global_route` call.** `DRT-0305` is raised inside `drt::pin_access_cmd` during "Reading design" (`5_1_grt.log:25–29`). `global_route` (`global_route.tcl:34,59,96,117,149`) is never invoked. Therefore a command placed after `pin_access` — exactly where D-013 specified — could not run.

6. **`set_special_nets` does not exist in this OpenROAD build.** `info commands ::*special*` is empty both before and after `read_db`; direct invocation returns `invalid command name "set_special_nets"`. No `proc set_special_nets` exists anywhere in either flow tree. So even a correctly placed, correctly targeted invocation would have aborted with a Tcl error, not DRT-0305.

7. **The loaded DB confirms the trigger state.** `zero_`: `sigType=GROUND`, `isSpecial=0`; the only special nets are `VDD` and `VSS`. No script in the executed chain rewrites special-net status. Manual flipping would therefore be required for a mechanical fix — but that is outside this read-only investigation and is not a verified remedy.

8. **Minor unresolved detail (NOT EVALUATED as to cause).** Applying the validated Tcl rule (reported proc line = file line − proc-definition line + 1) to today's file predicts proc-line **59** for `log_cmd pin_access` at file line 66 (proc starts line 8); the logs report proc-line **57**. The top-level frame (`global_route.tcl` line 188) and `util.tcl`'s `log_cmd` frame (reported 13 = file line 18 − 6 + 1) match exactly. The 2-line discrepancy has no observed cause; preflight shows a clean tree at all run starts and no alternate copy of the file exists on disk. It does **not** affect any conclusion: the command text and absolute file path in the stack trace are unambiguous.

---

## 5. Conclusion

**(a) Which script actually ran?**
`/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow/scripts/global_route.tcl` — the **LF execution mirror (D:\SattvaRoute\tools)**. Proven by `make: Entering directory '/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow'` (`stage_route.log:1`), `flow.sh 5_1_grt global_route` from that tree (`:17`), and the absolute path in the Tcl stack frame (`:55`, and `5_1_grt.log:42`). The `D:\tools` (`/mnt/d/tools`) copy never appeared in any execution log.

**(b) Was D-013 ever in the executed path?**
**No.** Convergence of five independent execution facts: (i) patch targeted `/mnt/d/tools`, which the runner never sources; (ii) executed mirror was git-clean at every run start (`preflight.txt:7`); (iii) no `set_special_nets` in any of 12 echoed command streams; (iv) failed command is `pin_access` before the prescribed insertion point; (v) the command name is invalid in this OpenROAD build, so any executed invocation would have produced `invalid command name`, which never appears. Verdict: **FAILED / REFUTED** — D-013 was never in the path that reached the router. Because the dedicated `orfs_baseline_d013_20261118T160213Z` run is empty, any claim it executed is **NOT EVALUATED**.

**(c) Would command execution reach the router?**
No, twice over. Temporally: `pin_access` is the first DRT call and throws before any `global_route` invocation, and D-013 was specified *after* `pin_access`. Mechanically: `set_special_nets` is not a registered Tcl command here, so it would fail at parse/invoke time inside `global_route_helper` before TritonRoute could consume any designation. `log_cmd` does not catch errors, so such a failure would be fatal and visible — it is absent from every log.

**(d) Remaining uncertainty**
- Exact cause of the 2-line proc-line discrepancy in the stack trace (§4 finding 8); no alternate file copy exists and preflights were clean.
- No empirical test (prohibited here) of whether any *working* special-net mechanism suppresses DRT-0305, or of downstream routing feasibility; no `5_*.odb` exists in any run.
- Content/intent of the empty `orfs_baseline_d013_20261118T160213Z` run and of any un-preserved attempt; whether an unlogged, in-run edit ever existed cannot be excluded absolutely (preflight is a start-of-run snapshot only), though identical normalized logs across 12 runs strongly argue against it.
- Out of scope / not evaluated: root cause of `zero_` itself, correctness of reclassifying it, `assign_ground_net`/`set_nets_to_route` behavior, and pin-access geometry once routing starts.

---

## 6. Handoff to orchestrator

1. Treat the **path mismatch as confirmed by execution evidence**: D-013 edits landed in `/mnt/d/tools`; the runner sources `/mnt/d/SattvaRoute/tools`. Any future patch must be applied to the mirror *and* verified in that run's `preflight.txt` (`orfs_mirror_status` must show the change) and in the echoed command stream of `5_1_grt.log`.
2. Stop treating `set_special_nets` as the fix — it is not a command in this OpenROAD build (`invalid command name`). The DRT-0305 diagnostic wording is not evidence of a Tcl command's existence.
3. Any special-net designation must be issued **before** `pin_access` (before `global_route.tcl:66`); the proposal's "after `pin_access`" location is unreachable.
4. Preserve evidence for the next run: ensure `evidence/stage_route.log` and `work/logs/.../5_1_grt.log` are captured, and confirm the executed absolute path in the stack frame.
5. For the defect itself, coordinate with Agent D's handoff: `zero_` is a driverless constant-tie net with GROUND type and six macro SIGNAL sinks; a durable fix likely belongs at the netlist/tie-cell or net-classification layer, not in `global_route.tcl` bookkeeping. This agent did **not** verify any remedy.
6. Do not claim routing, extraction, timing, or signoff success — global routing has never completed in any preserved run.

## 7. Labels

| Item | Label |
|---|---|
| Executed script = mirror copy | **PASS** (execution evidence) |
| D-013 present in executed path | **FAIL** (refuted) |
| D-013 would reach router even if present | **FAIL** (wrong order + invalid command) |
| `set_special_nets` valid in this OpenROAD build | **FAIL** (directly disproved) |
| Mirror clean at all run starts | **PASS** |
| `zero_` GROUND / non-special in `4_cts.odb` | **PASS** (read-only DB) |
| Macro pin-access / routing feasibility after a fix | **NOT EVALUATED** |
| Empirical suppression of DRT-0305 by special-net designation | **NOT EVALUATED** |
| 2-line stack-trace discrepancy cause | **NOT EVALUATED** |
| Agent A modified only its assigned report | **PASS** |

— End of Agent A report.
