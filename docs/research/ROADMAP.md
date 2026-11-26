# Roadmap and research direction

Status: completed items are evidence-backed; future items are **planned/research**, not delivery commitments. See `docs/research/LIMITATIONS.md`.

## Completed (evidence-backed)

- Runner reliability with per-stage evidence capture and preflight.
- Approval integrity and patch authorization (exact hash, scope, ledger, path safety).
- Failure evidence collection and bounded deterministic diagnosis.
- Macro pin-access and missing-collateral investigations (historical reports preserved).
- Timing-unit audit and correction (historical 1000 ns preserved; approved 1 ns active).
- Dependency fingerprinting and reproducibility (manifest v2, pinned ORFS + 2 patches, tool/collateral hashes).
- Independent recovery verification (`verify_run.py`, report-level, fail-closed).
- Frozen diagnosis evaluation v2 and held-out evaluation protocol.
- Held-out failure recovery with explicit human approval (`docs/HELDOUT_RECOVERY.md`).
- Benchmark packaging and publication; PR #1 merged into `main`.
- Documentation/product-identity overhaul (this milestone).

## Current capability

Today a user can: run the pinned control baseline; capture evidence; deterministically diagnose bounded failures in that benchmark; review an exact-diff proposal; obtain human approval; apply it in an isolated stage-limited recovery attempt; and independently verify the result. See `docs/reference/CAPABILITIES.md`, `docs/workflow/WORKFLOW.md`.

## Known gaps

Live model availability (`SATTVA_MODEL_URL` unset → advisory path unavailable), single benchmark/generalization, incomplete evaluation, no external independent reproduction, no signoff, no functional correctness, inactive profiles unverified, DRT-0073 unresolved. See `docs/research/LIMITATIONS.md`.

## Near-term potential (planned)

Broader failure taxonomy; more diagnosis benchmarks; improved evidence correlation; better model evaluation; expanded supported EDA configurations; reproducible benchmark expansion; recovery-quality metrics; improved usability; independent reproduction.

## Long-term research

Evidence-grounded EDA agents; cross-stage failure reasoning; constraint intelligence; physical-design failure knowledge; safe agentic engineering; multi-agent diagnosis with separation of duties; recovery strategy evaluation.

No dates are promised. All future items remain `PLANNED` or research until implemented and validated with evidence.

## Related

`docs/product/VISION.md`, `docs/product/GOALS.md`, `docs/research/HYPOTHESES.md`, `docs/reference/CAPABILITIES.md`.
