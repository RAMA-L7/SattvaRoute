# TASK_BOARD — all tasks

Status: QUEUED · IN_PROGRESS · BLOCKED · DONE · CANCELLED
Evidence = path to proof (log, report, artifact) — required for DONE.

| ID | Task | Owner | Status | Files | Registered | Evidence / notes |
|---|---|---|---|---|---|---|
| T-M0-001 | Environment audit | orchestrator | DONE | docs/milestone0-environment-audit.md | 2026-11-18 | audit doc |
| T-M0-002 | ORFS location + SYNTH_NETLIST_FILES verification | orchestrator | DONE | docs/milestone0-environment-audit.md | 2026-11-18 | synth_preamble.tcl:17 |
| T-M0-003 | OpenFinRAM build + v2lvs patch + macro generation | orchestrator | DONE | benchmark/design/OpenFinRAM | 2026-11-18 | run EXIT=0; GDS/LEF/LIB verified |
| T-M0-004 | Memory system (AGENTS/PROJECT_STATE/logs/coordination) | orchestrator | DONE | AGENTS.md, PROJECT_STATE.md, logs/*, coordination/* | 2026-11-18T18:50:42+05:30 | this repo |
| T-M1-001 | Phase A: macro inspection, controller RTL, synthesized netlist + provenance | orchestrator (EDA) | DONE | benchmark/design/sattva_sram/**, docs/benchmark/** | 2026-11-18T18:50:42+05:30 | netlist/sattva_ctrl_synth.v sha256 f3ae7aa3…4f0d; netlist/synth_provenance.txt (POSTCHECK PASS, `check -assert` 0 problems, 57 cells, 1 macro instance); docs/benchmark/macro-sram-x4x4x1.md; yosys_synth.log |
| T-M1-002 | Phase B: pinned ORFS config (netlist/LEF/LIB/GDS/SDC/PDN/layers) | EDA | DONE | config.mk, constraint.sdc, pdn_sattva.tcl, macro_placement.tcl, macro views | 2026-11-18T20:10+05:30 | all files written; D-009..D-011 + D-012 config done; baseline run captured |
| T-M1-003 | Phase C: baseline run + evidence capture → runs/ | EDA | IN_PROGRESS | runs/orfs_baseline_20261118T152845Z/ | 2026-11-18T15:28+05:30 | 6/7 stages pass; route DRT-0305 blocker investigated; D-013 set_special_nets verified by subagent (all 7 checks PASS) but does not complete routing through ORFS flow; new run attempted with same error; original baseline preserved immutable; next: document finding, determine alternate fix or workaround |
| T-M1-004 | Milestone 1C-R: DRT-0305 root-cause investigation + routing recovery | orchestrator + Agents A/B/C/D | DONE | reports/agent_{A,B,C,D}_*.md; MILESTONE_1C-R_DRT0305_ROOT_CAUSE_REPORT.md; docs/decisions/D-014_proposal.md; runs/orfs_baseline_20261118T171712Z/ | 2026-11-18T22:18:25+05:30 | Root cause adjudicated HIGH confidence; D-013 retired. D-014 approved + applied in mirror; run 17:17:12Z: DRT-0305 RESOLVED (snets 2→3), new blocker DRT-0073 (macro clk pin access). No second fix. Baseline immutable. |
| T-M1-005 | Milestone 1 report + PROJECT_STATE handoff | Documentation | QUEUED | logs/REPORT_LOG.md | | |