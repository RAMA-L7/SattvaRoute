# Diagram F — Evidence lifecycle

Status: implemented capture/fingerprint/reference/validation; audit and reproducibility are documented properties.

```mermaid
flowchart LR
    CAP["Capture: runner logs + artifacts"] --> FP["Fingerprint: manifest v2 canonical digest"]
    FP --> ST["Store: curated evidence + hashes"]
    ST --> REF["Reference: evidence_refs in diagnosis and checks"]
    REF --> VAL["Validate: preflight + verify_run fail-closed"]
    VAL --> AUD["Audit: append-only approval + knowledge ledgers"]
    AUD --> REP["Reproduce: pinned inputs, no author paths"]
    REP --> CAP
```

Notes: missing evidence is never a pass; declared expectations are separate from captured fingerprints. Bulk databases are not published; local paths are not public evidence. See `docs/architecture/EVIDENCE.md`, `docs/security/EVIDENCE_INTEGRITY.md`.
