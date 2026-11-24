# T-ENGINEERING-011 — Control vs Candidate Diagnostic Results

- **Instrument:** provenance binary `7461d0d0…`, `read_db` + D-014 `zero_ setSpecial` + `pin_access`; no flow stage beyond `pin_access`.
- **Artifacts:** `experiments/ENG011-GEOMETRY/ENG011-GEOM-20261124T000000Z-0001/logs/pa_*.log`, `evidence/census.txt`, `evidence/final_hashes.txt`.

## 1. Primary results (VERIFIED from logs)

| Arm | CREATE | ACCEPT | DROP | MARKER/PROV | DRT-0073 | DRT-0305 | Sparse | AP coordinates |
|---|---|---|---|---|---|---|---|---|
| control | 9 | **0** | 9 | 107/107 | 2 | 0 | 0<3 | unchanged 9 x-positions |
| r1n_ref | 9 | **0** | 9 | 148/148 | 2 | 0 | 0<3 | identical |
| C1 (y±48) | 9 | **0** | 9 | 148/148 | 2 | 0 | 0<3 | identical |
| C2 (corner tab) | 9 | **0** | 9 | 208/208 | 2 | 0 | 0<3 | identical |

**No arm recovered any access point. DRT-0073 persists in all arms.**

## 2. Marker families

| Arm | Short | Metal Spacing | Lef58EolKeepOut | Lef58SpacingEndOfLine |
|---|---|---|---|---|
| control | 72 | 5 | 30 | 0 |
| r1n_ref | 54 | 63 | 30 | 1 |
| C1 | 54 | 63 | 30 | 1 |
| C2 | 54 | 121 | 30 | 3 |

- x-widening (control→r1n_ref) changed the family: Short 72→54, Metal Spacing 5→63.
- y-widening (r1n_ref→C1) changed **nothing** in type counts.
- C2's x=3618 seam added 58 Metal Spacing markers — actively harmful.

## 3. Marker-boundary shift (decisive observation)

C1's `Metal Spacing` bboxes moved from y 16536/16584 to **16512/16632** — exactly the widened OBS edges — with unchanged counts. Marker provenance again names only `clknet` (victim) and `u_sram` (aggressor), no foreign net. The markers follow the **OBS geometry**, not physical metal.

## 4. Collateral / provenance

- All arms had identical AP candidate coordinates and 0 accepted APs; no new legal access was created.
- DRT-0305=0 in all arms (D-014 parity held).
- ODB hashes differ per arm (`662993ad…`, `46e47a65…`, `d6084ddf…`, `2c1a39d4…`), confirming intended geometry reached each DB.
- No production file, baseline, LEF/GDS or config changed.

## 5. Interpretation

The y-envelope/EOL-keepout hypothesis is **refuted as a remedy**: the maximal legal y margin neither reduced marker counts nor created APs. The boundary shift confirms the OBS object itself is the aggressor; widening it merely relocates the spacing violation. This is a stronger result than ENG010's INFERRED envelope claim.

Remaining gaps: only `clk` was measured (tool aborts at first failing term); no full-flow DRC/timing; aggressor rect/net tag still absent from PROV lines. These do not change the no-remedy verdict for this narrowly scoped study.
