# Architecture overview

Status: describes the **implemented** system. Planned extensions are only in `docs/research/`. Canonical diagram: `docs/diagrams/SYSTEM_ARCHITECTURE.md`; context: `docs/diagrams/SYSTEM_CONTEXT.md`.

## Architectural statement

SattvaRoute does not implement synthesis, placement, CTS, routing, extraction, or STA. It **orchestrates an existing OpenROAD Flow Scripts (ORFS) flow**, captures evidence, diagnoses failures deterministically, gates changes behind human approval, applies them in an isolated attempt, and verifies the result independently. Python controls stage execution; OpenROAD executes; parsers read reports; an optional model provider may add advisory narrative.

Two properties are enforced structurally:

1. **Separation of responsibilities** — diagnose, propose, approve, apply, execute, verify are distinct commands/modules. No single component both proposes and approves a change.
2. **Evidence over exit codes** — a process return code is recorded but never treated as engineering success. Verification reads reports.

## Components

| Component | File | Responsibility |
|---|---|---|
| Entry CLI | `scripts/pnr_cli.py` | `status`, `baseline`, `failure-demo`, `diagnose`, `live-diagnose`, `propose`, `approve-view`, `resume` |
| Runner | `scripts/run_baseline_orfs.sh` | Preflight, stage execution, evidence capture, optional approved apply, postflight |
| Manifest / fingerprint | `scripts/manifest.py` | Profile resolution, revision + patch + hash checks, canonical fingerprint |
| Diagnosis | `scripts/diagnosis_agent.py` | Classification, mechanism, evidence refs, earliest affected stage, bounded proposal |
| Approval service | `scripts/sattva_approval.py` | `create`, `validate`, `apply`, `guard`, `check-source-artifacts`; append-only ledger |
| Recovery controller / KB | `scripts/remedy_engine.py`, `scripts/remedy_kb.py`, `config/remedy_budgets.json` | Candidate ranking, budget bounds, remedy ledger |
| Verifier | `scripts/verify_run.py` | Independent report-level checks for execution, artifacts, engineering signals, evidence, recovery |
| Timing audit | `scripts/timing_audit.py` | Read-only `report_units`/Liberty/SDC reconciliation |
| Diagnosis evaluation | `scripts/evaluate_diagnosis.py`, `scripts/evaluate_diagnosis_v2.py` | Deterministic grading; frozen v2 rubric |
| Optional model client | `scripts/live_diagnosis.py` | Bounded advisory call; never applies or approves |
| Evidence packaging | `scripts/evidence_package.py` | Bundles for evaluation |
| Knowledge base | `scripts/sattva_kb.py` | Immutable, verifiable investigation records |
| Policy / manifest | `state/approval_policy.json`, `config/sattva_manifest.json` | Allowed roots, stage inputs, pinned dependencies |

## Data flow (summary)

```
config/manifest + pinned ORFS ──> runner preflight ──> stage execution ──> evidence/
                                        │                                    │
                                        └──> diagnosis ──> proposal ──> human approval
                                                                          │
evidence/ ──> independent verify <── isolated recovery attempt <──────────┘
```

See `docs/architecture/LIFECYCLE.md` and `docs/workflow/WORKFLOW.md` for the full sequence.

## Boundaries

- **Approval boundary:** no patch is applied unless `sattva_approval.py validate` passes against the exact patch hash, policy, design root, run ID, and decision ID.
- **Isolation boundary:** recovery runs in a separate attempt directory; originals and baseline are preserved.
- **Profile boundary:** only the active manifest profile is checked; other profiles are declared and can be explicitly selected with `--profile`, but are not validated for the control benchmark.
- **Verification boundary:** verification never modifies the run it inspects.

## Related

`docs/architecture/DIAGNOSIS.md`, `EVIDENCE.md`, `APPROVAL.md`, `RECOVERY.md`, `VERIFICATION.md`, `docs/reference/CAPABILITIES.md`.
