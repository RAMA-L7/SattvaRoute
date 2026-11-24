# T-ENGINEERING-013 — Directional Planar DRC Report

- **Instrument:** log-only rectangle fields added to `fde006rPairsLabel` in the preserved instrumented source; new binary `db876fbf…` from `7461d0d0…`; source `0815de7d… → 797b282c…`; patch diff `8495405b…`.
- **ODBs:** control `662993ad…` (0 APs) and broad `616e39f8…` (3 APs), replayed with the same Tcl and tool path.

## 1. Directional results

| Direction / DB | clean flag | Marker | Aggressor object / layer / rect | fixed |
|---|---|---|---|---|
| W (`dir=3`), control, x=4812 y=16572 | **false** (9/9 checks) | `Short`, cid=0, rid=48, M4, box `(4704,16560,4764,16584)` | `u_sram#3:292@L8`, **M4**, `rect=(4704,16560,4764,16584)` | **1** |
| W, broad carve | **true** (3/3) | none in west band | west rect carved out | — |
| E (`dir=4`), broad | false | E-side marker `(4880,16560,4902,16584)` remains | right OBS strip | 1 |

Macro pin acceptance needs only one clean planar direction; W-clean in broad is sufficient. Via-stage M5 Shorts and EOL/spacing markers are present but non-binding.

## 2. Predicate chain

`filterPlanarAccess` (`FlexPA_acc_point.cpp:761-783`) → `isPlanarViolationFree` (`:787-866`) → `getMarkers().empty()` (`:867`). The failing sub-check is `Short` from `checkMetalSpacing_short` (`FlexGC_main.cpp:800-850, :832`), between the westward escape stub (endpoint x=4716 = pin xl 4764 − pitch 48) and the fixed M4 obstruction west of the pin. `no_drv=false` → `setAccess(W,false)` → final `hasAccess()` drop.

## 3. Neutrality

Debug-off new binary vs ENG011 control log: only the pre-existing aggregate sparse line differs (no patch-attributable change). Debug-on old vs new: 107/107 changed lines are PROV lines gaining `rect=`/`fixed=`; 0 non-PROV changes; all DRT/FDE006R counts identical. Instrumentation is behavior-neutral.

## 4. Reproduction

Control: RC=1, DRT-0073=2, 9 CREATE / 0 ACCEPT / 9 DROP. Broad: RC=0, DRT-0073=0, 3 CREATE / 3 ACCEPT / 0 DROP, sparse 3≥3. No protected artifact changed; control `662993ad…`, broad `616e39f8…` unchanged before/after.
