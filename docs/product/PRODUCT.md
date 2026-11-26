# Product definition

**Authoritative.** Other documents link here; do not redefine.

## One-sentence definition

> **SattvaRoute is an evidence-driven physical-design diagnosis and controlled recovery framework for VLSI implementation workflows. It helps engineers investigate implementation failures, identify evidence-supported causes, evaluate precise corrective actions, authorize changes, execute isolated recovery attempts, and independently verify outcomes.**

## Scope of "physical design"

SattvaRoute orchestrates evidence around an existing EDA physical-design flow. Verified scope today is the **OpenROAD Flow Scripts (ORFS) + OpenROAD** path (pinned revision `25b6429c…`, two recorded local patches), specifically a reproducible **Nangate45 + `fakeram45_64x32` `nangate_macro_control`** benchmark. It instruments stages from synthesis through routing, extraction, and timing analysis **only insofar as those stages emit evidence**; it does not implement synthesis, placement, CTS, routing, extraction, or STA itself. Historical ASAP7 work is preserved but inactive.

General engineering background on synthesis → routing → extraction → timing → verification is in `docs/engineering/`, clearly separated from what SattvaRoute actually implements.

## Status

Research prototype. **Not** production signoff. **Not** autonomous. See `docs/research/LIMITATIONS.md` and `docs/reference/CAPABILITIES.md`.

## Related

`docs/product/PROBLEM.md`, `MISSION.md`, `GOALS.md`, `NON_GOALS.md`, `USERS.md`, `USE_CASES.md`, `VALUE.md`, `NAMING.md`, `docs/architecture/`, `docs/security/`.
