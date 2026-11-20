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

**Status: STOPPED at Gate 2 (new approval).** No second speculative run was launched; no production file changed; no DRC waiver or suppression.
