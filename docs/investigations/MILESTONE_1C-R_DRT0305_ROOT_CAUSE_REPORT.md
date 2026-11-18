# MILESTONE 1C-R — DRT-0305 Root Cause Investigation and Routing Recovery

- **Task:** T-M1-004 (Milestone 1C-R)
- **Investigation window:** 2026-11-18T22:18:25+05:30 → 2026-11-18T22:39:01+05:30
- **Orchestrator:** orchestrator (Hy4 flash Free)
- **Investigators:** Agent A (execution path), Agent B (net/DB trace), Agent C (special-net mechanism), Agent D (independent failure analysis)
- **Evidence policy:** all findings from actual logs, DBs, installed source, and read-only runtime probes; no fabricated metrics. Status labels: PASS / FAIL / BLOCKED / NOT EVALUATED.

---

## 1. Executive summary

**Root cause adjudicated (high confidence):** DRT-0305 is a **database-state defect caused by a mis-typed logical constant-tie net**, not a routing-algorithm failure and not a PDN configuration error. The pre-synthesized netlist carries raw constant-zero literals on macro SIGNAL input pins. Because `SYNTH_NETLIST_FILES` short-circuits Yosys, `hilomap` tie-cell insertion never runs. OpenROAD's Verilog reader creates a net named `zero_`, types it `GROUND`, but never sets its SPECIAL bit. TritonRoute's DB importer rejects any supply-typed net that is not SPECIAL — hence DRT-0305 at `pin_access`.

**Why D-013 failed (four independent reasons, all evidence-backed):**
1. `set_special_nets` **does not exist** in this OpenROAD build (absent from source, ORFS tree, and binary; direct invocation → `invalid command name`). The prior "7/7 checks PASS" inferred validity circularly from the DRT diagnostic text.
2. All D-013 edits targeted `/mnt/d/tools` (`D:\tools`), but the runner sources the LF mirror `/mnt/d/SattvaRoute/tools` (D-010). The mirror was git-clean at every run start.
3. The proposed insertion was **after** `pin_access` — dead code, since `pin_access` is the call that raises the error.
4. The dedicated D-013 run has empty `evidence/` and `work/` — no preserved execution proof.

**New fix:** D-014 — mark `zero_` SPECIAL via the OpenDB object method `$net setSpecial` in the **execution mirror** `global_route.tcl` immediately before `pin_access`. A read-only in-memory probe confirmed the primitive is callable (`rc=0`, `isSpecial` 0→1).

**Status:** D-014 was **approved and applied**. In the controlled run `runs/orfs_baseline_20261118T171712Z`, **DRT-0305 was eliminated** (`snets` 2→3, `zero_` reclassified SPECIAL). Global routing then failed on a **distinct** blocker: `DRT-0073 No access point for u_sram/clk`. Per the directive, no second fix was applied. Original baseline preserved immutable.

| Verdict item | Status |
|---|---|
| Root cause adjudicated | PASS |
| D-013 failure explained | PASS |
| Execution path traced | PASS |
| `zero_` DB state traced | PASS |
| Special-net mechanism understood | PASS |
| Independent analysis integrated | PASS |
| New minimal fix proposal | PASS (D-014) |
| Approval obtained | PASS (user approved D-014 + controlled run) |
| Recovery experiment | PASS (executed, `runs/orfs_baseline_20261118T171712Z`) |
| DRT-0305 elimination | **PASS** (no DRT-0305 in new run) |
| Global routing | **BLOCKED — new cause DRT-0073** (macro `clk` pin access) |
| Detailed routing / extraction / timing | NOT EVALUATED (never reached) |
| Signoff | NOT CLAIMED |

---

## 2. Task and subagent assignments

| Agent | Scope | Deliverable | Status |
|---|---|---|---|
| A | ORFS execution path, source order, command execution, DB effect | `reports/agent_A_orfs_execution_path.md` | DONE |
| B | `zero_` net trace across synth→floorplan→place→CTS→GRT | `reports/agent_B_zero_net_database_trace.md` | DONE |
| C | Installed ORFS/TritonRoute special-net mechanism, source and docs | `reports/agent_C_special_net_mechanism.md` | DONE |
| D | Independent challenge to the root-cause hypothesis | `reports/agent_D_independent_failure_analysis.md` | DONE |
| Orchestrator | Coordination, integration, adjudication, D-014 proposal, records | this report + `docs/decisions/D-014_proposal.md` | DONE (pre-gate) |

File ownership was disjoint: subagents wrote only their assigned report; orchestrator alone owns `PROJECT_STATE.md`, `DECISIONS.md`, `ACTIVE_WORK.md`, `TASK_BOARD.md`, and logs.

## 3. Investigation scope

In scope: execution path, DB state, special-net mechanism, D-013 retrospective, minimal fix proposal. Out of scope by directive: RTL/netlist/macro/SDC edits, baseline modification, speculative fix stacking, flow execution during investigation.

