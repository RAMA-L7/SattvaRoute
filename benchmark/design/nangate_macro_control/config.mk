# SattvaRoute control benchmark: Nangate45 + platform fakeram45_64x32 macro.
# Generated blackbox stub is a synthesis placeholder only; no memory compiler,
# macro abstraction, SDC target or design rule was edited.
export DESIGN_NICKNAME = nangate_macro_control
export DESIGN_NAME = sattva_macro_top
export PLATFORM = nangate45
export VERILOG_FILES = $(DESIGN_DIR)/rtl/sattva_macro_top.v $(DESIGN_DIR)/rtl/fakeram45_64x32_bb.v
export VERILOG_FILES_BLACKBOX = $(DESIGN_DIR)/rtl/fakeram45_64x32_bb.v
export SDC_FILE = $(DESIGN_DIR)/constraint_1ns.sdc
# Prepared separately (see netlist/sattva_macro_top_synth.v provenance); PnR
# starts from this cached gate-level netlist, no re-synthesis during recovery.
export SYNTH_NETLIST_FILES = $(DESIGN_DIR)/netlist/sattva_macro_top_synth.v
export ADDITIONAL_LEFS = $(PLATFORM_DIR)/lef/fakeram45_64x32.lef
export ADDITIONAL_LIBS = $(PLATFORM_DIR)/lib/fakeram45_64x32.lib
# Explicit die/core area sized for the 20.14 x 61.60 um platform macro;
# utilization/margin floorplan initialization is intentionally not combined.
export DIE_AREA = 0 0 100 100
export CORE_AREA = 2 2 98 98
export PLACE_DENSITY = 0.70
export MACRO_PLACE_HALO = 2 2
export TNS_END_PERCENT = 100
export WORK_HOME ?= /mnt/d/SattvaRoute/runs/orfs
export KLAYOUT_CMD ?= /mnt/d/tools/KLayout/bin/klayout.sh
# Environment compatibility only: skip a Yosys frontend annotation read whose
# flags do not exist in the installed Yosys 0.33. No design/data change.
export SATTVA_YOSYS_COMPAT = 1
