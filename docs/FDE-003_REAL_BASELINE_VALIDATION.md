# FDE-003 — Real Baseline Validation of the Hardened Runner

- **Task:** T-FDE-003
- **Date:** 2026-11-19
- **Coordinator:** orchestrator
- **Independent reviewers:** Agent A (environment/tool identity), Agent B (runner/state), Agent C (artifacts/reports), Agent D (independent execution review)
- **Status:** **COMPLETE** — runner validation PASS; physical-design baseline still BLOCKED at DRT-0073.

## 1. Verified starting revision and environment

- Publish tree `fc10d593aad4c32a4f34c0fbac99fb068a6016dc`; remote HEAD identical; clean before the run.
- Live runner sha256 `0c790cc976b3fcd30ff59a7d8d2b1bbe662edd47c21196adde7d9b0f2c65b39a` (byte-identical to published copy).
- ORFS mirror HEAD `25b6429c1644a8682852646bebf19ff164402c76`; mirror status ` M flow/scripts/global_route.tcl`; mirror patched file sha256 `cd86b58724f6c401b40d2cb464118d86590fa86b60cbe953eb4de53514d08099`; read-only `D:\tools` copy `3968898c9abd8c0fd56c50d08bed6d3943bdc641f63c8674817449bbec2706ce` (D-014 patch absent there).
- Ubuntu 24.04.4, kernel 6.6.87.2-WSL2, 8 CPUs, 7.6 GiB RAM (7.1 free), 114 GiB free on `/mnt/d`, Python 3.12.3, GNU Make 4.3.
- No `SATTVA_APPROVAL*` variables; no active `openroad`/`yosys`/`make` processes; 16 prior run directories, none with the new nanosecond+PID format.
- All 9 benchmark input hashes identical to the D-014 run's `preflight.txt` and `synth_provenance.txt`.

## 2. Agent assignments and findings

| Agent | Pre-execution verdict | Post-run verdict |
|---|---|---|
| A — environment/tool identity | **SAFE TO LAUNCH**; tool binary paths/hashes established; 9/9 input hashes match; 114 GiB free; no duplicates | (not re-run; identity cross-checked by D) |
| B — runner/state | 6/6 PASS (published revision, gate inactive, state consistent, collision-safe, no auto-rerun, offline tests ≠ EDA validation) | 7/7 PASS; one scoped NOT EVALUATED (independent re-observation of process rc) |
| C — artifact expectations | Defined 18 evidence files, 56 work files, no `stage_finish.log` | 18/18 evidence files; 56/56 hash manifest verified; route-only artifacts; 10 post-route reports correctly NOT EVALUATED |
| D — independent review | **CONDITIONAL GO**; no hidden mutation; exit observable via `$LASTEXITCODE`; expected route rc=2 / DRT-0073 is a valid validation result | **GO**; reproducibility, state, provenance, binary identity, verdict support all PASS; no overclaims |

Coordinator reconciliation: no conflicting findings. Agent B corrected its own earlier check-count (16 checks: 14 required, 2 optional); the runner and run state were correct.

## 3. Preflight evidence

`evidence/preflight.json`: `required_ok=true`; 16 checks (14 required all OK; 2 optional: `macro_gds` OK, `klayout` MISSING). Mirror hash `cd86b587…`, runner hash `0c790cc9…`. `evidence/mirror.patch` contains the pre-existing 8-line D-014 diff — recorded, not applied. No critical prerequisite failed; execution proceeded.

## 4. Real execution command

```powershell
$out = wsl -d Ubuntu-24.04 -- bash -c 'bash /mnt/d/SattvaRoute/scripts/run_baseline_orfs.sh' 2>&1; $rc = $LASTEXITCODE
```

Exactly one launch. No approval gate, no recovery patch, no EDA design/config change.

## 5. Actual exit code

`PROCESS_EXIT_RC=2` — the hardened runner propagated the failed stage's return code (FDE-001 contract verified against a real EDA run). Terminal lines: `STAGE FAILED: route (rc=2) — stopping`, `OVERALL_RC=2`, `RUN_COMPLETE … rc=2`.

New run ID: `orfs_baseline_20261119T131025284719666Z_9263`.

## 6. Stage-by-stage results and duration

| Stage | rc | Duration (s) |
|---|---:|---:|
| check-yosys | 0 | 0 |
| check-openroad | 0 | 1 |
| synth | 0 | 7 |
| floorplan | 0 | 19 |
| place | 0 | 33 |
| cts | 0 | 11 |
| route | **2** | 7 |
| finish | not launched | — |

Timestamps monotonically increasing with no gaps; exactly one `route` entry; no automatic rerun.

## 7. Artifact inventory

