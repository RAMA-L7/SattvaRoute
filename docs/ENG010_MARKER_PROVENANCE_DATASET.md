# T-ENGINEERING-010 — Marker Provenance Dataset

- **Primary artifact:** `experiments/ENG009-DIAG-001/ENG009-DIAG-001-20261124T000000Z-0001/logs/full_provenance.log` (SHA-256 `92b2a54e…7825`).
- **Full run log:** `logs/full_run.log` (DRT-0073 present, RC=1).

## 1. Dataset structure

Every marker emits a `FDE006R MARKER` line (type, rule id, layer, bbox, stage) immediately followed by a `FDE006R PROV` line with source/victim/aggressor object identities. Labels are stable `name#frcType:id` strings from `getId()`/`getName()`, null-safe and const-correct (Agent B verified).

Sample:
```
FDE006R PROV stage=planar x=4812 y=16572 lay=8 idx=0
  src=[clknet_1_0__leaf_clk#0:67,u_sram#3:56]
  victim=[clknet_1_0__leaf_clk#0:67@L8]
  aggressor=[u_sram#3:56@L8]
```

## 2. Census (VERIFIED)

| Stage | MARKER | PROV | Pairing |
|---|---|---|---|
| planar | 27 | 27 | 1:1 |
| via | 80 | 80 | 1:1 |
| **Total** | **107** | **107** | **0 mismatches** |

DRT-0305=0, DRT-0073=2 in full run; no new DRT codes; no unattributable markers. All 107 PROV lines were emitted; ≥90% attribution criterion met with 100%.

## 3. Attribution pattern

- Victims are consistently the `clk` net's own access shapes (`clknet_1_0__leaf_clk#0:67`) at the relevant layers.
- Aggressors are consistently the macro instance `u_sram#3:56` (M4/M5 master OBS / macro geometry), not a foreign signal net.
- No PROV line names a foreign-net aggressor. This converts the previous spatial/correlational attribution into object-level provenance.

## 4. Limitation (Agent B F1)

PROV lines provide object identity but do **not** include aggressor rectangle geometry, net field, or an explicit `OBS` tag. Therefore provenance alone cannot prove "OBS edge vs real aggressor"; the conclusion requires combination with Agent C's GDS census (no foreign-net `40/0` at any residual bbox). This is an honest limitation, not a contradiction.

## 5. Reproducibility

Patch hash `92ef2aac…`, source `0fc94a9d…→0815de7d…`, binary `0d890431…→7461d0d0…`, frozen ODB `35bff121…`, approval ENG010-AP-001, cost cap respected, no abort triggered. All commands and logs are preserved in the experiment directory.
