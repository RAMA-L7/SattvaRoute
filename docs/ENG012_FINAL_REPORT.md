# T-ENGINEERING-012 — Pin-Access Generation and Rejection Forensics: Final Report

- **Date:** 2026-11-24
- **Status:** COMPLETE at the forensic decision boundary. No experiment launched, no remedy implemented.
- **Verdict:** the 0→3 AP observation is **explained at predicate level**; one shape-level provenance gap remains.

## 1. Executive finding

Broad-carve did not create new AP candidates. It removed the M4 OBS interior so the **westward planar probe** from the first generated candidates became DRC-clean; the macro pin needs only one clean planar direction, so x=4812/4788/4836 were accepted, sparse threshold 3 was met, and generation stopped. ENG011 variants generated all 9 candidates but every one failed `hasAccess()` because the x-adjacent obstruction remained. C1's y-widening moved marker bands to the new OBS edges without changing counts or APs — confirming the x-side overlap, not y-keepout, is binding.

## 2. Evidence

- Broad-carve ODB hash `616e39f8…` verified; bounded replay reproduced CREATE=3/ACCEPT=3/DROP=0, DRT-0073 absent, accepted x=4812/4788/4836 y=16572.
- MASTER OBS: broad has 4-rect frame with interior x1500–3650/y300–13300 removed; all other geometry (placement, pin rects, tracks, layers, via defs) identical across six ODBs.
- Source trace: coordinate generation ignores OBS; OBS enters only through DRC helpers; final `hasAccess()` at `FlexPA_acc_point.cpp:1371-1389`; sparse gate at `:1262-1305`, threshold 3.
- ENG011: 9 CREATE / 0 ACCEPT in all arms; marker types non-binding (broad accepted x=4836 with 3 via/stage markers).

## 3. Independent review

Agent A (source), B (artifacts), C (blind mechanism). Reconciliation: the same first three coordinates are generated in both arms; the other six are never generated in broad because the sparse threshold breaks the generation loop. Agent C's objection is accepted: the `u_sram` "OBS aggressor" label may be an instance-level provenance artifact; the exact blocking rectangle is UNKNOWN at shape level.

## 4. Deliverables

`ENG012_AP_SOURCE_TRACE.md`, `ENG012_BROAD_CARVE_PROVENANCE.md`, `ENG012_ARTIFACT_COMPARISON.md`, `ENG012_GENERATION_REJECTION_MATRIX.md`, `ENG012_PREDICATE_FAILURE_ANALYSIS.md` (within generation matrix), `ENG012_INDEPENDENT_REVIEW_AND_ADJUDICATION.md`, `ENG012_HYPOTHESIS_UPDATE.md`, `ENG012_NEXT_DIAGNOSTIC_RANKING.md`, this report; state/logs/handoff updated. All artifacts preserved in `experiments/ENG012-FORENSICS/…`.

## 5. Integrity

KB verify PASS (19 records/19-link chain), protected artifacts 9/9, validator 13/13, R2 unchanged and inactive, no production/baseline/binary change.

## 6. Stop

Ranked next diagnostic: per-direction DRC source/rect logging (ENG012-DIAG-002, design only). **Do not launch it** without explicit authorization. No remedy, production change, or full-flow run authorized.
