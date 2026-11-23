# PROJECT_STATE.md — Single Current Snapshot

> This is the FIRST file every agent reads. Update it before ending any session.

- **Project name:** SattvaRoute — AI-assisted Physical Design Orchestration and Recovery
- **Current milestone:** Milestone 1 — Baseline Execution (routing incomplete)
- **Current phase:** none — T-ENGINEERING-010 complete; ENG009-DIAG-001 executed and adjudicated; R2 remains DRAFT/INACTIVE
- **Current status:** T-ENGINEERING-010 COMPLETE. ENG009-DIAG-001 executed in isolated scratch: log-only getSrcs instrumentation, binary `7461d0d0…`, OFF/OFF byte-identical equivalence, 107/107 marker-provenance pairs. 2 nm sliver **CONFIRMED ARTIFACT** (own-net clk metal, zero foreign-net 40/0); DRT-0073 root cause updated. Agent B ACCEPT WITH LIMITATIONS; non-blocking F1 reconciled with GDS census. KB appended KB-0019 (19 records, chain PASS). Protected artifacts 9/9, validator 13/13. No remedy, geometry change, or production modification.
- **Last updated:** 2026-11-24 (orchestrator, T-ENGINEERING-010)
- **Current active task:** none — await explicit authorization for any corrective experiment or production remedy; FDE-007 remains BLOCKED (no validated remedy)
- **Active agents:** orchestrator; Agents A/B/C completed and released
- **Skill system:** no project skills installed; see `.skills/PROJECT_SKILLS.md` for the catalog and `.skills/README.md` for binding usage rules

## Completed milestones

- **Milestone 0 — Feasibility & Architecture: COMPLETE (2026-11-18)**
  - Environment audit verified (hardware, WSL, EDA toolchain, registry).
  - ORFS located at `D:\tools\OpenROAD-flow-scripts` (commit `25b6429`) with ASAP7 platform + `SYNTH_NETLIST_FILES` support verified.
  - OpenFinRAM (real SRAM compiler, BSD-3) cloned, built, patched (v2lvs non-fatal), and run end-to-end → EXIT=0.
  - Real macro `sram_x4x4x1` generated and verified: GDS (529 KB, 65 cells) + LEF (CLASS BLOCK, 3.672×13.608 µm, 22 pins) + Liberty (estimated model).
  - Report: `logs/REPORT_LOG.md` (M0) · Audit: `docs/milestone0-environment-audit.md`

## Verified environment (summary)

| Item | State |
|---|---|
| OS / RAM / disk | Win build 26200 · 15.79 GB (WSL 7.6 GiB) · D: ~116 GB free |
| WSL | Ubuntu-24.04.4, WSL2, default distro, running |
| OpenROAD | `/usr/local/bin/openroad`, `bazel-nostamp`, headless, 8 threads |
| ORFS | `D:\tools\OpenROAD-flow-scripts` @ `25b6429` (ASAP7 platform complete) |
| Yosys | 0.33 system (ORFS) · 0.71 yowasp WASM (OpenFinRAM, PATH shim) |
| KLayout | 0.30.13 headless + python bindings (user site) |
| OpenFinRAM | built `build/OpenFinRAM`, v2lvs patch applied, run verified EXIT=0 |
| Python / Node | WSL 3.12.3 / 22.23.4 · Windows —/26.7.0 |
| Missing | Calibre, tcsh (LVS unavailable, non-fatal) · Verilator/Icarus Windows-only |

## Current benchmark

- **Macro:** `sram_x4x4x1` — OpenFinRAM real SRAM, ASAP7, generated 2026-11-18T13:10+05:30(WSL)
  - Views: `benchmark/design/OpenFinRAM/results/sram_x4x4x1_20261118_131017/{sram_x4x4x1.gds,.lef,.lib}`
  - LEF: CLASS BLOCK, SIZE 3.672 × 13.608 µm, 22 pins, SYMMETRY X Y
  - Liberty: **estimated** (skip-characterization) — not silicon-characterized
  - GDS: top cell `sram_x4x4x1`, 65 cells, dbu 0.00025
- **Controller RTL:** DONE (T-M1-001) — `benchmark/design/sattva_sram/rtl/sattva_ctrl.v` (sha256 `3b7d6fa6…`, see `netlist/synth_provenance.txt`)
- **Synthesized netlist:** DONE (T-M1-001) — `benchmark/design/sattva_sram/netlist/sattva_ctrl_synth.v` (sha256 `f3ae7aa3…4f0d`, POSTCHECK PASS). Correction applied 2026-11-19; earlier "NOT YET" text was stale.
- Fallback: ORFS FakeRAM `fakeram7_256x32` (LEF+Lib, no GDS) — not in use

## Existing working components

