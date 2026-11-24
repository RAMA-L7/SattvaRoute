# T-ENGINEERING-013 — Predicate-Level Failure Trace

| Step | Source | Outcome |
|---|---|---|
| planar access pre-check | `FlexPA_acc_point.cpp:761` | `ap->hasAccess(W)` true; proceed |
| endpoint generation | `:676-682` (block pin) | W endpoint x = pin xl 4764 − pitch 48 = **4716**, y=16572 |
| DRC worker setup | `:798-810` | `FlexGCWorker`; `addTargetObj(inst)`; `initPA0(getDesign())` |
| planar probe DRC | `:777` → `isPlanarViolationFree:787-866` | `Short` marker, M4, box `(4704,16560,4764,16584)` |
| decisive predicate | `:867` | `getMarkers().empty()` false → `no_drv=false` |
| access bit | `:781` | `setAccess(W,false)` |
| final gate | `:1371-1389` | `hasAccess()` false → `DROP reason=no_access` |
| sparse gate | `:1262-1305` | 0 APs → `n_sparse=0 < 3` → DRT-0073 |

Sub-check: `checkMetalSpacing_short` (`FlexGC_main.cpp:800-850, :832`), `Short` cid=0 rid=48. EOL/spacing and via-stage markers are recorded but not decisive; macro acceptance needs one clean planar direction.
