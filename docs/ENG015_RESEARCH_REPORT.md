# T-ENGINEERING-015 — Phase 1 Research Report

- **Date:** 2026-11-24
- **Mode:** RESEARCH ONLY. No EDA, no source/geometry/ODB/LEF/GDS/config/production change.
- **Agents:** A (literature/industry), B (OpenROAD source), C (independent assessment), coordinator adjudication.
- **Baseline:** `docs/ENG015_BASELINE_RECORD.md`.

## 1. Confirmed failure (premise, not re-derived)

`u_sram/clk` has zero accepted M4 APs → DRT-0073. Westward planar escape stub ends at abs x=4716 (local 3486), inside the fixed M4 master-OBS rectangle abs `(4704,16560)-(4764,16584)` / local `(3474,8376)-(3534,8400)`. Decisive predicate `getMarkers().empty()`; failing check `checkMetalSpacing_short`, Short cid=0, rid=48. Broad carve removes the whole interior (local x1500–3650, y300–13300) → W clean 3/3, 3 APs; physically illegal (120 `M4/0` + 92 `M4/251` real shapes).

## 2. Key physics derived this phase (Agent C, VERIFIED geometry / INFERRED predicate)

| Item | Value |
|---|---|
| W probe endpoint | local x3486 / abs 4716 |
| R1-N-W new OBS edge | local x3474 → only **12 nm** from endpoint |
| M4 parallel spacing / ENDOFLINE | 24 nm / 25 nm WITHIN 40 |
| Required west clearance | x≤3462 clears spacing; x≤3461 clears ENDOFLINE; x≤3445 outside WITHIN-40 |
| Adjacent-net M4 metal | local y8304/8472 → 96 nm pitch; 120 nm y envelope leaves only 24 nm (<25 ENDOFLINE) |
| Broad-carve clearance | nearest OBS at local x1500 → **1986 nm** from endpoint |

**Why narrow carves fail (new mechanistic explanation):** the exact blocker strip is *necessary but not sufficient*. Carving it leaves a new OBS edge 12 nm from the probe endpoint — below both 24 nm spacing and 25 nm ENDOFLINE — so markers persist. This quantitatively explains R1-N-W's 2 nm sliver and 0 APs. Broad carve wins because it removes the entire OBS field from the probe's influence neighborhood, not merely the one rectangle that produced the first `Short`.

## 3. Authoritative documentation and upstream fixes (Agent A, with citations)

