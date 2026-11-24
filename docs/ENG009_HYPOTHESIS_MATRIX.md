# T-ENGINEERING-009 — Consolidated Root-Cause Hypothesis Matrix

Classification: **CONFIRMED** (direct evidence), **SUPPORTED** (convergent evidence, bounded),
**WEAKENED** (evidence reduces claim), **ELIMINATED** (refuted), **UNTESTED** (no decisive evidence).

| ID | Hypothesis | Classification | Evidence (VERIFIED / OBSERVED / INFERRED) | Current implication |
|---|---|---|---|---|
| H1 | `clk` is genuinely evaluated by FlexPA (not skipped as supply/special/abutment) | **CONFIRMED** | ODB CLOCK, non-special; `isSkipInstTermLocal` only skips supply/special/abutment; instrumented BEGIN targets `u_sram/clk` | Failure is in AP generation/filtering, not net classification |
| H2 | AP candidates are generated, then rejected at planar DRC → via DRC → final `hasAccess()` → sparse 0<3 | **CONFIRMED** | FDE-006T/006U logs: 9 CREATE, marker violations, 9 DROP `reason=no_access`, `n_aps=0`; code chain `FlexPA_acc_point.cpp:1514-1535,1318-1331,1215-1252` | Proximate mechanism established; exact per-marker source still unknown |
| H3 | Full-body M4 master OBS blocks planar escape (binding in FDE-006U) | **CONFIRMED (bounded)** | same-binary single-variable broad M4 OBS carve flips 0→3 APs and removes DRT-0073; M4 `Short` left box disappears | Mechanism-level root cause ESTABLISHED for that scratch DB; NOT a production remedy |
| H4 | Broad M4 OBS carve is a production-relevant remedy | **ELIMINATED** | FDE-007 Gate 1 GDS census: window exposes 120 M4/0 + 92 M4/251 real shapes; physically unjustified | Do not return to broad carve |
| H5 | Narrow per-pin M4 OBS corridors (R1-N/R1-N-W) resolve pin access | **WEAKENED / REJECTED as tested** | both reached DB but rc=2 DRT-0073, 0 APs; residual `Short`, `Metal Spacing`, `Lef58`. T-ENGINEERING-010: 2 nm sliver **CONFIRMED ARTIFACT** (own-net metal, zero foreign-net 40/0), not sole blocker | One family, two levels; no repeat without new mechanism |
| H6 | Thin-pin EOL / metal spacing is a contributing factor | **SUPPORTED contributing; y-envelope remedy REFUTED (T-ENGINEERING-011)** | pin height 24 DBU = M4 min width; maximal legal y margin (pin±48, 120 nm) produced 0 APs and identical marker counts vs R1-N reference; spacing bboxes shifted to new OBS edges, confirming OBS object as aggressor | Do not widen y again as a remedy; markers follow OBS geometry |
| H7 | M5 via landing is contributing but not decisive | **SUPPORTED contributor; ELIMINATED as binding** | VIA45 M5 `Short` persists in FDE-006U exp_b where 3 APs accepted and DRT-0073 absent; macro GDS has no M5 metal | Do not treat M5 Shorts as the primary blocker |
| H8 | Sparse threshold collision heuristic is limiting | **ELIMINATED** | `n_aps=0`; no APs exist to collide; threshold fails as a consequence. 3 geometrically viable x positions exist (INFERRED) | Lowering threshold would mask, not fix |
| H9 | Placement / bypassed Snapper / track misalignment causes DRT-0073 | **ELIMINATED** | legal LOCKED R0; 0 DBU center-to-M4-track; no MPL-0005; `check_placement` clean | Do not adjust placement as a DRT-0073 fix |
| H10 | Grid/clock layer/via config causes DRT-0073 | **ELIMINATED** | track phases match; M4 in clock range; no design-level overrides; all config hashes parity | No config-only fix |
| H11 | `zero_` / D-014 / DRT-0305 causes DRT-0073 | **ELIMINATED** | different net; DRT-0305=0; D-014 replicated in all arms | Orthogonal |
| H12 | via-in-pin config (`-via_in_pin_* M4`) is a remedy | **ELIMINATED for tested lever** | FDE-005 A/B identical; global restrictive window, not an enabler | Do not repeat |
| H13 | LEF↔GDS pin-marker mismatch | **ELIMINATED** | GDS pin box reproduces LEF RECT under +0.054 µm FOREIGN offset | Geometry abstraction consistent |
| H14 | Marker provenance (`getSrcs()`) would change attribution | **CONFIRMED (T-ENGINEERING-010)** | 107/107 markers attributed after log-only instrumentation; aggressors are macro/OBS objects (`u_sram#3:56`), victims own-net `clk`; equivalence byte-identical OFF vs OFF | Was top gap; now closed. PROV lacks aggressor rect/net, so GDS census is combined for physical attribution |
| H15 | GDS drawn-metal continuity under full pin marker | **UNTESTED** | FDE004_A label 5c NOT EVALUATED; FDE007_A censused only corridor regions | Secondary capability gap |
| H16 | Tool bug / stale binary | **WEAKENED, not fully eliminated** | three-way runtime equivalence PASS; unpatched-control byte-match inherited; determinism not re-run | Low priority, monitor via equivalence gate |
| H17 | DRT-0419 shares DRT-0073 mechanism | **ELIMINATED** | different code/phase/severity/pins/layer; no DRT-0419 for `clk`; DRT-0419 persists where DRT-0073 removed | Investigate separately; not a proxy |
| H18 | Any carve yields DRC-clean routing / timing / signoff | **UNTESTED / UNKNOWN** | no global_route, detailed route, SPEF, STA, LVS/PEX; FDE-007 full-flow variants failed | Never claim production success |

## Coordinator adjudication

H14 was the major uncertainty at ENG009 and is now **confirmed** by ENG009-DIAG-001: residual marker sources are macro/OBS objects, and the 2 nm sliver is an artifact. T-ENGINEERING-011 then tested the y-keepout account directly: the maximal legal y margin did not recover APs and moved spacing markers to the new OBS edges, so H6's y-envelope remedy is refuted. H3/H6/H7 form the bounded mechanism; H5's failure is attributable to OBS-object geometry and edge artifacts, not foreign-metal shorts. No failed experiment is repeated without a new requirement, and no remedy is authorized.
