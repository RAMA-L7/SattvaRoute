# Reproducibility (Phase 9 + control benchmark package)

Goal: another engineer can obtain the published benchmark and reproduce the
supported flow **without relying on untracked files or author-specific paths**.
Nothing here claims another engineer tested it; see *Validation status*.

## What is project-owned (published, license permits)

`benchmark/design/nangate_macro_control/`:
- `config.mk` (design configuration; no machine paths; `$(DESIGN_DIR)`,
  `$(PLATFORM_DIR)`)
- `constraint.sdc` (historical executed 1000 ns clock; preserved). `config.mk`
  `SDC_FILE` now points to applied `constraint_1ns.sdc` (1 ns; approved).
  Historical baseline `...1144339456871595Z_11464` ran at 1000 ns; new
  `orfs_baseline_control_1ns_20261126T133241476241945Z_4600` runs at 1 ns.
- `rtl/sattva_macro_top.v` (wrapper RTL; no functional change)
- `rtl/fakeram45_64x32_bb.v` (synthesis blackbox interface; **not** memory
  geometry/timing; not a memory compiler)
- `netlist/sattva_macro_top_synth.v` (prepared gate-level netlist; one
  `fakeram45_64x32` instance; no added logic)
- `netlist/synth_provenance.txt` (netlist preparation + provenance)
- (no project-owned placement/PDN scripts for this profile; ORFS platform PDN
  is used; see `floorplan`/`pdn` stage)

## Prepared netlist provenance / reproduction

See `benchmark/design/nangate_macro_control/netlist/synth_provenance.txt`.
Exact commands (offline; originals unmodified):

1. ORFS canonicalize stage (Yosys 0.33 `read_liberty -lib`, `SATTVA_YOSYS_COMPAT=1`
   skips one unsupported annotation read in the execution mirror), writes
   `1_1_yosys_canonicalize.rtlil`.
2. `yosys 0.33`: `read_rtlil <canonicalize>; hierarchy -check -top
   sattva_macro_top; synth -top sattva_macro_top; dfflibmap -liberty
   NangateOpenCellLibrary_typical.lib; abc -liberty <same>; opt_clean -purge;
   write_verilog -noattr sattva_macro_top_synth.v`.

Result preserves one `fakeram45_64x32`; no functional RTL change. PnR starts
from the cached netlist (`SYNTH_NETLIST_FILES`); no re-synthesis during
recovery. **Macro interface consistency** across netlist ↔ LEF ↔ Liberty is
checked: cell `fakeram45_64x32`, pins `clk, we_in, ce_in, addr_in[5:0],
w_mask_in[31:0], rd_out[31:0]` + `wd_in[31:0]`, etc., matching the platform
`fakeram45_64x32.lef`/`.lib`. (Macro blackbox stub is synthesis-only.)

## External pinned collateral (NOT committed; not relicensed)

OpenROAD Flow Scripts (ORFS) and platform data are external. This repository
does not redistribute them. Pinned references:

- **ORFS checkout**: revision `25b6429c1644a8682852646bebf19ff164402c76`.
  Source `https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts`.
  License BSD-3-Clause (see upstream `LICENSE`). **Two local patches** are
  applied in the execution mirror and recorded in `evidence/mirror.patch` /
  `config/sattva_manifest.json`:
  - `flow/scripts/global_route.tcl` (+8): D-014 mark `zero_` net `SPECIAL`
    before `pin_access` (DRT-0305). sha256 `cd86b587…`.
  - `flow/scripts/synth_stdcells.tcl` (+11/-2): `SATTVA_YOSYS_COMPAT` gate.
    sha256 `5a94e9d6…`.
  No other tracked flow changes. `manifest.py` verifies HEAD == pinned and
  that tracked changes are exactly the declared patches.
- **Platform `nangate45`**: `flow/platforms/nangate45` in the pinned ORFS.
  - `lib/NangateOpenCellLibrary_typical.lib` sha256 `8d540a4d…` (Liberty
    `time_unit 1ns`, `typical`, 1.1V, 25C). License per upstream Nangate
    notice; **script license does not cover all platform data**.
  - `lib/fakeram45_64x32.lib` sha256 `bcf9eb40…` (`time_unit 1ns`, `tt_1.0_25.0`).
  - `lef/NangateOpenCellLibrary.tech.lef` `834a7929…`;
    `lef/NangateOpenCellLibrary.macro.mod.lef` `a43aea33…`.
  - `lef/fakeram45_64x32.lef` `7b7ee9ce…` (abstract macro; no bit-cells).
  - `rcx_patterns.rules` `2f65fafb…`; `setRC.tcl` `521df813…`;
    `config.mk` `1d8e639c…`.
  FakeRAM is an ORFS-provided abstract macro; not a foundry-characterized SRAM.
