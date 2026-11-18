# ACTIVE_WORK — current tasks in progress

> Registered before work begins. Released when the task status is no longer IN_PROGRESS.
> Format: task ID · agent · files (locked) · started · status.

| Task | Agent | Files (locked) | Started | Status |
|---|---|---|---|---|
| T-M1-002 pinned ORFS config + baseline run | orchestrator (as EDA role) | `benchmark/design/sattva_sram/**` (except `netlist/`, `rtl/` — closed with T-M1-001), `runs/**` | 2026-11-18T20:10+05:30 | DONE; T-M1-001 released; lock removed |
| T-M1-003 baseline run | orchestrator (as EDA role) | `runs/**` (stage 1–5 done, rc=2 at route) | 2026-11-18T15:28+05:30 | IN_PROGRESS; route DRT-0305 blocker investigated; D-013 set_special_nets verified by subagent (all 7 checks PASS) but does not complete routing through ORFS flow; original baseline runs/orfs_baseline_20261118T152845Z preserved immutable; new run attempted with same DRT-0305 error; next: document finding, determine alternate fix or workaround |
| T-M1-004 | Milestone 1C-R DRT-0305 root-cause investigation | orchestrator + Agents A/B/C/D | Agents: read-only investigation (reports/ only). Orchestrator owns PROJECT_STATE.md, DECISIONS.md, ACTIVE_WORK.md, TASK_BOARD.md, logs/* | 2026-11-18T22:18:25+05:30 | DONE — D-014 approved/applied/tested; DRT-0305 resolved; new DRT-0073 blocker; no second fix. Agents released. Mirror global_route.tcl intentionally left patched (approved change, cd86b587…). |
| T-M1-005 | Milestone 1 report + PROJECT_STATE handoff | Documentation | QUEUED | logs/REPORT_LOG.md | |