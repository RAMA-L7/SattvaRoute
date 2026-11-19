# REPORT_LOG — formal milestone reports

> Newest first. Each report: Objective · Work completed · Files created/modified ·
> Commands executed · Test results · Evidence · Failures · Limitations ·
> Remaining tasks · Milestone verdict.

## FDE-006 — Instrumented FlexPA candidate-level investigation (2026-11-19, orchestrator)

- **Objective:** expose candidate AP coordinates/rejection reasons for `u_sram/clk` via target-specific instrumentation and a scratch OBS control.
- **Work completed:** source pipeline mapped, instrumentation patch designed (not applied), geometry candidates reconstructed, isolated source workspace created, offline build dry-run executed and captured.
- **Evidence:** `experiments/FDE-006/FDE-006-20261119T143807Z-7004/build/gate2_nobuild.log`, `patches/FDE006_instrumentation_PROPOSED.diff`, manifests.
- **Failures:** Gate 2 NO-GO — offline Bazel analysis fails on missing `rules_go` go_sdk; build image unmountable; no network/install permitted.
- **Milestone verdict:** **INCONCLUSIVE** (build blocked); root cause remains ROOT CAUSE PROBABLE from earlier milestones; no fix approved or applied.
- **Remaining tasks:** obtain offline cache/fetch authorization or a prebuilt instrumented binary; rerun FDE-006 gates.

## FDE-005 — Controlled FlexPA diagnostic (2026-11-19, orchestrator)

- **Objective:** resolve FDE-004's remaining uncertainty about FlexPA candidate generation/rejection for `u_sram/clk`.
- **Work completed:** isolated A/B `pin_access` diagnostics on scratch copies; GO gate; four independent agent reviews; source-protection proof.
- **Evidence:** `experiments/FDE-005/FDE-005-20261119T135453Z-4d06/` logs/manifests/scripts; source ODB `35bff121…` unchanged.
- **Test results:** A rc=1, B rc=1; identical aggregate diagnostic and DRT-0073; via-in-pin M4 no effect.
- **Failures/limitations:** no candidate coordinates or rejection reasons exposed by this build; exact filter stage NOT EVALUATED; via-in-pin may be a no-op.
- **Milestone verdict:** FDE-005 accepted as an investigative milestone; root cause remains **ROOT CAUSE PROBABLE**; no fix approved or applied; no second baseline.
- **Remaining tasks:** instrumented candidate-level diagnostic (FDE-006) only after approval.

## FDE-004 — DRT-0073 macro pin-access investigation (2026-11-19, orchestrator)

- **Objective:** establish a defensible root cause for `DRT-0073 No access point for u_sram/clk` using geometry, tracks, vias, ODB and FlexPA source evidence.
- **Work completed:** four independent read-only investigations; coordinator adjudication; D-015 finding record; report and session handoff.
- **Evidence:** primary run `orfs_baseline_20261119T131025284719666Z_9263`; LEF/GDS/Liberty/ODB geometry; ASAP7 `make_tracks.tcl`; VIA34/VIA45 rules; FlexPA source; placement ODB.
- **Failures/limitations:** exact FlexPA filter stage and per-candidate rejection reasons NOT EVALUATED; no routed DB exists; no detailed routing/extraction/timing.
- **Milestone verdict:** **ROOT CAUSE PROBABLE** — thin M4 `clk` pin over full-macro M1–M5 OBS leaves no legal via/escape access point. No fix approved or applied; no second run.
- **Remaining tasks:** approved scratch-copy AP diagnostic; then a new decision for any remedy.

## M1C-R — DRT-0305 Root Cause Investigation (2026-11-18, orchestrator)

