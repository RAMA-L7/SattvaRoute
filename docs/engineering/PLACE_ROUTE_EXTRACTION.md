# Placement, routing, extraction, and timing evidence

Status: engineering background tied to implemented verification signals. SattvaRoute reads these outputs; it does not implement the engines.

## Placement / congestion

Evidence: floorplan and placement stage logs, `2_floorplan.odb` input to place, `3_place.odb` input to CTS. Stage inputs are declared in `state/approval_policy.json` and drive invalidation. Diagnosis may attribute a failure to the earliest stage whose input is missing or stale. General congestion analysis beyond log/report signals is **not** an implemented feature.

## CTS

Evidence: `3_place.odb` input, clock reports, and the intermediate `updated_clks.sdc`. The intermediate constraint is not the executed final constraint; see `docs/engineering/SDC_TIMING.md`. Clock-tree quality metrics are reported but not used to claim timing closure.

## Routing

Evidence: `4_cts.odb` input, `route.guide`, `5_route.odb`, `5_route_drc.rpt`. The verifier reads the **last** `[INFO DRT-0199] Number of violations = N` from the routing log; intermediate counts (e.g. 25 → 2 → 0) are not final, and absent report lines are not treated as clean. Router/OpenROAD-internal DRC=0 is a tool-level signal, **not** foundry DRC. See `docs/engineering/VERIFICATION_BOUNDARIES.md`.

## Extraction

Evidence: `6_final.spef`, `[INFO RCX-0045] Extract N nets`, `Found N unannotated drivers`. Extraction completeness is checked as evidence; incomplete extraction blocks timing claims.

## Timing (STA)

Evidence: `6_finish.rpt`, `period_min`/`fmax`, worst slack, setup/hold violation counts, TNS/WNS. Numbers are interpreted only after `report_units`/Liberty units are established. Zero violations in a single typical corner are not characterized multi-corner signoff.

## What is implemented vs background

| Topic | SattvaRoute behavior |
|---|---|
| Stage execution | Implemented via runner |
| Log-based failure classification | Implemented (bounded families) |
| Endpoint artifact checks | Implemented |
| DRT-0199 last-count reading | Implemented |
| Extraction/STA report signal checks | Implemented |
| Independent physical analysis (e.g. computing DRC from geometry) | **Not implemented** |
| Congestion optimization / clock-tree tuning | **Not implemented** |

## Related

`docs/engineering/VERIFICATION_BOUNDARIES.md`, `docs/architecture/VERIFICATION.md`, `docs/research/LIMITATIONS.md`.
