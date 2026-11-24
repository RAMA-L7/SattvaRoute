# T-ENGINEERING-012 — No-op vs Broad Carve vs C1/C2 Comparison

| ODB | AP result | M4 OBS boxes | M4 geometry (master-local) | DRT-0073 |
|---|---|---|---|---|
| source `35bff121…` | 0 APs (historical) | 1 | full `(0,0)-(3672,13608)` | 2 |
| ENG011 no-op control `662993ad…` | CREATE 9 / ACCEPT 0 / DROP 9 | 1 | full body (rebuilt path) | 2 |
| broad carve `616e39f8…` | CREATE 3 / ACCEPT 3 / DROP 0 | 4 | frame; interior x1500–3650 y300–13300 removed | 0 |
| r1n_ref `46e47a65…` | CREATE 9 / ACCEPT 0 / DROP 9 | 14 | right-edge combs x3534–3672, y±24 | 2 |
| C1 `d6084ddf…` | CREATE 9 / ACCEPT 0 / DROP 9 | 10 | right-edge combs x3534–3672, y±48 | 2 |
| C2 `2c1a39d4…` | CREATE 9 / ACCEPT 0 / DROP 9 | 23 | R1-N base + right-edge y±48 tab | 2 |

## Correlates with 0→3
Only the **M4 OBS shape**: broad carve removes the interior of the right-edge obstruction, opening the `u_sram/clk` candidate corridor at absolute x=4788/4812/4836, y=16572.

## Does NOT correlate
- inst/net/bterm counts, placement, 22 pin rects, track grids, layer set, via definitions (all identical after normalization);
- number of OBS boxes (4 broad, 14/10/23 narrow — all 0 APs except broad);
- marker volume/types (present in both 0-AP and 3-AP runs);
- candidate coordinates: ENG011 enumerates the same 9 x positions; the first three are exactly the broad-accepted set.

## Generation nuance (reconciled)

Agent A and B: broad carve produced CREATE for x=4812/4788/4836; the same coordinates are generated in ENG011. Agent C: in broad carve the generation loop **stopped after 3 APs** because sparse threshold 3 was met, so the other 6 candidates were never generated there; ENG011 generated all 9 because no AP ever survived. Both statements are correct at different stages — generation order matters for interpreting "9 candidates" in A vs B logs.

## Marker-vs-access distinction

Broad carve still records Short / Metal Spacing / Lef58 markers, yet accepts APs because the macro pin needs only one clean planar direction and via-stage markers are non-binding. C2's 208 markers (Metal Spacing 121) with 0 APs confirms markers alone are not the discriminator; access-bit outcome is.
