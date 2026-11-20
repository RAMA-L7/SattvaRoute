# FDE-007 Gate 2 Approval Record

- **Decision ID:** D-022 (PROPOSED, adopted with approval below)
- **Remedy ID:** R1-N — narrow GDS-derived per-pin M4 OBS corridor carve (Variant A, x 3534–3672 DBU, 72 nm tall corridors at each of 12 M4 signal pins)
- **Approver:** project owner (user), via explicit approval response to the FDE-007 Gate 2 question
- **Timestamp:** 2026-11-20 (session record)
- **Scope:** isolated scratch design tree and scratch macro LEF ONLY; full-flow validation with a unique run ID; no production file, RTL, netlist, SDC, macro, PDN, placement, layer, via, ORFS config, D-014, or production binary change; no DRC waiver or deployment
- **Target file:** `experiments/FDE-007/FDE-007-20261120T181000Z-0001/scratch_design/macro/sram_x4x4x1.lef` (scratch copy)
- **Validation requirements:** pin access → floorplan/place → CTS → global routing → detailed routing → DRC → extraction → timing; honest reporting of any BLOCKED/NOT EVALUATED stage
- **Exact delta:** production LEF `f1c18877…` → scratch LEF `a0e2ea7c…`; diff touches only the M4 OBS RECT (1 line → 14 lines)
- **Note:** approval of this remedy does not authorize alternatives, production deployment, or any subsequent fix.
