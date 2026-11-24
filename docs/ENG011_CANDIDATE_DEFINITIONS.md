# T-ENGINEERING-011 — Candidate Definitions and Rationale

- **Approval:** ENG011-AP-001; bounded scratch `pin_access` diagnostics only.
- **Injection:** scratch macro-LEF edit → exported DEF → DB rebuild (`read_lef` tech+SC+scratch macro, `read_def`, `write_db`) → `read_db` + D-014 + `pin_access`. In-memory master-OBS mutation is unsafe (NULL-SWire crash).

## Arms

| Arm | M4 OBS geometry (local) | Mechanism tested | Status |
|---|---|---|---|
| **control** | unchanged production LEF, same rebuild path | isolates injection path | executed |
| **r1n_ref** | R1-N equivalent: x 3534–3672, y pin±24 (14 RECTs) | path-matched reference to prior failed family | executed |
| **C1 full-EOL** | x 3534–3672, y pin±48 (120 nm, 10 RECTs) | first test of y-envelope / EOL-corner-keepout margin | executed |
| **C2 corner-tab** | R1-N base plus right-edge x 3618–3672 y±48 (23 RECTs) | corner-only relief at the empty 54 nm strip | executed |
| **C3 strict-clean** | x 3564–3672, y pin±24 | R1-N Variant B; re-blocks VIA34/VIA45 pads | **REJECTED before execution** (Agent C) |

## Legality (Agent A/C VERIFIED)

All executed deltas: area-conserving, non-overlapping, within macro bounds, M4-OBS-only, zero foreign-net 40/0 exposure. Candidate LEF hashes are in `experiments/ENG011-GEOMETRY/.../evidence/final_hashes.txt`; exact RECT blocks are in the scratch `candidates/` directory and `evidence/` logs.

## Control fix from independent review

Agent C found that using the raw source ODB as control would confound the rebuild path. The control was changed to a **no-op rebuilt ODB** using the same DEF and LEF pipeline; `r1n_ref` is path-matched to isolate the y change. All four arms used one exported DEF (SHA-256 `fe1a5e07…`) and the same instrumented binary `7461d0d001768831a47095e60c17ee6a0cf34ce2890bfd5534e23f17b7e51841`.

## Measurements

AP CREATE/ACCEPT/DROP coordinates, rejection reasons, marker type/rule-id/layer/bbox, marker provenance (`getSrcs()`), DRT-0073/0305 counts, and ODB/LEF/log hashes per arm.