| Source | Finding | Relevance |
|---|---|---|
| LEF/DEF 5.8 Language Reference — `OBS SPACING` | per-box `SPACING` overrides all layer-based spacing/EOL/PRL rules; `SPACING 0` used to control router access around pins | semantic lever on the exact fixed OBS |
| LEF/DEF 5.8 — `USEMINSPACING OBS` | `ON` (default): OBS treated as min-width wire; `OFF`: treated as actual routing shape (wide OBS → wide-wire spacing) | directly affects required spacing on a 3.672 µm full-body OBS |
| OpenROAD PR [#10856](https://github.com/The-OpenROAD-Project/OpenROAD/pull/10856) (merged 2026-07-31) | ODB/DRT honor LEF `OBS SPACING`; metal abutting a `SPACING 0` blockage no longer raises shorts | targets `checkMetalSpacing_short` against OBS; only *abutment* excused, true overlap is not |
| OpenROAD issue [#1550](https://github.com/The-OpenROAD-Project/OpenROAD/issues/1550) | `USEMINSPACING OBS OFF` caused DRT-0073 on a macro with minimal pin clearance; reverting restored access | direct experience that OBS spacing-model choice alone can cause DRT-0073 |
| OpenROAD PR [#9935](https://github.com/The-OpenROAD-Project/OpenROAD/pull/9935) (unmerged) | `write_abstract_lef` full-body OBS covering pins → DRT-0073; proposal subtracts pin shapes bloated by one layer pitch | generator-level, pin-local carve-out — previously unexplored avenue |
| LEF round-trip fixes [#11547](https://github.com/The-OpenROAD-Project/OpenROAD/pull/11547), [#11410](https://github.com/The-OpenROAD-Project/OpenROAD/pull/11410), [#11069](https://github.com/The-OpenROAD-Project/OpenROAD/pull/11069) (merged) | per-box / polygon OBS `SPACING` preserved on write/read | needed if regenerating the abstract with a current build |
| OpenROAD PR [#12162](https://github.com/The-OpenROAD-Project/OpenROAD/pull/12162) (merged 2026-11-10) | MPL snapped macros by signal pins only, leaving clock pins off-track → DRT-0073; now all non-supply pins snap | our failing pin is `clk`; ASAP7 M4 has RIGHTWAYONGRIDONLY; status depends on local build version |
| OpenROAD issue [#11766](https://github.com/The-OpenROAD-Project/OpenROAD/issues/11766) | DRT-0073 aborts at first pin; `detailed_route_debug -pa -pa_markers -pin` enumerates rejection reasons; closest analogue is macro-wide M4 OBS + Short on M4 | diagnostic prerequisite |
| Cadence Abstract Generator blog | industry practice: remove blockages around pins for router access | supports generator-level pin-aware OBS |
| TritonRoute papers (TCAD 2019, ICCAD 2018, PAO) | AP definition, pin-access oracle, PA-aware routing | supporting background only |

`websearch` returned HTTP 402; Agent A used GitHub REST API, raw docs/source, DuckDuckGo HTML, and Read the Docs directly. Every cited claim has a URL.

## 4. Coordinator-verified tech-LEF fact (new, this phase)

`benchmark/design/OpenFinRAM/tech/lef/asap7_tech.lef`:
- line 36: **`USEMINSPACING OBS OFF`** — confirmed by direct read.
- M4: WIDTH/PITCH/SPACING = 0.024/0.048/0.024 µm; `LEF58_SPACING ENDOFLINE 0.025 WITHIN 0.04`; `SPACINGTABLE PARALLELRUNLENGTH 0.0 / WIDTH 0.0 0.024 / WIDTH 0.025 0.072` (wide-vs-min metal needs 0.072 µm); `RIGHTWAYONGRIDONLY`; `RECTONLY`.

With `OFF`, the 3.672 µm full-body M4 OBS is scored as a wide routing shape (72 nm spacing), not a min-width wire (24 nm). This makes the `USEMINSPACING OBS` lever concrete and previously untested.

## 5. Agent C independent verdict (strict standard)

- Broad carve is the only geometry known to empty the marker set, and it is physically illegal → mechanism proof only.
- Exact minimal west-strip carve is **REJECTED** (12 nm new-edge gap < 24/25; already disproven by R1-N-W).
- Extended west carve (x≤3461, y held at 72 nm) is **CONDITIONAL** (W-clean plausible, complete fix uncertain; region x3445–3474 GDS-uncensused).
- Generator-level OBS regeneration is **CONDITIONAL** (only all-pin candidate explaining the broad/narrow differential; configurability and defect status UNKNOWN).
- No implementable fix is CREDIBLE today under the strict standard; immediate posture = no remedy / further diagnostic.

## 6. Agent B source findings (decisive)

- **Local build** fingerprinted to upstream `a77fc27fa463` (2026-11-04) or tree-equivalent descendant; no `.git`, unstamped. Predates the 2026-11-17 `src/`→`openroad/` rename.
- **Fail path:** target macro's own LEF OBS → `frInstBlockage` → fixed `gcRect` with `isBlockage()==true` (`FlexGC_init.cpp:58-69,136-175`); PA stub added **non-fixed** (`:220`); Short from `checkMetalSpacing_short` (`FlexGC_main.cpp:800-849`, `:827-833`); decisive `getMarkers().empty()` at `FlexPA_acc_point.cpp:873` → DRT-0073 at `:1704-1710`.
- **PR #10856 code is PRESENT** (`rects_abut` + `reqSpcVal==0` early return at `FlexGC_main.cpp:657-666`): it suppresses **abutment with zero required spacing only, NOT true overlap/short**. Our probe endpoint (x4716) lies *inside* the OBS rect (4704–4764), so this exemption cannot fire.
- **`USEMINSPACING OBS` / OBS `SPACING` are consulted only in `checkMetalSpacing_prl_getReqSpcVal`** and therefore only in the abutment branch — they cannot suppress the Short. Agent A's top LEF-semantics candidates are **refuted for this failure** at source level.
- **No supported Tcl/config knob can create an AP where zero exist**; `set_ppl_mode` absent; `-via_in_pin_*` can only remove APs; `-min_access_points` only changes the "enough" threshold.
- **No upstream backport exists** after the local commit; open issues #12199/#12200 (OBS-boxed pins) have no linked fix.
- Source-grounded intervention points exist (AP-only provenance filtering at `:873`/`:1271`, OBS-aware `genEndPoint`, PA-only `checkMetalSpacing_short_obs` early return) but all are tool-source changes with physical-legality risk and no upstream precedent.

## 7. Generator-level avenue — closed by direct read (coordinator)

`benchmark/design/OpenFinRAM/src/lef_extractor.cpp:285-292` hard-codes a full-body M1–M5 `OBS RECT 0 0 width height` for every macro ("FakeRAM abstraction convention; explicit PIN shapes remain available even where they overlap this OBS box"). `scripts/gds2lef.py:137-142` likewise emits blanket OBS with no pin-aware carve. There is **no configurable OBS generation** and **no generator-level pin-exemption logic** in this project. Regenerating a pin-aware abstract would require a generator source change plus proof of legal per-pin corridors — it is not a configuration lever.

## 8. Disposition

No candidate qualifies for Phase 3 execution. The research gate decision is published in `ENG015_RESEARCH_GATE.md`. No experiment, source change, geometry change, or production change was made.
