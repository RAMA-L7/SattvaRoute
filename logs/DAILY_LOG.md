# DAILY_LOG — chronological engineering activity

Template per entry (see AGENTS.md session lifecycle):

```text
Date:
Session start:
Session end:
Agent/model:
Starting state:
Work performed:
Files changed:
Commands executed:
Verification:
Problems discovered:
Decisions made:
Current status:
Next action:
```

---

## 2026-11-18 — sessions M0-S001 (audit/baseline) and M1-S001 (this session)

```text
SESSION START
Project: SattvaRoute
Milestone: 1
Agent: orchestrator (EDA role for T-M1-001)
Model: mimo-v2.6-flash-free
Timestamp: 2026-11-18T18:50:42+05:30
Task: Establish shared memory system; Milestone 1 Phase A (macro inspection, controller benchmark, synthesized netlist)
Starting commit: none (repo not yet initialized — first commit = this state)
Files expected to change: AGENTS.md, PROJECT_STATE.md, docs/**, logs/**, coordination/**, benchmark/design/sattva_sram/**
Current project status: M0 complete; macro sram_x4x4x1 verified; no controller RTL or netlist yet
```

**M0 sessions (earlier same day, summarized):** environment audit; ORFS located
(`D:\tools\OpenROAD-flow-scripts`); OpenFinRAM clone/build/patch/run → EXIT=0 with
verified GDS/LEF/LIB; yowasp-yosys 0.71 + klayout bindings installed (user site);
`scripts/gen_sram_macro.sh` written; `docs/milestone0-environment-audit.md` written.

**This session (M1-S001) — work performed:**
- Created memory structure: `logs/{REVIEW,REPORT,DAILY,AGENT_ACTIVITY}.md`, `logs/sessions/`, `coordination/{ACTIVE_WORK,TASK_BOARD}.md`, `coordination/LOCKS/`, `docs/decisions/`, `artifacts/`
- Wrote `AGENTS.md` (rules, roles, lifecycle), `PROJECT_STATE.md` (snapshot), `docs/decisions/DECISIONS.md`
- Registered T-M1-001..005; acquired lock T-M1-001

**Phase A (T-M1-001) — completed this session:**
- Macro inspection: LEF pin/layer map (vdd/vss M3; clk/ce_n/oe_n/we_n/sdel/A M4; D/Q M3; OBS M1–M5; SYMMETRY X Y), Liberty timing-arc audit (13 setup/hold arcs vs clk, estimated flat 0.05 ns), GDS bbox/layers, **no Verilog model exists** → `rtl/sram_x4x4x1_bb.v` stub; `docs/benchmark/macro-sram-x4x4x1.md`
- `rtl/sattva_ctrl.v`: self-test FSM (4 writes of `{addr,~addr}`, readback compare) genuinely instantiating `sram_x4x4x1 u_sram`; address held during RD+CAP (macro Liberty has no read-latency arcs)
- Standalone synthesis with system Yosys 0.33 + ORFS ASAP7 TT/RVT libs; obstacles fixed en route (all recorded as **D-009**): `dfflibmap`/`abc` in 0.33 reject `-dont_use`; bundled `yosys-abc` segfaults (rc 139) in `buffer`/`&nf` → local `scripts/abc_map_sattva.script`; gz liberty crashes abc (rc 134) → gunzip to /tmp; false `check` "no driver" warnings → `read_liberty -lib` all cells first
- Result: SYNTH_EXIT=0, `check -assert` **0 problems**, 57 cells (10 DFF + 46 comb + 1 macro), area 6.1965 µm², netlist sha256 `f3ae7aa3538191fd31c28957e415702a2660953acb1bf92d3a9c3a75b1ab4f0d`, full provenance (tool versions + sha256 of 8 inputs); macro views copied to stable `benchmark/design/sattva_sram/macro/`; TASK_BOARD T-M1-001 → DONE, lock released

