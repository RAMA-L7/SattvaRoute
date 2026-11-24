# T-ENGINEERING-011 — Verified Geometry and Rule Calculations

- **Source:** Agent A report `ENG011_A_geometry_rules.md`; independent review `ENG011_C_review.md`.
- **Labels:** VERIFIED = read from file; OBSERVED = prior measurement; INFERRED = reasoned; UNKNOWN = engine semantics not established.

## 1. Exact geometry (local/absolute DBU)

| Object | Local DBU | Absolute DBU | µm | Source |
|---|---|---|---|---|
| `clk` M4 pin | (3534,8376)–(3618,8400) | (4764,16560)–(4848,16584) | 84×24 nm | LEF:33 VERIFIED |
| Pin center / M4 track | (3576,8388) | (4806,16572) | track #345, 0 DBU offset | make_tracks.tcl:6 VERIFIED |
| Full-body M1–M5 OBS | (0,0)–(3672,13608) | (1230,8184)–(4902,21792) | full macro | LEF:190–198 VERIFIED |
| Empty right escape strip | x 3618–3672 | x 4848–4902 | 54 nm | GDS 40/0 = 0 OBSERVED |
| Neighbor M4 paths | y 8280–8304 / 8472–8496 | — | 96 nm pitch | GDS 40/0 OBSERVED |

## 2. Rule values (VERIFIED, tech LEF `:282–304`)

| Rule | Value |
|---|---|
| M4 SPACING / WIDTH / PITCH | 24 / 24 / 48 nm |
| LEF58_SPACING ENDOFLINE | 25 WITHIN 40 ENDTOEND 40 |
| CORNERSPACING CORNERONLY | 48 / 40 |
| EOLKEEPOUT EXTENSION | 48 / 24.25 / 48 CORNERONLY |
| USEMINSPACING OBS | OFF |

## 3. Envelope resolution

- **72 nm** = 24 + 2×24 (parallel SPACING only) — exactly R1-N/R1-N-W y window (8352–8424 local).
- **120 nm** = 24 + 2×48 using `max(24,25,40,48)` = 48 nm — defensible conservative envelope (8328–8448 local).
- The 48 nm perpendicular interpretation is **INFERRED** because CORNERONLY rules specify convex-corner distances, not perpendicular edge clearance; engine semantics UNKNOWN.
- 120 nm is also the physical limit: tracks #344/#346 are GDS-free near `clk`, and real other-net M4 starts at y 8304/8472 — only 24 nm margin, below ENDOFLINE 25.

## 4. Conclusion

C1's 120 nm y corridor was the maximal physically bounded test of the y-envelope hypothesis. It reached the database (ODB hash `d6084ddf…`) and was executed; results are in `ENG011_DIAGNOSTIC_RESULTS.md`. No larger legal y corridor exists, so the lever is exhausted.
