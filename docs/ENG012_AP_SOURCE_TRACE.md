# T-ENGINEERING-012 — AP Pipeline and Predicate Trace

- **Source:** `FlexPA_acc_point.cpp` instrumented copy `305230b9…` in FDE-006R experiment; provenance diff `ENG010_provenance.diff.txt`; source pre-image shared with `0fc94a9d…→0815de7d…`. Caveat: exact `0815de7d…` file not present on Windows host; line offsets from verified instrumented copy with noted diff.

## 1. Call chain (VERIFIED)

`pin_access` → `FlexPA::main/prep` (lines UNKNOWN in this session) → `genAllAccessPoints:1604` → `genInstAccessPoints:1581` → `genPinAccess:1465` → `genPinAccessCostBounded:1344` → coordinate generation (`:579/:519/:413/:209/:253`) → planar DRC (`filterPlanarAccess:676` → `isPlanarViolationFree:738`) → via DRC (`:906/:1041/:1100`) → final `hasAccess():1371` → sparse gate (`:1330/:1262`, threshold 3 at `drt-global.h:62-63`) → DRT-0073 at `:1593-1600`.

## 2. Rejection predicates

| Predicate | Line | Input → condition → outcome |
|---|---|---|
| coordinate generation | `:579,:519,:413,:209,:253` | derived ONLY from pin shapes, track coords, via defs, maxrects — **no OBS read** |
| `endpoint_inside` | `:684-701` | planar probe endpoint inside blocking shape → clear access bit |
| planar DRC | `:676,:738` | `markers.empty()` per direction; any marker → `clean=false` |
| via DRC | `:906,:1041,:1100` | via-stage markers → clear U/D bits |
| final `hasAccess()` | `:1371-1389` | no access bit → `DROP stage=final reason=no_access`; macro needs only ONE clean direction |
| sparse gate | `:1262-1305` | greedy half-width collision; `n_sparse≥3` → `met=true`, else DRT-0073 |

`frAccess.h:26-212` stores point, layer, 6 access bits, viaDefs, typeL/typeH — **no rejection-reason field**. Markers live in stack-local `FlexGCWorker`s and are discarded; `getSrcs()` provenance is populated by FlexGC but exact sites UNKNOWN.

## 3. Why OBS affects rejection but not generation

OBS is not read in coordinate generation. Design geometry enters only inside DRC helpers via `initPA0(getDesign())` (`:762,:1135`) and `addTargetObj(inst)` (`:758,:1126`). Therefore a geometry change can only alter which generated candidates survive, not their coordinates — confirmed by identical CREATE x-coordinates in A/B logs.

## 4. Predicate-level 0→3 explanation (VERIFIED)

- Original OBS: `CREATE x=4812`; planar W `clean=false` with M4 `Short (4704,16560)-(4764,16584)`, E `clean=false` with `(4848,16560)-(4902,16584)`; via M5 `Short` persists; all 9 DROP; sparse 0<3.
- Broad carve: same `CREATE x=4812`; planar W `clean=true` (left interior OBS removed); E still fails, M5 via Short still present; macro needs one clean direction → ACCEPT. Loop continues to 4788/4836 → 3 APs, sparse 3≥3, break; no DRT-0073.
- Narrow variants: candidates generated but still fail `markers.empty()` → rejection issue, not generation.

## 5. Remaining gaps / smallest measurement

UNKNOWN: exact DRC sub-check and OBS rectangle per marker; `0815de7d…` absolute offsets; all-pin AP status; full-flow DRC/timing. Smallest measurement: a per-direction `PLANAR-DRC clean` + aggressor rect log on the narrow-carve DB (R2 advisory only).
