# Failure classifications (reference)

Status: compact reference. Detail: `docs/engineering/FAILURE_TAXONOMY.md`, `docs/architecture/DIAGNOSIS.md`.

## Implemented families

| Code | Meaning | Typical evidence |
|---|---|---|
| `MISSING_MACRO_LIB` | Missing Liberty file | `No rule to make target … .lib`; resolved lib variable; also `not found in library` |
| `MISSING_MACRO_LEF` | Missing LEF file | Missing `.lef` target; `ADDITIONAL_LEFS`/`SC_LEF`/`MACRO_LEF` |
| `MISSING_TECH_LEF` | Missing technology LEF | Missing tech LEF target |
| `MISSING_SC_LIB` | Missing standard-cell Liberty | Missing SC lib target |
| `MISSING_SC_LEF` | Missing standard-cell LEF | Missing SC LEF target |
| `MISSING_CONSTRAINT` | Missing SDC | Missing `SDC_FILE` target |
| `MISSING_NETLIST` | Missing netlist | Missing netlist/verilog target |
| `UNKNOWN` | No bounded rule matched | Classifier fallback |
| `PIN_ACCESS` | Macro pin unreachable | `No access point` or `DRT-0073`; LEF/Liberty pin geometry is supporting evidence, not a DRT-code blanket rule |
| `insufficient_evidence` | No bounded correction rule applies | Proposal status; abstain, do not guess |

Log patterns include `No rule to make target`, `No such file or directory`, `cannot/can't/unable to open`, `not found`, `does not exist`, `DRT-\d+`, `not found in library`, `No access point`, `ERROR`.

## Classification rules

- Bind to `evidence_refs`; declare earliest affected stage and downstream invalidation.
- Symptom ≠ cause; no root-cause claim from a single message.
- Conflicting/insufficient evidence → `INCONCLUSIVE` / `insufficient_evidence`.
- No invented collateral, no constraint relaxation, no corner substitution.

## Historical cases

DRT-0073/OpenFinRAM: `UNRESOLVED_DRT0073_PRESERVED`, excluded, not reopened. DRT-0305: historical investigation; declared local patch in manifest. Detailed historical verdicts are in `docs/` and indexed in `docs/REPORT_INDEX.md`; do not relabel.

## Related

`docs/engineering/FAILURE_TAXONOMY.md`, `docs/reference/STATUS_CODES.md`, `docs/workflow/TROUBLESHOOTING.md`.