- **Objective:** explain why D-013 failed in the actual ORFS execution path, adjudicate root cause, propose a minimal justified fix, and establish a reliable path to detailed routing.
- **Work completed:** four independent read-only investigations executed and integrated; execution path traced via logs; `zero_` traced across all stage ODBs; special-net mechanism located in exact-build source; independent hypothesis challenge completed; D-014 fix proposal authored.
- **Files created/modified:** `MILESTONE_1C-R_DRT0305_ROOT_CAUSE_REPORT.md`, `docs/decisions/D-014_proposal.md`, `docs/decisions/DECISIONS.md`, `reports/agent_{A,B,C,D}_*.md`, `logs/sessions/M1C-R_S001_handoff.md`, coordination/state/logs.
- **Commands executed:** read-only `openroad` Tcl introspection on ODBs, `grep`/`find`/`sha256sum`/`git` over both ORFS trees, source-level inspection, one in-memory `$net setSpecial` probe.
- **Test results:** DRT-0305 trigger condition confirmed (`sigType=GROUND, isSpecial=0`); `set_special_nets` absent; `$net setSpecial` callable (`rc=0`). No flow run performed.
- **Evidence:** 4 agent reports + verbatim logs/ODB dumps/source line references; original baseline `runs/orfs_baseline_20261118T152845Z` immutable.
- **Failures/limitations:** D-013 retired as failed; official web docs unavailable (402/404); no `5_1_grt-failed.odb`; empirical fix efficacy and downstream routing NOT EVALUATED (no authorized run).
- **Remaining tasks:** obtain approval for D-014; controlled run; detailed routing/extraction/timing verification.
- **Milestone verdict:** investigation COMPLETE; root cause adjudicated HIGH confidence; recovery NOT performed (approval gate). Global routing BLOCKED; extraction/timing NOT EVALUATED; signoff not claimed.

### M1C-R addendum — D-014 controlled run (2026-11-18T22:47+05:30)
- **Objective:** execute the approved minimal DRT-0305 fix and verify at report level.
- **Work completed:** applied exact D-014 diff to the LF execution mirror only (D:\tools untouched); recorded before/after hashes; ran `scripts/run_baseline_orfs.sh` → unique run `orfs_baseline_20261118T171712Z`; preserved all logs/artifacts.
- **Test results:** DRT-0305 RESOLVED (snets 2→3, zero_ SPECIAL). New failure DRT-0073 `No access point for u_sram/clk`; route rc=2; no routed DB/guide.
- **Failures/limitations:** distinct macro pin-access blocker; no second speculative fix applied per directive; detailed routing/extraction/timing/signoff NOT EVALUATED.
- **Milestone verdict:** D-014 verified against DRT-0305; global routing still BLOCKED by DRT-0073. Not a completion claim.

## M0 — Milestone 0: Feasibility & Architecture (2026-11-18, orchestrator)

- **Objective:** Verify environment and choose benchmark; establish reproducible real-PnR preconditions.
- **Work completed:** full read-only system audit; EDA registry review; ORFS located and verified (`SYNTH_NETLIST_FILES`, ASAP7 platform); OpenFinRAM cloned, built, patched (v2lvs non-fatal), run end-to-end; real macro `sram_x4x4x1` generated; memory system established.
- **Files created/modified:**
  - `docs/milestone0-environment-audit.md`, `scripts/gen_sram_macro.sh`
  - `benchmark/design/OpenFinRAM/**` (clone + build + patch to `src/openroad_manager.cpp`)
  - `AGENTS.md`, `PROJECT_STATE.md`, `docs/*`, `logs/*`, `coordination/*`
- **Commands executed:** system/WSL audit scripts; `git clone --recursive`; `cmake -S . -B build && make -j4`; `./build/OpenFinRAM --num-wls 2 --num-data-bits 4 --num-banks 1 --single-port --openroad --skip-characterization`; klayout verification of GDS.
- **Test results:** build rc=0; macro run EXIT=0; GDS read back via `klayout.db` (top cell `sram_x4x4x1`, 65 cells, dbu 0.00025); LEF header parsed (CLASS BLOCK, SIZE 3.672 BY 13.608, 22 pins).
- **Evidence:** `benchmark/design/OpenFinRAM/results/sram_x4x4x1_20261118_131017/` (gds/lef/lib); run log `/tmp/openfinram_run2.log` (WSL, session) — key lines: v2lvs warning + LVS skip + LEF/Liberty export; audit doc.
- **Failures:** Yosys 0.33 parse failure on `sram_control.v:50` (resolved via yowasp 0.71); PEP 668 pip block (resolved via `--user --break-system-packages`); PowerShell/WSL quoting issues (worked around with script files).
- **Limitations:** macro Liberty is estimated, not characterized · LVS unavailable (no Calibre/tcsh) · controller SPICE skipped by patch · WSL RAM 7.6 GiB · no baseline PnR yet.
- **Remaining tasks:** M1 Phases A–D.
- **Milestone verdict:** **COMPLETE** — all four M0 checklist items verified with evidence.
