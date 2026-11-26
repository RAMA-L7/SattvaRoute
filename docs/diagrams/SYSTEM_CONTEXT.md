# Diagram A — System context

Status: implemented context. Optional model path is shown dashed; no live-AI recovery.

```mermaid
flowchart TB
    ENG["Engineer"]
    subgraph SR["SattvaRoute"]
        CLI["pnr_cli.py"]
        DIAG["Deterministic diagnosis"]
        APR["Human approval gate"]
        VER["Independent verifier"]
    end
    EDA["EDA flow: ORFS + OpenROAD / Yosys"]
    EV[("Evidence: logs, reports, hashes")]
    AI["Optional model provider (advisory only)"]
    ISO["Isolated recovery attempt"]

    ENG -->|"commands and approval"| CLI
    CLI <-->|"stage execution"| EDA
    EDA --> EV
    EV --> DIAG
    DIAG -->|"bounded proposal"| APR
    ENG -->|"explicit approval"| APR
    APR -->|"approved exact patch"| ISO
    ISO -->|"stage-limited rerun"| EDA
    EV --> VER
    ISO --> VER
    VER -->|"report-level verdict"| ENG
    AI -.->|"optional advisory note"| DIAG
    AI -.->|"no apply, no approval"| CLI
```

Notes: AI never controls the flow directly. Approval is a human boundary. Verification reads evidence and attempts but applies nothing. See `docs/reference/GLOSSARY.md`, `docs/security/TRUST_BOUNDARIES.md`.