**Phase B (T-M1-002) — in progress:**
- Wrote `benchmark/design/sattva_sram/config.mk` (DESIGN_NAME sattva_ctrl, CORNER=TC to match TT synth libs, SYNTH_NETLIST_FILES short-circuit, ADDITIONAL_{LEFS,LIBS,GDS} → macro/, DIE/CORE 30×30 explicit because the design is smaller than the macro, MACRO_PLACE_HALO 4 4, WORK_HOME default pinned to `/mnt/d/SattvaRoute/runs/orfs`)
- Wrote `constraint.sdc` (950 ps clock = synthesis `if -D 950` target, io 12.5%) and `pdn_sattva.tcl` (**D-011**: lowercase `vdd`/`vss` global connects, macro grid M3↔M5 instead of M4↔M5)
- **Blocker discovered:** the `D:\tools` ORFS checkout is fully CRLF (Windows git `core.autocrlf=true`) → shebang scripts fail under WSL (`/usr/bin/env: 'bash\r': No such file or directory`), including during `make -n`; GNU make 4.3 itself tolerates CRLF (probe: variables/recipes strip `\r`)
- **D-010:** creating an LF execution mirror `D:\SattvaRoute\tools\OpenROAD-flow-scripts` (clone of the same commit 25b6429) — `D:\tools` never modified; pre-existing uncommitted diff in `flow/platforms/sky130hd/lib/*` noted (asap7 flow unaffected, source-of-truth clone takes committed state)
- Environment facts for the run: `openroad` at `/usr/local/bin/openroad` (bazel-nostamp), `yosys` 0.33 at `/usr/bin/yosys` → must pass `OPENROAD_EXE`/`YOSYS_EXE` (defaults point at non-existent `tools/install/`), **klayout not installed** (finish/GDS merge will need it — pending), `check-yosys`/`check-openroad` gate on executability only

(Entry continues below as work proceeds.)

```text
SESSION END
Timestamp: (filled at end of session)
Completed: (filled at end of session)
Incomplete: (filled at end of session)
Verification: (filled at end of session)
Current milestone: (filled at end of session)
Next recommended action: (filled at end of session)
Safe for another agent to continue: (filled at end of session)
```

--- D-013 Fix Attempt (2026-11-18) ---
D-013: set_special_nets [list zero_] added to global_route.tcl
Subagent verification: all 7 checks PASS (net exists, GROUND type, command valid, insertion point, isolation, no false classification, baseline preserved)
ORFS flow result: DRT-0305 error persists despite command; same error at route stage rc=2
Original baseline: runs/orfs_baseline_20261118T152845Z preserved immutable (6/7 stages pass)
New run: attempted with same DRT-0305 error
Finding: set_special_nets command valid per ORFS error message but ORFS execution model prevents taking effect on TritonRoute; alternate fix approach needed

--- SESSION START — T-M1-004 / Milestone 1C-R (2026-11-18T22:18:25+05:30) ---
Date: 2026-11-18
Session start: 2026-11-18T22:18:25+05:30 (UTC 2026-11-18T16:48:25Z)
Agent/model: orchestrator (Hy4 flash Free) + 4 independent subagents (A/B/C/D)
Starting state: T-M1-003 IN_PROGRESS; D-013 recorded as verified-but-ineffective; original baseline runs/orfs_baseline_20261118T152845Z immutable; both global_route.tcl copies confirmed clean (no set_special_nets) at session start; runner MIRROR = /mnt/d/SattvaRoute/tools/OpenROAD-flow-scripts.
Work performed (so far): mandatory initialization reads done; T-M1-004 registered (repurposed queued Phase-D review row); this SESSION START logged.
Files changed (so far): coordination/TASK_BOARD.md, coordination/ACTIVE_WORK.md, logs/DAILY_LOG.md, logs/AGENT_ACTIVITY.md, logs/sessions/ handoff.
Commands executed: date -u; grep both global_route.tcl copies for set_special_nets; grep runner MIRROR/FLOW.
Verification: direct grep + file reads; no flow-script edits made.
Problems discovered: KEY LEAD — all prior D-013 edits targeted /mnt/d/tools (D:\tools) but the runner executes /mnt/d/SattvaRoute/tools (D-010 mirror); this is a candidate explanation for D-013 failure, to be confirmed by Agent A with execution evidence.
Decisions made: none new yet; no fix applied; approval gate remains.
Current status: T-M1-004 IN_PROGRESS; 4 subagents to launch.
Next action: launch Agents A/B/C/D; integrate; adjudicate root cause; propose new decision ID only if evidence supports it.

