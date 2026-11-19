# FDE-005 — Controlled FlexPA Access-Point Diagnostic Experiment

- **Task:** T-FDE-005 (diagnostic experiment only, not recovery)
- **Date:** 2026-11-19
- **Coordinator:** orchestrator
- **Agents:** A (FlexPA diagnostics/syntax), B (geometry/obstruction), C (isolation/reproducibility), D (independent experiment review)
- **Verdict:** **ROOT CAUSE PROBABLE (unchanged)** — refined but not upgraded. The experiment produced a direct tool-level observation (`At least 3 sparse access points`) but **no candidate-level rejection data**; the via-in-pin control had no effect. No fix was applied.

## 1. Executive summary

Two isolated `pin_access` diagnostics were run on independent scratch copies of the immutable FDE-003 CTS database. Both arms reproduced the FDE-004 failure exactly: `u_sram/clk` failed with DRT-0073 after generating fewer than three sparse access points. Explicit via-in-pin flags (`-via_in_pin_bottom_layer M4 -via_in_pin_top_layer M4`) did not change the outcome. The source run is byte-identical before and after. The FDE-004 root-cause classification stays **PROBABLE**: the mechanism class (thin M4 pin + full-body OBS) remains the best explanation, but the exact FlexPA filter stage that eliminated candidates is still **NOT EVALUATED** because this build exposes only an aggregate threshold message.

## 2. Experiment objective
Determine how FlexPA generates/rejects candidates for `clk`, whether OBS/via enclosure/track alignment are responsible, and whether via-in-pin configuration changes the result.

## 3. Verified source revision
Publish HEAD `a5d2b85c9795f461f14ee412520f6ba5c62dba10` = remote before changes; ORFS mirror HEAD `25b6429c…` with only the approved D-014 patch (`cd86b587…`); OpenROAD binary `/usr/local/bin/openroad` sha256 `c1b90e0af69bc9779cde8fd1579a92a10738ddebb9ea16e459f280556c349ee9`.

## 4. Source run identity
`orfs_baseline_20261119T131025284719666Z_9263` (FDE-003 validated). Route rc=2, DRT-0073, no routed DB.

## 5. Source ODB identity
- Path: `runs/orfs_baseline_20261119T131025284719666Z_9263/work/results/asap7/sattva_sram/base/4_cts.odb`
- SHA-256 `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1`
- Size 861482 bytes; mtime/ctime `2026-11-19 13:11:43.658031900 +0000`; inode 281474978030812; links 1; regular file, not symlink.
- After both arms: identical hash, size, mtime, ctime, inode and links → **source unchanged**.

## 6. Orchestration assignments
Coordinator owned GO gate, isolation, execution, adjudication and records. Agents A–D worked in parallel with disjoint read-only scopes; no agent modified project files.

## 7. Independent agent findings
- **A (FlexPA diagnostics) PASS:** `set_debug_level <tool> <group> <level>` is registered; tool must be uppercase `DRT`, group `pin_access`, level 1 (empirically rc=0). `pin_access` flags validated: `-via_in_pin_bottom_layer` / `-via_in_pin_top_layer` take **layer-name strings** (e.g. `M4`). Only one debug statement exists in `drt/src/pa/` (`FlexPA_acc_point.cpp:1484-1490`), printing an aggregate unmet requirement; `-verbose` prints only aggregate progress. No candidate coordinates or rejection reasons exist in logs at any level.
- **B (geometry) PASS:** `clk` M4 RECT 84×24 DBU at absolute (4764,16560)–(4848,16584), center on M4 track (0 DBU); VIA34 grid x=4797 lands in M3 OBS, VIA45 grid x=4812 lands in M5 OBS; zero y-margin for enclosure. Correction to FDE-004: no single grid x fits both vias. Honest counter-argument: a planar M4 escape across the 54 DBU OBS strip may be legal — not evaluated.
- **C (isolation) GO conditional:** ID `FDE-005-20261119T135453Z-4d06`; `cp -p` copies verified by SHA-256, `cmp`, distinct inodes, symlink rejection; manifest schema and source-protection proof defined; no EDA executed by C.
- **D (independent review) GO conditional:** flagged critical requirement to replicate D-014's in-memory `zero_ setSpecial` in both arms; via-in-pin is a restrictive global window, not an enabler; A/B alone cannot establish exact filter stage; AP success ≠ routability.

## 8. Isolation evidence
Experiment dir `experiments/FDE-005/FDE-005-20261119T135453Z-4d06/` with `source/`, `scratch/arm_a`, `scratch/arm_b`, `experiment_a/`, `experiment_b/`, `logs/`, `evidence/`, `manifests/`, `reports/`. Both scratch copies hash-identical to source (`35bff121…`), distinct inodes 281474978039655/656, links 1, no symlinks. Source protection verified after both arms.

