# T-ENGINEERING-009 — Prior-Experiment Review: What Was Learned and What Remains Unknown

| Experiment | What it established | What it did NOT establish | Reuse constraint |
|---|---|---|---|
| **FDE-005 via-in-pin A/B** | Same binary/ODB/config; flag-only arm difference; both fail identically → tested lever is a no-op | Nothing about OBS mechanism or candidate rejection detail | Do not repeat the via-in-pin lever |
| **FDE-006T candidate diagnostic** | 9 M4 candidates generated; all dropped at final `hasAccess()`; `n_aps=0`; three-way runtime equivalence; SIGKILL = external supervisor, not OOM | OBS causality (Experiment B blocked by no safe Tcl API); per-marker provenance | Instrumented binary `9c0ed727…` preserved; use for equivalence baseline |
| **FDE-006U broad carve A/B** | Same-binary single-variable broad M4 OBS carve flips APs 0→3 and removes DRT-0073 in the scratch DB; mechanism bounded | Production relevance; no no-op control; no full flow; no per-marker provenance | Mechanism-level only; broad carve physically unjustified (120+92 real shapes) |
| **FDE-007 R1-N (x 3534–3672)** | Corridor reached DB (18 OBS boxes); still DRT-0073, 0 APs; left strip remained OBS | Why spacing/EOL markers persist; provenance of 2 nm sliver | REJECTED as tested; one family with R1-N-W |
| **FDE-007 R1-N-W (x 3474–3672)** | 2 nm sliver at new OBS edge; `Short` 54→45 but `Metal Spacing` 63→82, `Lef58` 31→40; 0 APs | Whether sliver is artifact or real obstruction (no `getSrcs()`); all-pin status | REJECTED as tested; INCONCLUSIVE sub-claim; no third variant without new mechanism |

## Consolidated lessons

1. **AP count is the binding response**, not marker count: 0 accepted APs caused DRT-0073; sparse threshold 3 is downstream.
2. **OBS x-only widening is insufficient**: a ±24 nm y margin is smaller than the ~48 nm M4 EOL/corner keepout reach, so residual bands produce spacing/EOL markers.
3. **No-op control remains absent**: FDE-006U's three-way equivalence checked instrumentation neutrality, not a control arm.
4. **Attribution is spatial/correlational**: marker `getSrcs()` was never logged; the 2 nm sliver stays INCONCLUSIVE.
5. **No full-flow evidence**: all remedy attempts stopped at route; no routing/DRC/timing claims.
6. **DRT-0419 is decoupled**: persists in FDE-006U exp_b where DRT-0073 was absent.

## What remains unknown

- Which object emits each `Short` / `Metal Spacing` / `Lef58` marker (source provenance).
- Whether the 2 nm sliver is an OBS-edge artifact or a real metal violation.
- The exact geometry envelope (x and y) that removes all blocking markers while exposing zero foreign-net GDS shapes.
- All-pin AP status and D/Q pin access.
- Whether any corrected geometry survives global/detail routing, DRC, extraction and timing.

**Decision:** do not repeat any previous remedy variant. The next diagnostic must add new information (provenance) before any new geometry is considered.