--- SESSION END (investigation phase) — T-M1-004 / Milestone 1C-R (2026-11-18T22:39:01+05:30) ---
Work performed: launched Agents A (execution path), B (zero_ DB trace), C (special-net mechanism), D (independent analysis) with disjoint read-only scopes; all 4 delivered evidence-backed reports. Adjudicated root cause: zero_ is a mis-typed constant-tie net (GROUND, non-special) from SYNTH_NETLIST_FILES bypass of hilomap; DRT guard io.cpp:1040 rejects it at pin_access. D-013 retired (command nonexistent, wrong checkout D:\tools vs mirror, wrong order after pin_access, empty evidence). Read-only runtime probe confirmed $net setSpecial callable (rc=0, isSpecial 0→1). Authored D-014 proposal + MILESTONE_1C-R_DRT0305_ROOT_CAUSE_REPORT.md.
Files changed: coordination/TASK_BOARD.md, coordination/ACTIVE_WORK.md, PROJECT_STATE.md, docs/decisions/DECISIONS.md, docs/decisions/D-014_proposal.md, MILESTONE_1C-R_DRT0305_ROOT_CAUSE_REPORT.md, logs/DAILY_LOG.md, logs/AGENT_ACTIVITY.md, logs/REVIEW_LOG.md, logs/REPORT_LOG.md, logs/sessions/M1C-R_S001_handoff.md, reports/agent_{A,B,C,D}_*.md (subagents).
Verification: 4 independent reports cross-checked; source-level (io.cpp:1040, dbReadVerilog.cc:768-773, OpenRoad.tcl:407-413, VerilogReader.cc:117/2019-2020), DB-level verbatim ODB dumps, execution logs, runtime probe. No flow run performed.
Problems discovered: prior D-013 "7/7 PASS" validity claim was circular (inferred from DRT text); set_special_nets absent from build; wrong checkout; insertion point unreachable.
Decisions made: D-013 recorded as FAILED/RETIRED; D-014 PROPOSED (approval required); no fix applied.
Current status: T-M1-004 investigation DONE; approval gate open; global routing still BLOCKED at DRT-0305; original baseline immutable.
Next action: obtain approval for D-014, then controlled run; or close with blocker documented.
Safe for another agent to continue: YES — no in-progress edits; all evidence preserved.

--- D-014 controlled experiment (2026-11-18T22:47:00+05:30 / UTC 17:17Z) ---
Approval: user approved "D-014 + controlled run" before any edit/run.
Applied: exact D-014 diff to execution mirror global_route.tcl; hash 3968898c... -> cd86b587...; D:\tools unchanged; preflight shows mirror modified. Original baseline stage_route.log hash unchanged (2dd7a167...).
Run: runs/orfs_baseline_20261118T171712Z (unique runner ID).
Result: DRT-0305 RESOLVED (absent from 5_1_grt.log; snets 2->3, nets 75->72 = zero_ now SPECIAL). NEW blocker: DRT-0073 No access point for u_sram/clk, at pin_access, source FlexPA_acc_point.cpp:1524-1533; preceded by DRT-0419 warnings on macro D/Q pin centers. Route rc=2; no 5_*.odb or route.guide.
Action: STOP per directive; no second speculative fix applied. DRT-0073 requires a new decision ID + approval and separate evidence.
Status: T-M1-004 DONE; global routing BLOCKED (new cause); extraction/timing NOT EVALUATED; signoff not claimed.

--- SESSION START — T-FDE-001 / FDE adoption (2026-11-19) ---
Agent/model: orchestrator (Hy4 flash Free) + 3 read-only reviewers (R1 runner, R2 approval/state, R3 engineering validity)
Starting state: live tree uncommitted; public repo at eb8ba8e; runner always exited 0, second-resolution run IDs, non-blocking preflight, patch unhashed.
Work performed: independent read-only inspection; rewrote scripts/run_baseline_orfs.sh (exit propagation, atomic nanosecond+PID run IDs, enforced preflight, exact-binary/binary hash/patch fingerprinting, preflight.json/mirror.patch/run.json, hash all artifacts, SATTVA_* parameterisation); added tests/test_runner.sh (14 offline stub tests); synced to public repo README/architecture; committed 43ffebb and pushed.
Verification: bash -n OK; tests 14 PASS / 0 FAIL in both live and published trees; no EDA flow run; no RTL/netlist/SDC/config/routing change.
Problems discovered: prior runner returned 0 on failure (R1 F1), collisions (F2), preflight not gating (F3), D-014 patch not fingerprinted (F5); approval remains documented-only, no machine-readable state, no parsers (R2); constant tie still physically undriven, macro pin access fails DRT-0073 (R3).
Decisions made: FDE milestone 1 = runner reliability first; no LangGraph/dashboard added; no EDA fix applied.
Current status: T-FDE-001 DONE; T-M1-004 remains DONE with DRT-0073 blocker unchanged.
Next action: FDE milestone 2 — machine-readable approval binding + exact-patch gate, then one automated diagnosis path.
Safe for another agent to continue: YES; lock released.

