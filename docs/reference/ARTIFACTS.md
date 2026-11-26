# Artifact reference

Status: describes artifacts actually produced/consumed. See `docs/architecture/EVIDENCE.md`, `docs/architecture/DATA_MODEL.md`.

## Run evidence (`<run>/evidence/`)

| Artifact | Content |
|---|---|
| `run.json` | Run identity, declared stages, summary |
| `stages.tsv` | Stage names + return codes |
| `stage_*.log` | Per-stage tool output (diagnosis source) |
| `preflight.txt`, `preflight.json`, `preflight_checks.tsv` | Profile-scoped preflight result |
| `manifest.json` | Resolved dependency view + canonical fingerprint |
| `mirror.patch` | Declared ORFS local patches |
| `artifact_sha256.txt` | Hash manifest for selected artifacts |
| `approval_*.json`, `approval_apply.json`, `approval_guard.json` | Approval records and apply/guard evidence |
| `postflight` | Post-execution capture |

## Work outputs (`<run>/work/`)

`results/` endpoint products: `5_route.odb`, `route.guide`, `6_final.odb`, `6_final.spef`, `6_final.def`, `6_final.gds`, `6_final.v`, `6_final.sdc`. `reports/`: `6_finish.rpt`, `5_route_drc.rpt` and stage reports. Full databases are not published.

## Project-owned benchmark files

`benchmark/design/nangate_macro_control/`: `config.mk`, `constraint.sdc` (historical 1000 ns, preserved), `constraint_1ns.sdc` (approved, active), `rtl/sattva_macro_top.v`, `rtl/fakeram45_64x32_bb.v`, `netlist/sattva_macro_top_synth.v`, `netlist/synth_provenance.txt`.

## Config / policy / records

`config/sattva_manifest.json`, `config/remedy_budgets.json`, `state/approval_policy.json`, `state/approval_ledger.jsonl`, `knowledge/kb_records.jsonl`, `knowledge/remedy_ledger.jsonl`.

## Curated evidence

`evidence/timing/`, `evidence/verification/`, `docs/` reports, `docs/REPORT_INDEX.md`. No bulk `.odb`/`.gds`/`.spef`/`runs/` in publication.

## Interpretation rules

- Paths in diagnosis/verification records are concrete; open them to check claims.
- Missing artifact → `FAIL`/`UNKNOWN`, never `PASS`.
- Do not treat local development paths as public evidence.
- Do not modify or relabel historical artifacts.

## Related

`docs/reference/CLI.md`, `docs/security/EVIDENCE_INTEGRITY.md`, `docs/REPRODUCIBILITY.md`.
