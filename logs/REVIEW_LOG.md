# REVIEW_LOG — engineering review history

> What was inspected · problems · risks · decisions · validation · reviewer conclusion · follow-up.
> Newest entry first.

## R-006 — FDE-006 instrumented FlexPA investigation (2026-11-19, orchestrator)

- **Inspected:** four agent reports, isolated source copy, production source/binary/ODB hashes, Gate 2 dry-run log, proposed patch design.
- **Findings:** pipeline and instrumentation points established from source; expected candidate set reconstructed geometrically; build blocked offline because `rules_go++go_sdk+go_toolchains` is not cached and the build image cannot be mounted; no candidate-level runtime data.
- **Conflict resolved:** Agent D's "373 dirty source files" vs Agent C's clean claim — direct `git -C /mnt/d/tools/src/OpenROAD status --porcelain | wc -l` = 2; the larger count came from the copied tree being evaluated against the enclosing SattvaRoute repo.
- **Decisions:** D-017 records BLOCKED/INCONCLUSIVE; root cause remains PROBABLE; no remedy approved.
- **Conclusion:** stop condition met; do not fetch dependencies, install toolchains, or apply a fix without separate approval.
- **Follow-up:** provide offline Bazel repo cache or a prebuilt instrumented binary, then rerun Gates 1–4.

## R-005 — FDE-005 controlled FlexPA diagnostic review (2026-11-19, orchestrator)

- **Inspected:** four agent reports, `reports/EXPERIMENT_GO.md`, both arm logs/Tcl scripts, manifests, source ODB before/after proof.
- **Findings:** source ODB `35bff121…` unchanged; scratch copies hash-identical, distinct inodes, non-symlink; A/B logs differ only by the echoed command; both arms report the single aggregate unmet condition `At least 3 sparse access points` and DRT-0073; via-in-pin M4 control had no effect.
- **Decisions:** D-016 finding adopted; root cause remains PROBABLE, not upgraded (no candidate-level rejection data).
- **Conclusion:** experiment executed safely and is reproducible; diagnostic ceiling is a tool limitation, not an experiment defect.
- **Follow-up:** instrumented candidate-level AP diagnostic requires separate approval.

## R-004 — FDE-004 DRT-0073 root-cause review (2026-11-19, orchestrator)

- **Inspected:** four parallel read-only agent reports; FDE-003 run `5_1_grt.log/.json`, `4_cts.odb`, macro LEF/GDS/Liberty, `macro_placement.tcl`, ASAP7 track/via definitions, installed OpenROAD FlexPA source.
- **Findings:** `clk` single M4 pin 0.084×0.024 µm, center exactly on M4 track; full-macro M1–M5 OBS with no carve-outs; one geometric via candidate but M3/M5 halves inside OBS; FlexPA evaluated the pin and all APs were filtered, exact stage unproven. Placement legal and on-track; Snapper bypass irrelevant; grid/classification/D-014 refuted.
- **Decisions:** D-015 finding adopted (root cause PROBABLE); no remedy approved.
- **Validation:** LEF↔GDS↔Liberty↔ODB agreement; four independent agents converged on mechanism class.
- **Conclusion:** ROOT CAUSE PROBABLE; missing per-candidate AP diagnostics prevent HIGH certainty on exact filter stage.
- **Follow-up:** scratch-copy FlexPA AP diagnostic with via-in-pin control, only after approval.

## R-003 — Milestone 1C-R DRT-0305 root-cause review (2026-11-18, orchestrator)

- **Inspected:** four independent subagent reports (`reports/agent_{A,B,C,D}_*.md`); installed OpenROAD source (`drt/src/io/io.cpp:1031-1070`, `odb/src/db/dbTypes.cpp:392-397`, `sta/verilog/VerilogReader.cc:117,2019-2020`, `dbSta/src/dbReadVerilog.cc:768-773`, `src/OpenRoad.tcl:367-413`); ODB DBs across stages; all preserved route logs and `preflight.txt`; a read-only in-memory probe of `$net setSpecial`.
- **Findings:** DRT-0305 is a DB-import guard (`supply sigtype && !isSpecial`) raised by `pin_access`, not a routing algorithm failure. `zero_` is a constant-tie net (six macro SIGNAL sinks) typed GROUND without SPECIAL, caused by `SYNTH_NETLIST_FILES` bypassing `hilomap`. `set_special_nets` does not exist. D-013 failed for four independent reasons (invalid command, wrong `D:\tools` checkout, unreachable insertion after `pin_access`, no preserved evidence). PDN/VDD/VSS and DB consistency are correct.
- **Risks:** marking `zero_` SPECIAL unblocks global routing but leaves six macro signal inputs without physical tie geometry — potential detailed-route opens/DRC. Must be disclosed, not hidden.
- **Decisions:** D-013 retired as FAILED; D-014 proposed (OpenDB `$net setSpecial` in mirror before `pin_access`), approval required.
- **Validation:** four independent agents converged; source + DB + execution-log + runtime-probe evidence; primitive probe `rc=0`, `isSpecial` 0→1.
- **Conclusion:** root cause adjudicated with HIGH confidence; no fix applied pending approval.
- **Follow-up:** approval gate; controlled run with new run ID; report-level verification per D-007.

