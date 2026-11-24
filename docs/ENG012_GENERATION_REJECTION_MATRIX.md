# T-ENGINEERING-012 — AP Candidate Generation / Rejection Matrix

All candidates are M4 (layer 8) at y=16572. Expected candidates from source arithmetic (Agent C): M5 full track x=4812, half tracks 4788/4836, center 4806, via-enclosure 4787/4825, near-grid 4740/4764/4860.

| x | Broad-carve (3-AP DB) | ENG011 control / C1 / C2 | Binding predicate |
|---|---|---|---|
| 4812 | generated, planar W clean → **ACCEPT** | generated, planar W/E Short + via Short → **DROP no_access** | `hasAccess()` at `:1371-1389`; west M4 OBS overlap |
| 4788 | generated, ACCEPT | generated, DROP no_access | same |
| 4836 | generated, ACCEPT **despite 3 via/stage markers** | generated, DROP no_access | marker types non-binding for macro when one planar dir is clean |
| 4806, 4787, 4825, 4740, 4764, 4860 | **never generated** (sparse threshold met after 3 APs; loop broke) | generated, all DROP no_access | generation-order effect, not rejection in broad |

## Categories

- **Never generated (broad):** remaining 6 candidates after the sparse threshold was met.
- **Generated then rejected:** all 9 in ENG011 arms; first 3 in original OBS A/B.
- **Accepted but omitted from counts:** none — ACCEPT lines match `SUMMARY aps`.

## Predicate-level failure analysis

1. `endpoint-inside`: 0 occurrences; not a factor.
2. `outside_maxrect` / `duplicate` / `outside_boundary` / `not_enclosed`: 0 occurrences.
3. `filterPlanarAccess` `markers.empty()` per direction: decisive — west planar probe to x=4716 overlaps the x-adjacent M4 OBS in narrow/original cases; broad carve removes that interior.
4. Via-stage M5 `Short`, `Metal Spacing`, `Lef58EolKeepOut`: present in both 0-AP and 3-AP runs; non-binding for macro pins under `hasAccess()` (4836 accepted with all three).
5. Sparse dedup: `n_sparse=3 ≥ thresh=3` in broad; `0<3` in ENG011 is a consequence of zero APs, not a cause.

## Strongest alternative to the OBS narrative (Agent C, INFERRED)

The `u_sram#3:56` "aggressor" label is likely an instance-level provenance artifact from `addTargetObj(inst_term->getInst())`; the true aggressor shape (OBS rect vs other macro-owned M4 metal) is still unresolved at shape level. The narrowed mechanism is the **westward planar probe overlapping the x-adjacent M4 OBS slab in the clk y band**, not a generic y-keepout rule.
