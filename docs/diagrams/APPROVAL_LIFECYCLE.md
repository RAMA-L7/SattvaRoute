# Diagram D — Approval lifecycle

Status: implemented. Expiration is optional (`--expires-at`), shown as optional.

```mermaid
flowchart TD
    PP["Proposed correction: exact diff"] --> RV["Scope + hashes + risk review"]
    RV --> HU{"Human decision"}
    HU -->|"approve"| AC["Approval record: IDs, patch sha256, target, earliest stage, rerun scope, approver"]
    HU -->|"reject"| RJ["REJECTED: cannot validate or apply"]
    AC --> EX{"Expired or reused?"}
    EX -->|"yes"| INV["Invalid: blocked by expiry / ledger"]
    EX -->|"no"| VD["validate: hash, path, scope, fingerprint, IDs"]
    VD -->|"pass"| RDY["Ready for apply"]
    VD -->|"fail"| BLK["FAIL: no apply"]
```

Notes: the CLI never manufactures an approval. Ledger is append-only; `validate` rejects reuse and unsafe scope. See `docs/architecture/APPROVAL.md`, `docs/security/SAFETY.md`.
