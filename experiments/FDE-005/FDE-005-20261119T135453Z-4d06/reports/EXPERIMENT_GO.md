# FDE-005 Experiment GO Record

- **Experiment ID:** `FDE-005-20261119T135453Z-4d06`
- **Decision:** **GO** (conditional conditions below satisfied)
- **Coordinator:** orchestrator, 2026-11-19
- **Agent reviews:** A (syntax) PASS, B (geometry) PASS, C (isolation) GO conditional, D (independent) GO conditional

## Execution gate checklist

- [x] Source ODB identified: `runs/orfs_baseline_20261119T131025284719666Z_9263/work/results/asap7/sattva_sram/base/4_cts.odb`
- [x] Source SHA-256 recorded: `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1` (size 861482, mtime/ctime `2026-11-19 13:11:43.658031900 +0000`, inode 281474978030812, links 1)
- [x] Source directory protection: only read-only access; no writes to the source run
- [x] Scratch copies created: `scratch/arm_a`, `scratch/arm_b` via `cp -p`; both hashes equal source; `cmp` clean; distinct inodes; no symlinks
- [x] A/B separation: separate scratch dirs, scripts and logs; no DB reuse
- [x] Commands reviewed: `openroad -no_init -exit <script>`, no `write_db`
- [x] Debug syntax verified: `set_debug_level DRT pin_access 1` (rc=0; lowercase `drt` rejected)
- [x] Via-in-pin syntax verified: `-via_in_pin_bottom_layer M4 -via_in_pin_top_layer M4` (layer-name strings; validated by Agent A)
- [x] D-014 replication: both arms call `$zero setSpecial` in-memory (prevents DRT-0305 before `clk`) — Agent D critical condition
- [x] Diagnostic limitation acknowledged: debug output is aggregate-only (`At least 3 sparse access points`); no candidate coordinates/rejection reasons
- [x] Via-in-pin interpretation: restrictive global via-in-pin window, not an "enabler"; result is a counterfactual, not proof of original root cause
- [x] No unrelated config change: production ORFS config, D-014 patch, RTL/netlist/SDC/LEF/GDS/PDN/placement/layers unchanged
- [x] Resource use acceptable: two short `pin_access` invocations, no full flow
- [x] Output destinations: `logs/`, `evidence/`, `manifests/` under this experiment ID
- [x] Rollback/cleanup: no deletion of artifacts; failed experiments preserved; source protected by before/after hash proof

## Conditions carried into interpretation

1. Label A/B output as non-authoritative for detailed routing, extraction, timing, or signoff.
2. Do not upgrade FDE-004's ROOT CAUSE PROBABLE to ESTABLISHED without candidate-level evidence.
3. Verify source ODB hash/size/mtime/ctime/inode/links after both arms; any change is a STOP event.
4. Verify scratch input hashes after each arm; DB writes (if any) must be confined to scratch.

Execution may proceed with Experiment A, then Experiment B. No second experiment beyond A/B is authorized.
