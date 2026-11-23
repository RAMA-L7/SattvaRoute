# T-ENGINEERING-010 — Sliver Verdict and Updated DRT-0073 Root-Cause Assessment

## 1. Pre-registered rule

- **ARTIFACT** if master OBS edge at local x=3474 and zero foreign-net 40/0 intersects the bbox.
- **REAL-METAL** if a foreign-net 40/0 intersects.
- **INCONCLUSIVE** otherwise.

## 2. Evidence

- Marker provenance: 107/107 markers attributed; aggressors are `u_sram#3:56` macro/OBS objects, victims are the `clk` net's own shapes; no foreign-net aggressor (ENG010_MARKER_PROVENANCE_DATASET.md).
- GDS census: the 2 nm sliver `(4703,16560)-(4705,16584)` contains exactly one own-net `clk` `40/0` shape and **zero foreign-net 40/0**; master OBS edge at local x=3474 (ENG010_STATIC_EOL_AND_GDS.md).
- Equivalence: instrumentation behavior-neutral; no result depends on the new logging (ENG010_INSTRUMENTATION_AND_EQUIVALENCE.md).

## 3. Sliver verdict

**CONFIRMED — ARTIFACT** under the pre-registered rule. The 2 nm box is an OBS-edge fragmentation artifact containing the clock's own M4 metal, not a foreign-net short. It is **not** the sole blocker of DRT-0073; FDE-007 already showed 0 accepted APs with spacing/EOL markers dominating.

## 4. Updated root-cause assessment

| Claim | Status | Change from ENG009 |
|---|---|---|
| Full-body M4 master OBS blocks planar escape | **CONFIRMED (bounded)** | unchanged |
| Residual markers arise from macro/OBS objects, not foreign-net metal | **CONFIRMED** | new — was UNTESTED |
| 2 nm sliver is OBS-edge artifact | **CONFIRMED** | was INCONCLUSIVE |
| Thin-pin EOL / metal spacing contributes | **SUPPORTED** | unchanged; y-envelope arithmetic quantified (INFERRED) |
| M5 via-landing shorts contribute but are not decisive | **SUPPORTED** | unchanged |
| Narrow x-only corridors are a production remedy | **ELIMINATED** | remains rejected |
| Any carve yields DRC-clean routing / timing | **UNTESTED** | unchanged |

**Updated bounded root cause:** DRT-0073 arises when zero legal access points survive FlexPA filtering on a thin M4 clock pin whose escape is constrained by full-body M4 OBS; residual failures under narrow corridors are attributable to the same OBS/macro geometry interacting with M4 EOL/corner-keepout and spacing rules, not to foreign-net metal. The 2 nm sliver is an artifact of that geometry and is not independently decisive.

## 5. Scope limits

- No geometry variant was run; the y-envelope conclusion remains INFERRED.
- All-pin AP status and full-flow DRC/extraction/timing remain NOT EVALUATED.
- This result does **not** authorize any OBS modification or production remedy.
- DRT-0419 remains a separate advisory mechanism; not investigated here.
