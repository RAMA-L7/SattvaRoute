# T-ENGINEERING-015 — Coordinator Adjudication

## 1. Reconciliation

| Reviewer | Core claim | Adjudication |
|---|---|---|
| A | Documented LEF/upstream fixes exist for OBS-related DRT-0073 | **CREDITED for research, REJECTED for application** — B's source trace proves the specific mechanisms (abutment / prl spacing) do not govern our true-overlap Short |
| B | No config knob; PR #10856 present but abutment-only; only source interventions remain | **ADOPTED** — source-grounded and decisive |
| C | Narrow carves fail due to 12 nm new-edge gap; no implementable fix credible today | **ADOPTED** — quantitative mechanism explains the broad/narrow differential |

Coordinator's independent check: the OpenFinRAM generator hard-codes full-body M1–M5 OBS (`lef_extractor.cpp:285-292`, `gds2lef.py:137-142`), so generator-level OBS regeneration is not a configuration lever but a generator source change with unproven legal corridors.

## 2. Unsupported claims rejected

- "OBS SPACING 0 / USEMINSPACING OBS ON will fix DRT-0073" — **REJECTED**: source shows these only affect prl spacing and abutment, not true overlap.
- "Upstream has a backportable fix" — **REJECTED**: none exists after the local commit in the relevant code area.
- "The documented clock-pin snapper fix applies" — **REJECTED**: `clk` is exactly on M4 track #345.
- "A minimal/extended carve is a fix" — **REJECTED as candidate**: prior negative plus unproven GDS vacancy and all-pin behavior.
- "Filter OBS markers in PA source" — **REJECTED under legality gate**: could admit APs over real macro metal with no upstream precedent.

## 3. Decision

**NO-GO.** No credible research-supported candidate survives. Research findings are complete; Phase 3 and Phase 4 are not authorized. This is a statement that no *demonstrated, legalizable* remedy exists in the current evidence, not a proof that no remedy can ever exist.

## 4. Evidence integrity

No research action changed any project, source, geometry, ODB/LEF/DEF/GDS, config, or production artifact. Historical milestones unchanged. KB verify PASS (19/19), protected artifacts 9/9, validator 13/13 at gate publication. R2 remains advisory/inactive.

## 5. Stop

End at the research gate. No experiment, no source patch, no geometry, no deployment, no additional iteration without explicit user authorization.
