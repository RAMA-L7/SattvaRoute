# Glossary — authoritative terminology

Status: authoritative. All SattvaRoute documentation uses these definitions. Related: `docs/product/PRODUCT.md`, `docs/reference/CAPABILITIES.md`.

Where a term has a common industry meaning that differs from SattvaRoute usage, the SattvaRoute meaning is stated explicitly.

## Core objects

| Term | Definition |
|---|---|
| **Baseline** | A clean, previously executed run of the pinned control benchmark used as a reference point. Preserved; never overwritten. See `docs/REPRODUCIBILITY.md`. |
| **Failure** | A run whose observed evidence shows a stage did not complete or whose reports show a target defect. A non-zero process return code alone is not a failure verdict. |
| **Failure mechanism** | The evidence-supported explanation of *why* a failure occurred (e.g. a missing macro Liberty file). Derived from logs, configuration resolution, and artifacts; not from a model guess. |
| **Diagnosis** | The deterministic process that reads run evidence and produces a classification, failure mechanism, evidence references, earliest affected stage, and affected downstream stages. Implemented in `scripts/diagnosis_agent.py`. |
| **Deterministic diagnosis** | Classification derived only from parsed evidence and bounded rules. This is the implemented default. It does not require a model or credentials. |
| **AI/model diagnosis** | Optional advisory note from a configured model provider via `scripts/live_diagnosis.py`. Advisory only; never applies or approves anything. Unavailable without credentials (`SKIPPED_NO_CREDENTIALS`). |
| **Evidence** | Immutable artifacts captured from a run: `evidence/run.json`, `stages.tsv`, `stage_*.log`, `preflight.txt`/`preflight.json`/`preflight_checks.tsv`, `manifest.json`, hashes, approval records, postflight. Missing evidence stays missing. |
| **Evidence reference** | A concrete path to an artifact that supports a diagnosis or verification check. Diagnoses carry `evidence_refs`. |
| **Candidate patch / proposed correction** | A textual, bounded, reviewable change derived from a diagnosis. It is **not applied** by proposal commands. Status `PENDING_HUMAN` until approved. |
| **Approval** | A human-signed record created by `scripts/sattva_approval.py` binding an exact patch hash, target, decision ID, source run ID, rerun scope, and earliest affected stage. |
| **Approved change** | A proposal that has passed explicit human approval and is eligible for application. Approval does not guarantee engineering success. |
| **Recovery attempt / recovery run** | An isolated run that applies an approved change and reruns only the affected stages. Originals and baseline are not modified in place. |
| **Verification** | Independent, report-level checking of a run (`scripts/verify_run.py`). Separate from diagnosis and from recovery execution. |
| **Engineering validation** | Human interpretation of verified reports to decide whether engineering goals (e.g. acceptable timing) are met. A tool PASS is not engineering acceptance. |
| **Recovery verdict** | An engineer's interpretation of a baseline/failure/recovery comparison: fixed, regressed, inconclusive, or blocked. Not an emitted status: `verify_run.py` emits `PASS`/`FAIL`/`UNKNOWN`. Derived from independent verification, not from the recovery process return code. |
| **Fingerprint** | A canonical digest of the resolved, active-profile inputs (dependencies, collateral, tool hashes, ORFS revision and local patches) produced by `scripts/manifest.py`. |
| **Reproducibility** | The goal that a documented run can be recreated from pinned inputs without author-specific paths or untracked files. The published `config.mk` now uses portable defaults (`runs/orfs`, `klayout`) with environment overrides. Not a claim that another engineer has tested it. |
| **Stage** | One step of the ORFS flow: `check-yosys`, `check-openroad`, `synth`, `floorplan`, `place`, `cts`, `route`, `finish`. Stage boundaries and inputs are declared in `state/approval_policy.json`. |
| **Rerun scope** | The set of stages an approved change is permitted to invalidate and rerun, derived from the earliest affected stage. Broad reruns are not permitted. |
| **Profile** | A named dependency scope in `config/sattva_manifest.json`. While `nangate_macro_control` is active, only that profile is checked; other profiles are declared and may be explicitly selected with `--profile`, but they are not validated for the control benchmark. |
| **Control benchmark** | `benchmark/design/nangate_macro_control`: Nangate45 standard cells plus the platform `fakeram45_64x32` abstract macro. The validated scope. |
| **Historical case** | A preserved, unresolved investigation (notably `DRT-0073`/OpenFinRAM). Not reopened or relabeled. |

## Status vocabulary

Result statuses used in reports: `PASS`, `FAIL`, `BLOCKED`, `UNKNOWN`, `INCONCLUSIVE`, `NOT RUN`, `NOT EVALUATED`. Missing data is never converted to `PASS`.

Capability statuses used in `docs/reference/CAPABILITIES.md`: `IMPLEMENTED`, `VALIDATED`, `EXPERIMENTAL`, `PARTIALLY IMPLEMENTED`, `PLANNED`, `BLOCKED`, `NOT IMPLEMENTED`.

## Timing vocabulary

- `report_units` — the OpenROAD timing report declaration of time/capacitance/resistance units; must be read before interpreting bare numbers.
- `time_unit` — Liberty declaration (pinned Nangate45 Liberty uses `1ns`).
- Two SDC files exist: `constraint.sdc` (historical executed 1000 ns, preserved) and `constraint_1ns.sdc` (approved 1 ns correction, active). See `docs/engineering/SDC_TIMING.md`.
- `6_final.spef` — extracted parasitic file used for extracted STA; `updated_clks.sdc` is an intermediate CTS artifact, not the executed final constraint.

## Related

`docs/reference/STATUS_CODES.md`, `docs/reference/CLI.md`, `docs/architecture/`, `docs/security/THREAT_MODEL.md`.