## 4. ORFS execution-path findings (Agent A — PASS)

- Runner `scripts/run_baseline_orfs.sh:17–18` pins `MIRROR=/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts`, `FLOW=$MIRROR/flow`.
- `evidence/stage_route.log:1`: `make: Entering directory '/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow'`; `:17` `flow.sh 5_1_grt global_route`; Tcl stack frame (`:55`, and `5_1_grt.log:42`): `(file "/mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts/flow/scripts/global_route.tcl" line 188)`.
- Source chain: `global_route.tcl:1–4` (load util + report_metrics, `load_design 4_cts.odb 4_cts.sdc`) → `proc global_route_helper` (line 8) → `global_route.tcl:188` top-level call → `log_cmd pin_access` (line 66). Single OpenROAD process (one banner); no separate routing context.
- `log_cmd` (`util.tcl:6–28`) echoes commands via `uplevel 1` without `catch`; an invalid command would abort fatally and be visible. No log contains `set_special_nets`.
- All 12 preserved route logs echo the same command stream (`source liberty_suppressions → read_liberty ×6 → read_db → read_sdc → source setRC → pin_access`), with no D-013 command; `preflight.txt:7` = `orfs_mirror_status: []` for every run.
- Both `global_route.tcl` copies are byte-identical, sha256 `3968898c9abd8c0fd56c50d08bed6d3943bdc641f63c8674817449bbec2706ce`, git-clean.
- STATIC vs EXECUTION evidence is explicitly separated in Agent A's report; the executed-path conclusions are EXECUTION-backed.

## 5. Net database trace (Agent B — PASS)

| Stage | `zero_` present | `sigType` | `isSpecial` | Connectivity |
|---|---|---|---|---|
| `1_synth.odb` | YES (earliest) | GROUND | 0 | 0 BTerm / 6 ITerm / 0 SWire / wire=NULL |
| Floorplan pre-PDN | YES | GROUND | 0 | unchanged |
| Floorplan post-PDN (`2_4_floorplan_pdn.odb`) | YES | GROUND | 0 | unchanged; PDN adds separate VDD/VSS |
| `3_place.odb` | YES | GROUND | 0 | unchanged |
| `4_cts.odb` (GRT input) | YES | GROUND | 0 | unchanged |
| GRT failure | same net per `5_1_grt.log:13` | GROUND | 0 | no `5_1_grt-failed.odb` exists (BLOCKED) |

- The 6 ITerms are all on `u_sram` (`sram_x4x4x1`): `sdel[3:0]`, `A[3]`, `A[2]` — LEF `DIRECTION INPUT / USE SIGNAL`, **not** the macro ground pin.
- Macro ground pin `vss` is on net `VSS` (GROUND, special=1, 283 ITerms, 1187 shapes); power `vdd` on `VDD` (POWER, special=1). No `zero`/`GND`/`gnd`/standalone `vss` net exists; lowercase names are pin names, not nets.
- `zero_` has no routing geometry at all. It is the same net object at CTS and at the failing global route.
- Netlist: `.A({ 2'h0, \A[1], \A[0] })`, `.sdel(4'h0)`; RTL `assign sdel = 4'b0000`. No literal `zero_` string in Verilog — the name is created by OpenROAD's reader.

## 6. Special-net mechanism (Agent C — PASS)

- Versions: ORFS `25b6429c1644a8682852646bebf19ff164402c76` in both trees; OpenROAD `bazel-nostamp` from source `629aa76b94ae420170d18692016a7be9101a53e7`; Yosys 0.33.
- DRT-0305 source: `drt/src/io/io.cpp:1040` — `if (!is_special && db_net->getSigType().isSupply())` → error 305. `isSupply()` = POWER/GROUND (`odb/src/db/dbTypes.cpp:392–397`). Called via `pin_access` → `TritonRoute::pinAccess()` → `initDesign()` → `readDesign()` → `setNets()` → `addNet()`; stage stack trace matches.
- `set_special_nets`: zero matches in OpenROAD source, ORFS tree, and binary strings → **not a command in this build**.
- Supported mechanism: `add_global_connection -net <n> ... -power|-ground` + `global_connect`; implemented at `OpenRoad.tcl:407–413` as `$net setSpecial` + `$net setSigType POWER|GROUND`. ORFS invokes it in the PDN stage (`pdn.tcl:6`, `PDN_TCL`). DEF `SPECIALNETS` round-trips the bit (`definSNet.cpp:37`, `defout_impl.cpp:141`).
- `PWR_NETS_VOLTAGES`/`GND_NETS_VOLTAGES` are IR-drop-only, not special-net controls. No `SPECIAL_NETS`/`PDN_NETS` flow variable exists.
- `zero_` origin in source: `VerilogReader.cc:117` (`zero_net_name_("zero_")`), `:2019–2020` (`addConstantNet(..., LogicValue::zero)`); `dbReadVerilog.cc:768–773` sets `GROUND` sigtype but never `setSpecial()`.
- Official web documentation NOT EVALUATED (HTTP 402 / 404); in-tree exact-build source and docs used instead — stronger evidence for this version.

