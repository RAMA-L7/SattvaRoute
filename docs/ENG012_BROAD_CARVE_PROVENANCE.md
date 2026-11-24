# T-ENGINEERING-012 — Broad-Carve 3-AP Artifact Provenance

## 1. Artifact identity (VERIFIED)

| Artifact | SHA-256 | Status |
|---|---|---|
| Broad-carve ODB (preserved copy) | `616e39f8d9be5cae2452042906e3d187161c3938c2f040c88d3d646f57d457e0` | matches FDE-006U recorded hash |
| FDE-006U `exp_b.log` | `4e8a85dcc859a53f34b620ec91b527725362f83236fdea` | CREATE=3 ACCEPT=3 DROP=0, DRT-0073 absent |
| Provenance binary | `7461d0d001768831a47095e60c17ee6a0cf34ce2890bfd5534e23f17b7e51841` | distinct from production `c1b90e0a…` |
| Production ODB (unchanged) | `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1` | frozen source |

## 2. Bounded replay (VERIFIED, reproduced)

Using `read_db` on the preserved broad ODB, in-memory `zero_ setSpecial`, `set_debug_level DRT pin_access 1`, `pin_access`, `exit` with the provenance binary:
RC=0; CREATE=3, ACCEPT=3, DROP=0, MARKER=13, DRT-0073=0, DRT-0305=0; accepted `x=4812 / 4788 / 4836, y=16572, lay=8`; `SUMMARY aps=3 n_sparse_last=3 met=true`. This exactly matches FDE-006U `exp_b.log`. No capability or availability failure.

## 3. Master OBS geometry (read-only DB dump, VERIFIED)

Broad-carve M4 OBS = 4 rectangles forming a frame:
- `(0,0)-(3672,300)`
- `(0,13300)-(3672,13608)`
- `(0,300)-(1500,13300)`
- `(3650,300)-(3672,13300)`

Interior master-local x=1500–3650, y=300–13300 is M4-OBS-free. Non-M4 OBS identical across all ODBs. Inst/net/bterm counts (293/75/6), 22 pin rects, track grids, 30 layers and via definitions are identical across broad/control/r1n_ref/c1/c2/source (normalized).

## 4. Limitations

No byte-level ODB diff and no broad-carve generating LEF located; conclusion rests on read-only DB geometry dumps plus the reproduced 3-AP replay. All artifacts preserved in `experiments/ENG012-FORENSICS/…`.
