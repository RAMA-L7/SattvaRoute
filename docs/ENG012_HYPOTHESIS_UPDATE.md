# T-ENGINEERING-012 — Root-Cause Hypothesis Update

| Hypothesis | Prior status | New status | Evidence |
|---|---|---|---|
| Full-body M4 OBS causes DRT-0073 by blocking planar escape | CONFIRMED (bounded) | **CONFIRMED at predicate level** | broad carve makes west planar DRC clean; all 9 candidates then survive sparse; reproduction with ODB `616e39f8…` |
| Y-envelope / EOL-keepout margin is a remedy | REFUTED (ENG011) | **REFUTED and explained** | candidate y fixed at pin center by `genAPCentered`; C1 widening changed no marker counts and relocated bands to new OBS edges |
| M5 via-landing Short is decisive | ELIMINATED as binding | **ELIMINATED** | broad accepted x=4836 with 3 via/stage markers; macro needs one clean planar direction |
| Metal Spacing / Lef58 EOL are decisive | contributing | **CONTRIBUTING, non-binding** | present in 3-AP run; C2 with 208 markers still 0 APs |
| Sparse threshold is causal | ELIMINATED | **CONFIRMED downstream, plus generation-order effect** | `n_aps=0` in ENG011; broad stops generation after 3 because threshold met |
| "OBS object" is the exact aggressor shape | INFERRED | **CONFIRMED at shape level (T-ENGINEERING-013)** | instrumented aggressor tuple gives layer M4, rect `(4704,16560)-(4764,16584)`, fixed=1; matches master OBS west strip |
| Remaining 6 candidates were rejected in broad carve | UNKNOWN | **ELIMINATED — never generated** | sparse threshold met after first 3; loop broke |

## Updated authoritative statement

DRT-0073 occurs because every generated AP on the thin M4 `clk` pin fails the final `hasAccess()` gate: the westward planar probe overlaps an x-adjacent M4 obstruction in the pin's y band. Broad interior M4 OBS carving removes that overlap for the first generated candidates, which meet the sparse threshold and terminate generation successfully. Narrow/corner/y variants retain the x-side obstruction and therefore fail. T-ENGINEERING-013 subsequently resolved the shape-level gap: the westward blocker is the fixed M4 master-OBS rectangle `(4704,16560)-(4764,16584)`, failing `checkMetalSpacing_short` (Short/cid0/rid48).

## Scope limits

No production remedy, full-flow DRC/timing, all-pin AP survey, or signoff claim. DRT-0419 remains separate.
