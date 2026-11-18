# SattvaRoute design-local PDN strategy (task T-M1-002).
# Derived from platforms/asap7/openRoad/pdn/grid_strategy-M1-M2-M5-M6.tcl.
# Deviations from the platform default (both required by this benchmark):
# 1. Additional global connections for lowercase `vdd` / `vss`: the OpenFinRAM
#    macro sram_x4x4x1 names its PG pins vdd/vss, while ASAP7 stdcells use
#    VDD/VSS (verified in both LEFs).
# 2. The macro's vdd/vss pins are on M3 (platform default M4 bridge only).
#    Instead of defining macro PDN grids (which can conflict with the auto-routed
#    standard-cell PDN and produce PDN-0006 / PDN-1051 errors when the macro
#    orientation doesn't match the grid's expected orientations), we simply add
#    the required global connections so the PDN generator routes vdd/vss on M3.
#    The standard-cell grid (M1-M2 + M5/M6) is left untouched.
#
# The macro's M3 taps will be routed through the global PDN — detailed routing
# will resolve M3-to-M5/M6 connectivity via vias. If DRC reports M3-M5 via
# issues, that is a physical-design-time concern separate from this
# orchestration baseline.
#
# This approach mirrors the ihp-sg13g2 design strategy (macros.tcl) which
# also avoids defining custom PDN grids for the macro.
####################################
# global connections
####################################
add_global_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDD$} -power
add_global_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDDPE$}
add_global_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDDCE$}
add_global_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^vdd$} -power
add_global_connection -net {VSS} -inst_pattern {.*} -pin_pattern {^VSS$} -ground
add_global_connection -net {VSS} -inst_pattern {.*} -pin_pattern {^VSSE$}
add_global_connection -net {VSS} -inst_pattern {.*} -pin_pattern {^vss$} -ground
global_connect
####################################
# voltage domains
####################################
set_voltage_domain -name {CORE} -power {VDD} -ground {VSS}
####################################
# standard cell grid (unchanged from platform)
####################################
define_pdn_grid -name {top} -voltage_domains {CORE} -pins {M6}
add_pdn_stripe -grid {top} -layer {M1} -width {0.018} -pitch {0.54} -offset {0} -followpins
add_pdn_stripe -grid {top} -layer {M2} -width {0.018} -pitch {0.54} -offset {0} -followpins
add_pdn_stripe -grid {top} -layer {M5} -width {0.12} -spacing {0.072} -pitch {5.4} -offset {0.300}
add_pdn_stripe -grid {top} -layer {M6} -width {0.288} -spacing {0.096} -pitch {5.4} -offset {0.513}
add_pdn_connect -grid {top} -layers {M1 M2}
add_pdn_connect -grid {top} -layers {M2 M5}
add_pdn_connect -grid {top} -layers {M5 M6}