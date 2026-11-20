# FDE-006S — WSL Recovery and Native Diagnostic Build Resumption

- **Task:** T-FDE-006S
- **Date:** 2026-11-20
- **Coordinator:** orchestrator
- **Agents:** A (WSL health), B (artifact integrity), C (native workspace), D (independent safety review)
- **Verdict:** **BLOCKED / INCONCLUSIVE** — WSL health was restored/verified without destructive recovery, the native workspace and offline gate passed, but the instrumented build was SIGKILLed (RC=137) during the final link. No diagnostic binary, no runtime equivalence, no Experiments A/B, no candidate-level evidence. No fix was applied. Root cause remains **ROOT CAUSE PROBABLE** from FDE-004/005.

## 1. Executive summary

FDE-006R was blocked by a WSL process-spawn failure and drvfs link slowness. FDE-006S verified that WSL is healthy again, identified the prior failure as a transient filesystem-I/O cluster following an unclean shutdown, recovered the missing native caches from the surviving D: artifacts, built an isolated native workspace at `/root/sattvaroute-fde006s/`, and passed the strict offline Bazel gate (RC=0). The instrumented `//:openroad` build compiled 13,480 of 13,482 actions but was killed during `Linking openroad_unstamped` after ~44 minutes (RC=137, no binary). No speculative retry was attempted.

## 2. Starting revision
Publish HEAD `7243a72583a3cadf559c1a4d05d991c102c4eec8` = remote HEAD, clean before the milestone.

## 3. WSL health and recovery
- Agent A: Ubuntu-24.04 Running, WSL2, Windows build 26200; shell spawn stability 10/10; root identity via `id`, `getent passwd root`, and Python `pwd.getpwuid(0)` all pass; `/etc/default/locale` readable; native ext4 r/w OK, 949 GB free; systemd 0 failed units; 7.1 GiB RAM available.
- Prior failure classification: transient cluster — unclean WSL shutdown → ext4 journal/`loop0` inconsistency → filesystem EIO → cascading NSS/locale read failures (`getpwuid(0)`, `UtilInitGroups`). Not persistent identity corruption or resource exhaustion.
- **No WSL recovery action was performed** (none needed); only verification. No unregister/reset/reinstall/repair/package install.
- Host C: free space was raised from 1.03 GB to 5.4 GB by user-authorized removal of regenerable caches/temp folders before the build.

## 4. Agent assignments and findings
- **A (WSL health):** PASS, no recovery needed; flagged C: space as recurrence risk — addressed.
- **B (artifact integrity):** CONDITIONAL PASS — patch `6da35dd4…610eb`, Go SDK `2852af0c…b613`, source ODB `35bff121…400e1`, production binary `c1b90e0a…49ee9` all verified; `/tmp` caches gone but D: copies intact (178,673 repo files, 13,601 disk files, identical counts); both gate logs RC=0.
- **C (native workspace):** native ext4 suitable; slow link root cause was drvfs output base; designed `/root/sattvaroute-fde006s/`; noted `git archive` submodule caveat (encountered and fixed).
- **D (independent review):** conditional GO on all gates; required C: ≥5 GB, cache reuse, equivalence before A/B; noted patch lacks DRC marker geometry, capping root cause at PROBABLE.

## 5. Native workspace and source identity
- Workspace: `/root/sattvaroute-fde006s/` (native ext4), with `source/`, `build/`, `cache/`, `logs/`, `experiments/`, `evidence/`, `patches/`.
- Initial `git archive` source omitted `src/sta` (submodule) and failed analysis; replaced with the FDE-006R isolated source copy (13,002 files), which includes all submodules.
- `FlexPA_acc_point.cpp`: pristine `ef9c84fe6de23506a5e29a81e7735ee28f8748df5f6b5cef370452b5eba0f739`, patched `305230b9dafcf64b5cbe4ff75fbc0dbdfe61230cd53b873fe47e35d6b2ca8559` — matches independent review.
- Corrected diff `FDE006R_instrumentation.diff` sha256 `6da35dd4ba54b2443f437f970327cf6a3710e2dc7a6522aca8d9e66ad16610eb`.
- Caches: D: repository/disk cache trees used read-only (no new fetch); Go SDK injected and hash verified.

## 6. Dependency status
Materialization gate RC=0 (1,513 packages, 90,801 targets, 138 aspects) after one authorized resolution from the verified cache; strict `--nobuild --nofetch` gate RC=0 (`evidence/gate_strict_offline.log`). No new dependencies fetched in FDE-006S.

## 7. Diagnostic build
- Command: `bazelisk --output_base=/root/sattvaroute-fde006s/build/output_base build --jobs=8 --remote_cache= --repository_cache=<D: repo cache> --disk_cache=<D: disk cache> -c opt //:openroad`.
- Result: reached **13,480 / 13,482** actions, `Linking openroad_unstamped` for 2,639 s, then process killed: `Killed ... RC=137` (`evidence/build.log`). No `blaze_oomed` marker and no journal OOM entry; SIGKILL cause not conclusively established (memory pressure under 7.6 GiB with ThinLTO is plausible but unproven).
- No binary produced; no binary hash or version output.

## 8–9. Runtime equivalence / Experiments A–B
**NOT EXECUTED** — no diagnostic binary. No candidate-level evidence, no A/B comparison.

## 10. Root-cause adjudication
**INCONCLUSIVE for FDE-006S** (blocked at build). Overall status remains **ROOT CAUSE PROBABLE** (thin M4 `clk` pin over full-body M1–M5 OBS with obstructed via landings). Not upgraded to ESTABLISHED.

## 11. Limitations
- WSL memory cap 7.6 GiB; final link exceeded available resources or was externally killed.
- `git archive` submodule caveat required source substitution (documented).
- `/tmp` caches not persistent across WSL restarts; D: copies used read-only.
- No production source, binary, design, ORFS config, or D-014 patch changed; no fix applied; no system repair beyond authorized C: cleanup.

## 12. Remedy options (unchanged, none approved)
OBS carve-out (MEDIUM), via-in-pin config (LOW — tested no effect), pin geometry/access threshold (LOW–MEDIUM), placement (LOW — refuted).

## 13. Next milestone recommendation
Resume FDE-006S only after a build environment with sufficient memory for the final ThinLTO link (e.g. raised WSL memory cap, or link with reduced jobs/LTO settings) is approved. Reuse the verified native workspace, caches, patch, and offline gate; then complete build → equivalence → Experiments A/B. No remedy or recovery without separate approval.

## Strict limitations
No RTL/netlist/SDC/LEF/GDS/Liberty/PDN/placement/layer/via/D-014 change; no production binary replacement; no full baseline; no detailed routing; no fix. Source ODB hash verified unchanged: `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1`.
