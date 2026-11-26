# Diagram C — Failure diagnosis lifecycle

Status: implemented deterministic lifecycle.

```mermaid
flowchart TD
    F["Failed run"] --> EC["Evidence capture: run.json, stages.tsv, logs"]
    EC --> ART["Artifact inspection: resolved config + reports"]
    ART --> FC["Failure classification: bounded family set"]
    FC --> RCA["Root-cause analysis: evidence-supported mechanism"]
    RCA --> EB["Evidence binding: evidence_refs + earliest stage"]
    EB --> S{"Bounded rule applies?"}
    S -->|"yes"| CP["Candidate correction: exact diff, hashes, risks"]
    S -->|"no"| IE["insufficient_evidence / NO_PROPOSAL"]
    CP --> VAL["Validation: reviewable proposal, PENDING_HUMAN"]
    VAL --> APR["Human approval gate"]
```

Notes: an error message is a symptom, not a root cause. Missing evidence stays missing. A right-hand branch must not become a guessed fix. See `docs/architecture/DIAGNOSIS.md`, `docs/engineering/FAILURE_TAXONOMY.md`.
