# T-ENGINEERING-014 — Remedy-Class Comparison Matrix

Conceptual assessment only. **No remedy was executed, no geometry created, no EDA flow launched.** Verdicts are those of Agent A (remedy feasibility), subject to coordinator adjudication in `ENG014_COORDINATOR_ADJUDICATION.md`.

## 1. Summary matrix

| Class | Feasibility | Expected benefit | DRC / routing risk | Pin-access impact | Authorization | Validation required | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Exact minimal west-strip M4 OBS carve | INFERRED high (scratch LEF injection path proven); blocker rect is exactly this strip | `clk` W clean → 3 candidates accepted; **not** a whole-`pin_access` pass | MEDIUM: new OBS-edge seam (R1-N-W 2 nm sliver precedent); full-strip GDS vacancy UNKNOWN; router entry into occupied metal if wrong | `clk` restored; E non-binding; other 11 unchanged → likely failure transfer to `ce_n` | NEW decision ID + explicit approval; D-022/D-023 consumed & non-transferable | single-variable A/B + area-preserving no-op control; canonical DB diff; all-pin AP census; full-strip GDS census; full route/DRC/SPEF/STA if promoted | **CONDITIONAL** (narrowest diagnostic/falsifier, not a production fix) |
| 2. Macro pin-geometry adjustment (LEF/GDS/generator) | Mechanically possible at GDS/generator level; no evidence pin shape binding | LOW; enlarging/translating pin does not remove west OBS; moving left edge west worsens overlap | HIGH: all 12 thin pins affected; LEF≠GDS if abstract-only; Calibre absent (no LVS/PEX); estimated Liberty | No demonstrated W access | NEW decision + protected macro-data + generator change + recharacterization | GDS continuity; generator diff; regenerated hashes; LEF↔GDS; LVS/DRC/PEX/STA; all-pin AP; full flow | **NOT VIABLE** on current evidence |
| 3. Macro placement / alignment | Directly refuted; rigid translation preserves pin↔OBS relative geometry | NONE | Possible new DRT-0419 off-grid warnings, congestion/timing regressions | Neutral / none | Would require floorplan approval, but class is refuted | Already validated negatively (FDE-004-D) | **NOT VIABLE** |
| 4. Supported pin-access configuration | Refuted: via-in-pin flags tested no-op; threshold cannot create AP 1; no `set_ppl_mode` in build | NONE; could only mask a diagnostic | Relaxation could admit unsafe APs; global scope; invalid layer names silent no-ops | NONE observed | Would require approval for env/flow forwarding | Already completed (negative). Any retest needs resolved layer numbers + A/B parity | **NOT VIABLE** |
| 5. Generator-level OBS semantic regeneration (all-pin) | Possible but unevidenced: OBS configurability, defect status, and effect on M4 OBS all UNKNOWN | Speculative but principled all-pin fix; avoids `clk`→`ce_n` transfer | HIGH: regenerated OBS over real metal → router shorts; GDS/silicon change; no LVS/PEX; all abstracts may shift | Potentially positive for all terms (UNKNOWN) | NEW decision + generator/source approval + recharacterization + protected hash updates | Generator diff; new GDS/LEF/LIB hashes; FDE-004-A continuity; full flow; all-pin AP; KLayout macro DRC | **CONDITIONAL** (last resort) |
| 6. No remedy / further diagnostic | VIABLE now; read-only and consistent with STOP. Rect/fixed enrichment already executed in ENG013-B; remaining gap is object class/owner/net | High information value, zero direct AP gain | NONE for logging-only; no geometry/flow change | NONE | No authorization for conceptual proposal; any execution needs new decision ID + scratch scope | Confirm object type/net via provenance extension; confirm EMPTY strip A/B; verify no-op parity | **VIABLE** (immediate posture) |

## 2. Comparison to broad-carve diagnostic

| Axis | Broad carve (reference) | Minimal west strip (class 1) |
|---|---|---|
| M4 OBS removed | Interior window master-local `(1500,300)-(3650,13300)`; 4 frame rects survive | Only abs `(4704,16560)-(4764,16584)` / local `(3474,8376)-(3534,8400)` |
| Real internal metal exposed | 120 `M4/0` + 92 `M4/251` shapes → physically illegitimate | Intended zero; full-strip design-level GDS census not performed (UNKNOWN) |
| `clk` W access | Restored 3/3, 3 APs | Predicted restored (high-confidence INFERENCE: blocker rect = this strip) |
| Other pins | Interior freed but not validated | Unchanged → expected failure transfer |
| Governance | REJECTED for production; no approval | New decision ID + approval required |
| Role | Bounded mechanism proof / counterfactual only | Decisive falsifier; not a production fix |

**Governing rule:** broad-carve success is used only to establish causality — never as authorization, never as a production solution, never as proof of route/DRC/timing/all-pin signoff.

## 3. Ranked disposition

1. **Class 6 — no remedy / further diagnostic: VIABLE** (immediate, authorized posture).
2. **Class 1 — minimal west-strip carve: CONDITIONAL** (diagnostic first; remedy only after all-pin + GDS + full-flow validation).
3. **Class 5 — generator-level OBS semantic regeneration: CONDITIONAL** (last resort).
4. **Class 2 — pin geometry: NOT VIABLE.**
5. **Class 3 — placement: NOT VIABLE.**
6. **Class 4 — config flags: NOT VIABLE.**

No class is authorized for implementation at this milestone.
