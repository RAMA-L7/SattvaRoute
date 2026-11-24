# T-ENGINEERING-011 — Targeted DRT-0073 Geometry Remedy Study: Final Report

- **Date:** 2026-11-24
- **Status:** COMPLETE. Stop after this milestone; no production remedy applied.
- **Verdict:** **NO-REMEDY OUTCOME SUPPORTED.** The maximal legal y-envelope remedy hypothesis is refuted; no candidate restored pin access.

## 1. What was done

Verified geometry/rule calculations; reconstructed the 72 nm vs 120 nm envelope; designed three path-matched arms plus a no-op rebuilt control; rejected an invalid candidate before execution; executed bounded `read_db` + `pin_access` diagnostics only; independently reviewed before and after execution.

## 2. Key evidence

- Control: 9 candidates, 0 accepted, 107 markers, DRT-0073=2.
- Path-matched R1-N reference: 0 accepted, 148 markers.
- C1 (y±48 = maximal legal 120 nm corridor): **0 accepted**, 148 markers with identical type census, DRT-0073=2; spacing-marker bboxes shifted to the new OBS edges (16512/16632).
- C2 (corner tab): 0 accepted, 208 markers (Metal Spacing 121) — harmful.
- All AP coordinates identical; no collateral access improvement; D-014 parity held (DRT-0305=0).

## 3. Interpretation

The y-envelope/EOL-corner-keepout hypothesis is refuted as a remedy. The maximal legal y margin changed neither marker counts nor APs; the markers follow the OBS geometry. This converts ENG010's INFERRED envelope claim into a tested negative result. The confirmed OBS-edge sliver is an artifact, not a foreign-metal short; widening the OBS simply relocates the spacing violation.

## 4. Independent review

Agent C pre-execution: ACCEPT WITH LIMITATIONS after control-path fix and C3 rejection. Agent C post-execution: y-hypothesis REFUTED; OBS object confirmed as aggressor; no-remedy recommended. Coordinator adjudication in `ENG011_INDEPENDENT_REVIEW_AND_ADJUDICATION.md`.

## 5. Files and integrity

Created `ENG011_GEOMETRY_RULE_CALCULATIONS.md`, `ENG011_CANDIDATE_DEFINITIONS.md`, `ENG011_DIAGNOSTIC_RESULTS.md`, `ENG011_INDEPENDENT_REVIEW_AND_ADJUDICATION.md`, this report; updated `ENG009_HYPOTHESIS_MATRIX.md`, state, coordination and logs. Experiment artifacts (LEFs, ODBs, logs, hashes, diffs) remain in isolated scratch.

Integrity: KB verify PASS (19 records/19-link chain), protected artifacts 9/9 PASS, validator 13/13 PASS, R2 unchanged and inactive.

## 6. Limitations

Only `clk` measured; no full-flow route/DRC/extraction/timing; PROV still lacks aggressor rect/net tag. These do not alter the no-remedy verdict for this bounded study.

## 7. Stop

No candidate is authorized for production. Await explicit authorization for any corrective experiment, geometry change or production remedy.
