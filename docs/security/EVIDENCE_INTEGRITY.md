# Evidence integrity

Status: describes implemented integrity behavior and documented rules. See `docs/architecture/EVIDENCE.md`, `docs/security/THREAT_MODEL.md`.

## Integrity properties

- **Immutability by practice** — run logs are captured during execution and not edited afterward; historical reports in `docs/` are preserved and not relabeled.
- **Fingerprints** — `manifest.py` produces a canonical digest of the resolved active-profile inputs; declared expectations are separated from captured fingerprints.
- **Hash manifests** — selected artifacts are hashed (`artifact_sha256.txt`); approval binds patch and original target hashes.
- **Append-only records** — `state/approval_ledger.jsonl` and remedy/KB ledgers are appended, not rewritten.
- **Bound references** — diagnosis and verification checks carry concrete evidence paths.

## Rules that prevent false success

1. Missing evidence is never `PASS`.
2. Empty report is clean only if the tool log shows completion with a zero violation count.
3. The **last** DRT-0199 count is authoritative; intermediate counts are not.
4. `rc=0` is not engineering acceptance.
5. Two identically incomplete runs both fail.
6. Recovery regressions are flagged against the baseline; a successful apply is not a fix.

## Publication integrity

- Curated evidence (summaries, logs excerpts, hashes) is published under `evidence/` and `docs/`.
- Large `*.odb`, `*.gds`, `*.spef`, full `runs/` and `work/` databases are not published.
- Local machine paths are not public evidence.
- No historical result, evaluation score, approval record, or Git history was changed in this documentation milestone.

## Limitations

Integrity relies on local filesystem permissions and process behavior, not cryptographic signing or a tamper-proof store. Publish-time review of staged diffs remains necessary.

## Related

`docs/reference/ARTIFACTS.md`, `docs/REPRODUCIBILITY.md`, `docs/architecture/VERIFICATION.md`, `docs/audit/SCOPE_INTEGRITY.md`.
