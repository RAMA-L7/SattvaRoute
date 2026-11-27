> **Historical snapshot (2026-11-18).** Preserved verbatim from the ASAP7/OpenFinRAM milestone. It is superseded by `PROJECT_STATE.md`, `docs/evidence/README.md` and `docs/reference/CAPABILITIES.md` for the active Nangate45 1 ns control profile. Do not read "baseline not complete" as the current state.

# Current status (2026-11-18)

## Milestones

- **Milestone 0 — Feasibility & Architecture:** COMPLETE (environment audit, ORFS verification, OpenFinRAM macro generation).
- **Milestone 1 — Baseline Execution:** foundational work complete; physical-design baseline **not complete**.
- **Milestone 1C-R — DRT-0305 root cause and recovery:** COMPLETE (root cause adjudicated, D-014 applied, DRT-0305 eliminated).

## Verified stages

| Stage | Status | Evidence |
|---|---|---|
| Macro generation / inspection | PASS | `docs/benchmark/macro-sram-x4x4x1.md` |
| Synthesis + provenance | PASS | `evidence/hashes.sha256`, `benchmark/.../synth_provenance.txt` |
| Floorplan / macro placement / PDN | PASS (rc=0) | curated run summaries, `evidence/RUNS.md` |
| Placement | PASS (rc=0) | curated run summaries |
| CTS | PASS (rc=0) | curated run summaries |
| Global routing | BLOCKED — `DRT-0073` | `evidence/d014_DRT-0073_excerpt.txt` |
| Detailed routing | NOT EVALUATED | — |
| Parasitic extraction | NOT EVALUATED | — |
| Final timing / setup / hold | NOT EVALUATED | — |
| Signoff | NOT PERFORMED | — |

## Routing investigations

- **DRT-0305:** eliminated by D-014. Root cause: `zero_` constant-tie net typed `GROUND` without SPECIAL; OpenDB `$net setSpecial` in the executed mirror before `pin_access`. Verified in `orfs_baseline_20261118T171712Z` (DRT-0305 occurrences: 0; special nets 2 → 3).
- **D-013:** failed attempt, retired (`set_special_nets` does not exist; wrong checkout; wrong order).
- **DRT-0073:** current blocker — `No access point for u_sram/clk (sram_x4x4x1)` at pin access. Macro pin-access/track alignment under investigation; no fix applied.

Full report: `docs/investigations/MILESTONE_1C-R_DRT0305_ROOT_CAUSE_REPORT.md`.

## Verdict labels

Execution complete: **NO**. Routing complete: **NO**. Extraction: **NOT EVALUATED**. Timing: **NOT EVALUATED**. Engineering pass: **NO**. Signoff: **NOT CLAIMED**.
