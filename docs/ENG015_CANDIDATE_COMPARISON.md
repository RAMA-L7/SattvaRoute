# T-ENGINEERING-015 — Candidate Remedy Comparison

Strict standard: a candidate is CREDIBLE only if (a) it explains why broad carve succeeds where every narrow carve failed, (b) it has a concrete documented/source mechanism, (c) it is not already disproven, and (d) physical legality is at least plausibly demonstrable.

| Candidate | Mechanism | Evidence | Prior experiments | Physical legality | Verdict |
|---|---|---|---|---|---|
| Broad interior carve | removes all OBS from probe neighborhood (1986 nm clearance) | VERIFIED replay: W clean 3/3, 3 APs | executed, but rejected for production | **ILLEGAL** — frees 120 `M4/0` + 92 `M4/251` real shapes | **REJECTED as remedy** (mechanism proof only) |
| Exact minimal west-strip carve | removes blocker rect but leaves new OBS edge 12 nm from endpoint | INFERRED from geometry + R1-N-W marker data | R1-N-W already carved this x-extent → 0 APs | strip is own-net metal; new edge violates 24/25 nm | **REJECTED** |
| R1-N / R1-N-W / C1 / C2 hand carves | x-only / y±48 / corner tab variants | ENG011: all 0 APs, C2 harmful | executed and failed | various | **REJECTED** |
| `USEMINSPACING OBS ON` (tech LEF currently `OFF`) | wide OBS would score as min-width (24 nm) instead of wide (72 nm) | LEF 5.8 + issue #1550; source `FlexGC_main.cpp:305-311` | never tested, but **source refutes applicability**: only prl/abutment path, not the true-overlap Short | geometry untouched | **REJECTED for this failure** (wrong predicate) |
| OBS `SPACING 0` (PR #10856) | zero required spacing suppresses abutment shorts | merged PR present in build (`FlexGC_main.cpp:657-666`) | never tested, but **source refutes**: only fires when `rects_abut`; our stub overlaps the OBS | geometry untouched | **REJECTED for this failure** (wrong predicate) |
| `detailed_route_debug -pa -pa_markers -pin` | diagnostic classification of rejection reasons | official docs + issue #11766 | not previously run with these flags | n/a | **USEFUL DIAGNOSTIC, not a remedy** |
| Clock-pin snapper fix (PR #12162) | MPL used signal pins only, leaving clock off-track → DRT-0073 | merged 2026-11-10 | local `clk` centre is exactly on M4 track #345 (0 offset) → refuted by measurement | n/a | **REJECTED as inapplicable** |
| Pin-geometry adjustment | widen/move pin so probe avoids OBS | ENG014 matrix | assessed nonviable; LEF≠GDS, no LVS/PEX | uncertain | **REJECTED** |
| Placement / grid adjustment | move macro to align pin | #6991/#6267; local pin on-track | FDE-004-D refuted; relative pin↔OBS invariant | n/a | **REJECTED** |
| Config flags (`-via_in_pin_*`, `-min_access_points`, `-via_access_layer`) | relax PA acceptance | TritonRoute.tcl source | via-in-pin tested no-op; threshold cannot create AP 1; source confirms none can create an AP where zero exist | n/a | **REJECTED** |
| Extended west carve (x≤3461, y window 72 nm) | moves new OBS edge ≥25 nm from probe endpoint | Agent C arithmetic (24/25 nm rules) | not executed; GDS region x3445–3474 uncensused | **UNKNOWN** — no foreign-net census; new-edge artifact precedent | **CONDITIONAL — not credible today** |
| Generator-level pin-aware OBS regeneration | emit per-pin corridors with >40 nm clearance for all terms | PR #9935 (unmerged) + Cadence practice; local generator hard-codes full-body OBS | not attempted; generator has no configurability | **UNKNOWN** — legal corridor not proven; generator source change required | **CONDITIONAL — not credible today** |
| PA-scoped OBS-marker filtering (tool source) | ignore target-inst OBS-only Short markers at `getMarkers().empty()` | Agent B source `:873`/`:1271` | not attempted; no upstream precedent | **UNCERTAIN** — could admit stubs over real macro metal / mask real shorts | **REJECTED under strict legality gate** |

## Conclusion

No candidate is simultaneously (i) applicable to the true-overlap Short, (ii) not disproven, and (iii) physically legal or demonstrably legalizable today. The two conditional geometry/generator ideas remain hypotheses behind a GDS vacancy proof, a rule-envelope proof, an all-pin survey, and fresh authorization — they are not validated remedy candidates.
