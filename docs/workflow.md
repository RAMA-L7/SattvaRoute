# Workflow and stage status

## Intended pipeline

```
input validation → synthesis → floorplan → macro placement → PDN → placement
→ clock-tree synthesis → global routing → detailed routing → parasitic extraction
→ final timing evaluation
```

## Actual runner stages

`check-yosys`, `check-openroad`, `synth`, `floorplan`, `place`, `cts`, `route`, `finish`. The runner stops at the first non-zero stage; later stages are not attempted.

## Verified stage outcomes

| Stage | Result | Notes |
|---|---|---|
| check-yosys / check-openroad | PASS | tool availability |
| synth | PASS | pre-synthesized netlist with provenance |
| floorplan | PASS (rc=0) | macro placement and PDN included |
| place | PASS (rc=0) | — |
| cts | PASS (rc=0) | 4_cts.odb is the router input |
| route (5_1_grt) | BLOCKED | DRT-0305 in the original baseline; DRT-0073 after D-014 |
| detail route | NOT EVALUATED | never reached |
| extraction | NOT EVALUATED | requires routed database |
| final timing | NOT EVALUATED | no routed/parasitic database |

## Key evidence chain

1. `4_cts.odb` is read by `5_1_grt` (`5_1_grt.log`: `read_db .../4_cts.odb`).
2. `pin_access` is the first DRT call in the global-route stage and fails before `global_route` runs.
3. Original baseline: `zero_` GROUND, non-special → DRT-0305.
4. D-014 run: `zero_` SPECIAL → DRT-0305 gone; `u_sram/clk` has no pin-access point → DRT-0073.

## D-007 rule

Exit code 0 is never sufficient evidence of success. Every claim is verified against reports, artifacts, and metrics. Since no run has produced a routed database, no routing/extraction/timing success is claimed.
