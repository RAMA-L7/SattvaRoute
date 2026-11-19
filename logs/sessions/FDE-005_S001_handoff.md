# Session Handoff — FDE-005 S001

- **Task:** T-FDE-005 — Controlled FlexPA access-point diagnostic experiment
- **Date:** 2026-11-19
- **Agent:** orchestrator (Hy4 flash Free) + Agents A/B/C/D (read-only design/review)
- **Safe for another agent to continue:** YES — lock released; source run unchanged; artifacts preserved.

## Verified state

- Starting publish HEAD `a5d2b85` = remote.
- Source ODB: `runs/orfs_baseline_20261119T131025284719666Z_9263/work/results/asap7/sattva_sram/base/4_cts.odb`, sha256 `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1`, size 861482, mtime/ctime `2026-11-19 13:11:43.658031900 +0000`, inode 281474978030812, links 1. Verified unchanged after both arms.

## Experiment

- ID `FDE-005-20261119T135453Z-4d06`; GO gate in `reports/EXPERIMENT_GO.md` (15 items, all satisfied).
- A: `pin_access` with `set_debug_level DRT pin_access 1` and D-014 in-memory `zero_ setSpecial`.
- B: identical plus `-via_in_pin_bottom_layer M4 -via_in_pin_top_layer M4`.
- Both isolated scratch copies verified byte-identical to source, distinct inodes, no symlinks; cwd confined to arm dirs; no `write_db`.

## Result

- A rc=1, B rc=1. Both logs: `[DEBUG DRT-pin_access] Access point generation for u_sram/clk did not meet : At least 3 sparse access points` then DRT-0073. DRT-0305 absent (D-014 replication worked). DRT-0419 count 8 in both.
- Log diff: only the echoed command line and script path. Scratch input hashes unchanged; no generated DBs beyond the two copies.

## Interpretation

Root cause remains **ROOT CAUSE PROBABLE** (refined: sparse-AP threshold unmet; via-in-pin control had no effect). Exact filter stage and candidate rejection reasons remain **NOT EVALUATED** — this build exposes only one aggregate debug line. D-016 adopted, no remedy approved.

## Next (requires separate approval)

FDE-006: instrumented candidate-level AP diagnostic (source-level debug print or API exposing candidate coordinates/rejection reasons) plus a scratch OBS variant comparison. Do not apply a remedy or launch a full flow.

Report: `docs/FDE-005_CONTROLLED_FLEXPA_DIAGNOSTIC.md`.
