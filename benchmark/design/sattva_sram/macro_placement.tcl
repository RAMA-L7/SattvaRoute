# =============================================================================
# SattvaRoute benchmark — manual macro placement (decision D-012)
#
# Why this file exists
# --------------------
# ORFS stage 2_2_floorplan_macro runs OpenROAD's rtl_macro_placer, whose
# Snapper (src/mpl/src/snapper.cpp) requires, for EVERY non-supply pin, the
# pin *center* to land EXACTLY on a track position after one rigid translation
# of the macro. When a pin sits on a layer flagged LEF58_RIGHTWAYONGRIDONLY
# (ASAP7 M3/M4 are), failure is fatal: MPL-0005
#   "Couldn't align pin u_sram/Q[0] from the RightWayOnGridOnly layer M3
#    with the track-grid."
#
# For sram_x4x4x1 this is provably impossible (measured against
# platforms/asap7/openRoad/make_tracks.tcl, M3 = VERTICAL, pitch 0.036):
#   D[*] x-center 1.620 -> track-phase 0.027
#   Q[*] x-center 2.203 -> track-phase 0.034
#   two distinct phases, differing by 0.007 which is not a multiple of 0.036,
#   so NO translation of the macro can align both groups. Supply pins vdd/vss
#   are skipped by the Snapper (isSupply), and all M4 pins share one phase
#   (0.024 on the 0.048-pitch HORIZONTAL grid), so M4 is satisfiable.
#
# What this file does
# -------------------
# Places u_sram explicitly with `place_macro ... -exact`, which per the mpl
# README "enforce[s] the exact -location" — it bypasses the Snapper entirely
# and marks the macro LOCKED. rtl_macro_placer then finds zero unfixed macros
# and skips placement (see mpl/test/no_unfixed_macros.tcl: "the macro
# placement should just be skipped"). This is the same mechanism used by the
# ORFS reference design flow/designs/ihp-sg13g2/i2c-gpio-expander/macros.tcl.
#
# NO design view is modified: RTL, netlist, LEF, LIB and GDS are untouched.
# This is a floorplan decision, exactly what a human PnR engineer would do.
#
# Chosen location (microns, lower-left corner, R0)
# -----------------------------------------------
#   x = 1.230 : x mod 0.036 = 0.006, inside the open interval (0, 0.011) that
#               puts an interior M3 track through BOTH the D[*] and Q[*] pin
#               shapes, so the detailed router can access them (routing
#               needs a track crossing the shape; only the *center* rule was
#               impossible). Also places the macro's vdd/vss M3 taps
#               (local x 0.117..0.171 -> abs 1.347..1.401) underneath the
#               top-grid M5 strap at x = 1.320..1.440 for PDN contact.
#   y = 8.184 : y mod 0.048 = 0.024, the ideal value — every M4 pin center
#               lands EXACTLY on an M4 horizontal track (all M4 pins share
#               phase 0.024, so this single translation aligns all 12).
# Both are multiples of the ASAP7 MANUFACTURINGGRID (0.001).
# Macro bbox = (1.230, 8.184) .. (4.902, 21.792), inside the core
# (1.08, 1.08) .. (28.92, 28.92), leaving the right-hand side of the die open
# for the sattva_ctrl stdcells; the macro's M4 control pins (local x
# 3.534..3.618) face that open area.
# =============================================================================

place_macro \
  -macro_name u_sram \
  -location {1.230 8.184} \
  -orientation R0 \
  -exact
