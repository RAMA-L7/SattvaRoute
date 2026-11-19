# Session Handoff — FDE-003 S001

- **Task:** T-FDE-003 — Real Baseline Validation of the Hardened Runner
- **Date:** 2026-11-19
- **Agent:** orchestrator (Hy4 flash Free) + Agents A/B/C/D (read-only)
- **Safe for another agent to continue:** YES — no in-progress edits; lock released; evidence preserved.

## Verified starting state

- Publish tree `fc10d59` = remote HEAD; publish tree had minor `evidence/*` dirt noted by Agent B (no flow-script change).
- Live runner sha256 `0c790cc976b3fcd30ff59a7d8d2b1bbe662edd47c21196adde7d9b0f2c65b39a` (equals published copy).
- D-014 mirror patch present: `global_route.tcl` sha256 `cd86b587…`; `D:\tools` copy `3968898c…` unchanged.
- No `SATTVA_APPROVAL*` vars, no active EDA processes, 114 GiB free, 16 prior run dirs (none with ns+PID IDs).

## Execution

- One real run: `orfs_baseline_20261119T131025284719666Z_9263`.
- Observed process rc = 2; runner printed `STAGE FAILED: route (rc=2)`, `OVERALL_RC=2`.
- No approval gate, no recovery patch, no design/config change, no rerun.

## Result

- Stages: check-yosys 0, check-openroad 0, synth 0, floorplan 0, place 0, cts 0, route 2; finish not launched.
- `run.json`: overall_rc=2, first_failed_stage=route, 7 stage records, verdict NOT EVALUATED — matches `stages.tsv` and observed rc.
- 18 evidence files; 56 work files; `artifact_sha256.txt` 56 lines, `sha256sum -c` 56 OK.
- DRT-0305 = 0, DRT-0073 = 2 (`5_1_grt.log:108`), DRT-0419 = 8; `snets: 3`, `nets: 72`.
- Prior-run sentinel `e9d0330c…33b26b` unchanged; no cross-run contamination; no approval artifacts.

## Independent reviews

- A: SAFE TO LAUNCH (tool identity, 9/9 input hashes, disk, no duplicates).
- B: 6/6 pre + 7/7 post PASS (state consistency, no auto-rerun, gate inactive).
- C: evidence inventory 18/18, hashes 56/56, post-route reports correctly NOT EVALUATED.
- D: GO — reproducibility/state/provenance/binary identity/verdict support PASS; no overclaims.

## Remaining limitations

- Global routing blocked by DRT-0073 (pre-existing macro `clk` pin access) — not fixed.
- OpenROAD binary pinned by hash only; `bazel-nostamp` gives no source revision.
- `klayout` absent (optional; final GDS streaming unavailable).
- Detailed routing, extraction, timing, signoff: NOT EVALUATED.

## Next action (requires separate authorization)

FDE-004: investigate DRT-0073 with FlexPA access-point dump, via rules, OBS/pin geometry and track directions under a new decision ID; obtain approval before any patch. Do not modify physical-design configuration in this handoff.
