# Third-party notices and redistribution scope

The MIT license in `LICENSE` covers **original SattvaRoute code and documents only**.

## Included third-party / derived material

| Item | Source | License / terms | Use here |
|---|---|---|---|
| OpenROAD-flow-scripts (ORFS, commit `25b6429`) | <https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts> | BSD-3-Clause (upstream) | Referenced as an external tool. Not vendored in this repository. |
| OpenROAD (routing/DB engine) | <https://github.com/The-OpenROAD-Project/OpenROAD> | BSD-3-Clause (upstream) | External tool. Source lines are quoted in investigation reports for evidentiary analysis. |
| OpenFinRAM | <https://github.com/ArunTS1992/OpenFinRAM> | BSD-3-Clause | SRAM generator used to produce the `sram_x4x4x1` benchmark macro. Not vendored. |
| `sram_x4x4x1.lef`, `sram_x4x4x1.lib` | Generated locally by OpenFinRAM with the public ASAP7 academic technology | Outputs of a BSD-3 generator; derived from public ASAP7 collateral | Included because the supported PnR flow requires them. Attribution retained; consult ASAP7 terms before commercial redistribution. |
| ASAP7 | Arizona State University predictive technology model | Public academic PDK; consult its own license | External platform. Standard-cell libraries and tech files are **not** included here. |
| Yosys | <https://github.com/YosysHQ/yosys> | ISC / GPL (see upstream) | External synthesis tool. Not vendored. |
| Nangate45 platform (ORFS `flow/platforms/nangate45`) | Pinned ORFS revision `25b6429c...` | Per upstream Nangate notice; the ORFS script license does not cover all platform data | External platform for the published `nangate_macro_control` benchmark. LEF/Liberty/RCX files are **not** committed; they are referenced by hash in `config/sattva_manifest.json`. Do not assume redistribution rights. |
| `fakeram45_64x32` abstract macro (`.lib`, `.lef`) | ORFS Nangate45 platform | Platform/upstream terms | Abstract macro used by the control benchmark. **Not** a foundry-characterized SRAM. Pinned by hash; not vendored. |

A full attribution and dependency inventory, including the Nangate45/FakeRAM package, is maintained in `docs/governance/THIRD_PARTY.md`. Licensing scope and a recommendation (owner decision required) are in `docs/governance/LICENSING.md`. This notice is supplemented, not rewritten.

## Deliberately excluded from this repository

The following were present in the local development tree but are **not published**:

- `tools/OpenROAD-flow-scripts/` — full ORFS mirror including platform libraries, GDS and macro collateral (hundreds of MB).
- `benchmark/design/OpenFinRAM/` — external Git clone, build outputs, Calibre rule decks, QRC tech files and licensed-tool collateral.
- `benchmark/design/sattva_sram/macro/sram_x4x4x1.gds` — generated GDS. It is not required by the supported flow (final GDS streaming was unavailable in the development environment). Regenerate it with `scripts/gen_sram_macro.sh` and the upstream OpenFinRAM + ASAP7 setup.
- `runs/` full directories — OpenDB databases and intermediate artifacts (~144 MB). Curated summaries, selected log excerpts and a hash manifest are published under `evidence/` instead.
- Local WSL paths, credentials, caches, virtual environments and IDE/OS files.

No proprietary EDA binaries, commercial tool files, licensed standard-cell libraries, QRC/Calibre decks or restricted PDK files are included in this repository.
