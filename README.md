# SattvaRoute

**Evidence-driven AI-assisted physical design orchestration, failure diagnosis, approval-gated recovery, and reproducible OpenROAD workflows.**

> Status: research prototype. The physical-design flow is **not complete**: global routing is currently blocked by `DRT-0073`. This repository documents what was verified, what failed, and what remains unevaluated — without rewriting failures as successes.

## Overview

SattvaRoute explores how an AI-assisted agent can drive a real VLSI physical-design flow responsibly. Instead of silently patching scripts until a tool stops complaining, the workflow:

1. executes EDA stages under a fixed, reproducible runner;
2. captures per-stage logs, databases, reports and hashes into immutable, timestamped run directories;
3. diagnoses failures from that evidence (logs, OpenDB state, and installed tool source);
4. proposes a **single, bounded** change with a decision ID, diff, rollback, and verification plan;
5. requires **human approval** before applying it;
6. re-runs with a new unique run ID and reports the result honestly.

The central engineering claim is procedural, not magical: *evidence before diagnosis, approval before modification, and explicit separation between "the process finished" and "the design is correct."*

## Problem

Conventional scripted PnR flows make failure recovery fragile:

- failures are diagnosed by reading logs manually, often from the wrong checkout or stale run;
- "fixes" are stacked, so causality is lost;
- exit code 0 is treated as success even when reports show violations;
- runs overwrite each other, destroying evidence;
- configuration changes are not recorded or reviewed;
- there is no clear line between execution completion and engineering quality.

SattvaRoute addresses these with immutable run directories, report-level verification, a decision ledger, and an approval gate.

## Design principles

- **Evidence before diagnosis** — conclusions cite logs, ODB state, and exact tool source lines.
- **Deterministic orchestration** — one scripted runner executes a fixed stage sequence.
- **Human-approved modifications** — no fix is applied without explicit approval.
- **Reproducible runs** — unique timestamps, recorded hashes, no overwrites.
- **Immutable evidence** — failed baselines are preserved, never relabeled.
- **Execution ≠ engineering quality** — `PASS / FAIL / BLOCKED / NOT EVALUATED` are reported separately.
- **No fabricated metrics** — unavailable checks stay unavailable.
- **Explicit uncertainty** — independent agents challenge hypotheses before adjudication.

## Architecture

The implemented system is deliberately small. Be aware of what is and is not code in this release:

| Component | Implementation | Status |
|---|---|---|
| Workflow controller | `scripts/run_baseline_orfs.sh` — stage sequence, per-stage logs, fail-fast, orchestration state | **Implemented** |
| EDA execution | OpenROAD / ORFS `make` targets invoked by the runner | **Implemented** |
| Tool adapters | ORFS platform files + design config (`config.mk`, `pdn_sattva.tcl`, `macro_placement.tcl`) | **Implemented** |
| Evidence collection | per-run `evidence/` and `work/` trees; `preflight.txt`, `postflight.txt`, `stages.txt`, hash manifests | **Implemented** |
| Diagnosis layer | documented multi-agent investigations stored under `docs/investigations/` | **Implemented as process** (agents are operators, not shipped code) |
| Approval service | `scripts/sattva_approval.py` + `state/approval_policy.json` — durable approval records, deterministic validator, narrow atomic patch applier, runner-boundary guard | **Implemented and offline-verified (FDE-002)**; no real EDA recovery run performed |
| Persistent run state | `PROJECT_STATE.md`, `coordination/TASK_BOARD.md`, `logs/*` | **Implemented (file-based)** |
| Artifact management | timestamped run directories, immutable baselines | **Implemented** |
| Dashboard / backend / worker | `app/`, `configs/`, `artifacts/`, `experiments/`, `tests/` exist as **empty placeholders locally** | **NOT implemented — do not assume a service exists** |

Architecture notes: [`docs/architecture.md`](docs/architecture.md).

## Workflow

Intended pipeline, with the actual verified status:

```
input validation → synth → floorplan → macro placement → PDN → placement
                 → CTS → global routing → detailed routing → extraction → timing
                  ✅      ✅            ✅         ✅       ✅      ✅
                                         ⛔ BLOCKED (DRT-0073)   ⛔  ⛔  ⛔
```

| Stage | Status |
|---|---|
| Synthesis / netlist provenance | PASS |
| Floorplan, macro placement, PDN | PASS |
| Placement | PASS |
| CTS | PASS |
| Global routing | **BLOCKED** — DRT-0073 (macro clock-pin access) |
| Detailed routing | NOT EVALUATED |
| Parasitic extraction | NOT EVALUATED |
| Final timing / signoff | NOT EVALUATED / NOT PERFORMED |

See [`docs/workflow.md`](docs/workflow.md) and [`docs/status/STATUS.md`](docs/status/STATUS.md).

## Benchmark

