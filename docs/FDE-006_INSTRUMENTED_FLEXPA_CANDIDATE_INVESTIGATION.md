# FDE-006 — Instrumented FlexPA Candidate-Level Access-Point Investigation

- **Task:** T-FDE-006
- **Date:** 2026-11-19
- **Coordinator:** orchestrator
- **Agents:** A (FlexPA source instrumentation), B (geometry), C (build/isolation), D (independent experiment review)
- **Verdict:** **INCONCLUSIVE** — the isolated diagnostic build is **BLOCKED** at Gate 2 (offline dependency resolution). No candidate-level evidence was obtained; no production remedy was applied. The prior root-cause status remains **ROOT CAUSE PROBABLE** from FDE-004/005 and is **not upgraded**.

## 1. Executive summary

FDE-006 aimed to expose candidate access-point coordinates and rejection reasons for `u_sram/clk` via target-specific instrumentation of FlexPA and a controlled scratch OBS comparison. Read-only source analysis produced a complete candidate-generation/filter pipeline and a narrow, one-file instrumentation design. Geometry analysis independently reconstructed the expected candidate set and the smallest discriminating OBS control. Build analysis found Bazel 9.3.2 cached offline but an empty repository cache; the prior build image could not be mounted read-only, and an offline `--nofetch` dry-run failed because `@@rules_go++go_sdk+go_toolchains` is not cached. Fetching dependencies or installing packages requires approval that FDE-006 does not grant, so the build and both experiments were stopped. All prior artifacts remain unchanged.

## 2. Starting revision
Publish HEAD `6f338df65fb37ac2ba570e2ee446c71d6ba8017e` = remote (`origin/main`), clean before the milestone. No history rewrite.

## 3. Source run and ODB identity
- Source run `orfs_baseline_20261119T131025284719666Z_9263`.
- ODB `4_cts.odb` sha256 `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1`, size 861482 bytes — unchanged before and after all FDE-006 work.
- OpenROAD source `/mnt/d/tools/src/OpenROAD` commit `629aa76b94ae420170d18692016a7be9101a53e7`; production binary `/usr/local/bin/openroad` sha256 `c1b90e0af69bc9779cde8fd1579a92a10738ddebb9ea16e459f280556c349ee9` — unchanged.
- Source dirty count: **2** (`git status --porcelain | wc -l` in the OpenROAD source tree). Agent D reported 373 dirty files; direct verification resolves the disagreement in favor of 2 (the larger count came from evaluating the copied tree against the enclosing SattvaRoute repository, which has no OpenROAD `.git`). Documented rather than silently choosing.

## 4. Orchestration and assignments
Coordinator owned gates, isolation, execution decisions and records. Agents worked independently and read-only: A source pipeline, B geometry, C build/isolation, D experiment review. No agent modified source, binary, design or run artifacts.

## 5. FlexPA source analysis (Agent A)
Exact call chain: `TritonRoute.tcl:281,351` → `pin_access_cmd` (`TritonRoute.i:123,140`) → `TritonRoute::pinAccess` (`TritonRoute.cpp:1099,1129`) → `FlexPA::main` (`FlexPA.cpp:450`) → `prep` (`:239`) → `genAllAccessPoints` (`FlexPA_acc_point.cpp:1537`) → `genInstAccessPoints` (`:1514`) → `genPinAccess` (`:1407`) → `genPinAccessCostBounded` (`:1292`) → filters → `EnoughAccessPoints` (`:1277`) → `EnoughSparsePoints` (`:1215`).

## 6. Candidate-generation pipeline (derived from code, not assumed)

```
pin shapes → layer/top-routing gating → rect/right-way gates
→ cost-pair coordinate generation (createAPsFromLayerToRectCoordsMap)
→ createSingleAccessPoint (outside-maxrect / duplicate drops)
→ planar DRC (filterPlanarAccess, :652-705)
→ via boundary / enclosure / DRC (filterViaAccess, :981-1119)
→ final hasAccess() gate (:1318-1331)
→ sparse-AP threshold >= 3 (:1215-1252) → FDE-005 message (:1484-1490)
```

`frAccessPoint` (`frAccess.h:26-212`) stores point, layer, access bits, viaDefs and types but **no rejection-reason field** — reasons must be logged at the decision points. Threshold = 3 for macro and std-cell pins (`drt-global.h:62-63`).

## 7. Instrumentation design
File-local, compile-time-targeted `thread_local` gate in `FlexPA_acc_point.cpp` only; target constants `u_sram` / `clk`; ~10 `FDE006_LOG` insertions at create/planar/via/final/sparse decision points. Pure logging, no header/signature/Tcl/config changes, no decision-condition changes. Gate clears on every exit of `genPinAccess`. Proposed patch preserved at `experiments/FDE-006/FDE-006-20261119T143807Z-7004/patches/FDE006_instrumentation_PROPOSED.diff` — **NOT APPLIED**.

