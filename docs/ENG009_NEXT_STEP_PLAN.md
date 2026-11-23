# T-ENGINEERING-009 — Ranked Next-Step Plan

Ranking basis: information gain first, then runtime cost, risk, reproducibility, and whether the step avoids repeating a rejected experiment. All steps are **proposals only**; none was executed.

| Rank | Action | Info gain | Cost | Risk | Reproducibility | Status |
|---|---|---|---|---|---|---|
| 1 | Add `getSrcs()` / `getVictims()` / `getAggressors()` logging to the two existing PA marker loops in the preserved instrumented source; rebuild single TU + relink; verify three-way runtime equivalence; replay existing ODB `pin_access` read-only | **HIGHEST** — classifies every residual marker by emitting object/net; resolves the 2 nm sliver ambiguity | low–medium | low (log-only, gate already exists) | high (hashes, harness, reference binaries preserved) | **PROPOSED** (ENG009-DIAG-001) |
| 2 | Recompute M4 LEF58 EOL/corner keepout and spacing envelopes around the pin; compare with R1-N/R1-N-W ±24 nm y margins; quantify required y margin | high — supplies the missing geometric model for narrow-corridor failure | very low (arithmetic) | none | very high | static analysis, can be done without approval |
| 3 | Read-only GDS census at exact residual marker bboxes (`Short`, `Metal Spacing`, sliver) with layer/datatype/net classification | high — distinguishes OBS artifact from real metal | low | none | high | static analysis using KLayout Python |
| 4 | All-pin AP survey on the unmodified ODB using the instrumented binary (diagnostic only, no geometry change) | medium–high — tests whether defect is pin-specific | low | low | high | requires bounded read-only run approval |
| 5 | Enumerate exposed `pin_access` flags and persist env/approval ledger state | low–medium — hygiene, no causal gain | very low | none | high | config-only diagnostic |
| 6 | Lower `min_access_points` sensitivity on scratch DB | low — would mask zero-AP defect; not recommended | low | medium (false suppression risk) | medium | **NOT RECOMMENDED** |
| — | Any new OBS corridor / geometry variant | — | — | — | — | **BLOCKED** until ranks 1–3 provide provenance + y-envelope model |

## Coordinator selection

**Select rank 1 as the single next diagnostic experiment (ENG009-DIAG-001)**, with ranks 2–3 as **mandatory zero-cost static pre-work before any rebuild** (Agent D B4/N1): if the GDS census shows foreign metal or the envelope calculation invalidates the mechanism, STOP and redirect before touching the build. A rebuild smoke test is required before the full replay. It is the only step that converts the 2 nm sliver and spacing bands from INCONCLUSIVE to evidence-backed classifications, and it does not repeat any rejected geometry variant.

R2 is applied in **advisory shadow mode** to the proposal (see `ENG009_PROPOSED_DIAGNOSTIC_EXPERIMENT.md`): it is not an active gate and no execution is authorized.

## Stop condition

Stop at the diagnostic decision boundary. Await explicit authorization before rebuilding, replaying ODB, or launching any flow. No remedy, production change, or additional geometry variant is authorized.
