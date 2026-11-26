# Product value

No quantified productivity, cost, or accuracy gains are claimed. Value is described in terms of engineering properties, not measured outcomes.

## Value to a physical-design engineer

- **Traceability:** diagnosis claims carry concrete `evidence_refs`; missing evidence is reported as missing.
- **Bounded change:** proposals target one variable and one earliest affected stage, with exact diff, hashes, risks, and verification criteria.
- **Safety:** nothing is applied without explicit human approval of the displayed exact diff.
- **Reduced guesswork:** timing-unit, collateral, and stage-propagation facts are derived from tool evidence rather than assumed.

## Value to an implementation / CAD team

- **Reproducibility:** manifest v2 pins ORFS revision, two local patches, tool hashes, collateral hashes, and the resolved active profile.
- **Integrity:** approval validation binds patch hash, decision ID, source run, and rerun scope; ledger records are append-only.
- **Drift control:** preflight fails on mismatched revision, patch set, or hashes instead of silently proceeding.

## Value to researchers

- **Controlled conditions:** frozen evaluation rubric (`evaluate_diagnosis_v2.py`), held-out bundles, preserved history.
- **Honest baselines:** deterministic classification separated from optional model output; live-AI absence explicit.
- **Reusable artifacts:** reproducible control benchmark and curated evidence without bulk run databases.

## Value to an organization

- **Auditability:** a recovery can be reconstructed from approval records, manifests, evidence, and independent verification.
- **Safer automation:** isolation, stage-limited rerun, and independent verification constrain what automation can change.

## What value is not claimed

Not "faster debugging by X%", not "higher accuracy than engineers", not "autonomous recovery", not "signoff". See `docs/product/NON_GOALS.md`, `docs/research/LIMITATIONS.md`.
