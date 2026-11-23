# T-ENGINEERING-009 — Current Engineering State Audit

- **Date:** 2026-11-23
- **Type:** read-only audit; no EDA, experiment, remedy or production change.
- **Coordinator:** reconciles Agents A (geometry), B (OpenROAD mechanism), C (flow/configuration).

## 1. Repository and integrity state (verified)

| Item | Verified value |
|---|---|
| Publication repo | `D:\SattvaRoute_publish`, branch `main`, HEAD `3dd78dab28e633bb124ff4a1fefcf1525a01f7b6`, equals `origin/main`, clean tree |
| Live repo | `D:\SattvaRoute`, branch `master`, uncommitted engineering records preserved; no locks before T-ENGINEERING-009 |
| KB | `verify` PASS — 18 records, 18-link chain, 0 problems |
| Protected artifacts | `verify-immutable` PASS — 9/9 OK, `changed=[]` |
| Skill validator | `validate_skills.py` PASS=13 FAIL=0 |
| R2 checklist | `6900ebc8b17821f7b1bb30f29224d0eb120042fd5e392dbbf42046877ba4cb9d`, DRAFT/INACTIVE |
| Production ODB | `runs/orfs_baseline_20261119T131025284719666Z_9263/.../4_cts.odb`, SHA-256 `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1` |
| Production binary | `/usr/local/bin/openroad`, SHA-256 `c1b90e0af69bc9779cde8fd1579a92a10738ddebb9ea16e459f280556c349ee9` |
| Production LEF / GDS | `f1c18877c27152bc81dce3bfa76308f29c9faa54047de4ac5a3f7d160b4bba31` / `12c56777a060270215ad7c43a881230febc9f3dc272bf9a436da60efd510d651` |
| Macro | `sram_x4x4x1`, 3.672 × 13.608 µm LEF; 22 pins; Liberty **estimated**, no silicon characterization |
| D-014 | `$net setSpecial` in execution mirror `global_route.tcl` before `pin_access`; DRT-0305 RESOLVED; mirror `cd86b587…` |
| DRT-0073 status | Unresolved; all FDE-007 remedy variants REJECTED; FDE-007 BLOCKED |

## 2. FDE lineage reconciled (no duplication)

| FDE | Contribution | Current status |
|---|---|---|
| FDE-003 | Hardened runner validated on real baseline; route rc=2 DRT-0073; DRT-0305=0 | authoritative baseline |
| FDE-004 | Geometry/track/source investigation; placement, grid, net-classification eliminated; root cause PROBABLE | finding adopted |
| FDE-005 | via-in-pin M4 config A/B no effect; aggregate-only log ceiling | remedy family ELIMINATED for tested lever |
| FDE-006 / 006R / 006S | Instrumentation build blockers; offline deps, WSL/drvfs, SIGKILL; no binary initially | BLOCKED history, superseded |
| FDE-006T | Diagnostic binary `9c0ed727…`; 9 candidates all dropped; three-way runtime equivalence; Experiment B blocked by no safe OBS API | candidate-level evidence |
| FDE-006U | Instrumented binary `0d890431…`; same-binary single-variable broad M4 OBS carve flips APs 0→3 and removes DRT-0073; **no no-op control arm** | mechanism ESTABLISHED (bounded), not a production remedy |
| FDE-007 | R1-N (`a0e2ea7c…`) and R1-N-W (`917e094e…`) narrow corridors; both rc=2 DRT-0073, 0 APs; one family `M4_OBS_CORRIDOR`; 2 nm sliver INCONCLUSIVE | BLOCKED; both remedies REJECTED |

No previous investigation is reopened or repeated; this task consumes their evidence as authoritative history.

## 3. Governing constraints

- Production artifacts, baseline runs, historical FDE reports and KB records are immutable for this task.
- Any remedy needs a new decision and approval; no experiment may be launched without explicit authorization.
- Failed families must not be repeated without new technical justification; `M4_OBS_CORRIDOR` is one family.
- R2 is applied only as an **advisory shadow** to the final proposed diagnostic; it is not a gate.
- Evidence labels remain VERIFIED / OBSERVED / INFERRED / UNKNOWN; no success inferred from missing evidence.
