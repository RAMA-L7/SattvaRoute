# Milestone 0 — Environment Audit & Benchmark Validation

Date: 2026-11-18
Status: **environment verified, benchmark provisionally selected (pending GDS decision)**

## 1. Hardware / OS

| Item | Value |
|---|---|
| Windows | Windows 10 Home Single Language (OEM label), build **26200** (Win11-era build) |
| CPU | Intel i5-11300H @ 3.10 GHz, 4 cores / 8 threads |
| RAM | 15.79 GB total; **WSL2 sees 7.6 GiB** (default 50% cap, no `.wslconfig`; decision: leave as-is) |
| D: drive | 116.4 GB free / 212.7 GB used |
| WSL | Ubuntu-24.04.4 LTS, WSL2, default distro, 2 GiB swap, 951 GB free on `/` |

## 2. Toolchain (authoritative source: `D:\tools\EDA_TOOL_REGISTRY.md`, updated 2026-11-14)

| Tool | Location | Version | Notes |
|---|---|---|---|
| OpenROAD | WSL `/usr/local/bin/openroad` → `D:\tools\openroad` | `bazel-nostamp` | headless, 8 threads, no `-gui` |
| ORFS | `D:\tools\OpenROAD-flow-scripts` | git `25b6429` (master) | **moved here during audit from `D:\rta-real-world-benchmark\02_projects\`** |
| OpenSTA | `D:\tools\opensta` | 3.1.0 | prefer embedded STA |
| OpenLane 2 | `/mnt/d/tools/bin/openlane` | v2.0.0b16 | not chosen as flow engine |
| Yosys | WSL `/usr/bin/yosys` | 0.33 | Windows: 0.69 (oss-cad-suite, `-s` mode) |
| Verilator | Windows-only | 5.053 | **not available in WSL** |
| Icarus | Windows-only | 14.0 devel | **not available in WSL** |
| KLayout | `D:\tools\KLayout` | 0.30.13 | headless, WSL |
| Magic / Netgen | `D:\tools\*` | 8.3.105 / 6.2.2401 | WSL |
| Python | WSL | 3.12.3, pip 24.0 | no Windows system Python |
| Node | WSL 22.23.4 / Windows 26.7.0 | npm 10.9.9 / 12.1.0 | |
| Git | Windows | 2.54.0 | |

Workspace instruction files `D:\AGENTS.md`, `D:\tools\AGENTS.md` **do not exist**; the
EDA registry is the only standing instruction document.

## 3. ORFS verification

- `flow/Makefile`, `flow/scripts`, `flow/platforms`, `flow/designs` all present.
- `SYNTH_NETLIST_FILES` (pre-synthesized netlist entry) **verified in this clone**:
  - `flow/scripts/synth_preamble.tcl:17-25` — copies/cat(s) netlist to `1_2_yosys.v`, bypasses synthesis.
  - Used in-tree by `gf12/ca53`, `gf12/bp_quad`, `gf12/bp_dual`.
- Prior evidence workspace `D:\tools\orfs_nangate45` = RTA test evidence (SDC lint,
  determinism, netlist-entry checks), **not** a flow installation.

## 4. ASAP7 platform — already present (no PDK download needed)

`flow/platforms/asap7/` (version 1.7, FakeRAM 2.0 macros):

| View | Status |
|---|---|
| Tech LEF | `lef/asap7_tech_1x_201209.lef` + `260907` ✓ |
| Cell LEF | `asap7sc7p5t_28_{L,R,SL,SRAM}_1x_220121a.lef` ✓ |
| Liberty | `lib/NLDM/` + `lib/CCS/` (RVT/LVT/SLVT × FF/SS/TT) ✓ |
| Stdcell GDS | `gds/asap7sc7p5t_28_{L,R,SL,SRAM}_220121a.gds` ✓ |
| **Macro LEF** | `lef/fakeram7_256x32.lef` etc. ✓ (`CLASS BLOCK`, `SIZE 8.360 BY 42.000`, pins M4/M5, OBS) |
| **Macro Liberty** | `lib/NLDM/fakeram7_256x32.lib` etc. ✓ |
| **Macro GDS** | ✗ **none** — platform README: GDS provided for standard cells only (FakeRAM is abstract-only) |

Design `flow/designs/asap7/riscv32i-mock-sram`:
- `BLOCKS=fakeram7_256x32` → hierarchical macro flow (macro placement, halo, blocks PDN strategy)
- parent `riscv32i` config wires `ADDITIONAL_LEFS/ADDITIONAL_LIBS` to fakeram views
- behavioral Verilog: `verilog/fakeram7_256x32.v` ✓

## 5. SRAM macro — DECIDED: OpenFinRAM (real SRAM, generated successfully)

**OpenFinRAM** (`shao-chien-lu/OpenFinRAM`, BSD-3) cloned to
`D:\SattvaRoute\benchmark\design\OpenFinRAM` and **built + run end-to-end on 2026-11-18**.

### Blockers found and resolved

| Blocker | Resolution |
|---|---|
| Calibre `v2lvs` (commercial) hard-fails run at `openroad_manager.cpp:159` | **Patch applied** (documented in source): downgrade fatal→warning. SPICE feeds only LVS, which is already non-fatal in `main.cpp:127`. Macro GDS/LEF are generated *before* this point. |
| Yosys ≥0.55 needed (multi-dim packed array ports in `sram_control.v:50`); system Yosys is 0.33 | **yowasp-yosys 0.71** (WASM) installed via pip; per-run PATH shim at `/tmp/ofr_bin/yosys` — system Yosys 0.33 untouched |
| klayout Python bindings missing (DEF→GDS stream-out) | `pip install --user --break-system-packages klayout` → 0.30.13 |
| PEP 668 blocks system pip | `--user --break-system-packages` (user site only) |

### Build/Run (WSL)
```bash
cd /mnt/d/SattvaRoute/benchmark/design/OpenFinRAM
cmake -S . -B build && make -j4          # cmake 3.28.3, g++ 13.3 ✓
# run with yosys shim on PATH:
./build/OpenFinRAM --num-wls 2 --num-data-bits 4 --num-banks 1 \
  --single-port --openroad --skip-characterization \
  --openroad-path /usr/local/bin/openroad
