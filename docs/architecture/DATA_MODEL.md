# Data model and artifacts

Status: describes artifacts actually produced/consumed. See `docs/reference/ARTIFACTS.md` for the compact reference.

## Configuration and policy inputs

| Path | Role |
|---|---|
| `config/sattva_manifest.json` | Manifest v2: profiles, pinned ORFS revision/local patches, collateral hashes, tool hashes, recovery/CLI references |
| `state/approval_policy.json` | Approval policy: allowed roots, stages, stage inputs, ledger, recovery profiles |
| `config/remedy_budgets.json` | Recovery candidate budgets |
| `benchmark/design/nangate_macro_control/config.mk` | Active design config; `SDC_FILE` → `constraint_1ns.sdc` |
| `benchmark/design/nangate_macro_control/constraint_1ns.sdc` | Approved 1 ns constraint (active) |
| `benchmark/design/nangate_macro_control/constraint.sdc` | Historical 1000 ns constraint (preserved, not active) |
| RTL + prepared netlist + provenance | `rtl/sattva_macro_top.v`, `rtl/fakeram45_64x32_bb.v`, `netlist/sattva_macro_top_synth.v`, `netlist/synth_provenance.txt` |

## Run artifacts

Per run: `evidence/` (run.json, stages.tsv, stage logs, preflight, manifest.json, mirror.patch, artifact hashes, approval records, postflight) and `work/results/`, `work/reports/`. Full databases are not published; curated summaries and hashes are.

## Records

- **Diagnosis record:** family, mechanism, evidence_refs, earliest affected stage, downstream invalidation, status.
- **Proposal record:** exact diff, target, variable, current/intended resolved values, original/patch hashes, risks, verification criteria, `approval_status: PENDING_HUMAN`.
- **Approval record:** approval/decision/source-run IDs, patch hash, target, earliest stage, rerun scope, approver, status, optional expiry/expected-final-hash. Written through the approval service; appended to `state/approval_ledger.jsonl`.
- **Fingerprint:** canonical manifest digest of resolved active-profile inputs.
- **Verification record:** named checks with status, detail, evidence paths.
- **Knowledge records:** `knowledge/kb_records.jsonl` and remedy ledger — immutable/append-only, verifiable.

## Naming conventions

Run tags: `control_*` (baseline), `failure_*` (fixture), `recovered_*` (recovery). Historical run IDs are preserved verbatim; do not rename to imply a different verdict. Timestamps are UTC (`…Z`).

## Related

`docs/engineering/PHYSICAL_DESIGN.md`, `docs/REPRODUCIBILITY.md`, `docs/reference/GLOSSARY.md`.
