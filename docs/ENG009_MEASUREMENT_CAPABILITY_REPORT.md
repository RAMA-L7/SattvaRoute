# T-ENGINEERING-009 — Measurement Capability Report

- **Session:** 2026-11-23/24
- **Method:** static source/artifact inspection plus bounded read-only integrity checks; no EDA flow or experiment executed.

## 1. Capability inventory

| Capability | Status | Evidence / limitation |
|---|---|---|
| Pin-shape extraction (LEF/ODB/GDS) | **AVAILABLE** | LEF RECT and ODB pin rect verified; GDS pin box reproduces LEF under +0.054 µm FOREIGN offset; hashes `f1c18877…`, `12c56777…`, ODB `35bff121…` |
| Track math | **AVAILABLE** | `make_tracks.tcl` / tech LEF formulas; M4 y=0.012+n·0.048; `clk` center y=16.572 = track #345, 0 DBU offset |
| Via enclosure / legality | **AVAILABLE (static)** | ASAP7 tech LEF rules captured; VIA45 M4 pad 46×24 nm fits pin; macro GDS has no VIA45 cell / M5 layer; dynamic DRC marker interpretation still needs provenance |
| AP coordinates | **AVAILABLE (instrumented)** | Binary `0d890431065688930e8b140cb644e304a0a3a6beeaf32b2cff762a8aa000d33d` verified present; logs CREATE x/y/layer for 9 candidates |
| Rejection stage/reason | **PARTIALLY AVAILABLE** | instrumented logs record MARKER stage (planar/via), type, rule id, layer, bbox and DROP `reason=no_access`; **no `frAccessPoint` rejection-reason field** (reasons exist only at decision points) |
| Marker provenance (`getSrcs()`) | **API AVAILABLE, UNCOLLECTED** | directly verified at `/root/sattvaroute-fde006s/source/OpenROAD/src/drt/src/db/obj/frMarker.h:67` (`getSrcs()`), `:73` (`getAggressors()`), `:80` (`getVictims()`); resolver exists in `FlexGC.cpp`; PA marker loops log type/id/layer/bbox but not sources |
| Stock production binary diagnostic depth | **LIMITED** | `c1b90e0a…`: fatal DRT-0073, DRT-0419 warnings, one aggregate debug line `At least 3 sparse access points`; end-of-run counters never reached |
| Three-way runtime equivalence | **AVAILABLE** | FDE-006U: prod == olddiag == newdiag_off except script path; debug-on additive only |
| GDS layer/datatype map | **AVAILABLE** | 40/0, 40/251, 30/0, 35/0, etc.; per-corridor census in `FDE007_A_geometry.md` |
| GDS metal continuity under full pin marker | **NOT EVALUATED** | FDE004_A label 5c; FDE007_A censused only corridor regions |
| All-pin AP status | **NOT AVAILABLE** | tool aborts at first zero-access term; D/Q AP success untested; DRT-0419 advisory only |
| Full-flow evidence | **NOT AVAILABLE** | no `5_*.odb`, global_route, detailed route, DRC, SPEF or STA for any remedy |
| Config parity | **AVAILABLE** | config.mk `63481bef…`, SDC `7b12de64…`, PDN `dec2ffed…`, placement `fc79c4fd…`, runner `0c790cc9…`, mirror `cd86b587…`; D-014 patch present, D:\tools unpatched `3968898c…` |
| Approval ledger state | **GAP** | `state/approval_ledger.jsonl` absent; FDE-007 approvals rest on per-run `APPROVAL.md` |
| Source revision pinning | **GAP** | `bazel-nostamp` binary/source not fully pinned to a single commit in all records; tool identity hashes recorded |

## 2. Bounded read-only checks performed this session

```
sha256sum /root/sattvaroute-fde006s/.../openroad_unstamped  → 0d890431065688930e8b140cb644e304a0a3a6beeaf32b2cff762a8aa000d33d
sha256sum /usr/local/bin/openroad                            → c1b90e0af69bc9779cde8fd1579a92a10738ddebb9ea16e459f280556c349ee9
grep -n 'getSrcs|getVictims|getAggressors' .../frMarker.h    → :67, :73, :80
python3 scripts/sattva_kb.py verify                          → PASS 18 records/18-link chain
verify-immutable                                             → 9/9 OK
.skills/validate_skills.py                                   → PASS=13 FAIL=0
```

No ODB was written; no flow stage or `pin_access` run was launched.

## 3. Measurement gaps that block stronger attribution

1. No per-marker source objects (`getSrcs()`) → 2 nm sliver and spacing bands cannot be classified as OBS artifacts vs real-metal violations.
2. No full GDS continuity under pin marker → cannot exclude drawn-metal interaction beyond corridor censuses.
3. No all-pin AP survey → cannot distinguish a pin-specific defect from a general M4 pin-access limitation.
4. No full-flow evidence → no routing/DRC/timing claim is possible.

## 4. Feasibility verdict

The highest-value missing measurement (marker provenance) is **technically feasible at low cost**: the API exists, the instrumented binary is preserved, and the existing two marker loops can be extended with log-only lines under the established gate. This requires a new approval before any rebuild/replay; it is proposed, not performed.
