# ACTIVE_WORK — current tasks in progress

> Registered before work begins. Released when the task status is no longer IN_PROGRESS.
> Format: task ID · agent · files (locked) · started · status.

| Task | Agent | Files (locked) | Started | Status |
|---|---|---|---|---|
| T-M1-002 pinned ORFS config + baseline run | orchestrator (as EDA role) | `benchmark/design/sattva_sram/**` (except `netlist/`, `rtl/` — closed with T-M1-001), `runs/**` | 2026-11-18T20:10+05:30 | DONE; T-M1-001 released; lock removed |
| T-M1-003 baseline run | orchestrator (as EDA role) | `runs/**` (stage 1–5 done, rc=2 at route) | 2026-11-18T15:28+05:30 | CLOSED/superseded by T-M1-004. Immutable baseline `runs/orfs_baseline_20261118T152845Z` (6/7 stages pass, route rc=2 DRT-0305). Earlier "D-013 all 7 checks PASS" note was static-text verification and is REFUTED — see DECISIONS.md D-013. Corrected 2026-11-19. |
| T-M1-004 | Milestone 1C-R DRT-0305 root-cause investigation | orchestrator + Agents A/B/C/D | Agents: read-only investigation (reports/ only). Orchestrator owns PROJECT_STATE.md, DECISIONS.md, ACTIVE_WORK.md, TASK_BOARD.md, logs/* | 2026-11-18T22:18:25+05:30 | DONE — D-014 approved/applied/tested; DRT-0305 resolved; new DRT-0073 blocker; no second fix. Agents released. Mirror global_route.tcl intentionally left patched (approved change, cd86b587…). |
| T-FDE-001 | Runner correctness + isolated attempts + offline tests | orchestrator | `scripts/run_baseline_orfs.sh`, `tests/test_runner.sh`; lock released | 2026-11-19 | DONE — 14/14 offline tests PASS; pushed as public commit 43ffebb |
| T-FDE-002 | Exact-patch approval enforcement + state integrity | orchestrator | `scripts/sattva_approval.py`, `scripts/run_baseline_orfs.sh`, `state/**`, `tests/test_approval.py`, docs/status files; lock released | 2026-11-19 | DONE — 25/25 + 14/14 offline tests PASS; public commits 4aa0595, fc10d59; no EDA run |
| T-FDE-003 | Real baseline validation of hardened runner | orchestrator + Agents A/B/C/D | Agents: read-only pre/post audits (temp reports only). Orchestrator owns coordination/state/logs and launched the single EDA run. | 2026-11-19 | DONE — real run rc=2 validated state/artifacts/exit propagation; route FAIL DRT-0073; lock released; agents released |
| T-FDE-004 | DRT-0073 macro pin-access root-cause investigation | orchestrator + Agents A/B/C/D | Agents: read-only investigation, temp reports only. Orchestrator owns coordination/state/logs/docs. | 2026-11-19 | DONE — ROOT CAUSE PROBABLE adjudicated; D-015 finding recorded; lock released; no fix/run/design change |
| T-M1-005 | Milestone 1 report + PROJECT_STATE handoff | Documentation | QUEUED | logs/REPORT_LOG.md | |