## 8. Diagnostic source patch
No source file was modified (original or copy). The patch above is a design artifact only.

## 9. Build reproducibility
Bazelisk v1.28.1 at `/usr/local/bin/bazelisk` resolves `.bazelversion` 9.3.2 from an offline cache; prior build profile estimated ~11.3 min for `//:openroad`. Hermetic LLVM/C++20/-O3/ThinLTO. Exact compiler revision and full offline repo completeness **NOT EVALUATED** — and then disproven by the dry-run below.

## 10. Diagnostic binary identity
No diagnostic binary was produced. Production binary hash verified unchanged (`c1b90e0a…`).

## 11. Experiment gates

| Gate | Verdict | Basis |
|---|---|---|
| 1 — Instrumentation | CONDITIONAL GO (design only) | A's target-only design; D required marker-level detail and behavior-neutral detectors, not fully resolved |
| 2 — Diagnostic build | **NO-GO — BLOCKED** | offline `--nofetch` fails: `@@rules_go++go_sdk+go_toolchains` not cached; image mount failed; repo cache empty |
| 3 — Experiment A | NOT ATTEMPTED | Gate 2 blocked |
| 4 — Experiment B | NOT ATTEMPTED | Gate 2 blocked |

## 12. Experiment A results
**NOT EXECUTED — BLOCKED at Gate 2.** No candidate coordinates, layers, via identities or rejection reasons were obtained.

## 13. Experiment B results
**NOT EXECUTED — BLOCKED at Gate 2.** The minimal OBS control was designed but never applied, even on scratch.

## 14. Candidate-level evidence
None from tools. Agent B's independently reconstructed expectation: VIA45-up candidates at x ≈ 4787/4812/4825 DBU on y = 16572, all with M3/M5 landing boxes inside full-macro OBS; VIA34 at x 4797 is geometrically legal but is not generated for macro inst-terms in this source. These are **geometric predictions**, not instrumented observations.

## 15. Filter-level evidence
Source-level only: planar DRC at `:700`, via enclosure/DRC at `:945-961`, final `hasAccess()` at `:1319`, sparse threshold at `:1215-1252`. No runtime confirmation.

## 16. A/B comparison
Not possible — neither arm ran. No claim is made about OBS causality beyond the prior geometric evidence.

## 17. Root-cause adjudication
**INCONCLUSIVE for FDE-006** (build blocked; no candidate-level data). Overall project root-cause status remains **ROOT CAUSE PROBABLE** from FDE-004/005: thin M4 `clk` pin over full-body M1–M5 OBS with obstructed via landings. Not upgraded to ESTABLISHED.

## 18. Confidence
HIGH that source pipeline and instrumentation points are correctly identified (Agent A, exact file:line); HIGH for geometry reconstruction (Agent B); HIGH that the build is blocked offline (reproduced dry-run, rc=1); ZERO new runtime candidate evidence.

## 19. Limitations
- `bazel` image `/mnt/d/tools/openroad-build.img` could not be mounted read-only in this WSL environment.
- Repository cache empty; missing `rules_go` go_sdk toolchain; network fetching and dependency installation are outside FDE-006 scope.
- Copied source tree is 1.85 GB / 13,002 files and is kept locally, not published.
- Agent D's requirement for an unpatched control build byte-identical to production was not satisfied; the intended alternative was a runtime equivalence arm (production binary vs instrumented debug-off/on), also not executed.
- No fix, no full baseline, no detailed routing.

## 20. Remedy options (none approved)
Unchanged from FDE-005: OBS carve-out (MEDIUM), via-in-pin configuration (LOW — tested with no effect), pin geometry/access threshold adjustment (LOW–MEDIUM), placement (LOW — refuted). All require a separate milestone and approval.

## 21. Recommendation
**FDE-006 rerun requires approval for one of:** (a) an offline repository/cache bundle containing `rules_go++go_sdk+go_toolchains` (or explicit authorization to fetch), or (b) a prebuilt instrumented binary from an environment with the full toolchain. After either, re-run Gates 1–4 unchanged, including the runtime equivalence arm and the minimal scratch OBS control. Do not apply any production remedy.

## Strict limitations
No production LEF/GDS/SDC/netlist/RTL/PDN/placement/layer/via/D-014 change; no source or binary modification; no fix; no full flow. The FDE-003 run and FDE-005 experiment artifacts are untouched.
