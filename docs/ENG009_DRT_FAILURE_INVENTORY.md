# T-ENGINEERING-009 — DRT Failure Inventory

| Code | Severity / phase | Exact condition and evidence | Mechanism verdict | Relevance to DRT-0073 |
|---|---|---|---|---|
| **DRT-0305** | FATAL at DRT DB import / `pin_access` | `Net zero_ of signal type GROUND is not routable by TritonRoute. Move to special nets.` — `io.cpp:1040` guard; historical baseline before D-014 | CONFIG-INDUCED; RESOLVED by D-014 `$net setSpecial` (D-014, mirror `cd86b587…`) | **Orthogonal**. Absent in all post-D-014 runs (DRT-0305=0 in baseline and both FDE-007 runs). Do not conflate. |
| **DRT-0073** | FATAL in `FlexPA::genInstAccessPoints`, `pin_access` | `[ERROR DRT-0073] No access point for u_sram/clk (sram_x4x4x1).` — baseline `5_1_grt.log:108`, stack `:109-124`; `FlexPA_acc_point.cpp:1526-1533` on `!n_aps` | GEOMETRY/OBS-INDUCED, mechanism bounded (D-021/FDE-006U); narrow remedies R1-N/R1-N-W REJECTED (D-022/D-023) | **Primary unresolved blocker.** Candidate APs rejected at planar/via DRC → final `hasAccess()` → sparse 0<3. |
| **DRT-0419** | NON-FATAL WARNING at design read (`io::Parser::checkPins`) | 8× `No routing tracks pass through the center of Term u_sram/D[0..3] / Q[0..3]` — `5_1_grt.log:36-43`; `io_parser_helper.cpp:926-929` | M3 D/Q pin-center advisory; 3–4 DBU off grid; **invariant count 8** across experiments | **Not shared with DRT-0073**: never emitted for `clk` (M4, 0 DBU); persists in FDE-006U exp_b where DRT-0073 was removed. D/Q AP status remains UNTESTED. |
| **MPL-0005** | Would be FATAL in Snapper if pin centers off track | Avoided by `-exact` placement (D-012); no MPL-0005 in logs; all 12 M4 centers exactly on-track | PREDICTED only, never observed | **Eliminated** as DRT-0073 cause. |
| **DRT-018** | Advisory, warm-up related | Present historically as normal warning | Non-causal parity item | No role in DRT-0073. |
| **DRT-0166 / others** | Not observed in primary path | Aggregate census 0 in route logs | N/A | No role. |

## Cross-cutting parity (VERIFIED)

- Baseline and both FDE-007 runs: DRT-0305=0, DRT-0073=2 (error + echo), DRT-0419=8, DRT-0166=0.
- D-014 parity identical across all arms; production binary `c1b90e0a…`, source ODB `35bff121…`.
- No FDE-007 run produced `5_*.odb`; global route, detailed route, DRC, extraction and timing remain NOT EVALUATED.

**Conclusion:** only DRT-0073 is the unresolved fatal mechanism. DRT-0419 is a separate advisory and must be investigated independently (its own AP status untested), not as a proxy for the clock failure.
