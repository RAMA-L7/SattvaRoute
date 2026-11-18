# =============================================================================
# SattvaRoute Milestone 1 — pinned ORFS design configuration (task T-M1-002)
#
# Flow engine : D:\tools\OpenROAD-flow-scripts  (D-001/D-003, commit 25b6429)
# Platform    : asap7, NLDM library model, CORNER=TC (TT libs @ 0C/0.70V) —
#               matches the TT/RVT libs used for Phase-A synthesis (abc -D 950)
# Benchmark   : sattva_ctrl + the REAL OpenFinRAM SRAM macro sram_x4x4x1
#               (D-002; views under benchmark/design/sattva_sram/macro/)
# Netlist     : pre-synthesized in Phase A (task T-M1-001). SYNTH_NETLIST_FILES
#               short-circuits yosys inside ORFS (synth_preamble.tcl), while
#               VERILOG_FILES is still consumed by the canonicalize step
#               (hierarchy -check -top sattva_ctrl). Full synthesis provenance:
#               benchmark/design/sattva_sram/netlist/synth_provenance.txt
#
# Path policy: every path below is relative to this file ($(DESIGN_DIR), which
# ORFS derives from DESIGN_CONFIG) — nothing is written into D:\tools. Run
# outputs go to WORK_HOME (default pinned here on D:\SattvaRoute; a per-run
# timestamped WORK_HOME passed on the make command line overrides it so that
# no previous run is ever overwritten).
# =============================================================================

export DESIGN_NICKNAME = sattva_sram
export DESIGN_NAME     = sattva_ctrl
export PLATFORM        = asap7

# TC corner (0C / 0.70V / TT libraries). See header.
export CORNER          = TC

# ---- design sources (RTL; canonicalize step + LEC reference) ---------------
export VERILOG_FILES = $(DESIGN_DIR)/rtl/sram_x4x4x1_bb.v \
                       $(DESIGN_DIR)/rtl/sattva_ctrl.v
export SDC_FILE      = $(DESIGN_DIR)/constraint.sdc

# ---- pre-synthesized gate-level netlist (Phase A output) -------------------
export SYNTH_NETLIST_FILES = $(DESIGN_DIR)/netlist/sattva_ctrl_synth.v

# ---- real OpenFinRAM macro views (D-002) -----------------------------------
# LEF: CLASS BLOCK, 3.672 x 13.608 um, PG pins vdd/vss on M3 (lowercase —
# see pdn_sattva.tcl), SYMMETRY X Y, OBS M1-M5.
export ADDITIONAL_LEFS = $(DESIGN_DIR)/macro/sram_x4x4x1.lef
export ADDITIONAL_LIBS = $(DESIGN_DIR)/macro/sram_x4x4x1.lib
export ADDITIONAL_GDS  = $(DESIGN_DIR)/macro/sram_x4x4x1.gds

# ---- floorplan -------------------------------------------------------------
# Explicit die/core (uart-style) instead of CORE_UTILIZATION: the design is
# tiny (~6.2 um^2 stdcells) so a utilization-derived die would be smaller
# than the 3.672 x 13.608 um macro itself.
export DIE_AREA              = 0 0 30 30
export CORE_AREA             = 1.08 1.08 28.92 28.92
export MACRO_PLACE_HALO      = 4 4
export PLACE_DENSITY_LB_ADDON = 0.10
export TNS_END_PERCENT       = 100

# Manual macro placement (D-012). rtl_macro_placer's Snapper cannot align
# this macro's M3 pins to the ASAP7 M3 track grid (D/Q pin centers fall on
# two different phases of the 0.036 pitch), which aborts with MPL-0005 on the
# RightWayOnGridOnly M3 layer. `place_macro -exact` bypasses the Snapper and
# LOCKs the macro, so rtl_macro_placer skips it. See macro_placement.tcl.
export MACRO_PLACEMENT_TCL = $(DESIGN_DIR)/macro_placement.tcl

# ---- power grid ------------------------------------------------------------
# Design-local override of the platform grid: the ASAP7 default connects
# ^VDD$ / ^VSS$ (uppercase, stdcell convention) and bridges macro PG M4-M5
# (fakeram convention), but this macro has lowercase vdd/vss pins on M3.
export PDN_TCL = $(DESIGN_DIR)/pdn_sattva.tcl

# ---- reproducibility / run isolation --------------------------------------
# Default work home lives on D:\SattvaRoute (never inside D:\tools). The
# baseline runner overrides this with a fresh timestamped directory per run.
export WORK_HOME ?= /mnt/d/SattvaRoute/runs/orfs
