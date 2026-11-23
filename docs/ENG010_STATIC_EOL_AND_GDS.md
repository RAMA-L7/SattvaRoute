# T-ENGINEERING-010 — Static EOL Envelope and GDS Census

- **Source:** Agent C report `ENG010_C_static.md`, independently sanity-checked by Agent B; read-only KLayout/Python and tech-LEF inspection. No ODB/GDS write.

## 1. M4 technology rules (VERIFIED, tech LEF `:280-322`)

| Rule | Value |
|---|---|
| M4 WIDTH / SPACING / PITCH | 24 nm / 24 nm / 48 nm |
| `LEF58_SPACING ENDOFLINE` | 25 nm `WITHIN 40` `ENDTOEND 40` |
| `CORNERSPACING` | 48 nm / 40 nm |
| `LEF58_EOLKEEPOUT` | 0.025 µm, `EXTENSION 48 / 24.25 / 48 nm CORNERONLY` |
| `USEMINSPACING OBS` | OFF (`:35-41`) |

## 2. Envelope arithmetic (INFERRED geometric implication)

- R1-N/R1-N-W corridors freed `y = 8352–8424` nm local (72 nm = pin 8376–8400 ±24 nm).
- Dominant EOL/corner keepout reach is 48 nm per side; required envelope ≈ **8328–8448 nm (120 nm)**.
- Shortfall: **24 nm per side (50%)**. This explains why residual `Metal Spacing` and `Lef58` markers persisted when only x was widened.
- This is **INFERRED**, not experimentally tested; no geometry variant was run.

## 3. GDS census at residual bboxes (VERIFIED)

| Bbox (absolute DBU/nm) | Layers/datatypes | Shapes | Foreign-net 40/0? | Interpretation |
|---|---|---|---|---|
| `(4703,16560)-(4705,16584)` — 2 nm sliver | `40/0` | 1, net `clk` (own net), full 48 nm² intersection | **NO** | own-net metal at master OBS edge x=3474 |
| `(4704,16536)-(4848,16560)` spacing band | — | 0 | NO | no GDS metal |
| `(4704,16584)-(4848,16608)` spacing band | — | 0 | NO | no GDS metal |
| right-side spacing analogues (FDE-006U) | — | 0 | NO | no GDS metal |
| right FDE-006U box abs x 4904–4914 | outside macro GDS | — | cannot adjudicate in macro GDS | design-level box needed |

Master OBS local edge at x=3474 confirmed. GDS dbu 0.00025 µm; FOREIGN offset +0.054 µm; 40/251 = pin shapes/text labels, not routing metal.

## 4. Pre-registered sliver rule application

Rule: **artifact** if master OBS edge at local x=3474 **and** zero foreign-net 40/0 intersects; **real-metal** if a foreign-net 40/0 intersects; else INCONCLUSIVE.

Result: **ARTIFACT** — master OBS edge present, zero foreign-net 40/0. Caveat: the 2 nm box is physically filled by the clock's **own-net** M4 metal; the rule keys on foreign-net aggressors, not on emptiness. This is consistent with the provenance data (own-net `clk` victim, `u_sram` OBS aggressor).

The sliver is **not the sole blocker**: FDE-007 already showed 0 accepted APs with `Metal Spacing` 63→82 and `Lef58` 31→40.
