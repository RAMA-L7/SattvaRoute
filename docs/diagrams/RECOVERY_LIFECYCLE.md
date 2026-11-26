# Diagram E — Recovery lifecycle

Status: implemented, deterministic and approval-gated. No live-AI recovery.

```mermaid
flowchart TD
    AP["Approved correction"] --> FP["Input fingerprint validation: manifest preflight"]
    FP -->|"mismatch"| STOP["BLOCKED: no attempt"]
    FP -->|"ok"| SS["Stage selection: earliest affected stage + downstream"]
    SS --> ISO["Isolated attempt directory"]
    ISO --> EX["Execution: validate approval, apply exact patch, rerun staged flow"]
    EX --> RC["Result collection: attempt-local evidence"]
    RC --> VF["Independent verification: baseline vs failure vs recovery"]
    VF --> VR["Recovery verdict: fixed / regressed / inconclusive / blocked"]
    VR --> ENG["Engineer engineering validation"]
```

Notes: originals and baseline are preserved; the runner return code is not the verdict. Verified example: `docs/HELDOUT_RECOVERY.md`. See `docs/architecture/RECOVERY.md`, `docs/architecture/VERIFICATION.md`.
