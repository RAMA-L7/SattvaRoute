# T-ENGINEERING-010 — ENG009-DIAG-001 Execution and Evidence Adjudication: Final Report

- **Session:** 2026-11-24
- **Status:** COMPLETE. Stop after this milestone; no follow-up experiment authorized.
- **Verdict:** sliver attribution **CONFIRMED — ARTIFACT**; DRT-0073 root cause updated; instrumentation neutrality demonstrated.

## 1. What was executed

The approved log-only ENG009-DIAG-001 diagnostic (ENG010-AP-001) was executed in isolated scratch workspace `experiments/ENG009-DIAG-001/ENG009-DIAG-001-20261124T000000Z-0001`:
- backup + log-only `getSrcs()`/`getVictims()`/`getAggressors()` patch (66 additions, 0 removals);
- single incremental relink (after a pre-compile SIGKILL of a stalled client and one supervisor retry);
- identity/equivalence replays on frozen ODB `35bff121…`;
- one full provenance replay;
- mandatory static EOL-envelope and GDS census pre-work.

No EDA flow stage beyond `read_db` + `pin_access`; no geometry/remedy change; no production or baseline change.

## 2. Evidence

| Check | Result |
|---|---|
| Patch / source / binary hashes | `92ef2aac…` / `0fc94a9d…→0815de7d…` / `0d890431…→7461d0d0…` |
| Equivalence OFF vs OFF | byte-identical after path normalization |
| ON vs OFF | only pre-existing debug lines + Tcl line shift; no behavior change |
| Marker/PROV pairs | 107/107 (27 planar + 80 via), 0 mismatches |
| Sliver GDS census | 1 own-net `clk` 40/0 shape, **zero foreign-net 40/0**, OBS edge local x=3474 |
| M4 envelope | 72 nm corridor vs ~120 nm required; 24 nm/side shortfall (INFERRED) |
| DRT-0305 / DRT-0073 | 0 / 2 in full run (unchanged) |
| Protected artifacts / KB / validator | 9/9 OK; KB verify PASS; validator 13/13 PASS |

## 3. Sliver verdict and root cause

**CONFIRMED — ARTIFACT** under the pre-registered rule: OBS-edge fragmentation containing own-net clock metal, not a foreign-net short. Not the sole blocker. Updated bounded root cause: zero legal APs arise from full-body M4 OBS plus thin-pin EOL/corner-keepout and spacing interaction with the same OBS/macro geometry; residual markers are traced to macro/OBS objects, not foreign metal.

No geometry variant was run; y-envelope arithmetic remains INFERRED; all-pin AP and full-flow DRC/extraction/timing remain NOT EVALUATED.

## 4. Independent review

Agent B verdict ACCEPT WITH LIMITATIONS; all primary evidence independently verified from logs/artifacts. Non-blocking F1 (PROV lacks aggressor rect/net and OBS tag) was reconciled by combining provenance with Agent C's GDS census. Agent A's authorship wording, RC=137 accounting and stale snapshots were corrected/documented. See `ENG010_INDEPENDENT_REVIEW_AND_ADJUDICATION.md`.

## 5. Files

Created: `ENG010_INSTRUMENTATION_AND_EQUIVALENCE.md`, `ENG010_STATIC_EOL_AND_GDS.md`, `ENG010_MARKER_PROVENANCE_DATASET.md`, `ENG010_SLIVER_VERDICT_AND_ROOT_CAUSE.md`, `ENG010_INDEPENDENT_REVIEW_AND_ADJUDICATION.md`, `ENG010_FINAL_REPORT.md`; experiment artifacts under `experiments/ENG009-DIAG-001/...`; updated `ENG009_HYPOTHESIS_MATRIX.md`, KB append, state, coordination, logs and handoff.

## 6. Limitations and stop

- Attribution is object-level plus GDS-based; no DRC engine internals were changed or observed beyond markers.
- EOL envelope is INFERRED, not experimentally tested.
- DRT-0419 not investigated (explicit non-goal).
- No follow-up experiment or remedy authorized. Explicit approval required before any corrective experiment, geometry change, or production modification.
- KB appended: **KB-0019** (record SHA-256 `51df0159…4282`), 19 records total, chain verify PASS. Historical records unchanged.
- Published text evidence: `docs/ENG010_provenance.diff.txt` (patch) and `docs/ENG010_provenance_sample.txt` (12 PROV lines). Full binary/ODB artifacts remain in the isolated experiment directory and are not published.