## 7. Independent analysis (Agent D — PASS)

- PARTIAL AGREE: the immediate DRT check condition is exactly `sigType=GROUND && isSpecial=0` at design-read time, before routing geometry.
- DISAGREE: `zero_` is not a genuine ground net and not CTS-created; it is a driverless constant-tie net (matches `RSZ-0020 found 1 floating nets`, `3_4_place_resized.log:31–32`). Marking it special would freeze the misclassification and leave six macro inputs physically undriven — a mask, not a durable design fix.
- The proposed command does not exist; D-013's failure is better explained by invalid command + wrong checkout + empty evidence.
- Upstream root cause: `SYNTH_NETLIST_FILES` bypass of `hilomap` tie-cell insertion.
- Ruled out: PDN/macro PG defects, DB inconsistency, net-type-change warnings, macro M3 PG pin access as the *trigger*.
- NOT EVALUATED: empirical suppression of DRT-0305 by any special-net designation; downstream macro pin-access feasibility; detailed routing/extraction/timing.

## 8. D-013 retrospective

| Dimension | Finding | Label |
|---|---|---|
| Command validity | `set_special_nets` absent from source/ORFS/binary; `invalid command name` on invoke | FAIL |
| Command execution | Never in executed file; mirror clean at all run starts; absent from 12 command streams | FAIL |
| Database effect | None — never executed | FAIL |
| Effect reaching router | None — also placed after the failing `pin_access` | FAIL |
| Prior "7/7 checks PASS" | Static-text verification only; validity inferred circularly from DRT text | FAIL |
| Dedicated D-013 run evidence | `orfs_baseline_d013_20261118T160213Z` empty evidence/work | NOT EVALUATED |

D-013 remains documented as a failed execution attempt in `docs/decisions/DECISIONS.md`; not overwritten.

## 9. Evidence-backed root cause (A–F)

**A. What is failing?** `drt::pin_access_cmd` at `5_1_grt`, during DRT DB import (`io::Parser::addNet`, `io.cpp:1040`), before any routing geometry or `global_route` call.

**B. Why?** `4_cts.odb` contains `zero_` with `sigType=GROUND, isSpecial=0`. Origin: raw constant-zero literals in the pre-synthesized netlist drive macro SIGNAL input pins; `SYNTH_NETLIST_FILES` bypasses `hilomap`; OpenROAD types the constant net GROUND without setting SPECIAL. DRT's importer guard rejects supply-typed non-special nets.

**C. Why D-013 failed?** Four independent causes: nonexistent command, wrong checkout (`D:\tools` vs mirror), wrong order (after `pin_access`), no preserved evidence. Command validity / execution / DB effect / router effect are all FAIL.

**D. Where must correction occur?** The DB must have `zero_` SPECIAL (or non-supply) before the first DRT call. Earliest correct stage: PDN (2_4) or netlist import. Under the investigation constraints (no RTL/netlist/macro/SDC edits), the viable intervention is in the execution mirror's `global_route.tcl` before `pin_access` (line 66).

**E. Smallest valid fix?** D-014: guarded `$net setSpecial` on `zero_` in the mirror `global_route.tcl` before `pin_access`. Confirmed callable in-memory (`rc=0`, `isSpecial` 0→1). One logical change; no design files touched.

**F. What could it affect?** Files: mirror `global_route.tcl` only; `D:\tools` untouched. Stages: `5_1_grt` entry only. Side effects: `zero_` becomes GROUND+SPECIAL (DRT preserves it); the six macro signal inputs remain without physical tie geometry → possible detailed-route opens/DRC. Reversibility: `git checkout` or delete 5 lines. Risk: low for global routing; unknown for detailed routing. Verification: report-level, new run ID, preflight + echoed stream + artifact checks per D-007.

## 10. Root cause confidence

**HIGH** — four independent agents converged on the same DB state and mechanism, with source-level (`io.cpp`, `dbReadVerilog.cc`, `OpenRoad.tcl`), DB-level (verbatim ODB dumps), and execution-log evidence, plus a direct runtime probe of the proposed primitive. The D-014 run confirmed the fix's efficacy against DRT-0305. Residual uncertainty now concerns the *new* DRT-0073 macro pin-access failure and downstream route feasibility (NOT EVALUATED — separate investigation required).

## 11. New fix proposal

`docs/decisions/D-014_proposal.md` — full proposal with before/after diff, side effects, rollback, verification plan.

