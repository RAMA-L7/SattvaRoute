# T-ENGINEERING-009 — Proposed Diagnostic Experiment ENG009-DIAG-001

- **Status:** PROPOSAL ONLY — NOT APPROVED, NOT EXECUTED. R2 applied in **advisory shadow mode**; R2 remains DRAFT/INACTIVE.
- **Session:** 2026-11-23/24

## 1. Identity and hypothesis

- **Experiment ID:** ENG009-DIAG-001
- **Class (R2-K):** `causal diagnostic` for **instrumentation behavior only** — Arm A vs Arm B is a one-variable contrast (log patch present/absent) with a pre-registered equivalence test; it asserts **no physical-design, geometry or remedy contrast**. Revising from the initial `mechanism-only` label resolves Agent D B2: Arm A is a genuine concurrent identity arm whose modification digest equals the approved baseline digest, not a disguised remedy control.
- **Question:** Which OpenDB objects emit each residual `Short`, `Metal Spacing` and `Lef58` marker in the `u_sram/clk` pin-access analysis, and is the FDE-007 2 nm sliver an OBS-edge artifact or real-metal violation?
- **Hypothesis H14:** marker provenance (`getSrcs()`) will attribute residual markers to master OBS boxes / self-shapes rather than foreign-net metal; if so, the narrow-corridor failures are explainable by OBS-fragment geometry and keepout envelopes, and no new remedy is authorized by this result alone.

## 2. Experimental units and arms

- **Unit:** one read-only `read_db` + `pin_access` replay on the frozen ODB `35bff121…`. AP candidates and DRC markers are **sub-units**, not replicates.
- **Arm A — identity/no-op:** existing instrumented binary `0d890431…` with current logging, original ODB and config. Confirms baseline replay reproduces FDE-006U candidate/marker counts.
- **Arm B — instrumented measurement:** same source and build with **log-only** additions of `getSrcs()`, `getVictims()` and `getAggressors()` in the two marker loops (planar ~789-809, via ~1177-1198). All DRC/decision conditions unchanged.
- Arm A is a **concurrent identity arm**: unmodified source, modification digest equal to the approved baseline digest, same ODB/config/binary build inputs, run in the same session window. Arm B differs only by the log-patch digest. This satisfies R2 A3's modification-digest identity rule for the instrumentation contrast; it does **not** close the historical physical no-op-control gap for any remedy. A behavior difference beyond new provenance lines → STOP.

## 3. Isolated variable

Only the log statements in the two marker loops change. No OBS, LEF, GDS, netlist, RTL, SDC, PDN, config, placement, layer/via rule, threshold or D-014 change. Patch digest and source/binary hashes recorded before and after.

## 4. Measurements

Per marker: type, rule id, layer, bbox, and source/victim/aggressor object (net/inst/term name where resolvable).
Per candidate: x/y/layer, rejection stage, marker association, final `hasAccess()` outcome.
Aggregate: CREATE / MARKER / DROP counts, `n_aps`, `n_sparse`, threshold, DRT-0073 status, rc.
Static pre-work: M4 EOL/corner keepout envelope vs ±24 nm corridor y margins; GDS census at each residual bbox.
§B evidence fields: per-marker provenance, same-net vs foreign-net classification, NOT_RUN labels for unreached pins.

## 5. Numeric acceptance criteria (pre-registered)

