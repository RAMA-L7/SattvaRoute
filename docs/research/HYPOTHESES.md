# Research hypotheses, open problems, and future directions

Status: research direction only. Nothing here is implemented or promised. See `docs/research/ROADMAP.md`, `docs/research/LIMITATIONS.md`.

## Hypotheses (to be tested, not asserted)

- **H1:** Binding each diagnosis claim to concrete evidence refs improves reviewability of failure analysis. (Not measured.)
- **H2:** Bounded, stage-limited reruns reduce unintended collateral change compared with full reruns. (Not measured.)
- **H3:** Independent report-level verification catches false-success cases that return codes miss. (Implemented checks exist; comparative study not performed.)
- **H4:** A model grounded in structured evidence produces more useful advisory diagnoses than an ungrounded model. (Live-AI evaluation limited; not concluded.)
- **H5:** Recovery quality can be scored beyond binary PASS/FAIL (e.g. magnitude of report improvement). (Not implemented.)

## Open problems

- Generalization beyond one pinned Nangate45 macro benchmark.
- Multi-corner / multi-mode timing reasoning.
- Reliable correlation between a diagnosis and the change that actually fixes it.
- Prompt-injection-resistant model use on untrusted logs.
- Quantifying recovery quality without signoff data.
- Independent reproduction by engineers outside the author environment.
- Bridging tool-level DRC to foundry-level verification — deliberately out of scope.

## Future research directions (planned)

- Broader failure taxonomy and more diagnosis benchmarks.
- Improved evidence correlation and cross-stage failure reasoning.
- Constraint intelligence with strict human approval.
- Physical-design failure knowledge representation (immutable KB already exists as a foundation).
- Safe agentic engineering and multi-agent diagnosis with separation of duties.
- Recovery-quality metrics and better model evaluation.
- Reproducible benchmark expansion.

## Boundaries

Future work must preserve the same principles: evidence before conclusions, narrow corrections, human control, isolation, independent verification, honest statuses. No delivery dates are committed.

## Related

`docs/product/VISION.md`, `docs/research/ROADMAP.md`, `docs/research/LIMITATIONS.md`, `docs/reproducibility/EVALUATION.md`.