- 18 evidence files (including new `preflight_checks.tsv`, `preflight.json`, `mirror.patch`, `stages.tsv`, `run.json`, `RUN_DIR_ID.txt`).
- 56 work files; `artifact_sha256.txt` has 56 lines; `sha256sum -c` → 56 OK / 0 FAILED. Spot checks: `1_synth.odb` `347ab375…`, `4_cts.odb` `35bff121…`, `5_1_grt.log` `93171767…`.
- synth/floorplan/place/cts ODB+SDC+reports present (24 results, 5 reports, 26 logs).
- route produced only `5_1_grt.log` and `5_1_grt.json`; no `5_*.odb`, no `route.guide`, no `6_final.*`, no congestion/timing/DRC reports.
- `stage_finish.log` correctly absent. No approval artifacts in the run.
- Cross-run: only the new run ID appears in stage logs; prior-run sentinel `e9d0330c…33b26b` unchanged; no hardlinks; no `D:\tools` paths in executed logs.

## 8. Input and infrastructure fingerprints

| Item | SHA-256 |
|---|---|
| Runner | `0c790cc976b3fcd30ff59a7d8d2b1bbe662edd47c21196adde7d9b0f2c65b39a` |
| Mirror `global_route.tcl` (D-014 patched) | `cd86b58724f6c401b40d2cb464118d86590fa86b60cbe953eb4de53514d08099` |
| `D:\tools` `global_route.tcl` (unpatched) | `3968898c9abd8c0fd56c50d08bed6d3943bdc641f63c8674817449bbec2706ce` |
| OpenROAD binary | `c1b90e0a…ee9` (version string `bazel-nostamp`) |
| Yosys binary | `88c0a12b…` (version `Yosys 0.33 (git sha1 2584903a060)`) |
| All 9 benchmark inputs | unchanged vs D-014 preflight / synth provenance |

## 9. Physical-design verdict

- Process execution: **FAIL (rc=2)** — accurately reported.
- ORFS stage completion: synth, floorplan, place, CTS **PASS** (rc=0 + artifacts); route **FAIL** at `pin_access`.
- Physical-design engineering verdict: **BLOCKED** — global routing never started; `5_1_grt.log:108` `[ERROR DRT-0073] No access point for u_sram/clk`; 8 × DRT-0419 warnings; DRT-0305 count 0 (D-014 still effective).
- Detailed routing / extraction / final timing / signoff: **NOT EVALUATED / NOT PERFORMED**. A process exit code never implied success here.

## 10. Failures and blockers

- `DRT-0073 No access point for u_sram/clk (sram_x4x4x1)` — pre-existing macro pin-access blocker, **not introduced by FDE-003** and deliberately not fixed in this milestone.
- `DRT-0419` warnings on macro `D`/`Q` pin centers.
- `klayout` absent (optional; only affects final GDS streaming).
- OpenROAD source revision not pinned by `bazel-nostamp` — binary-hash-level reproducibility only.

## 11. Independent review findings

All reviewers agree: the run is reproducible from recorded inputs, `run.json` matches `stages.tsv`/`stages.txt`/logs/observed rc, artifact provenance is valid, the OpenROAD binary identity is trustworthy by hash (source revision not), and no claim exceeds the evidence. Agent D's overall verdict: **GO** — accept as the FDE-003 validation baseline; not a routed-baseline milestone.

## 12. Changes made

- One new run directory `runs/orfs_baseline_20261119T131025284719666Z_9263/` with full evidence; no prior run modified.
- Task registration, coordination/log updates, this milestone report, and session handoff.
- No RTL/netlist/SDC/macro/PDN/placement/layer/routing change; D-014 patch untouched; no recovery applied.

## 13. Tests executed

- **Real EDA run:** one (this milestone) — exit 2 as designed.
- **Offline suites (not re-run as part of FDE-003):** FDE-001 `test_runner.sh` 14/14 PASS; FDE-002 `test_approval.py` 25/25 PASS.
- Post-run evidence checks: `sha256sum -c artifact_sha256.txt` 56/56 OK; JSON validity; cross-run sentinel; error census.

## 14. Git and publication status

Documentation-only publication after the run (see final report for exact commits). No history rewrite, no force-push.

## 15. Updated project state

`PROJECT_STATE.md`, `coordination/TASK_BOARD.md` (T-FDE-003 DONE), `coordination/ACTIVE_WORK.md` (lock released), `logs/DAILY_LOG.md`, `logs/AGENT_ACTIVITY.md`, `logs/sessions/FDE-003_S001_handoff.md`, and published `evidence/RUNS.md` updated.

## 16. Recommended next milestone

**FDE-004 (separate authorization required):** DRT-0073 evidence investigation under a new decision ID (FlexPA access-point dump, via rules, OBS/pin geometry, track directions), followed by an exact-patch approval experiment if evidence supports a change. Do not begin here. SattvaRoute now has one trustworthy real baseline validation; it still has no routed baseline.