- **Tools** (pinned identities; see manifest `tools`):
  - OpenROAD `bazel-nostamp` `/usr/local/bin/openroad` sha256 `c1b90e0a…`.
  - Yosys `0.33` sha256 `88c0a12b…`. GNU Make, Python ≥3.10. KLayout optional.
- **Deterministic acquisition**: 
  ```
  git clone https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts
  git -C OpenROAD-flow-scripts checkout 25b6429c1644a8682852646bebf19ff164402c76
  git -C OpenROAD-flow-scripts apply <path-to>/evidence/mirror.patch
  # build openroad + yosys to match pinned sha256 in config/sattva_manifest.json
  ```
  Then `SATTVA_MIRROR=<checkout>`. The manifest **fails** if HEAD/working tree
  or a pinned hash differs.

## Active-profile dependency manifest (Phase 4)

`config/sattva_manifest.json` (v2). `scripts/manifest.py --check --profile
nangate_macro_control`. The selected profile resolves actual consumed
dependencies: config+SDC, prepared netlist, macro LEF/Liberty, standard-cell
LEF/Liberty, technology LEF, applicable placement/PDN scripts, extraction
rules + RC setup, relevant flow scripts + local patches, **actual tool binary
hashes**, **verified ORFS revision**. **Declared expectations** separated from
**captured fingerprints**. One canonical `fingerprint`. Runner preflight,
approval validation, resume, and evidence bundles consume the same set.
Inactive profiles are not checked. See `docs/VERIFICATION.md` and
`tests/test_manifest.py`.

## Setup + launch (no author-specific paths)

Project root = `SATTVA_ROOT`; ORFS = `SATTVA_MIRROR` (default
`$SATTVA_ROOT/tools/OpenROAD-flow-scripts`); tool binaries via `OPENROAD_EXE`
/ `YOSYS_EXE`. `WORK_HOME` set by runner. No `/mnt/d/...` in published config.

```
# baseline (control benchmark)
SATTVA_ROOT=<checkout> SATTVA_MIRROR=<orfs> \
  python3 scripts/pnr_cli.py baseline            # or scripts/run_baseline_orfs.sh
  SATTVA_DESIGN=<checkout>/benchmark/design/nangate_macro_control \
  SATTVA_DESIGN_PROFILE=nangate_macro_control SATTVA_ROOT=<checkout> ...
# manifest preflight
python3 scripts/manifest.py --check --profile nangate_macro_control --mirror <orfs>
# timing audit (read-only)
python3 scripts/timing_audit.py --run <run> --platform <orfs>/flow/platforms/nangate45 \
  --macro-lib fakeram45_64x32.lib --out <audit.json>
# verify
python3 scripts/verify_run.py --run <run> --audit <audit.json>
# tests (offline)
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Recovery entry point (documented, approval-gated)

```
python3 scripts/pnr_cli.py diagnose --run <failed-run>            # textual proposal
python3 scripts/pnr_cli.py propose  --diagnosis <d> --target <t>  # not applied
python3 scripts/pnr_cli.py approve-view --proposal <p>            # review exact diff
# then a HUMAN creates/approves exact patch via scripts/sattva_approval.py
# (create -> validate -> guard/apply); resume reruns affected stages.
python3 scripts/pnr_cli.py resume --approval <a> --patch <p> ...
# independent verification
python3 scripts/verify_run.py --baseline B --failure F --recovery R ...
```
Nothing is applied without explicit human approval of the exact displayed diff.
Evaluation v2 is frozen: `scripts/evaluate_diagnosis_v2.py`.

## Curated evidence (small; no bulk artifacts)

`evidence/timing/`, `evidence/verification/`, run `evidence/` (`run.json`,
`stages.tsv`, stage logs, `preflight`, `manifest.json`, `mirror.patch`,
`approval_*.json`, `artifact_sha256.txt`, `postflight`), `docs/`,
`config/sattva_manifest.json`, `state/approval_policy.json`. Large `*.odb`,
`*.gds`, `*.spef`, `runs/`, `work/` are **not** published; **local paths are
not public evidence**. Hashes + selected excerpts are published instead.

## Validation status

**Author-run clean-environment validation**, not another engineer. Offline test
suite: `python3 -m unittest discover -s tests`. Verified baseline PASS via
`scripts/verify_run.py`. Timing units/corner/coverage established. No claim of
foundry signoff, functional verification, or external independent reproduction.

## Limitations

See `docs/TIMING_AUDIT.md`. Pass-through wrapper; abstract FakeRAM; single
typical corner; trivial timing; not representative; no signoff; no functional
correctness. Remaining gaps in `docs/` + `PROJECT_STATE.md`.