- **Design:** `sattva_ctrl` — a small SRAM controller.
- **Macro:** `sram_x4x4x1`, generated by [OpenFinRAM](https://github.com/ArunTS1992/OpenFinRAM) (BSD-3-Clause), 4 words × 4 bits, one bank, single port.
- **Platform:** ASAP7 (public academic predictive technology), NLDM TT/RVT libraries.
- **Toolchain:** OpenROAD (`bazel-nostamp`), Yosys 0.33, ORFS commit `25b6429`.
- **Synthesis:** pre-synthesized netlist with recorded provenance and SHA-256 hashes (`benchmark/design/sattva_sram/netlist/synth_provenance.txt`).
- **Constraints:** 950 ps clock, 12.5% I/O (`constraint.sdc`).
- **Configuration:** `config.mk`, `pdn_sattva.tcl`, `macro_placement.tcl`.

**Limitations:** the macro Liberty model is *estimated* (`--skip-characterization`), not silicon-characterized; no behavioral macro model exists, so RTL simulation is not possible; no LVS/PEX (commercial Calibre unavailable). Details: [`docs/benchmark/macro-sram-x4x4x1.md`](docs/benchmark/macro-sram-x4x4x1.md).

## Current engineering status (honest)

- Macro inspection and synthesis: **complete**
- Provenance: **verified**
- Floorplan / placement / CTS: **PASS**
- DRT-0305: **eliminated by D-014** (approved, applied, verified)
- Global routing: **blocked by DRT-0073**
- Detailed routing / extraction / timing / signoff: **NOT EVALUATED / NOT PERFORMED**

**D-014:** OpenROAD's Verilog reader created a net named `zero_` for constant-zero literals tied to macro signal pins, typed it `GROUND`, and never set its SPECIAL bit. TritonRoute's import guard (`drt/src/io/io.cpp:1040`) rejects supply-typed, non-special nets. D-014 marks `zero_` SPECIAL through OpenDB (`$net setSpecial`) in the executed flow mirror immediately before `pin_access`. In run `orfs_baseline_20261118T171712Z`, DRT-0305 disappeared and the design imported 3 special nets (previously 2).

**DRT-0073:** global routing now fails earlier in pin access — `No access point for u_sram/clk (sram_x4x4x1)` — with `DRT-0419` warnings that no routing tracks pass through the macro `D`/`Q` pin centers. This is a distinct macro pin-access / track-alignment issue. It remains under investigation; no further fix was applied without evidence and approval.

## Failure investigations

Four independent, read-only investigations were run before any fix was applied:

| Report | Finding |
|---|---|
| `docs/investigations/agent_A_orfs_execution_path.md` | Runner sources the LF mirror, not `D:\tools`; D-013 was never in the executed path. |
| `docs/investigations/agent_B_zero_net_database_trace.md` | `zero_` exists from synthesis, is non-special, and drives six macro *signal* pins — not the ground pin. |
| `docs/investigations/agent_C_special_net_mechanism.md` | DRT-0305 source guard; `set_special_nets` does not exist; supported mechanism is `add_global_connection` + `global_connect`. |
| `docs/investigations/agent_D_independent_failure_analysis.md` | Independent challenge: mis-typed driverless constant-tie net; D-013 premise invalid. |

- **D-013 (failed attempt):** `set_special_nets [list zero_]` — the command does not exist in this OpenROAD build, the edit targeted the wrong checkout, and it was placed after the failing call. Retained as a failed experiment in [`docs/decisions/DECISIONS.md`](docs/decisions/DECISIONS.md).
- **D-014 (applied):** one guarded OpenDB `setSpecial` in the executed mirror → DRT-0305 eliminated.
- **Adjudicated root cause:** [`docs/investigations/MILESTONE_1C-R_DRT0305_ROOT_CAUSE_REPORT.md`](docs/investigations/MILESTONE_1C-R_DRT0305_ROOT_CAUSE_REPORT.md).

Distinctions are kept explicit: hypothesis → verification → applied change → experiment result → engineering verdict.

## Recovery model

1. capture evidence (logs, ODB state, hashes, run ID);
2. formulate a hypothesis and challenge it independently;
3. write a decision record with exact diff, affected stages, side effects, rollback, verification plan;
4. obtain explicit human approval;
5. apply **one** change to the **executed** tree;
6. re-run with a new unique ID;
7. verify at report level (D-007: exit code 0 is never sufficient);
8. if a new failure appears, stop — do not stack another fix.

See [`docs/recovery.md`](docs/recovery.md).

## Project structure

```
README.md, LICENSE, CONTRIBUTING.md, SECURITY.md, CITATION.cff
AGENTS.md, PROJECT_STATE.md
benchmark/design/sattva_sram/     RTL, netlist + provenance, config, SDC, PDN, placement, macro LEF/LIB
docs/                             architecture, workflow, recovery, environment audit
  benchmark/                      macro documentation and provenance
  decisions/                      D-001..D-014 decision ledger + D-014 proposal
  investigations/                 four agent reports + root-cause report
  history/                        point-in-time milestone assessment
  status/                         current status summary
evidence/                         curated run summaries, log excerpts, hash manifest
logs/                             daily log, agent activity, review log, report log, session handoff
coordination/                     task board, active work, lock documentation
scripts/                          runner, synthesis, macro generation, failure-injection demos
```

The original full run directories (with ODB databases, ~144 MB) are kept locally and **not** published; curated summaries are in `evidence/`.

## Getting started

### Requirements

- Windows with WSL2 Ubuntu 24.04 (the development environment).
- OpenROAD (built from source; tested build: `bazel-nostamp`).
- ORFS at commit `25b6429` (upstream: <https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts>).
- Yosys 0.33; Python 3; GNU Make 4.3.
- KLayout Python bindings are optional (final GDS streaming only — unavailable in the development environment).
- Commercial Calibre/`v2lvs` is **not** required for the supported flow.

### Setup and launch

1. Obtain ORFS and build OpenROAD following upstream instructions.
2. Place a local ORFS checkout at the path configured in `scripts/run_baseline_orfs.sh` (`MIRROR`).
3. Provide the generated macro `sram_x4x4x1` LEF/Liberty views (included here) or regenerate them with `scripts/gen_sram_macro.sh` and OpenFinRAM + ASAP7.
4. Run:

```bash
bash scripts/run_baseline_orfs.sh
```

Each run creates a collision-safe `runs/orfs_baseline_<UTC stamp>_<pid>/` directory with per-stage evidence; nothing is overwritten. Paths are parameterised by `SATTVA_ROOT`, `SATTVA_MIRROR`, `SATTVA_DESIGN`, `SATTVA_RUNS`, `OPENROAD_EXE`, `YOSYS_EXE`, and an optional `RUN_TAG`.

Runner contract: required preflight checks block execution; a failed stage is reflected in the process exit code **and** in `evidence/stages.txt` / `evidence/run.json`; the executed binaries, design inputs, runner, and patched flow script are hashed. `evidence/preflight.json`, `evidence/mirror.patch`, and `evidence/run.json` are machine-readable.

**Note:** the defaults are environment-specific (`/mnt/d/...`); adapt the variables above for your machine.

### Tests

`tests/test_runner.sh` is an **offline, credential-free** suite that stubs `make`, `openroad`, and `yosys` in a temporary sandbox. It verifies failed-stage exit propagation, success exit, unique run IDs/directories, preflight blocking of missing inputs, valid JSON state, and patch fingerprinting. Verified result: **14 PASS / 0 FAIL** (2026-11-19). No EDA flow is executed by these tests.

`tests/test_approval.py` is an **offline** suite for the exact-patch approval boundary: missing/rejected/malformed approvals, patch/input/run/decision/scope/hash mismatches, path traversal and symlink escapes, atomic apply, rollback, concurrent modification, restart recovery, approval reuse, and runner-boundary enforcement. Verified result: **25 PASS / 0 FAIL** (2026-11-19). No real EDA run or real approval was used.

`failure_case_1_workflow.py` is now a clearly labeled **SIMULATED** dry-run demo (no file writes by default); `routing_fix_demo.py` is **RETIRED** with an explanation because it advertised a D-013 fix that was proven failed. Neither is part of the automated suite.

## Configuration

| File | Purpose |
|---|---|
| `benchmark/design/sattva_sram/config.mk` | ORFS design configuration (netlist, LEF/LIB/GDS, platform, PDN, constraints) |
| `benchmark/design/sattva_sram/constraint.sdc` | 950 ps clock, 12.5% I/O timing constraints |
| `benchmark/design/sattva_sram/pdn_sattva.tcl` | PDN grid plus lowercase `vdd`/`vss` macro global connections |
| `benchmark/design/sattva_sram/macro_placement.tcl` | exact macro placement (bypasses MPL-0005) |

## Decisions

D-001..D-014 are recorded in [`docs/decisions/DECISIONS.md`](docs/decisions/DECISIONS.md). Highlights: D-007 (exit code ≠ success), D-010 (LF execution mirror), D-013 (failed attempt, retired), D-014 (applied DRT-0305 fix).

## Limitations

- Global routing is blocked by DRT-0073; no downstream stage has been evaluated.
- No routing congestion/overflow/wirelength or setup/hold metrics exist.
- Macro Liberty is estimated; no behavioral model; no LVS/PEX.
- WSL memory capped at 7.6 GiB; environment-specific absolute paths.
- No automated tests, no dashboard/backend implementation.
- No signoff of any kind was performed.

## Roadmap

1. Investigate DRT-0073 with database and tool-source evidence; propose a new decision.
2. Complete global routing, then detailed routing, extraction, and final timing reports.
3. Add automated regression tests for the stage runner and evidence parsers.
4. Implement the persistent state service and dashboard only when there is verified functionality to expose.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). In short: preserve evidence, never rewrite failed results, one change per decision, approval before application, and report-level verification.

## License

Original project code and documentation are licensed under the **MIT License** — see [`LICENSE`](LICENSE). Third-party components and generated benchmark collateral are **not** covered by this license; see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Acknowledgments

- [OpenROAD](https://theopenroadproject.org/) and [OpenROAD-flow-scripts](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts) — EDA flow and routing engine.
- [OpenFinRAM](https://github.com/ArunTS1992/OpenFinRAM) — BSD-3 SRAM generator used for the `sram_x4x4x1` macro.
- ASAP7 — public academic predictive technology model.
- Yosys, KLayout, and the open-source EDA community.