## 12. Approval status

**APPROVED** — user selected "Approve D-014 + controlled run" before any edit or run. D-013 remains recorded as `Failed / retired`; D-014 is recorded as `APPLIED — partial success; new blocker DRT-0073`.

## 13. Experiment results

**Executed:** `runs/orfs_baseline_20261118T171712Z` (unique ID, runner-generated).
- Mirror hash `3968898c…` → `cd86b587…`; `D:\tools` unchanged (`3968898c…`); `preflight.txt` shows `orfs_mirror_status: [ M flow/scripts/global_route.tcl]`; original baseline `stage_route.log` hash unchanged.
- **DRT-0305 RESOLVED** — absent from `5_1_grt.log`; `Number of snets: 3` (vs 2 before), `Number of nets: 72` (vs 75) confirm `zero_` became SPECIAL.
- **New blocker:** `[ERROR DRT-0073] No access point for u_sram/clk (sram_x4x4x1).` (`5_1_grt.log:108`; `flexPA_acc_point.cpp:1524–1533`, zero access points for the inst-term). Preceded by DRT-0419 warnings for macro `D[0..3]`/`Q[0..3]` pin centers.
- Route rc=2; no `5_*.odb`, no `route.guide`. STOP — no second speculative fix applied.

## 14. Routing status

- Original baseline `runs/orfs_baseline_20261118T152845Z`: 6/7 stages pass; route rc=2 DRT-0305 (immutable).
- D-014 run `runs/orfs_baseline_20261118T171712Z`: route rc=2 **DRT-0073** (macro clock-pin access) — DRT-0305 resolved, but global routing not complete.
- No run has ever produced a `5_*.odb` or `route.guide`.

## 15. Detailed routing status

NOT EVALUATED — global routing never completed.

## 16. Extraction status

NOT EVALUATED — requires successful routing first.

## 17. Timing status

NOT EVALUATED — no final timing reports; setup/hold WNS/TNS unavailable. Signoff not claimed.

## 18. Metrics and violations

- Violation: DRT-0305 (`zero_`, GROUND, non-special) at `pin_access`.
- Floating-net warning: `RSZ-0020 found 1 floating nets` (`zero_`).
- No congestion/overflow/wirelength/WNS/TNS metrics — flow stopped before detailed routing. No fabricated values.

## 19. Artifact paths

- Subagent reports: `reports/agent_{A,B,C,D}_*.md`
- D-014 proposal: `docs/decisions/D-014_proposal.md`
- Decision index: `docs/decisions/DECISIONS.md`
- Session handoff: `logs/sessions/M1C-R_S001_handoff.md`
- Original immutable baseline: `runs/orfs_baseline_20261118T152845Z/`
- Failed D-013-era runs preserved (e.g. `runs/orfs_baseline_20261118T163553Z/`, `runs/orfs_baseline_20261118T163746Z/`, empty `runs/orfs_baseline_d013_20261118T160213Z/`)
- Runtime probe: `<temp>/opencode/probe_setspecial.tcl` (read-only, in-memory)

## 20. Limitations

- No recovery run performed (approval gate).
- No official web documentation for DRT-0305 obtainable (HTTP 402/404); in-tree source used.
- `5_1_grt-failed.odb` does not exist in any run (DRT aborts in `pin_access` before writing a DB); failure-moment state inferred from the stage log plus its documented input `4_cts.odb`.
- Empirical suppression of DRT-0305 by `setSpecial`, and downstream macro pin-access/DRC, remain untested.

## 21. Updated project state

`PROJECT_STATE.md`, `coordination/TASK_BOARD.md`, `coordination/ACTIVE_WORK.md`, `logs/DAILY_LOG.md`, `logs/AGENT_ACTIVITY.md`, `logs/REVIEW_LOG.md`, `logs/REPORT_LOG.md`, and `docs/decisions/DECISIONS.md` updated to reflect T-M1-004 completion (investigation phase), D-013 retirement, and D-014 pending approval.

## 22. Recommended next action

1. **CLOSED for this directive:** D-014 was approved, applied, and tested. DRT-0305 is verified eliminated; global routing remains BLOCKED by a new, distinct cause (DRT-0073). No second fix applied, as required.
2. Open a **new investigation and new decision ID** (e.g. D-015) for DRT-0073: macro `u_sram/clk` pin on M4 has no generated access point, with DRT-0419 warnings that no routing tracks pass through macro `D`/`Q` pin centers. Likely a macro-LEF/track-alignment or pin-access geometry issue — must be verified with evidence before any change.
3. Do **not** change routing layers, macro placement, LEF, or constraints without that separate evidence and fresh approval.
4. Re-run with a new unique run ID only after that approval; verify at report level (D-007) before claiming routing/extraction/timing success.
5. Original baseline and all failed attempts remain preserved as immutable evidence.
