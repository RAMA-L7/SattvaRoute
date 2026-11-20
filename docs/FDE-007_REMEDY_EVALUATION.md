# FDE-007 — Remedy Evaluation (Gate 1)

- **Task:** T-FDE-007 (Gate 1 only — research and proposal)
- **Date:** 2026-11-20
- **Coordinator:** orchestrator
- **Agents:** A physical geometry/GDS, B remedy research, C validation planning, D independent safety review
- **Gate 1 status:** **COMPLETE — awaiting explicit approval (Gate 2)**. No source, LEF, GDS, config, or flow-file modification; no physical-design run; no remedy implemented.

## 1. Established root cause (from FDE-006U)
Same-binary, single-variable A/B proved that the **full-body M4 master OBS** on `sram_x4x4x1` blocks planar escape of the thin M4 `clk` pin:
- A (original OBS): 9 candidates, 0 accepted, sparse 0 < 3, DRT-0073, rc=1.
- B (scratch M4 OBS carve): 3 candidates, 3 accepted, sparse 3 ≥ 3, no DRT-0073, rc=0.
Scope: `pin_access` on ODB `35bff121…` with the installed OpenROAD/ASAP7 toolchain. Not proof of a production LEF defect, routing/DRC/timing success, or other pins' health.

## 2. State verification and revision reconciliation
- Publish repo `D:\SattvaRoute_publish`: branch `main`, HEAD `cb11fd9e551bbd9e789c3c270c870d058c98ee0d` = remote HEAD; clean at start.
- Working project `D:\SattvaRoute`: branch `master`, HEAD `3d7b936…` with uncommitted engineering records. This is the authoritative *working* tree; `main` in the publish tree is the authoritative *publication* revision. Agent D's "revision drift" is this expected split, not an unexplained change.
- Source ODB `35bff121…`, production binary `c1b90e0a…`, production LEF `f1c18877…`, GDS `12c56777…`, OpenROAD source `629aa76…` — all verified.
- FDE-006U diagnostic binaries `9c0ed727…` (reference) and `0d890431…` (attribution) unchanged.

## 3. Physical geometry findings (Agent A)
- Macro 3.672 × 13.608 µm; `FOREIGN … 0.054 0`; 1 DBU = 1 nm. 12 M4 signal pins, each 84 × 24 nm at x 3.534–3.618 µm, 54 nm inside the right edge.
- M4 Short marker bboxes from FDE-006U resolve to the strips immediately **left and right of the clk pin**, not adjacent-y pins.
- Read-only KLayout census: the FDE-006U carve `(1500,300)–(3650,13300)` DBU contains **120 M4/0 routing shapes + 92 M4/251 pin shapes** (8 full-width straps, 40 control paths, VIA34 pads). It declares occupied SRAM interior as routable — **not physically justified**.
- GDS supports only a **~54 nm right-edge escape corridor** per M4 pin (LEF x 3.618–3.672 µm), where no M4/0 metal exists. No VIA45 cell and no M5 metal inside the macro GDS.
- VIA45 M4 landing pad (46 × 24 nm) fits inside the clk pin, so via-on-pin is geometrically legal; the blocking issue is OBS over the approach.
- Tech rules: M4 width/spacing 0.024 µm; `LEF58_EOLKEEPOUT 0.025 EXTENSION …` (rule 59); `LEF58_SPACING ENDOFLINE …`.

## 4. Remedy comparison

| Remedy | Physical justification | Scope | Risk | Reversibility | Evidence | Recommendation |
|---|---|---|---|---|---|---|
| **R1** broad carve `(1500,300)–(3650,13300)` | Causally effective at pin_access | ~59% × 95% of M4 abstraction | **Unacceptable** — frees 120 real M4 shapes; router could short SRAM metal | High (scratch only) | FDE-006U A/B | **REJECT for production** |
| **R1-N** narrow per-pin/right-edge M4 OBS corridors derived from GDS-empty strips | GDS shows empty 54 nm strips at each M4 pin | M4 only, per-pin corridors; all 12 M4 signal pins may be required | Moderate — must prove no routed metal overlays real SRAM M4; small carves shift failure to next pin | Full (scratch LEF) | Requires GDS-derived geometry + no-op control + full flow | **PROPOSE only** |
| **R2** pin-geometry adjustment | LEF generated from GDS pin markers; LEF-only edit creates abstract≠silicon mismatch | Pin shapes (~12 pins), LEF/GDS/generator | High — manufacturing/LVS/PEX unresolved | Low | No evidence OBS is generator-configurable | **REJECT now** |
| **R3** pin-access configuration | `-via_in_pin_* M4` was a controlled no-op; `-min_access_points` cannot create first AP; no `set_ppl_mode` | Global tool config; lowering threshold would be suppression | Unsafe APs could hide design-view defect | Trivial | FDE-005 A/B, source inspection | **REJECT as fix**; diagnostics only |
| **R4** placement/regeneration | Placement alignment refuted (clk centre exactly on M4 track); OBS configurability unevidenced | Largest scope | New GDS/LEF/LIB hashes, recharacterization | Low | None | **REJECT now** |