1. **Equivalence (rewritten, B1):** Arm A (diag-off) and Arm B (diag-on) must produce identical candidate coordinates, marker type/rule-id/layer/bbox census, DROP counts, `n_aps`, `n_sparse` and rc; the **only** permitted difference is added provenance lines. The production binary `c1b90e0a…` is compared at the **aggregate level only** (DRT-0073/0305/0419 counts and rc), because it emits no per-marker records. A smoke replay must pass before the full replay.
2. **Attribution (operational, B3):** "resolvable" = `getSrcs()` returns at least one OpenDB object with a net/inst/term name **or** an identified master-OBS box id. ≥90% of residual markers in Arm B must meet this; every unresolved marker is listed as UNKNOWN with reason. Attribution completeness is a proxy, not proof of physical truth — criterion 4 requires the GDS check.
3. **Sliver decision rule (B3):** for bbox `(4703,16560)-(4705,16584)`, classify **OBS-artifact** if sources identify a master OBS edge at local x=3474 and a read-only GDS census shows no foreign-net 40/0 shape intersecting the bbox; classify **real-metal** if a foreign-net 40/0 shape intersects; otherwise **INCONCLUSIVE** with named missing evidence. No assertion-only classification.
4. Metal-spacing/EOL bands are attributed to specific OBS bands or neighbor shapes **and** cross-checked against the GDS census; disagreement is reported, not silently resolved.
5. Static rank-2/3 work (EOL envelope arithmetic and GDS census at residual bboxes) is completed **before** the rebuild; if it shows foreign metal at the sliver/spacing bands, STOP and redirect before any build. The envelope result is explicitly **INFERRED**, not a tested geometry rule (B4).
6. DRT-0305=0, DRT-0419 count unchanged (8 parity), and no protected hash changes.
7. **Cost cap (B2 consequence):** maximum one TU patch + one relink attempt, one smoke replay, one full replay, ≤2 bounded debug iterations; STOP and report on exceeding.

## 6. Abort conditions

- Any behavior difference beyond added provenance log lines.
- Rebuild failure or inability to reproduce Arm A's FDE-006U counts.
- >10% of residual markers unattributable without documented reason.
- Protected-artifact or baseline hash change.
- Resource/supervisor condition approaching prior SIGKILL; stop and preserve logs.

## 7. Cost, risk, reproducibility

Single translation-unit log patch + relink; read-only ODB replay; expected minutes, not a full flow. Existing harness, hash manifests, binaries and equivalence gate make it highly reproducible. Risk is low because only logging changes; approval is still required.

## 8. R2 advisory shadow assessment (not a gate)

| R2 item | Shadow disposition | Basis |
|---|---|---|
| Class | `mechanism-only diagnostic` | no causal contrast, no remedy |
| A1/A2 | PASS | question/unit/response written; N=1 replay per arm; markers sub-units |
| A3 | PASS (instrumentation identity) | Arm A modification digest equals approved baseline; digest-backed, not label-backed; not a remedy control |
| A4 | PASS (log-only digest change) | one variable: marker-log statements |
| A5/A14 | PARTIAL → complete at gate | binary/source/manifest hashes to be pinned before approval |
| A7 | N/A | no remedy family named; any future geometry must run `assess`/`duplicate_check` |
| A8 | PASS (pre-registered above) | numeric criteria and decision rules fixed in this proposal |
| A11 | PARTIAL / preflight DEFERRED | bounded read-only replay; smoke test before full replay; preflight at execution |
| A12 | PARTIAL / post-run DEFERRED | baseline hashes named; post-run confirmation at execution |
| A13 | PASS (bounded cost cap added) | causal class → explicit cap and STOP conditions |
| A15 | DEFERRED-SHADOW | no approval; named reviewer required at gate |
| A16 | N/A | demoted reference; no patch to production |
| A17 | PARTIAL (capability partly proven) | `getSrcs()` API and binary verified, but rebuild capability requires smoke test; not a silent PASS |

R2 is advisory only; no item here authorizes execution.

## 9. Classification-only / no-geometry gate (Agent D B5)

Results from ENG009-DIAG-001 may **only** classify markers and quantify the keepout envelope. They do not authorize, recommend or rank any geometry variant. Any future OBS proposal requires a separate decision and must include: provenance classification, full x-and-y keepout envelope, zero foreign-net 40/0 GDS census, a genuine no-op control, canonical DB diff and a full-flow plan. Repeated `M4_OBS_CORRIDOR` family variants remain REJECTED without new justification.

## 10. Explicit non-goals

No EDA flow, no remedy, no geometry variant, no production change, no KB/approval/historical rewrite, no R2 activation. Await explicit authorization.