```
Result: **EXIT=0**. LVS skipped as designed (no tcsh/Calibre; non-fatal).

### Verified outputs (`results/sram_x4x4x1_20261118_131017/`)
- **GDS**: `sram_x4x4x1.gds` 529 KB, top cell `sram_x4x4x1`, 65 cells, dbu 0.00025 (ASAP7)
- **LEF**: `CLASS BLOCK`, SIZE 3.672 × 13.608 µm, 22 pins (vdd/vss M3, ctrl/addr/data)
- **Liberty**: `sram_x4x4x1.lib` — *estimated* model (`--skip-characterization`; not silicon-characterized — acceptable for recovery experiments; Experiment 01 removes it entirely)

### Not chosen: FakeRAM (in ORFS) — retained as fallback
`flow/platforms/asap7` fakeram7_* views (LEF+Lib, **no GDS**) remain available for a
zero-setup fallback baseline; `riscv32i-mock-sram` design unchanged.

## 6. Experiment fit (OpenFinRAM macro `sram_x4x4x1`)

| Experiment | Mechanism |
|---|---|
| 01 missing macro timing view | remove/exclude `sram_x4x4x1.lib` from `ADDITIONAL_LIBS` → link+STA failure |
| 02 illegal macro placement | `CLASS BLOCK` macro placed outside core → placer geometry violation |
| 03 invalid routing layer | platform layer config vs `asap7_tech.lef` layers → router failure |

**Known follow-ups:** (a) scale macro (e.g. 256×32) + wrap in a controller design for the
real benchmark; (b) Liberty is estimated — fine for experiments, characterize if QoR matters;
 (c) LVS path needs tcsh+Calibre if signoff LVS is ever required (not needed for Milestone 1).

## 7. Locked stack

Python 3.12 (WSL) · LangGraph · FastAPI · React+TS+Vite · SQLite · ORFS+OpenROAD (WSL,
`D:\tools\OpenROAD-flow-scripts`) · benchmark: **ASAP7 + OpenFinRAM real SRAM macro
(`sram_x4x4x1`, GDS+LEF+Lib verified)** · Yosys: yowasp 0.71 for OpenFinRAM, system 0.33 for ORFS.
