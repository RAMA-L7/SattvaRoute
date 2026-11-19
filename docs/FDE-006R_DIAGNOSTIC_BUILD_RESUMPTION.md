# FDE-006R — Diagnostic Build Unblock and Controlled Resumption

- **Task:** T-FDE-006R
- **Date:** 2026-11-19
- **Coordinator:** orchestrator
- **Agents:** A (Bazel dependencies), B (patch review), C (build isolation), D (independent review)
- **Verdict:** **BLOCKED / INCONCLUSIVE** — the dependency blocker was resolved and the instrumentation patch was corrected, but the diagnostic build could not complete because of filesystem performance and then a WSL process-spawn failure. No candidate-level evidence was obtained; no fix was applied. Root cause remains **ROOT CAUSE PROBABLE** from FDE-004/005.

## 1. Executive summary

FDE-006R successfully recovered the missing Bazel external repositories from the local build image via `debugfs`, identified the only genuinely absent dependency (pinned Go 1.25.0 SDK), obtained explicit user authorization to fetch it, verified its SHA-256 against `MODULE.bazel.lock`, and made the offline Bazel dry-run pass (RC=0). Agent B found the FDE-006 proposed patch was not applicable as written; a corrected, target-only patch was generated, applied to the isolated source copy, converted into a valid unified diff, and dry-run verified. The actual diagnostic build on the `D:`-mounted workspace reached 13,480/13,482 actions (linking) but was prohibitively slow; a switch to a native `/tmp` workspace was attempted, after which WSL began failing to spawn processes (`getpwuid(0) failed`, I/O errors) and work was stopped. No production source, binary, design file, or run artifact was changed.

## 2. Starting revision
Publish HEAD `5da725060c442e717442edce7e46028120462e0a` = remote HEAD, clean before the milestone.

## 3. Dependency investigation and status
- Root cause of FDE-006 blocker: a fresh Bazel output base plus `--nofetch` forbids creating bzlmod extension repos; `rules_go` forces loading `@@rules_go++go_sdk+go_toolchains` during analysis.
- **Local recovery succeeded:** `debugfs -R 'rdump /bazel-repo-cache …'` extracted 178,673 files (~4 GB) and `rdump /bazel-cache` 13,601 files (~508 MB) from `/mnt/d/tools/openroad-build.img`; `rules_go` 0.62.0 source was present in local caches/image.
- **Missing dependency:** `go1.25.0.linux-amd64.tar.gz`, sha256 `2852af0cb20a13139b3448992e69b868e50ed0f8a1e5940ee1de9e19a123b613` (pinned in `MODULE.bazel.lock:2995-2997`), absent locally; no Go installation.
- **Authorization:** user explicitly authorized fetching only the pinned Go SDK and strictly required Bazel externals, with hash verification and isolated storage.
- Fetch result: tarball downloaded, SHA-256 exactly matched the pin, stored at `experiments/FDE-006R/FDE-006R-20261119T150000Z-0001/dependencies/` and in the isolated repository cache.
- Authorized dependency resolution (`--nobuild`, fetch allowed): RC=0, 1,513 packages loaded, 90,801 targets configured. Strict `--nobuild --nofetch` re-test: **RC=0** (`evidence/gate2_dryrun.log`).

## 4. Build environment
Bazelisk v1.28.1, Bazel 9.3.2 (offline cached), hermetic LLVM/C++20/-O3/ThinLTO, `--jobs=8`, `--remote_cache=`, isolated `--output_base`, isolated repository/disk caches. Build command and logs preserved in `evidence/build.log`.

## 5. Source identity and instrumentation patch
- OpenROAD source `/mnt/d/tools/src/OpenROAD` commit `629aa76b94ae420170d18692016a7be9101a53e7`; production binary `c1b90e0af69bc9779cde8fd1579a92a10738ddebb9ea16e459f280556c349ee9` — unchanged.
- Agent B verdict on the original FDE-006 patch: **NEEDS CORRECTION** (descriptive hunk headers, missing gate clear, missing log points, misleading SUMMARY).
- Corrected patch: one file (`FlexPA_acc_point.cpp`), target-only `thread_local` gate for `u_sram/clk`, 14 log points including DRC marker counts, gate cleared before every return, truthful SUMMARY. Applied to the isolated source copy; exported as a valid unified diff `patches/FDE006R_instrumentation.diff` (186 lines, sha256 `6da35dd4ba54b2443f437f970327cf6a3710e2dc7a6522aca8d9e66ad16610eb`); `patch -p1 --dry-run` passed all 14 hunks.
- Original file preserved as `patches/FlexPA_acc_point.cpp.orig`.

## 6. Build status
The isolated build on `D:` reached **13,480 / 13,482** actions (linking `openroad_unstamped`) but the foreground client timed out; the Bazel server remained CPU-bound (>44 min CPU). The server was stopped and a native `/tmp` workspace was attempted for faster linking. During that copy, WSL filesystem operations began failing with `Input/output error`, and subsequent WSL process creation failed (`getpwuid(0) failed`, `UtilInitGroups` I/O error). Per the stop condition, no system repair, alternate build, or dependency workaround was attempted. No diagnostic binary was produced.

## 7. Diagnostic binary identity
None produced.

## 8. Runtime equivalence
**NOT EVALUATED** — no binary to compare. Agent C's equivalence plan (production binary vs diagnostic debug-off, then debug-on target-only) remains the gate for any resumption.

## 9–10. Experiment A / B
**NOT EXECUTED** — blocked before a usable diagnostic binary existed. No scratch OBS control was applied; only the design exists.

## 11. Candidate-level evidence
None from tools. Geometric predictions from FDE-005/006 remain unconfirmed.

## 12. Rejection-stage evidence
Source-level only (FDE-006 pipeline); no runtime confirmation.

## 13. A/B comparison
Not possible.

## 14. Root-cause verdict
**INCONCLUSIVE for FDE-006R** (blocked). Overall status remains **ROOT CAUSE PROBABLE** from FDE-004/005: thin M4 `clk` pin over full-body M1–M5 OBS with obstructed via landings. Not upgraded to ESTABLISHED.

## 15. Confidence
HIGH that dependencies were recovered and the offline gate passed; HIGH that the corrected patch is valid and target-only; HIGH that the WSL environment failure is real; ZERO new runtime candidate evidence.

## 16. Limitations
- WSL process-spawn failure is an environment-level blocker outside FDE-006R scope.
- Building on the Windows-mounted workspace is prohibitively slow for the final link.
- External fetch was limited to the authorized pinned artifacts; no further downloads were attempted.
- No production remedy was applied.

## 17. Remedy options (unchanged, none approved)
OBS carve-out (MEDIUM), via-in-pin configuration (LOW — tested with no effect), pin geometry/access threshold (LOW–MEDIUM), placement (LOW — refuted).

## 18. Next milestone recommendation
After WSL health is restored, resume FDE-006R in a native-WSL workspace (`/tmp`) using the already-verified caches, corrected patch, and passed offline gate; complete build → runtime equivalence → Experiment A → minimal scratch OBS Experiment B. No remedy or recovery without separate approval.

## Strict scope statement
No RTL/netlist/SDC/LEF/GDS/Liberty/PDN/placement/layer/via/D-014 change; no production binary replacement; no full flow; no detailed routing; no fix. Source ODB hash verified unchanged from Windows: `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1`.