- `scripts/gen_sram_macro.sh` — reproducible macro generation (yosys shim encoded)
- `scripts/` + `benchmark/design/OpenFinRAM/` — full macro flow, verified
- Memory system itself: this file + logs/ + coordination/
- **FDE-001 (verified):** `scripts/run_baseline_orfs.sh` — collision-safe run IDs, enforced preflight, process exit propagation, input/binary/patch fingerprinting, `run.json`/`preflight.json`; 14/14 offline tests in `tests/test_runner.sh` (public commit `43ffebb`).
- **FDE-002 (offline-verified, no EDA run):** `scripts/sattva_approval.py` + `state/approval_policy.json` — durable approval records, deterministic validator, narrow atomic patch applier with rollback evidence, ledger-based reuse rejection, scope enforcement from `flow/Makefile` inputs; 25/25 offline tests in `tests/test_approval.py`. Approval enforcement is implemented in code; physical correctness of any patch remains a separate engineering decision.

## Known blockers

- **DRT-0305 (root cause adjudicated, HIGH confidence)**: `zero_` is a logical constant-zero tie net created by OpenROAD's Verilog reader (`VerilogReader.cc:117,2019-2020`) for raw `4'h0`/`2'h0` literals driving macro SIGNAL pins `sdel[3:0]`/`A[3:2]`; `dbReadVerilog.cc:768-773` types it GROUND but never sets SPECIAL. `SYNTH_NETLIST_FILES` bypasses Yosys `hilomap` tie-cell insertion. DRT's DB-import guard (`io.cpp:1040`: supply sigtype && !isSpecial) rejects it at `pin_access`. PDN/VDD/VSS are correct. Report: `MILESTONE_1C-R_DRT0305_ROOT_CAUSE_REPORT.md`.
- **D-013 RETIRED (failed execution attempt)**: `set_special_nets` does not exist in this build; edits targeted `D:\tools` while runner uses the `D:\SattvaRoute\tools` mirror; prescribed after the failing `pin_access`; dedicated run has no evidence. Prior "7/7 PASS" was static-text only.
- **DRT-0073 (new, current blocker)**: `[ERROR DRT-0073] No access point for u_sram/clk (sram_x4x4x1)` at `pin_access` in run `orfs_baseline_20261118T171712Z`; source `drt/src/pa/FlexPA_acc_point.cpp:1524–1533` (zero access points for inst-term), preceded by DRT-0419 warnings on macro `D`/`Q` pin centers. Distinct from DRT-0305; requires a new decision ID and approval. Macro pin-access/track alignment NOT EVALUATED as a fix target.
- **D-014 APPLIED (partial success)**: mark `zero_` SPECIAL via OpenDB `$net setSpecial` in mirror `global_route.tcl` before `pin_access`. Run `orfs_baseline_20261118T171712Z`: DRT-0305 eliminated (snets 2→3); new DRT-0073 blocker. Mirror hash `3968898c…` → `cd86b587…`; `D:\tools` unchanged. No further fix applied.

## Next action

1. Open a new investigation/decision ID (e.g. D-015) for DRT-0073 macro `clk` pin access; gather evidence before any change.
2. Do NOT change routing layers, macro placement, LEF, or constraints without that evidence and fresh approval.
3. Re-run with a new unique run ID only after approval; verify at report level (D-007).
4. Original baseline and all failed attempts remain preserved as immutable evidence.

## Important project decisions (index: docs/decisions/DECISIONS.md)

- D-001 Flow engine = existing ORFS clone (not OpenLane 2)
- D-002 Benchmark = ASAP7 + OpenFinRAM real SRAM (not FakeRAM; FakeRAM kept as fallback)
- D-003 ORFS canonical path = `D:\tools\OpenROAD-flow-scripts` (user-moved, policy-compliant)
- D-004 Calibre v2lvs dependency downgraded to warning via documented patch (SPICE feeds LVS only; GDS/LEF generated before that point)
- D-005 OpenFinRAM uses yowasp-yosys 0.71 via per-run PATH shim; system Yosys 0.33 untouched
- D-006 WSL memory left at default 7.6 GiB (revisit only on OOM)
- D-007 Exit code 0 is never sufficient evidence of a successful baseline
- D-008 Memory/logging system (this system) is mandatory for every agent/model/session
- D-009 Local ABC script `scripts/abc_map_sattva.script` (`strash`/`if -D 950`/`map`) replaces ORFS `abc_speed.script` (yosys 0.33's bundled `yosys-abc` segfaults (rc 139) in `buffer`/`&nf` with ASAP7 NLDM libs; gz liberty must be gunzipped first (rc 134))
- D-010 LF execution mirror at `D:\SattvaRoute\tools\OpenROAD-flow-scripts` (resolved CRLF blocker)
- D-011 PDN override with lowercase vdd/vss; PDN-0006 resolved
- D-012 macro_placement.tcl with -exact bypasses MPL-0005 (floorplan rc=0)
- D-013: `set_special_nets [list zero_]` in `global_route.tcl` — FAILED/RETIRED; command does not exist in this build, wrong checkout, wrong order; retained as failed execution attempt
- D-014: mark `zero_` SPECIAL via OpenDB `$net setSpecial` in the execution mirror before `pin_access` — APPLIED; DRT-0305 RESOLVED; new blocker DRT-0073; no second fix applied