# T-ENGINEERING-012 — Predicate-Level Failure Analysis

| Predicate | Source | Observed outcome | Role in 0→3 |
|---|---|---|---|
| Coordinate generation | `FlexPA_acc_point.cpp:209/253/413/519/579` | same first three x generated in both arms; OBS not read | not the cause |
| `endpoint_inside` | `:684-701` | 0 occurrences in all logs | not a factor |
| Planar `markers.empty()` per direction | `:676,:738` | west planar Short `(4704,16560)-(4764,16584)` in original/narrow; clean in broad | **decisive** |
| Via DRC markers | `:906,:1041,:1100` | M5 Short/Metal Spacing/EOL present in both 0-AP and 3-AP runs | non-binding for macro |
| Final `hasAccess()` | `:1371-1389` | 9 `DROP reason=no_access` in ENG011; macro accepts with one clean planar dir | **acceptance gate** |
| Sparse dedup | `:1262-1305`, `drt-global.h:62-63` | broad `n_sparse=3≥3` stops generation; ENG011 `0<3` consequence | downstream + generation-order effect |

**Conclusion:** the failure is at planar DRC → `hasAccess()` on the x-adjacent M4 obstruction, not at generation, via legality, marker volume, or sparse threshold alone. Exact blocking rectangle remains shape-level UNKNOWN because PROV logs instance/net identity but not rect/type.
