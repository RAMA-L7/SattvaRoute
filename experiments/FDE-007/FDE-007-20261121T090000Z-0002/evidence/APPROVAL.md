# FDE-007 Gate 2 Approval — R1-N-W

- **Decision ID:** D-023
- **Remedy:** R1-N-W — widen the 12 scratch M4 OBS corridors from x 3534–3672 to x 3474–3672 DBU (same y windows; pin's own-net left strip freed). Scratch LEF only.
- **Approver:** project owner (user), via explicit approval response.
- **Timestamp:** 2026-11-21 session.
- **Target:** `experiments/FDE-007/FDE-007-20261121T090000Z-0002/scratch_design/macro/sram_x4x4x1.lef` (scratch copy, hash `917e094e…`).
- **Scope:** one new unique run ID; same full-flow validation gates as R1-N; no production file/config/binary change; no waiver; no deployment; stop if route fails again.
- **Rationale:** R1-N's remaining planar Short is the clk pin's own-net left strip at local x 3474–3534, which the approved R1-N corridor did not free.
