# Benchmark methodology

Status: describes the published control benchmark. Authoritative: `docs/REPRODUCIBILITY.md`, `docs/CONTROL_BENCHMARK_PACKAGE.md`, `docs/CONTROL_BENCHMARK_SELECTION.md`.

## Control benchmark

`benchmark/design/nangate_macro_control`:

- Nangate45 standard cells + ORFS platform `fakeram45_64x32` **abstract** macro.
- `config.mk` with `$(DESIGN_DIR)`/`$(PLATFORM_DIR)`. Note (QA finding): `WORK_HOME` and `KLAYOUT_CMD` still carry overridable `/mnt/d/...` `?=` defaults; set them in your environment. The config file was not changed in this milestone.
- `constraint.sdc` (historical 1000 ns, preserved) and `constraint_1ns.sdc` (approved active 1 ns).
- `rtl/sattva_macro_top.v` (pass-through-style wrapper; no functional change), `rtl/fakeram45_64x32_bb.v` (synthesis blackbox interface, not a memory compiler).
- `netlist/sattva_macro_top_synth.v` (prepared gate-level netlist, one macro instance) plus `netlist/synth_provenance.txt`.
- No project-owned placement/PDN scripts for this profile; ORFS platform PDN is used.

## Netlist provenance

Prepared from the ORFS canonicalize stage (Yosys 0.33, `SATTVA_YOSYS_COMPAT=1` gate for the pinned build) and Yosys synthesis with the pinned typical Liberty; exact commands are in `docs/REPRODUCIBILITY.md` and the provenance file. PnR starts from the cached netlist (`SYNTH_NETLIST_FILES`); no re-synthesis during recovery. Macro interface consistency (netlist ↔ LEF ↔ Liberty pins) is checked.

## External, not redistributed

ORFS revision and two patches, Nangate45 platform LEF/Liberty/RCX files, `fakeram45_64x32` views, and tool binaries are external and pinned by hash. They are not vendored. See `docs/governance/THIRD_PARTY.md`.

## Controlled failure fixtures

- `failure-demo`: attempt-local config with one omitted macro Liberty reference; originals untouched.
- Held-out case: one omitted macro LEF reference; real failure at `synth`; deterministic diagnosis; approved patch; isolated recovery verified PASS. See `docs/HELDOUT_RECOVERY.md`.

## Baseline acceptance

`docs/BASELINE_ACCEPTANCE_CRITERIA.md` was frozen before treatment; `verify_run.py` provides report-level checks. A zero return code is not an acceptance criterion.

## Limitations

Single typical corner, trivial timing, abstract macro, not representative of production designs, no foundry signoff, no functional correctness. See `docs/research/LIMITATIONS.md`.

## Related

`docs/reproducibility/EVALUATION.md`, `docs/engineering/CONFIG_COLLATERAL.md`, `docs/research/LIMITATIONS.md`.