### R-003 addendum — D-014 experiment (2026-11-18T22:47+05:30)
- **Inspected:** `runs/orfs_baseline_20261118T171712Z/evidence/preflight.txt`, `stage_route.log`, `work/logs/.../5_1_grt.log`; mirror and `D:\tools` hashes.
- **Findings:** D-014 applied only to the mirror (hash 3968898c…→cd86b587…), `D:\tools` unchanged, preflight shows the modified mirror. DRT-0305 eliminated; design imports 3 snets (was 2), confirming `zero_` SPECIAL. New blocker DRT-0073 `No access point for u_sram/clk` at pin access (`FlexPA_acc_point.cpp:1524–1533`), with DRT-0419 warnings for macro D/Q pin centers. No `5_*.odb`/`route.guide`.
- **Conclusion:** D-014 is a verified fix for DRT-0305 but is NOT a completion claim — global routing is blocked by a distinct macro pin-access issue.
- **Risk/next:** do not stack a second fix; new decision ID and evidence required for DRT-0073; routing/extraction/timing remain NOT EVALUATED.

## R-001 — Milestone 0 environment & toolchain review (2026-11-18, orchestrator)

- **Inspected:** Windows/WSL/hardware; `D:\tools\EDA_TOOL_REGISTRY.md`; ORFS clone; ASAP7 platform; OpenFinRAM source (flow order, Calibre touchpoints, Yosys requirements).
- **Findings:**
  - WSL sees only 7.6 GiB (default 50% cap, no `.wslconfig`) — risk for large designs, accepted for small benchmark (D-006).
  - ORFS `SYNTH_NETLIST_FILES` confirmed in clone (`flow/scripts/synth_preamble.tcl:17-25`).
  - ASAP7 platform in clone is complete for PnR but fakeram macros have **no GDS** (abstract-only) — acceptable fallback, not primary benchmark.
  - OpenFinRAM hard-fails on missing Calibre `v2lvs` at `openroad_manager.cpp:159`, **after** GDS (line 128) and **before** nothing else critical; LVS already non-fatal in `main.cpp:127`.
  - OpenFinRAM `sram_control.v:50` needs Yosys ≥0.55 (multi-dim packed array ports); system Yosys 0.33 fails with parse error at `sram_control.v:50`.
- **Decisions:** D-003 (ORFS path), D-004 (v2lvs patch), D-005 (yowasp shim), D-006 (WSL RAM).
- **Validation:** OpenFinRAM full run EXIT=0; GDS top cell `sram_x4x4x1` (65 cells, dbu 0.00025); LEF CLASS BLOCK 3.672×13.608 µm, 22 pins; Liberty present (estimated).
- **Conclusion:** Environment is sufficient for Milestone 1 baseline. Macro flow is reproducible via `scripts/gen_sram_macro.sh`.
- **Follow-up:** (1) controller RTL + netlist provenance; (2) first ORFS run may expose OpenROAD-version or PDN incompatibilities — treat as evidence, not failure; (3) macro Liberty is estimated — document as limitation.

## R-002 — OpenFinRAM v2lvs patch review (2026-11-18, orchestrator)

- **Inspected:** `src/openroad_manager.cpp:159-166` patch (fatal→warning).
- **Problem addressed:** commercial Calibre absent; SPICE output feeds LVS only.
- **Risk:** controller SPICE for LVS is silently absent — mitigated: LOGW emitted at run time (log line 48-49 of run) and LVS itself reports non-fatal skip; signoff LVS out of scope for M1.
- **Conclusion:** Acceptable for Milestone 1. Must be disclosed in every baseline report (see REPORT_LOG limitations).
