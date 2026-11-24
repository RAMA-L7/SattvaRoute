# T-ENGINEERING-014 — Independent Agent Reviews

Three independent reviewers were commissioned under read-only/conceptual constraints. Their full reports are preserved at:
- Agent A: `C:\Users\91846\AppData\Local\Temp\opencode\ENG014_A_feasibility.md`
- Agent B: `C:\Users\91846\AppData\Local\Temp\opencode\ENG014_B_physical.md`
- Agent C: `C:\Users\91846\AppData\Local\Temp\opencode\ENG014_C_validity.md`

## Agent A — Remedy feasibility (conceptual)

- **Posture:** VIABLE = class 6 (no remedy / further diagnostic); CONDITIONAL = class 1 (minimal west-strip carve) and class 5 (generator-level OBS regeneration, last resort); NOT VIABLE = class 2 (pin geometry), class 3 (placement), class 4 (config).
- **Key correction by A:** the rect/fixed provenance enrichment was **already executed** in ENG013-B; the remaining diagnostic gap is the aggressor **object class / owner and net**, not the rectangle or fixedness.
- **Governance:** D-022/D-023 consumed and non-transferable; `allowed_roots` = `flow/scripts` only; any implementation needs a new decision ID + explicit approval.
- **Broad carve:** causal evidence only; frees 120 `M4/0` + 92 `M4/251` real shapes; not authorization, not a production solution.

## Agent B — Independent physical-design review

- **West-strip carve is not vacant:** the strip contains the `clk` net's own M4 path (GDS 40/0); zero foreign-net 40/0 in the 2 nm sliver census. So carving it is not a foreign-net short hazard, but it exposes real own-net SRAM metal and is **not sufficient** — FDE-007 R1-N-W freed exactly this strip and still produced 0 APs.
- **Broad carve proves mechanism, not legality:** it is the geometry most clearly shown physically illegal (120 M4/0 + 92 M4/251 real shapes, including foreign nets) while being the only one that passes `pin_access`.
- **OBS semantics:** master OBS can be narrowed without touching GDS or LEF `PIN … RECT` shapes; legitimacy rests on foreign-net GDS coverage, pin/FOREIGN offset consistency, master-level all-pin scope, canonical single-variable DB diff + no-op control, DRC-rule compliance, all-pin AP, and full-flow signoff.
- **Strongest physical objection (INFERRED, high):** the only geometry yielding APs is physically illegal; every legal narrow carve fails because the ~120 nm EOL/corner keepout envelope cannot fit at 96 nm pin pitch (adjacent-net metal 24 nm away < 25 nm ENDOFLINE). Carving the west strip alone does not change this.
- **Beyond `pin_access`:** global/detail route, signoff DRC, LVS/PEX (Calibre absent), timing (estimated Liberty, no SPEF), and KLayout signoff are all unvalidated.

## Agent C — Experimental validity and reproducibility

- **PROVEN about broad carve:** artifact hash `616e39f8…` recomputed; bounded `pin_access` replay reproduces CREATE=3/ACCEPT=3/DROP=0, DRT-0073=0, DRT-0305=0, RC=0, accepted x=4812/4788/4836 y=16572; W clean 3/3, E not clean; M4 OBS interior removed; all other static geometry identical (after pointer masking). "3 APs" is bounded to one instance terminal in a `pin_access`-only diagnostic.
- **INFERRED / UNKNOWN / rejected:** production LEF defect, DRC-clean routing, timing, all-pin AP, physical legality, and minimality are all unproven. y-envelope family is REFUTED; markers non-binding; sparse threshold is downstream, not causal.
- **Reproducibility gaps:** invalid 46-char "SHA-256" label for `exp_b.log` in ENG012 provenance (actual hash recomputed by C); replay used equivalent-but-different binary `7461d0d0…` vs `0d890431…`; broad generating LEF never located; no canonical ODB diff; two minor documentation inaccuracies in historical reports (recorded in `ENG014_EVIDENCE_VS_INFERENCE.md`, not edited).
- **Prerequisites before any future remedy test:** GDS census at exact west strip, all-pin AP survey, path-matched no-op control, canonical DB diff, collateral DRC/DRT-0305 parity, written full-flow plan, explicit approval.
- **Final recommendation (C, revised):** **FURTHER DIAGNOSTIC (class 6) — immediate, read-only posture; no remedy experiment now.** C's earlier draft recommended a bounded west-strip experiment, but C revised it after recognizing that the exact west strip was already carved under D-023 (R1-N-W, x 3474–3672) with 0 APs. C also rejects "no viable remedy" as overstating the negative, since no rule-envelope proof exists. **Coordinator adopts C's final recommendation**, which concurs with Agent B's physical objection and the coordinator decision.
