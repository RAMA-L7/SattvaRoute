# T-ENGINEERING-014 — Remedy Feasibility and Engineering Decision: Final Report

- **Date:** 2026-11-24
- **Status:** COMPLETE. Stop at this milestone. No subsequent milestone, remedy, experiment, or implementation without explicit user authorization.
- **Decision:** **NO REMEDY AUTHORIZED. Further diagnostic is required first; a bounded remedy experiment is not justified on current evidence.**

## 1. Authoritative decision

The confirmed root cause is a fixed M4 master-OBS rectangle, absolute `(4704,16560)-(4764,16584)` (master-local `(3474,8376)-(3534,8400)`), producing a `Short` (`checkMetalSpacing_short`, cid=0, rid=48) against the westward planar escape stub for `u_sram/clk`. Broad-carve removes that rectangle and restores 3/3 W access with 3 accepted APs — but frees 120 `M4/0` + 92 `M4/251` real SRAM shapes and is a diagnostic counterfactual only.

**Every conclusion is traceable to existing published evidence; no new measurement, geometry, or flow was produced in this milestone.**

## 2. Remedy-class disposition

| Class | Verdict | Reason |
|---|---|---|
| 1. Exact minimal west-strip M4 OBS carve | **CONDITIONAL — not authorized** | Narrowest causal descendant, but x-extent already freed in failed R1-N-W; strip contains own-net `clk` metal; full-strip GDS vacancy and rule-envelope proof missing; likely failure transfer to `ce_n` |
| 2. Macro pin-geometry adjustment | **NOT VIABLE** | Contributing not binding; LEF↔GDS mismatch; no LVS/PEX; no evidence pin shape is binding |
| 3. Macro placement / alignment | **NOT VIABLE** | Directly refuted; relative pin↔OBS geometry invariant; `clk` already on-track |
| 4. Supported pin-access configuration | **NOT VIABLE** | via-in-pin tested no-op; threshold flags cannot create AP 1; no config lever fixes a zero-AP fatal |
| 5. Generator-level OBS semantic regeneration | **CONDITIONAL — last resort** | Principled all-pin path, but configurability, defect status, and effect on M4 OBS all UNKNOWN; largest scope |
| 6. No remedy / further diagnostic | **VIABLE — immediate posture** | Consistent with consumed approvals STOP; closes decisive evidence gaps |

## 3. Why a bounded remedy experiment is not justified now

1. The exact west strip was already included in the R1-N-W carve (x 3474–3672, y±24), which produced 0 accepted APs. The strip being the *binding* blocker at first candidates does not make it *sufficient*.
2. Agent B's verified physical objection: after removing the strip, spacing/EOL/via families become binding; the ~120 nm EOL/corner envelope cannot fit at 96 nm pin pitch (adjacent-net metal 24 nm away < 25 nm ENDOFLINE). No legal geometry has been proven to exist.
3. Agent C's own prerequisites are unmet: full-strip GDS census, all-pin AP survey, path-matched no-op control, canonical DB diff, collateral DRC, written full-flow plan, and fresh explicit approval.
4. Broad carve is a reproducible `pin_access` positive control only — not evidence of physical legality, routing success, timing, or all-pin health.

This is **not** a claim that no remedy can ever exist (that would overstate the negative); it is a finding that **no legal, sufficient, evidence-supported remedy has been demonstrated under current constraints**.

## 4. Independent reviews

Agent A (feasibility), Agent B (independent physical review), and Agent C (validity/reproducibility) were commissioned under read-only constraints. B's physical objection and C's provenance caveats were reconciled against A's class matrix in `ENG014_COORDINATOR_ADJUDICATION.md`. C's recommendation to run a bounded experiment was **partially rejected as premature**; A's and B's positions were adopted with the correction that rect/fixed provenance enrichment was already executed in ENG013-B.

C identified two minor documentation inaccuracies and one invalid hash label in historical reports. They are recorded in `ENG014_EVIDENCE_VS_INFERENCE.md`; historical reports were preserved, not edited.

## 5. Required validation before any future authorized work

See `ENG014_RISK_AND_VALIDATION.md`: marker `getSrcs()`/object-type/net provenance; full-region GDS foreign-net census; quantitative rule-envelope proof; single-variable A/B with area-preserving no-op control and canonical DB diff; all-pin AP survey; full-flow route/DRC (by type/layer/bbox/source)/extraction/STA/KLayout signoff; fresh decision ID and explicit approval. None were performed here.

## 6. Integrity and stop

No EDA flow, geometry edit, ODB/LEF/DEF/GDS/source/config change, remedy execution, or production change occurred. R2 remains advisory-only and inactive. In the authoritative live tree (`D:\SattvaRoute`): KB verify PASS (19/19), protected artifacts 9/9, validator 13/13. Scope note: the publication mirror (`D:\SattvaRoute_publish`) intentionally excludes the GDS via the publication blocklist, so `verify-immutable` there reports the GDS as missing — a pre-existing environmental limitation, not a T-ENGINEERING-014 change. Protected-artifact verification is authoritative on the live tree. Publication closes this milestone.

**Stop. No subsequent milestone, remedy, experiment, or implementation without explicit user authorization.**
