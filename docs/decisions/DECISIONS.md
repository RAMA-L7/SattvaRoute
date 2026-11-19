# DECISIONS — index

| ID | Decision | Date | Status |
|---|---|---|---|
| D-001 | Flow engine = existing ORFS clone (not OpenLane 2) | 2026-11-18 | Active |
| D-002 | Benchmark = ASAP7 + OpenFinRAM real SRAM; FakeRAM kept as fallback | 2026-11-18 | Active |
| D-003 | ORFS canonical path = `D:\tools\OpenROAD-flow-scripts` (user-moved during M0) | 2026-11-18 | Active |
| D-004 | Calibre `v2lvs` fatal→warning patch in OpenFinRAM (SPICE/LVS only; disclosed in reports) | 2026-11-18 | Active |
| D-005 | OpenFinRAM runs on yowasp-yosys 0.71 via per-run PATH shim; system Yosys 0.33 untouched | 2026-11-18 | Active |
| D-006 | WSL memory stays at default 7.6 GiB; revisit only on OOM evidence | 2026-11-18 | Active |
| D-007 | Exit code 0 is never sufficient evidence — baseline success requires report-level verification (Phase D) | 2026-11-18 | Active |
| D-008 | Memory/logging system (this system) is mandatory for every agent/model/session | 2026-11-18 | Active |
| D-009 | Local ABC script `scripts/abc_map_sattva.script` (`strash`/`if -D 950`/`map`) replaces ORFS `abc_speed.script` — yosys 0.33's bundled `yosys-abc` segfaults (rc 139) in `buffer`/`&nf` with ASAP7 NLDM libs; gz liberty must be gunzipped first (rc 134) | 2026-11-18 | Active |
| D-010 | ORFS **execution mirror** at `D:\SattvaRoute\tools\OpenROAD-flow-scripts` (git clone of `D:\tools` @ 25b6429, `core.autocrlf=false` → LF) — the `D:\tools` checkout is CRLF (Windows git autocrlf) and shebang scripts fail under WSL (`env: 'bash\r'`); `D:\tools` stays untouched as read-only source of truth | 2026-11-18 | Active |
| D-011 | Design-local PDN override `benchmark/design/sattva_sram/pdn_sattva.tcl` — platform grid connects `^VDD$`/`^VSS$` and bridges macro M4–M5, but macro `sram_x4x4x1` has lowercase `vdd`/`vss` on M3 | 2026-11-18 | Active |
| D-012 | `macro_placement.tcl` with `-exact` bypasses MPL-0005 (floorplan rc=0) | 2026-11-18 | Active |
| D-013 | `set_special_nets [list zero_]` in `global_route.tcl` — **FAILED execution attempt** (retired): command does not exist in this build, was targeted at the unused `D:\tools` copy, and was prescribed after the failing `pin_access`. Retained as evidence, not relabeled. | 2026-11-18 | Failed / retired |
| D-014 | Mark `zero_` SPECIAL via OpenDB `$net setSpecial` in the **execution mirror** `global_route.tcl` before `pin_access` — minimal DB-level DRT-0305 recovery. Applied and tested in `runs/orfs_baseline_20261118T171712Z`: **DRT-0305 RESOLVED**, but global routing now blocked by a distinct `DRT-0073 No access point for u_sram/clk` (macro pin access). No second fix applied. | 2026-11-18 | APPLIED — partial success; new blocker DRT-0073 |
| D-015 | FDE-004 adjudication: DRT-0073 root cause **PROBABLE** — thin M4 `clk` pin over full-macro M1–M5 OBS leaves no legal via/escape access point; placement, grid alignment, net classification and D-014/`zero_` refuted. Exact FlexPA filter stage NOT EVALUATED. | 2026-11-19 | FINDING ADOPTED — **no remedy approved**; full report `docs/FDE-004_DRT0073_ROOT_CAUSE_INVESTIGATION.md` |
| D-016 | FDE-005 controlled diagnostic: both isolated A/B arms fail identically with DRT-0073; tool exposes only aggregate `At least 3 sparse access points`; via-in-pin M4 window has no effect. Root cause remains **PROBABLE** (not upgraded); source run unchanged. | 2026-11-19 | FINDING ADOPTED — **no remedy approved**; report `docs/FDE-005_CONTROLLED_FLEXPA_DIAGNOSTIC.md` |
| D-017 | FDE-006 instrumented FlexPA investigation **BLOCKED at Gate 2**: offline Bazel dry-run fails (`rules_go++go_sdk+go_toolchains` not cached; build image unmountable). No candidate-level data obtained; root cause remains PROBABLE, not ESTABLISHED. | 2026-11-19 | BLOCKED / INCONCLUSIVE — **no remedy approved**; report `docs/FDE-006_INSTRUMENTED_FLEXPA_CANDIDATE_INVESTIGATION.md` |

Details: D-001..D-006 rationale recorded in `docs/milestone0-environment-audit.md`;
D-007 in Phase D rules; D-008 in `AGENTS.md`; D-009..D-012 in `logs/DAILY_LOG.md`
(2026-11-18 M1-S001) and the files they name. D-013 retrospective and D-014 proposal:
`docs/decisions/D-014_proposal.md` and `MILESTONE_1C-R_DRT0305_ROOT_CAUSE_REPORT.md`.