## 5. Selected remedy proposal (requires approval)
**Remedy ID R1-N**: in an **isolated scratch copy** of the macro LEF, narrow the M4 full-body OBS only to exclude GDS-verified empty right-edge escape corridors for the M4 signal pins (starting with `clk`; likely all 12 M4 signal pins needed because pin_access aborts at the first failing term). Exact geometry must be derived from the read-only GDS check and documented as a per-box delta before implementation. No M1/M2/M3/M5 OBS, pin rectangles, dimensions, placement, technology, via rules, SDC, netlist, RTL, ORFS config, or D-014 changes.

Injection path (Agent C): copy the design tree to a scratch `SATTVA_DESIGN`, modify only the scratch macro LEF, append an `ADDITIONAL_LEFS` override in the scratch config, and run the hardened runner with a unique run ID. Environment variables cannot override ORFS variables declared with `export VAR = …`; command-line/`SATTVA_DESIGN` override is required. Approval policy currently permits patches only under `flow/scripts`, so a new decision + policy amendment + explicit approver + ledger entry are mandatory before any LEF change.

## 6. Validation plan (Agent C; all gates conditional)
1. Scratch implementation + canonical DB diff (OBS sole delta), no-op control, all-pin AP survey.
2. Pin-access validation with same binary/harness: APs accepted, sparse ≥ 3 for all `u_sram` signal terms, DRT-0073/0305 absent.
3. Floorplan/place from modified LEF (not ODB patch): placement/orientation parity, no new congestion/MPL regressions.
4. CTS: clock arc through `clk`, no DRT-0305, PDN parity, D-014 parity.
5. Global route: `route.guide`, all signal nets routed, no DRT-0073/0305, congestion/wirelength captured.
6. Detailed route: completion, DRC census by type/layer/bbox, KLayout DRC of carved region proving no routed metal/via overlays real SRAM M4 (KLayout currently absent → BLOCKED unless available).
7. Extraction/timing: `6_final.spef`, STA setup/hold WNS/TNS, clock latency/skew; estimated Liberty and no LVS/PEX disclosed. `make finish` may fail on missing KLayout GDS step — explicit disposition required.
Full-flow acceptance requires all stages; AP success alone is never sufficient (D-007).

## 7. Independent review (Agent D)
- Gate 1: **CONDITIONAL GO** for a scoped proposal only; **NO-GO** for the broad carve as a production fix, any LEF/GDS/ODB/tech/config edit, any flow run, any threshold/debug/DRC suppression, any waiver, any auto-deployment at this gate.
- All later gates CONDITIONAL GO with explicit fresh approval and the previous gate's evidence. STOP on protected-hash change, multi-variable/unverifiable edit, no-op control delta, DRT-0305 reappearance, or AP success presented as routing/DRC/timing success.

## 8. Explicit approval request
Approval is required for:
- **Remedy ID:** R1-N (narrow GDS-derived M4 OBS corridor(s), scratch only).
- **Exact change:** per-pin M4 OBS corridor geometry in a scratch LEF copy; no other design data changed.
- **Target file:** scratch `benchmark/design/sattva_sram/macro/sram_x4x4x1.lef` under a new experiment directory — **not** the production file.
- **Scope:** scratch LEF + scratch design tree; full-flow validation only; no production deployment.
- **Validation:** all gates in §6; DRC/extraction/timing reported honestly; no waiver.

**Until this is explicitly approved, FDE-007 stops. No implementation, no physical-design run, no production change.**

## 9. Verdict labels
VERIFIED: FDE-006U A/B, hashes, GDS occupancy census. OBSERVED: marker bboxes and types. INFERRED: per-pin corridor necessity. PROPOSED: R1-N. UNVERIFIED: full-flow remedy success, DRC cleanliness, timing. BLOCKED: KLayout signoff DRC/LVS/PEX (tool absent).
