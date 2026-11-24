# T-ENGINEERING-014 — Risk and Validation Requirements

These are *requirements for any future, separately authorized work*. None were performed in this milestone.

## 1. Risk register (for any future remedy experiment)

| Risk | Evidence basis | Severity | Required control |
|---|---|---|---|
| Carve exposes real/foreign SRAM metal → router shorts | broad carve freed 120 `M4/0` + 92 `M4/251`; west strip contains own-net `clk` metal | HIGH | full-region design-level GDS census proving zero foreign-net 40/0 over the *entire* carve bbox |
| New OBS-edge seam creates artifact `Short`/`Metal Spacing` | R1-N-W 2 nm sliver `(4703,16560)-(4705,16584)`, classified artifact | MEDIUM | marker census by type/layer/bbox/source; no-op area-preserving control |
| Spacing / EOL envelope cannot fit at 96 nm pin pitch | adjacent-net metal 24 nm away < 25 nm ENDOFLINE; ~120 nm required envelope | HIGH (possible dead end) | quantitative rule-envelope proof (rules 7/52/58/59) that a legal geometry exists before any sweep |
| `clk` fixed but DRT-0073 relocates to `ce_n` | `clk`-local carve fixed `clk`, then failed `ce_n` | HIGH | all-pin AP survey for all 12 M4 terms + M3 D/Q |
| Accepted APs sit on occupied metal → route/DRC failure | `pin_access` only was run; no route/DRC report exists | HIGH | full global/detail route, DRC census by type/layer/bbox/source, KLayout macro-region DRC |
| LVS/PEX unavailable | Calibre absent (D-004); Liberty estimated (`--skip-characterization`) | MEDIUM-HIGH | disclose limitation; extraction/SPEF + STA if tooling permits |
| Unauthorized geometry change | D-022/D-023 consumed; approvals non-transferable | CRITICAL | new decision ID + explicit human approval + new gate before any implementation |
| Non-single-variable DB delta | prior OBS edits had per-box dump Tcl bug | MEDIUM | canonical DB diff with OBS as sole delta; in-experiment OBS dump; inst/net/bterm parity; byte-identical DEF round-trip |
| Suppression mistaken for fix | `-min_access_points` / config flags cannot create AP 1 | CRITICAL | forbid threshold/debug/DRC suppression and waivers |

## 2. Validation gate sequence (all mandatory before promoting any remedy)

1. **Provenance:** log marker `getSrcs()` / object type / net for W `Short`, spacing bands and VIA45 M5 shorts — attribute each to OBS blockage, own-net pin metal, or foreign net.
2. **Physical vacancy:** full-region read-only GDS census over the entire proposed carve, not a 2 nm sliver; zero foreign-net 40/0.
3. **Rule envelope:** arithmetic proof that a geometry satisfying rules 7/52/58/59 exists; not an empirical sweep.
4. **Single-variable A/B:** control vs carve on hash-identical DBs; area-preserving no-op split control; canonical DB diff; OBS as sole delta.
5. **All-pin AP census:** all 12 M4 terms + M3 D/Q; no DRT-0073 relocation.
6. **Full-flow signoff:** global route + congestion; detailed route with DRC census by type/layer/bbox/source (zero new violations in freed region); KLayout macro-region DRC; SPEF/extraction; STA setup/hold WNS/TNS with clock path through `clk`; IR-drop.
7. **Authority:** fresh decision ID + explicit approval; scratch-only; no `write_db` to inputs; no production write.

## 3. Stop conditions

Any protected-hash change; production GDS/LEF/tech/config edit without new approval; `write_db` to an input; DRT-0305 reappearing; multi-variable or unverifiable edit; no-op control showing a delta; AP success presented as route/DRC/timing success; any threshold/debug/DRC suppression or waiver; further geometry variant under consumed approvals.

## 4. Applicability

No item in this document authorizes or triggers work. All items are preconditions that must be satisfied under a future, explicit authorization. This milestone performed none of them.
