# Patch validation

Status: implemented. Sources: `scripts/diagnosis_agent.py` (proposal), `scripts/sattva_approval.py` (validation/apply), `state/approval_policy.json` (bounds), `config/remedy_budgets.json` (budgets).

## Boundaries on a proposal

A bounded correction must satisfy all of the following:

- **Targeted:** one target file and one variable/parameter where applicable; no broad deletion or rewrite.
- **Evidence-bound:** tied to a diagnosis mechanism with concrete `evidence_refs`.
- **Staged:** declares `earliest_affected_stage` and `downstream_invalidation` derived from `stage_inputs`.
- **Reviewable:** carries exact diff, current resolved value, intended value, original hash, patch hash, expected effect, risks, and verification criteria.
- **Non-fabricating:** never invents collateral; insufficient evidence yields `NO_PROPOSAL` / `insufficient_evidence`.
- **Non-relaxing:** does not silently change constraints or technology rules. The one SDC change (`constraint_1ns.sdc`) was explicitly approved and applied with the original preserved.

## Validation gates before application

1. Proposal is displayed via `approve-view`; human reviews exact diff.
2. Human creates approval with explicit IDs and approver identity.
3. `sattva_approval.py validate` checks patch hash, policy, allowed root, design root, run/decision IDs, and (where used) expiry and expected final hash.
4. Only then does `resume` call the runner with the approved patch; apply writes evidence to the attempt's evidence directory.

## Recovery controller

`scripts/remedy_engine.py rank` ranks candidate remedies from a JSON file against KB records (`knowledge/kb_records.jsonl`) using `--signature-hint` and budgets (`config/remedy_budgets.json`). `scripts/remedy_kb.py` maintains an append-only, verifiable ledger (`init`, `append`, `verify`, `retrieve`, `refuted`). Ranking informs review; it does not authorize application.

## Limitations

- No static proof that a patch is functionally correct.
- No guarantee a patch generalizes beyond the bounded profile.
- Hash binding protects integrity of the exact patch, not its engineering correctness.
- Model-generated patches are advisory; a human must still approve. See `docs/security/INPUT_AND_AI_RISKS.md`.

## Related

`docs/architecture/APPROVAL.md`, `docs/security/SAFETY.md`, `docs/reference/CAPABILITIES.md`.
