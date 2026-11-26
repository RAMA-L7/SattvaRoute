# Current limitations

Status: authoritative limitations statement. Related: `docs/product/NON_GOALS.md`, `docs/engineering/VERIFICATION_BOUNDARIES.md`.

## Implementation scope limits

- **Single validated workflow:** Nangate45 + `fakeram45_64x32` `nangate_macro_control` on the pinned ORFS revision with two local patches and pinned tool binaries. No other design/PDK is validated.
- **Pass-through wrapper:** the RTL wrapper is not a meaningful design; the benchmark is deliberately simple.
- **Abstract macro:** `fakeram45_64x32` is an abstract ORFS macro, not a foundry-characterized SRAM.
- **Single typical corner, trivial timing:** `typical`, 1.1 V, 25 °C, 1 ns constraint after explicit approval. Not representative of production timing closure.
- **Bounded diagnosis:** a fixed family set and heuristics; no general physical-design reasoning engine.
- **Benchmark-specific verification patterns:** DRT-0199, RCX-0045, and report regexes are tied to this toolchain.

## Verification / signoff limits

No foundry DRC/LVS, no antenna/power/IR-drop/EM signoff, no SDF/formal functional signoff, no coverage, no characterized multi-corner timing. Router DRC=0 ≠ foundry DRC. Timing ≠ functional correctness. Flow completion ≠ engineering acceptance.

## AI limits

- Live AI evaluation unavailable without credentials (`SKIPPED_NO_CREDENTIALS` / `BLOCKED`).
- No live-AI recovery is claimed; the verified recoveries were deterministic and human-approved.
- Model output is advisory only; no general engineering competence claim.
- Historical live-AI reports include a `REJECTED` verdict; preserved, not relabeled.

## Process limits

- No external independent reproduction by another engineer is claimed.
- No quantified productivity, cost, or accuracy gains.
- `DRT-0073`/OpenFinRAM unresolved, preserved, excluded; not reopened.
- Inactive manifest profiles (`riscv32i_sattva`, `sattva_sram`) are declared, not validated.
- Security controls are local/convention-based; no authentication, sandbox, fuzzing, or signed approvals.
- LICENSE change requires owner approval; no change made in this milestone.

## Consequence

SattvaRoute is a research-grade engineering framework for evidence-bound diagnosis and controlled recovery on one pinned benchmark — not a production signoff or autonomous EDA system.

## Related

`docs/research/ROADMAP.md`, `docs/research/HYPOTHESES.md`, `docs/REPRODUCIBILITY.md`, `docs/security/THREAT_MODEL.md`.
