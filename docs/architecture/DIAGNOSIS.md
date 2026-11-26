# Diagnosis engine

Status: implemented (deterministic); optional model note is advisory. Source: `scripts/diagnosis_agent.py`. Canonical diagram: `docs/diagrams/DIAGNOSIS_LIFECYCLE.md`.

## Inputs

A run directory containing `evidence/`: `stages.tsv`, `stage_*.log`, `run.json`, configuration resolution data, and preflight/manifest records. Diagnosis reads logs and resolved configuration; it does not rerun the flow.

## Classification

The engine maps observed patterns to a bounded family set, including:

`MISSING_LIB`, `MISSING_LEF`, `MISSING_TECH_LEF`, `MISSING_SC_LIB`, `MISSING_SC_LEF`, `MISSING_CONSTRAINT`, `MISSING_NETLIST`, `UNKNOWN_LIB_CELL`, `PIN_ACCESS`, `INSUFFICIENT_EVIDENCE`.

Log patterns include `No rule to make target`, `No such file or directory`, `cannot/can't/unable to open`, `not found`, `does not exist`, `DRT-\d+`, `not found in library`, `No access point`, and generic `ERROR`. Configuration variables are grouped as library vars (`ADDITIONAL_LIBS`, `ADDITIONAL_LIB`, `SC_LIB`, `MACRO_LIB`, `LIB_FILES`), LEF vars (`ADDITIONAL_LEFS`, `ADDITIONAL_LEF`, `SC_LEF`, `TECH_LEF`, `MACRO_LEF`), SDC vars (`SDC_FILE`), and netlist vars (`VERILOG_FILES`, `SYNTH_NETLIST_FILES`, `VERILOG_FILES_BLACKBOX`). Make constructs (`$(shell …)`, unresolved `$(VAR)`, conditionals) are recognized so an overridden value is not mistaken for an absolute one.

## Output

A diagnosis record contains: `family`, `mechanism`, `evidence_refs`, earliest affected stage, downstream invalidation, resolved/intended values where applicable, and a status. When evidence is insufficient the status is `insufficient_evidence`, not a guessed cause.

## Evidence binding

Every diagnosis claim that can be bound is tied to a concrete path (`evidence/stages.tsv`, `evidence/run.json`, specific stage logs). This is what makes the diagnosis auditable and reviewable: a reviewer can open the referenced file and check the claim.

## Proposal generation

`propose` converts a diagnosis into a bounded patch only when a rule applies. The proposal includes exact diff, current resolved value, intended value, original hash, patch hash, earliest affected stage, downstream invalidation, risks, expected effect, and verification criteria. It sets `approval_status: PENDING_HUMAN`. If no bounded rule applies, it returns `NO_PROPOSAL` (`exit 1`) — it does not invent collateral or relax constraints.

## Model-generated narrative (optional, advisory)

`live-diagnose` calls a configured model provider through `scripts/live_diagnosis.py`. The result is advisory: no patch application, approval, or execution. With no configured credentials the tool reports `SKIPPED_NO_CREDENTIALS` / `BLOCKED`. Deterministic results never depend on a live model. See `docs/security/INPUT_AND_AI_RISKS.md`.

## What the engine does not claim

- Not a general AI engineer; no cross-design generalization claim.
- No functional-correctness inference from timing results.
- No signoff inference from router DRC=0.
- No quantified accuracy gain.

## Related

`docs/engineering/FAILURE_TAXONOMY.md`, `docs/architecture/EVIDENCE.md`, `docs/research/LIMITATIONS.md`.
