# Configuration reference

Status: verified against `config/sattva_manifest.json`, `state/approval_policy.json`, `config/remedy_budgets.json`, and the runner/CLI source.

## Environment variables

| Variable | Meaning | Source |
|---|---|---|
| `SATTVA_ROOT` | Project root | manifest `project_root_env`; pnr_cli |
| `SATTVA_MIRROR` | ORFS checkout root | manifest `orfs.root_env` |
| `SATTVA_DESIGN` | Design directory | runner via pnr_cli |
| `SATTVA_DESIGN_PROFILE` | Active manifest profile | runner via pnr_cli |
| `OPENROAD_EXE` | OpenROAD binary override | manifest `tools.openroad.env` |
| `YOSYS_EXE` | Yosys binary override | manifest `tools.yosys.env` |
| `WORK_HOME` | Runner work directory | runner |
| `RUN_TAG` | Run tag | runner via pnr_cli |
| `SATTVA_APPROVAL`, `SATTVA_PATCH`, `SATTVA_POLICY`, `SATTVA_SOURCE_RUN`, `SATTVA_SOURCE_RUN_ID`, `SATTVA_DECISION_ID` | Resume bindings | pnr_cli `resume` |
| `SATTVA_MODEL_URL` (optional) | Model provider for advisory diagnosis | live_diagnosis |
| `SATTVA_MODEL_KEY`, `SATTVA_MODEL_NAME`, `SATTVA_MODEL_PROVIDER` (optional) | Advisory model credentials/identity; never stored in the repo | `live_diagnosis.py:72-77` |
| `SATTVA_MODEL_TIMEOUT_SECS`, `SATTVA_MODEL_MAX_ATTEMPTS`, `SATTVA_MODEL_MIN_INTERVAL_S`, `SATTVA_MODEL_TEMPERATURE`, `SATTVA_MODEL_MAX_TOKENS` (optional) | Bounded advisory call parameters | `live_diagnosis.py:78-82` |

## Manifest (`config/sattva_manifest.json`, v2)

Top-level keys: `manifest_id`, `version`, `description`, `approval_tool`, `policy`, `project_root_env`, `runner`, `recovery`, `orfs`, `profiles`, `tools`.

- `orfs`: `revision`, `verify_revision`, `root_default`, `root_env`, `local_patches[]` (`path`, `reason`, `sha256`).
- `profiles.<name>`: `description`, `status` (where applicable), `design_root`, `design_files[]`, `approval_inputs[]`, `flow_files[]`, `platform_dir`, `platform_files{path: sha256}`.
- `tools`: `openroad`/`yosys` with `default`, `env`, `expected_sha256`.
- `recovery`: `budgets`, `cli`, `controller`, `kb`.

Profiles: `nangate_macro_control` (active/validated), `riscv32i_sattva` (`FEASIBILITY_FAILED_YOSYS_ASAP7`, inactive), `sattva_sram` (`UNRESOLVED_DRT0073_PRESERVED`, inactive).

## Approval policy (`state/approval_policy.json`)

`policy_id`, `description`, `allowed_roots[]`, `stages[]`, `stage_inputs{}`, `input_files[]`, `ledger`, `recovery_profiles{}`. Stages: `check-yosys`, `check-openroad`, `synth`, `floorplan`, `place`, `cts`, `route`, `finish`.

## Recovery budgets (`config/remedy_budgets.json`)

Bounded candidate budgets consumed by `scripts/remedy_engine.py rank`.

## Design config (`benchmark/design/nangate_macro_control/config.mk`)

Uses `$(DESIGN_DIR)` / `$(PLATFORM_DIR)`; `SDC_FILE` points to `constraint_1ns.sdc` (approved). `constraint.sdc` is preserved historical 1000 ns and is not active. QA finding: `WORK_HOME` and `KLAYOUT_CMD` have overridable `/mnt/d/...` `?=` defaults in the published file; override them for your environment. The config file itself was not changed.

## Rules

- Do not add configuration keys in documentation that do not exist in these files.
- Do not claim inactive profiles are validated.
- Any config change affecting the PnR flow requires explicit human approval; the SDC change is the recorded example.

## Related

`docs/reference/CLI.md`, `docs/engineering/CONFIG_COLLATERAL.md`, `docs/reproducibility/REPRODUCIBILITY_MODEL.md`.
