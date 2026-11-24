# T-ENGINEERING-013 — Independent Review and Coordinator Adjudication

## 1. Agents

| Agent | Verdict | Contribution |
|---|---|---|
| A — source trace | VERIFIED | exact predicate chain; failing `markers.empty()` at `:867`; Short/cid0/rid48 from `checkMetalSpacing_short`; minimal rect/fixed patch |
| B — instrumentation/replay | COMPLETE, neutrality PASS | patch, rebuild, control/broad replays; exact W blocker rect/fixed; broad W clean |
| C — blind challenge | PREDICTION CONFIRMED | predicted west M4 OBS rect from geometry; challenged instance label; required rect/type proof |

## 2. Reconciliation

Agent C's pre-execution prediction (M4 OBS west strip at abs x 4704–4764 y 16560–16584) is **confirmed** by Agent B's instrumented marker tuple. The `u_sram` instance label is an attribution artifact of `addTargetObj(inst)` and its numeric id is unstable; the stable, decisive evidence is the layer/rect/fixed tuple.

Agent A's caution that `clean=` on MARKER lines is always false inside the loop is accepted; the authoritative direction flag is `FDE006R PLANAR-DRC`.

## 3. Adjudication

The remaining shape-level uncertainty from T-ENGINEERING-012 is **closed**: the westward blocker is the fixed M4 master-OBS rectangle `(4704,16560)-(4764,16584)` intersecting the westward escape stub at y=16572. Broad carving removes that rectangle; narrow y/corner variants retain it. No geometry, production, or full-flow change was made.

## 4. Limitations

Literal tech-LEF text for rid 48 UNKNOWN; all-pin AP status and full-flow signoff remain NOT EVALUATED. These do not affect the blocker attribution.

## 5. Stop

No remedy or follow-up experiment authorized. Explicit approval required for any corrective study.
