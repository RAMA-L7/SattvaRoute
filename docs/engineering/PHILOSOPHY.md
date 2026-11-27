# Engineering philosophy

Status: authoritative engineering principles. Applied across `docs/architecture/`, `docs/security/`, and `docs/workflow/`.

## 1. Evidence before conclusions

Every diagnosis claim is traceable to concrete evidence (`evidence_refs`). If the evidence is missing, the claim is not made. An error message is treated as a symptom to be traced, not as a root cause by itself.

## 2. Narrow corrective actions

Proposals target one identified mechanism, one variable, and one earliest affected stage. Broad configuration deletion, corner changes, and constraint relaxation are not acceptable bounded corrections. The one SDC change in project history was explicitly approved and preserved alongside the original.

## 3. Preserve original state

Baselines, original collateral, approval records, evaluations, and historical reports are preserved. Recovery happens in an isolated attempt. No history rewrite, no force-push, no deletion of failed experiments.

## 4. Human control

Nothing is applied without explicit human approval of the exact displayed diff. The CLI never manufactures approval. Deterministic tools, optional model reasoning, approval, application, and verification are separate actors.

## 5. Isolation

Recovery does not silently contaminate unrelated runs or source collateral. Profiles are scoped; inactive profiles are not touched. Tool revisions, patches, and collateral are fingerprinted so drift is detected rather than absorbed.

## 6. Independent verification

Diagnosis and verification are separate responsibilities. A recovery is not declared successful by the component that applied it. Report-level verification reads artifacts, not just return codes.

## 7. Honest outcomes

Use `PASS`, `FAIL`, `BLOCKED`, `UNKNOWN`, `INCONCLUSIVE`, `NOT RUN`, `NOT EVALUATED`. Do not convert missing data into success. `rc=0` ≠ engineering pass; flow completion ≠ timing closure ≠ coverage ≠ characterized timing ≠ signoff; router DRC=0 ≠ foundry DRC; timing ≠ functional correctness.

## 8. Reproducibility

Inputs, dependencies, versions, hashes, and run state are recorded wherever the implementation supports it. Declared expectations are separated from captured fingerprints. Avoiding author-specific paths is a **goal**: the published `config.mk` now uses portable defaults and `SATTVA_MIRROR`/`KLAYOUT_CMD` overrides. Curated evidence records may still contain absolute provenance paths; those identify the executed run, not required local setup. Avoid reliance on untracked files.

## Related

`docs/product/NAMING.md`, `docs/product/NON_GOALS.md`, `docs/security/SAFETY.md`.
