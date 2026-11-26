# Product vision

Status: product direction. Current capabilities are bounded by evidence; see `docs/reference/CAPABILITIES.md`.

## Long-term vision

A physical-design engineer facing an implementation failure should be able to answer, from preserved evidence alone: **what failed, why it failed, what was changed, who authorized it, what was rerun, and whether the outcome is actually better** — without relying on undocumented local state, memory, or a tool exit code.

SattvaRoute aims to make that chain of reasoning reproducible and auditable for EDA workflows. The long-term direction is an **evidence-grounded engineering assistant** that reasons across synthesis, placement, CTS, routing, extraction, and timing stages, proposes narrowly scoped corrections, and operates only within explicit human authorization and isolation boundaries.

## What the vision is not

- Not autonomous production design modification.
- Not a replacement for the engineer's judgment or for EDA tools.
- Not a signoff system.
- Not a claim of general AI engineering competence.

## Path from here

1. **Current foundation (delivered):** deterministic diagnosis, approval-gated patch application, isolated recovery, independent verification, reproducible manifest v2, frozen diagnosis evaluation, preserved control benchmark.
2. **Research direction (planned):** broader failure taxonomy, richer evidence correlation, cross-stage reasoning, better model evaluation, recovery-quality metrics. See `docs/research/ROADMAP.md`.
3. **Long-term (research):** evidence-grounded EDA agents and safe agentic engineering. Nothing here is a delivery commitment.

## Related

`docs/product/PRODUCT.md`, `docs/product/MISSION.md`, `docs/product/GOALS.md`, `docs/research/HYPOTHESES.md`.
