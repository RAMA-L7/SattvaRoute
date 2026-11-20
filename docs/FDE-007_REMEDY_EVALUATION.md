# FDE-007 — Remedy Evaluation (Gate 1 + Gate 3–4 result)

## Addendum: R1-N scratch full-flow attempt (2026-11-20)

### Approved remedy and implementation
- Approval: user approved **R1-N** (narrow GDS-derived per-pin M4 OBS corridors in a scratch LEF, full-flow validation), recorded at `experiments/FDE-007/FDE-007-20261120T181000Z-0001/evidence/APPROVAL.md`.
- Scratch design: `experiments/FDE-007/FDE-007-20261120T181000Z-0001/scratch_design/`; production LEF `f1c18877…` unchanged; scratch LEF `a0e2ea7c…` differs **only** in the M4 OBS RECT (full-body → 14 rects with 12 corridors at x 3534–3672 DBU, pin y ±24 DBU).
- Run ID: `orfs_baseline_20261120T182251409618918Z_97829`; process rc=2; stages: check/synth/floorplan/place/cts PASS, route rc=2; flow completed in ~93 s.

### Verified effect of the approved change
- The modified LEF **reached the flow**: `1_synth.odb`, `2_floorplan.odb`, and `4_cts.odb` all show 18 M4 OBS boxes with the intended 12 corridors; preflight hashes the scratch LEF `a0e2ea7c…`.
- DRT-0305 = 0 (D-014 still effective); DRT-0419 = 8 (parity).
- **DRT-0073 persists on `u_sram/clk`** → the approved R1-N geometry does **not** resolve pin access.

### Root cause of the remedy failure (instrumented diagnostic, binary `0d890431…`)
- Remaining planar `Short` bbox `(4704,16560)-(4764,16584)` absolute = local `(3474,8376)-(3534,8400)` — the **left strip** of the `clk` pin, which the approved corridor (x 3534–3672) did not free.
- `Metal Spacing` markers at y bands `(4704,16536)-(4848,16560)` and `(4704,16584)-(4848,16608)` — immediately above/below the pin.
- VIA45 M5 landing `Short` markers persist (as in FDE-006U, where they were not decisive).
- Result: 3 candidates created, all dropped at final `hasAccess()`, sparse 0 < 3, DRT-0073.

### Required new approval (R1-N-W)
Widen each of the 12 M4 OBS corridors in the **scratch LEF only** from x 3534–3672 to **x 3474–3672 DBU**, keeping the same y windows (pin y ±24 DBU). Rationale: the left strip contains the pin's **own-net** M4 terminal stub (Agent A GDS census: same-net `clk` path, zero foreign-net 40/0 shapes), so freeing it does not expose occupied foreign metal. A narrower y margin cannot fix the observed metal-spacing markers. This is a materially different geometry than the approved R1-N delta; a new approval is required before any implementation.

**Status after R1-N-W execution: FDE-007 BLOCKED — both approved scratch remedies REJECTED as tested.** No further geometry variant was attempted; no production file changed; no DRC waiver or suppression.

### Addendum: R1-N-W execution result (2026-11-21)
- Approval: user approved D-023 (R1-N-W) after R1-N failed; record at `experiments/FDE-007/FDE-007-20261121T090000Z-0002/evidence/APPROVAL.md`.
- Scratch LEF `917e094e…` (corridors x 3474–3672 DBU, same 12 y windows); production LEF `f1c18877…` unchanged; diff touches only M4 OBS (24 lines).
- Run ID `orfs_baseline_20261120T183451711584818Z_99729`: check/synth/floorplan/place/cts PASS, route rc=2 DRT-0073, ~96 s.
- Verified OBS reached `4_cts.odb` (18 boxes, M4 bands starting at x=3474); DRT-0305=0, DRT-0419=8 parity.
- Instrumented diagnosis: planar `Short` bbox `(4703,16560)-(4705,16584)` — a 2 nm strip centred on the new OBS edge (local x=3474); `Metal Spacing` bands, `Lef58` EOL markers and VIA45 M5 `Short`s persist; 0 accepted APs, sparse 0<3. Widening reduced `Short` 54→45 but raised `Metal Spacing` 63→82 and `Lef58` 31→40 — net APs stayed 0.
- Independent review verdict: **FDE-007 BLOCKED** (new approval gate), **R1-N REJECT**, **R1-N-W REJECT** (2 nm sliver INCONCLUSIVE — boundary-correlated; marker provenance absent). No further variant authorized.
- Required for any new proposal: `getSrcs()` marker provenance, GDS census at sliver/spacing bands, mechanism for spacing/EOL failures, all-pin AP evidence, canonical DB diff + no-op control, foreign-metal-free justification, full-flow plan.
