# Non-goals

SattvaRoute is **not** currently intended to:

- **Replace a physical-design engineer.** It assists; human judgment + approval required.
- **Autonomously modify production designs.** Nothing applied without explicit human approval; recovery isolated; originals preserved.
- **Guarantee routing completion.**
- **Guarantee timing closure.**
- **Guarantee physical signoff.** No foundry DRC/LVS, no power/IR-drop/antenna/EM, no SDF/functional signoff. Router/OpenROAD-internal DRC=0 + 0 DRT-0199 + clean antenna + extracted STA ≠ foundry signoff.
- **Replace EDA tools.** ORFS/OpenROAD executes; SattvaRoute orchestrates + verifies evidence.
- **Replace DRC, LVS, or signoff verification.**
- **Invent engineering collateral.** No invented library/macro/corner; insufficient evidence → `insufficient_evidence`.
- **Treat tool exit codes as engineering success.** `rc=0` ≠ PASS.
- **Claim general AI engineering competence** based on limited tests. Live-AI not counted without credentials; no live-AI recovery claimed.
- **Reopen `DRT-0073`/OpenFinRAM.** Unresolved; preserved; excluded.
- **Change constraints or technology rules silently.** SDC change (1 ns) explicitly approved; originals preserved.
- **Rewrite historical results.** Historical runs/evals preserved; not relabeled.

Adjusted only with evidence. Research/planned separated in `docs/research/`.
