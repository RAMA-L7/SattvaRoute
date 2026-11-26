# Documentation index

Status: entry point for all current documentation. Historical engineering reports remain in `docs/` and are indexed in `docs/REPORT_INDEX.md`; they are preserved, not rewritten. Start at `README.md` for the short product introduction.

## 1. Product identity — `docs/product/`

| Document | Purpose |
|---|---|
| `PRODUCT.md` | **Authoritative** product definition (other docs link here) |
| `PROBLEM.md` | Engineering problem statement |
| `MISSION.md` | Mission |
| `VISION.md` | Long-term vision (research direction separated) |
| `GOALS.md` | Engineering / product / research / safety / reproducibility / usability goals |
| `NON_GOALS.md` | Explicit boundaries and non-claims |
| `USERS.md` | Target users and beneficiaries |
| `USE_CASES.md` | Implemented use cases and non-use cases |
| `VALUE.md` | Value proposition without quantified claims |
| `NAMING.md` | SattvaRoute name and identity rationale |

## 2. Architecture — `docs/architecture/`

| Document | Purpose |
|---|---|
| `ARCHITECTURE.md` | Components, data flow, boundaries |
| `LIFECYCLE.md` | Stage model, baseline/failure/recovery lifecycles |
| `DIAGNOSIS.md` | Diagnosis engine and bounded proposal generation |
| `EVIDENCE.md` | Evidence capture, fingerprinting, storage, references |
| `APPROVAL.md` | Human approval boundary and commands |
| `PATCH_VALIDATION.md` | Bounded corrections and validation gates |
| `RECOVERY.md` | Isolated, approval-gated, stage-limited recovery |
| `VERIFICATION.md` | Independent report-level verification |
| `DATA_MODEL.md` | Artifacts and record types |
| `FAILURE_STATES.md` | Failure-state handling |

## 3. VLSI engineering — `docs/engineering/`

| Document | Purpose |
|---|---|
| `PHYSICAL_DESIGN.md` | Flow context; what SattvaRoute reads vs implements |
| `FAILURE_TAXONOMY.md` | Implemented failure families and cross-cutting mechanisms |
| `SDC_TIMING.md` | Units, 1000 ns → 1 ns correction, final vs intermediate SDC |
| `CONFIG_COLLATERAL.md` | Effective config, profiles, pinned collateral |
| `MACRO_PIN_ACCESS.md` | Macro views, pin-access evidence, DRT-0305 note |
| `PLACE_ROUTE_EXTRACTION.md` | Placement/CTS/routing/extraction/timing evidence |
| `VERIFICATION_BOUNDARIES.md` | What PASS does and does not mean |
| `PHILOSOPHY.md` | Engineering principles |

## 4. Workflow — `docs/workflow/`

| Document | Purpose |
|---|---|
| `GETTING_STARTED.md` | Prerequisites, pinned setup, first baseline |
| `WORKFLOW.md` | End-to-end implemented sequence |
| `TROUBLESHOOTING.md` | Failure handling |

Artifact reference is the single source at `docs/reference/ARTIFACTS.md`.

## 5. Security / safety — `docs/security/`

| Document | Purpose |
|---|---|
| `THREAT_MODEL.md` | Threat register with verified controls and gaps |
| `TRUST_BOUNDARIES.md` | Boundaries and data trust levels |
| `SAFETY.md` | Safety principles, approval model, patch policy |
| `INPUT_AND_AI_RISKS.md` | Input handling, prompt injection, credentials |
| `EVIDENCE_INTEGRITY.md` | Integrity rules and publication boundaries |

## 6. Reproducibility — `docs/reproducibility/`

| Document | Purpose |
|---|---|
| `REPRODUCIBILITY_MODEL.md` | Manifest v2, fingerprinting, baseline preservation |
| `BENCHMARK.md` | Control benchmark methodology |
| `EVALUATION.md` | Diagnosis/recovery evaluation methodology |
| `docs/REPRODUCIBILITY.md` | **Authoritative** pinned facts, commands, validation status |
| `docs/HELDOUT_RECOVERY.md`, `docs/TIMING_AUDIT.md` | Key evidence records |

## 7. Reference — `docs/reference/`

| Document | Purpose |
|---|---|
| `GLOSSARY.md` | **Authoritative** terminology |
| `CAPABILITIES.md` | **Authoritative** capability/evidence matrix |
| `CLI.md` | Verified command reference |
| `CONFIGURATION.md` | Verified env vars, manifest, policy keys |
| `STATUS_CODES.md` | Status vocabulary and verdicts |
| `ARTIFACTS.md` | Artifact reference |
| `FAILURE_CLASSIFICATIONS.md` | Compact classification codes |
| `FAQ.md` | Common questions |

## 8. Governance — `docs/governance/`

| Document | Purpose |
|---|---|
| `GOVERNANCE.md` | Decision authority and coordination |
| `LICENSING.md` | License scope and recommendation |
| `THIRD_PARTY.md` | Attribution / dependency inventory |
| `DECISIONS.md` | Pointer to decision records |
| `RELEASE.md` | Release/publication policy |

Root: `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`, `CITATION.cff`, `AGENTS.md`, `PROJECT_STATE.md`.

## 9. Research — `docs/research/`

| Document | Purpose |
|---|---|
| `ROADMAP.md` | Completed / current / gaps / planned / long-term |
| `LIMITATIONS.md` | Authoritative limitations |
| `HYPOTHESES.md` | Research hypotheses and open problems |

## 10. Diagrams — `docs/diagrams/`

`SYSTEM_CONTEXT.md`, `SYSTEM_ARCHITECTURE.md`, `DIAGNOSIS_LIFECYCLE.md`, `APPROVAL_LIFECYCLE.md`, `RECOVERY_LIFECYCLE.md`, `EVIDENCE_LIFECYCLE.md`.

## 11. Audit / coordination — `docs/audit/`, `coordination/`

`docs/audit/SKILLS_USED.md`, `DOC_AUDIT.md`, `CLAIM_EVIDENCE.md`, `QA_FINAL.md`, `SCOPE_INTEGRITY.md`; `coordination/DOC_OVERHAUL_PLAN.md`, `TASK_BOARD.md`, `ACTIVE_WORK.md`.

## 12. Historical material (preserved)

`docs/REPORT_INDEX.md` indexes all historical engineering reports (`ENG*`, `FDE-*`, `WF-*`, `T1-*`, `T-SKILL-*`, investigations, benchmark prep, decisions). Superseded current-looking notes are marked at the top of `docs/architecture.md`, `docs/workflow.md`, `docs/recovery.md` and retained verbatim. No historical result was changed.

## Reading paths

- **New engineer:** README → `docs/product/PRODUCT.md` → `docs/workflow/GETTING_STARTED.md` → `docs/workflow/WORKFLOW.md`.
- **VLSI reviewer:** `docs/engineering/PHYSICAL_DESIGN.md` → `docs/architecture/` → `docs/engineering/VERIFICATION_BOUNDARIES.md`.
- **Security reviewer:** `docs/security/` → `docs/governance/` → `docs/audit/`.
- **Researcher:** `docs/reproducibility/` → `docs/research/` → `docs/REPORT_INDEX.md`.