--- SESSION END — T-FDE-001 (2026-11-19) ---
Completed: runner reliability + offline test suite, published as 43ffebb.
Incomplete: approval enforcement in code, structured state beyond run.json, report parsers, DRT-0073 investigation.
Verification status: 14/14 offline tests PASS; remote commit 43ffebb == local main; working tree clean in publish tree.
Files modified: live scripts/run_baseline_orfs.sh, tests/test_runner.sh, coordination/*, logs/DAILY_LOG.md; publish README.md, docs/architecture.md, scripts/run_baseline_orfs.sh, tests/test_runner.sh.
Known problems: DRT-0073 still blocks global routing; zero_ remains physically undriven; two demo scripts fail py_compile; stale status docs still need correction.
Commit status: publish 43ffebb pushed; live tree uncommitted by design (working tree with local evidence).

--- SESSION START — T-FDE-002 / exact-patch approval enforcement (2026-11-19) ---
Agent/model: orchestrator (Hy4 flash Free)
Starting state: publish HEAD 43ffebb; live tree uncommitted; no approval code, no machine-readable approval record, two demo scripts failed py_compile, stale status claims present.
Work performed: verified current revision and ORFS Makefile stage inputs; added scripts/sattva_approval.py (durable approval schema, deterministic validator, narrow atomic unified-diff application with backup/rollback, ledger reuse rejection, scope validation); added state/approval_policy.json; wired guard into scripts/run_baseline_orfs.sh (validate+revalidate+apply before stages, second revalidation, scoped stages, source-artifact check); added tests/test_approval.py (25 offline tests); corrected PROJECT_STATE.md, MILESTONE_ASSESSMENT.md (historical banner), D-014 proposal header/claims, TASK_BOARD/ACTIVE_WORK stale D-013 claim; fixed failure_case_1_workflow.py syntax + dry-run default + SIMULATED label; retired routing_fix_demo.py with explicit explanation.
Verification: 25/25 approval tests PASS; 14/14 runner tests still PASS; py_compile OK for new/fixed scripts; bash -n OK; dry-run demo left config.mk hash unchanged; no EDA flow run.
Safety: no RTL/netlist/SDC/macro/PDN/placement/layer/parameter change; D-014 patch untouched; DRT-0073 fix not attempted; no approval was fabricated for a real operation.
Current status: T-FDE-002 milestone implemented and offline-verified; publication pending.
Next action: sync to public repo, commit focused milestone, push, verify remote.
Safe for another agent to continue: YES.

--- SESSION END — T-FDE-002 (2026-11-19) ---
Completed: approval records + validator + narrow applier + runner gate + 25 offline tests + status/demo corrections.
Incomplete: no real EDA recovery run; no real approval for any actual patch; no dashboard; DRT-0073 remains blocked.
Verification status: 25/25 + 14/14 offline tests PASS; no fabricated approvals; remote verification after push recorded below.
Files modified: scripts/sattva_approval.py, scripts/run_baseline_orfs.sh, state/approval_policy.json, tests/test_approval.py, scripts/failure_case_1_workflow.py, scripts/routing_fix_demo.py, PROJECT_STATE.md, coordination/ACTIVE_WORK.md, coordination/TASK_BOARD.md, coordination/MILESTONE_ASSESSMENT.md, docs/decisions/D-014_proposal.md, logs/DAILY_LOG.md, logs/AGENT_ACTIVITY.md.
Known problems: approval ledger is JSONL append-only (single-process serialization via target lock only); no UI; scope validation requires explicit operator-declared contiguous scope; DRT-0073 unresolved.
Commit status: public commit 4aa059591811fcbe20ca657fd6aa1cb67211d588 pushed to origin/main (43ffebb..4aa0595); remote HEAD verified equal to local; publish working tree clean after final state sync.