## 9. Experiment GO record
`reports/EXPERIMENT_GO.md` — all 15 gate items checked, including D-014 replication, syntax validation, A/B parity, resource acceptability, output destinations, and no unrelated configuration changes. Conditions: outputs non-authoritative for engineering success; no root-cause upgrade without candidate-level evidence.

## 10. Experiment A commands and results
- Script `experiment_a/pin_access_a.tcl`: `read_db <scratch arm A>`; `$zero setSpecial` (D-014 replication); `set_debug_level DRT pin_access 1`; `pin_access`; `exit`.
- Command: `openroad -no_init -exit <script>` with cwd `experiment_a/`, stdout/stderr → `logs/experiment_a.log` (sha256 `c479d626…866c7`).
- Exit code **1**. Verbatim: `[DEBUG DRT-pin_access] Access point generation for u_sram/clk did not meet : At least 3 sparse access points`, then `[ERROR DRT-0073] No access point for u_sram/clk (sram_x4x4x1).`
- Census: DEBUG=1, DRT-0305=0, DRT-0073=2, DRT-0419=8.

## 11. Experiment B commands and results
- Script `experiment_b/pin_access_b.tcl`: identical to A plus `pin_access -via_in_pin_bottom_layer M4 -via_in_pin_top_layer M4` (the sole intended difference; flag syntax validated by Agent A).
- Exit code **1**. Log sha256 `5d6013f4…807c3`. Same aggregate debug line, same DRT-0073. Census identical to A.
- Scratch input hashes unchanged after both arms; no output DB generated beyond the copies.

## 12–14. Diagnostic / candidate / rejection evidence
The **only** tool-level candidate evidence is the aggregate unmet requirement: fewer than three sparse access points were found for `u_sram/clk`. No candidate coordinates, layers, via cuts, OBS intersections, enclosure margins, or per-candidate rejection reasons are emitted by this build. Source inspection confirms no `debugPrint` path for those details (the coordinate-printing code is dead code, `is_debug_mode=false`). Per-pin AP containers are not exposed through the Tcl/SWIG API in this build.

## 15. A/B comparison

| Observation | Experiment A | Experiment B | Difference |
|---|---|---|---|
| Target pin evaluated | Yes | Yes | none |
| Aggregate reason | At least 3 sparse APs | At least 3 sparse APs | none |
| Candidate count/coords/layers | Not exposed | Not exposed | none |
| Via / OBS / enclosure rejection detail | Not exposed | Not exposed | none |
| Tool result | DRT-0073, rc=1 | DRT-0073, rc=1 | none |
| Log diff | — | — | only the echoed command line and script path |

Interpretation: the via-in-pin control, as applied, did **not** change access-point generation for `clk`. Because the flags form a restrictive global window and may be a no-op for this geometry, this does not prove or disprove OBS/via enclosure as the underlying mechanism.

## 16–17. Updated root cause and confidence
**ROOT CAUSE PROBABLE (unchanged, refined).** New direct evidence: FlexPA failed because it could not generate at least three sparse access points for `clk`; the via-in-pin control had no effect. The geometric mechanism (thin M4 stub over full-body M1–M5 OBS, M3/M5 via landings inside OBS, zero enclosure margin) remains the best-supported explanation. Confidence: HIGH that `clk` was evaluated and sparse-AP generation failed; MEDIUM-HIGH for the OBS/via mechanism; LOW for the exact filter stage, which remains NOT EVALUATED.

## 18. Limitations
No candidate-level diagnostics available without source instrumentation (out of scope); via-in-pin flags may have been a no-op; planar M4 escape hypothesis untested; AP success would not prove routability/timing; no second pin evaluated because the tool aborts on the first failing term; `bazel-nostamp` gives hash-level binary identity only.

## 19. Remedy evaluation (none approved)

| Remedy | Evidence supporting | Risk | Confidence | Required next test |
|---|---|---|---|---|
| Via-in-pin configuration (M4 window) | Tested in B — **no effect** | Restrictive global scope; may affect other pins | LOW | Different layer pair only with candidate diagnostics |
| Macro LEF OBS carve-out near `clk` | B: via landings inside OBS; zero enclosure margin | LEF/GDS consistency; broad impact | MEDIUM | Instrumented AP dump on a copy, then controlled OBS scratch variant |
| Pin geometry/access-point threshold adjustment | Debug shows sparse-AP threshold unmet | Tool behavior; may mask geometry defect | LOW–MEDIUM | Source instrumentation or newer build comparison |
| Placement change | FDE-004/D refuted | Could break legal placement | LOW | — |

## 20. Recommendation for next milestone
**FDE-006 (separate approval required):** instrumented access-point diagnostic on a scratch copy (build-level debug print or API exposing candidate coordinates/rejection reasons), plus a scratch OBS variant comparison, to establish the exact filter stage. Do not begin a remedy or another baseline. No fix is authorized by FDE-005.
