# FDE-006T — Diagnostic Link Resource Investigation and Build Completion

- **Task:** T-FDE-006T
- **Date:** 2026-11-20
- **Coordinator:** orchestrator
- **Agents:** A resources, B linker/build configuration, C workspace resumption, D independent review
- **Verdict:** **ROOT CAUSE PROBABLE** (refined, high confidence) — candidate-level evidence now identifies the rejection stage, but Experiment B's OBS control is blocked, so OBS causality is not proven by a controlled comparison. No production fix applied.

## 1. Executive summary

The FDE-006S build SIGKILL was **not an OOM kill**: guest `oom_kill=0`, no OOM log entries, unused swap. Evidence points to an external ~2,640 s wall-clock supervisor terminating the tool-session-attached process. The diagnostic build was completed by launching the identical command as an independent host process — **no resource, memory, swap, LTO, or Bazel-flag change**. The resulting binary (`9c0ed727…`) passed runtime equivalence against the production binary (logs identical apart from script path) and, with instrumentation enabled, exposed candidate-level FlexPA evidence for `u_sram/clk`: nine candidate APs generated, all rejected by planar and via DRC checks, zero accepted, sparse count 0 < threshold 3. The minimal scratch OBS control could not be executed because this OpenROAD Tcl binding has no safe API to remove a master-level obstruction (direct deletion crashes the tool).

## 2. Starting revision and evidence
Publish HEAD `62316d8e2124c4959f9baa3b52723130112bfdbc` = remote. Source ODB `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1` verified unchanged. Production binary `c1b90e0a…` verified unchanged.

## 3. Resource diagnosis (Agent A)
- WSL 7.6 GiB RAM, 2 GiB swap (unused), default 8 GiB cap (`hv_balloon: 8082 MB`), no `.wslconfig`.
- `oom_kill=0` for the boot spanning the build; no `journalctl -k`/`dmesg` OOM entry; no `blaze_oomed`; Bazel started with `--noshutdown_on_low_sys_mem`.
- Progress stopped at exactly ~2,639 s in the link → external wall-clock supervisor (confidence HIGH). Host memory pressure was a background condition, not a proven cause.
- Leftover Bazel daemon from FDE-006S was shut down before resumption; an unrelated project's `openroad flow.tcl` was left untouched.

## 4. Linker configuration (Agent B)
- Exact command: `bazelisk --output_base=/root/sattvaroute-fde006s/build/output_base build --jobs=8 --remote_cache= --repository_cache=<D:> --disk_cache=<D:> -c opt //:openroad`.
- **ThinLTO was NOT active** — `thin_lto` is under `build:opt` in `.bazelrc`, and only `-c opt` was used (production too). Prior claims of ThinLTO were wrong.
- Linker: hermetic LLVM 23.1.2 clang++ with `-fuse-ld=lld`, 4,398 object inputs, `--gc-sections`, `--icf=safe`; one final link action.
- LTO changes rejected: would break binary equivalence with the production control.

## 5. Workspace and gate (Agent C)
Workspace `/root/sattvaroute-fde006s/` verified: 13,002 source files, patched `FlexPA_acc_point.cpp` `305230b9…`, diff `6da35dd4…`, Go SDK `2852af0c…`, production binary protected. Strict `--nobuild --nofetch` gate RC=0 before build. Agent C labelled the prior kill OOM — contradicted by Agent A's direct kernel evidence; adjudicated as **not OOM**.

## 6. Independent review (Agent D)
Conditional GO on all gates; no resource change on an unclassified cause; no LTO change; reuse output base only after integrity gates; equivalence must precede A/B; current evidence ceiling PROBABLE without a valid A/B.

## 7. Resource strategy
| Strategy | Decision |
|---|---|
| More WSL RAM / swap | Not applied — no OOM evidence; would not address wall-clock kill |
| Lower concurrency / LTO change | Not applied — single link action; changes equivalence |
| Resume existing build state detached | **Applied** — least invasive; identical command, no flag change |

No Windows or WSL configuration was modified.

## 8. Build resumption
Launched as an independent Windows-hosted process (`Start-Process wsl.exe`), avoiding the tool-session supervisor. Result: **RC=0**, completed 2026-11-20T16:38:01Z, 781 actions (12,701 cache hits, 777 disk-cache hits). Binary: `openroad_unstamped`, 118,207,328 bytes, sha256 `9c0ed727dea3c6a07c04369472eef8c51c68ca7c095a0c9d925da7e2440ed86f`, version `bazel-nostamp`. Production binary untouched.

## 9. Runtime equivalence
Three arms on independent scratch copies of `4_cts.odb` (each input hash `35bff121…`), all with the approved D-014 in-memory `zero_ setSpecial`:
- production binary, debug off: rc=1, DRT-0305=0, DRT-0073=2, no FDE006R lines.
- diagnostic binary, debug off: rc=1, identical log except Tcl script path — **PASS**.
- diagnostic binary, debug on: rc=1, 132 FDE006R lines, only for `u_sram/clk` — target filtering confirmed.

## 10. Experiment A — original OBS (candidate-level evidence)
Nine AP candidates generated, all at y=16572 on layer 8 (M4): x = 4740, 4764, 4787, 4788, 4806, 4812, 4825, 4836, 4860. Every candidate had planar DRC markers (n=1–5) and via DRC markers (n=1–9); all were dropped at the final `hasAccess()` gate (`reason=no_access`, 9 drops); `aps_out=0`; sparse `n_aps=0 n_sparse=0 thresh=3 macro=true`; `SUMMARY aps=0 n_sparse_last=0 met=false`; final DRT-0073. This directly identifies the rejection stage: DRC/obstruction-invalid planar and via access at every generated candidate, followed by the sparse-AP threshold failure.

## 11. Experiment B — scratch OBS control — **BLOCKED**
Master has five full-body OBS boxes (M1–M5, local 0,0–3672,13608 DBU). The Tcl binding offers no usable removal API: `$o delete` is invalid, `odb::delete_dbSBox` expects a different type, and `odb::delete_dbBox` crashes the process. No production LEF/GDS/DB was modified. Per the stop condition, the control was not improvised; OBS causality remains unproven by controlled comparison.

## 12. A/B comparison
Not possible (B blocked). Experiment A alone provides candidate-generation and rejection-stage evidence.

## 13. Root-cause verdict
**ROOT CAUSE PROBABLE**, high confidence: FlexPA generates nine M4 candidates for `clk`, but planar and via DRC checks find violations at every one (consistent with the full-body OBS and thin-pin geometry), leaving zero access points and failing the sparse threshold of 3. **Not ESTABLISHED** because the minimal OBS control could not be executed.

## 14. Limitations
No valid A/B control; patch logs DRC marker counts but not marker type/bbox; no routed database; AP success would not prove routability; `bazel-nostamp` gives hash-level binary identity only.

## 15. Remedy options (none approved)
OBS carve-out (MEDIUM — causal role not control-proven), via-in-pin config (LOW — no effect in FDE-005), pin-geometry/threshold adjustment (LOW–MEDIUM), placement (LOW — refuted).

## 16. Next milestone
Approve a controlled OBS experiment using a supported mechanism (scratch LEF rebuild or source-level OBS-edit hook), or a patch that logs DRC marker type/geometry; then repeat A/B. No remedy or recovery without separate approval.

## Strict scope
No RTL/netlist/SDC/LEF/GDS/Liberty/PDN/placement/layer/via/D-014 change; no production binary replacement; no full baseline; no detailed routing; no fix.
