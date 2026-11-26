# Diagram B — System architecture

Status: implemented components. Source files are named in `docs/architecture/ARCHITECTURE.md`.

```mermaid
flowchart LR
    subgraph IN["Inputs"]
        CFG["Manifest v2 + policy"]
        BN["Control benchmark design"]
        ORFS["Pinned ORFS + local patches"]
        TOOLS["Pinned OpenROAD / Yosys"]
    end
    subgraph CORE["SattvaRoute components"]
        RUN["Runner: run_baseline_orfs.sh"]
        MAN["Manifest / fingerprint"]
        CLI["pnr_cli.py"]
        DX["diagnosis_agent.py"]
        AP["sattva_approval.py"]
        RC["remedy_engine + remedy_kb"]
        VF["verify_run.py"]
        TA["timing_audit.py"]
        EVF["evaluate_diagnosis_v2.py"]
        MD["live_diagnosis.py (optional)"]
    end
    subgraph OUT["Outputs"]
        EV[("Run evidence")]
        DR["Diagnosis + proposal"]
        APV["Approval + ledger"]
        RA["Isolated recovery attempt"]
        VD["Verification verdict"]
    end

    CFG --> MAN
    BN --> RUN
    ORFS --> RUN
    TOOLS --> RUN
    MAN -->|"preflight"| RUN
    CLI --> RUN
    RUN --> EV
    EV --> DX
    DX --> DR
    DR --> CLI
    CLI --> APV
    AP --> APV
    APV -->|"validate"| RA
    RC -->|"ranking"| DR
    RA --> RUN
    EV --> VF
    RA --> VF
    VF --> VD
    EV --> TA
    EV --> EVF
    MD -.->|"advisory"| DR
```

Notes: propose, approve, apply, execute, verify are distinct components. No component both proposes and approves. See `docs/architecture/ARCHITECTURE.md`, `docs/reference/CAPABILITIES.md`.
