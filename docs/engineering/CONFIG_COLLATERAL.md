# Configuration and collateral analysis

Status: describes the implemented profile-scoped analysis. See `config/sattva_manifest.json`, `state/approval_policy.json`, `docs/REPRODUCIBILITY.md`.

## Effective configuration

SattvaRoute resolves configuration rather than trusting declarations. `scripts/diagnosis_agent.py` recognizes:

- multiline declarations and multiple library paths,
- attempt-local overrides (e.g. `failure-demo` config),
- `$(…)` constructs; `$(shell …)`, `$(call …)`, conditionals and unresolved variables are flagged as ambiguous,
- variable groups: library (`ADDITIONAL_LIBS`, `ADDITIONAL_LIB`, `SC_LIB`, `MACRO_LIB`, `LIB_FILES`), LEF (`ADDITIONAL_LEFS`, `ADDITIONAL_LEF`, `SC_LEF`, `TECH_LEF`, `MACRO_LEF`), SDC (`SDC_FILE`), netlist (`VERILOG_FILES`, `SYNTH_NETLIST_FILES`, `VERILOG_FILES_BLACKBOX`).

A missing-file error is matched against resolved paths, so an override in an attempt-local config is attributed correctly and the original control config is not blamed.

## Profiles

| Profile | Status | Meaning |
|---|---|---|
| `nangate_macro_control` | Active / validated | Nangate45 + platform `fakeram45_64x32` abstract macro; prepared netlist; 1 ns SDC |
| `riscv32i_sattva` | `FEASIBILITY_FAILED_YOSYS_ASAP7` | Inactive; ASAP7 feasibility profile |
| `sattva_sram` | `UNRESOLVED_DRT0073_PRESERVED` | Inactive; historical ASAP7 SRAM regression; not reopened |

Only the active profile is checked during the control-benchmark flow. Other profiles are declared and can be explicitly selected with `--profile` (the runner has branches for them), but they are not validated for the control benchmark and were not modified in this milestone.

## Collateral (pinned, external, not redistributed)

`config/sattva_manifest.json` pins SHA-256 hashes for the Nangate45 platform: `config.mk`, tech/macro LEF, standard-cell LEF, typical Liberty, `fakeram45_64x32.lib`, `rcx_patterns.rules`, `setRC.tcl`. The manifest also pins ORFS revision `25b6429c…` and two local patches (global_route.tcl DRT-0305 special-net gate; synth_stdcells.tcl Yosys compat gate), plus tool binary hashes for OpenROAD and Yosys.

`manifest.py --check --profile nangate_macro_control` fails on mismatch. Preflight, approval validation, resume, and evidence packaging consume the same resolved view.

## Rules for corrections

- Never substitute a different corner or technology to make a failure disappear.
- Never invent a library/macro file; insufficient evidence → `insufficient_evidence`.
- Never silence a rule or relax a constraint as a "fix".
- Preserve originals; any approved change is a separate file/patch with recorded hashes.

## Related

`docs/engineering/MACRO_PIN_ACCESS.md`, `docs/engineering/SDC_TIMING.md`, `docs/governance/THIRD_PARTY.md`.
