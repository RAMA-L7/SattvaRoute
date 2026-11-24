# T-ENGINEERING-013 — Root-Cause Matrix Update

`docs/ENG012_HYPOTHESIS_UPDATE.md` was updated in place (append-oriented content addition, no historical deletion) to record:

| Hypothesis | Previous | Updated |
|---|---|---|
| "OBS object" exact aggressor shape | INFERRED / UNKNOWN at shape level | **CONFIRMED at shape level** — fixed M4 OBS rect `(4704,16560)-(4764,16584)`, `fixed=1`, Short/cid0/rid48 |
| Remaining shape-level uncertainty (ENG012) | open | **closed** by directional blocker instrumentation |

Authoritative statement: DRT-0073's westward AP failure is caused by a fixed M4 master-OBS rectangle intersecting the west planar escape stub; broad carving removes that rectangle and W becomes clean. The instance-level `u_sram` aggressor label is not relied upon as proof.

Unchanged: y-envelope remedy REFUTED, M5 via/EOL markers non-binding, sparse threshold downstream, all-pin AP and full-flow signoff NOT EVALUATED.
