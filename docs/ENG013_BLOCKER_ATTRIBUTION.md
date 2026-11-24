# T-ENGINEERING-013 — Exact Blocking Object Attribution

## Authoritative attribution (CONFIRMED, HIGH confidence)

| Field | Value |
|---|---|
| Direction | W (`frDirEnum::W = 3`) |
| Candidate / layer | x=4788/4812/4836, y=16572, M4 (`lay=8`) |
| Failing predicate | `getMarkers().empty()` false in `isPlanarViolationFree` |
| DRC sub-check | `Short`, cid=0, rid=48, `checkMetalSpacing_short` |
| Blocking object type | fixed M4 obstruction (`fixed=1`), not a pin shape, not routing metal, not a rule-only keepout |
| Blocking object label | `u_sram#3:292@L8` (instance-level label; numeric id unstable across runs) |
| **Blocking layer** | **M4 / L8** |
| **Blocking rectangle** | **absolute `(4704,16560)-(4764,16584)`** = master-local `(3474,8376)-(3534,8400)` |
| Victim | `clknet…@L8`, rect `(4704,16560,4848,16584)`, `fixed=0` |

## Why this is shape-level, not just instance-level

- The new log emits the aggressor **rectangle** and `fixed` flag from the DRC marker's `(layer, rect, isFixed)` tuple; it is not inferred from the instance name.
- The rectangle matches the full-body M4 master OBS west strip derived from LEF/ODB geometry (pin left edge 4764 minus pitch 48 → endpoint 4716; OBS rect ends at 4764).
- Broad carve removes exactly this rectangle from the DB; W becomes clean and 3 APs are accepted. E-side strip `(4880,16560,4902,16584)` remains and still blocks E.
- Instance id instability (`u_sram#3:56` in ENG009 vs `#3:292` in ENG011) is irrelevant: the rect and fixed flag are stable and decisive.

## Exclusions

- Not a pin-shape short: the victim is the `clk` access stub; the aggressor is a fixed obstruction.
- Not a rule-derived keepout alone: `Short`/rid 48 is a metal short; EOL/spacing markers are non-binding (broad accepted x=4836 with them present).
- Not foreign-net routing metal: no foreign net in provenance; fixed obstruction inside the macro master.

## Confidence

HIGH (~0.95) for M4 OBS rect `(4704,16560)-(4764,16584)` as the westward blocker. Residual: literal tech-LEF rule text for rid 48 not mapped (UNKNOWN), but rule ID and DRC sub-check are verified in source/logs.
