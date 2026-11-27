# Evidence system

Status: implemented. Source: `scripts/run_baseline_orfs.sh`, `scripts/evidence_package.py`, `scripts/manifest.py`. Canonical diagram: `docs/diagrams/EVIDENCE_LIFECYCLE.md`.

## What is captured

For each run, under the run directory's `evidence/`:

| Artifact | Purpose |
|---|---|
| `run.json` | Run identity, declared stages, environment summary |
| `stages.tsv` | Stage names and return codes |
| `stage_*.log` | Per-stage tool output (the source for log-based diagnosis) |
| `preflight.txt`, `preflight.json`, `preflight_checks.tsv` | Profile-scoped manifest preflight outcome (profile, revision, patches, hashes) |
| `manifest.json` | Resolved active-profile dependency view and canonical fingerprint |
| `mirror.patch` | Declared local patches applied to the pinned ORFS mirror |
| `artifact_sha256.txt` | Hash manifest for selected artifacts |
| `approval_*.json` | Approval records bound to the run |
| `postflight` | Post-execution capture |

The verifier additionally reads work `results/` and `reports/` to check endpoint products and engineering report signals.

## Lifecycle

Capture → fingerprint → store → reference → validate → audit → reproduce.

1. **Capture:** runner writes evidence during execution; logs are not edited after the fact.
2. **Fingerprint:** `manifest.py` produces a canonical digest of resolved active-profile inputs, including tool binary hashes and ORFS revision + declared local patches.
3. **Store:** curated evidence is published; large `*.odb`, `*.gds`, `*.spef`, full `runs/` and `work/` databases are **not** published. Local paths are not public evidence.
4. **Reference:** diagnoses carry `evidence_refs`; verification checks carry `evidence` lists.
5. **Validate:** preflight fails on mismatch; verification fails when evidence is missing.
6. **Audit:** approvals and ledger records are append-only; history is preserved.
7. **Reproduce:** documented commands plus pinned inputs aim at reconstruction without author-specific paths (goal; the published `config.mk` now uses portable defaults with environment overrides, though curated evidence records retain absolute provenance paths).

## Integrity rules

- Missing evidence is never a pass.
- An empty report is clean only when the tool log establishes completion with a zero violation count.
- The last `DRT-0199` count in the routing log is read; intermediate counts and missing report lines are not treated as final.
- Declared expectations (manifest) are kept separate from captured fingerprints (evidence).

## Evaluation bundles

`scripts/evidence_package.py` builds bounded bundles for diagnosis evaluation. Bundles contain the evidence a diagnosis is allowed to see; ground-truth files are kept separate and used only by grading. See `docs/reproducibility/EVALUATION.md`.

## Related

`docs/reference/ARTIFACTS.md`, `docs/security/EVIDENCE_INTEGRITY.md`, `docs/REPRODUCIBILITY.md`.
