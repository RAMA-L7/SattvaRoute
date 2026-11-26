# SattvaRoute timing-unit and constraint audit (read-only).
#
# Mirrors the ORFS 6_report ordering (liberty -> db -> sdc -> setRC -> SPEF) so
# the numbers reproduce the flow's own final report, then dumps the tool's
# unit, clock, corner and coverage view. It never writes design data.
#
# Required environment:
#   AUDIT_RESULTS   directory holding 6_final.odb, 6_final.sdc, 6_final.spef
#   AUDIT_PLATFORM  platform directory (lef/lib/...)
#   AUDIT_MACRO_LIB macro Liberty file name inside $AUDIT_PLATFORM/lib
#
# Every section is wrapped in catch so one unsupported command cannot discard
# the rest; failures are printed explicitly.

proc section {name body} {
  puts "===== $name ====="
  if {[catch {uplevel 1 $body} err]} {
    puts "SECTION_ERROR $name: $err"
  }
}

set results  $::env(AUDIT_RESULTS)
set platform $::env(AUDIT_PLATFORM)
set macrolib $::env(AUDIT_MACRO_LIB)

section LIBERTY {
  read_liberty $platform/lib/NangateOpenCellLibrary_typical.lib
  read_liberty $platform/lib/$macrolib
}
section LOAD {
  read_db $results/6_final.odb
  read_sdc $results/6_final.sdc
  set_propagated_clock [all_clocks]
}
section RC_CORNER {
  source $platform/setRC.tcl
}
section SPEF {
  read_spef $results/6_final.spef
}
section UPDATE_TIMING {
  update_timing -full
}

section REPORT_UNITS {
  report_units
}
section CLOCK_PROPERTIES {
  report_clock_properties
}
section WORST_SLACK {
  report_worst_slack -max
  report_worst_slack -min
}
section MIN_PERIOD_REG_TO_REG {
  report_clock_min_period
}
section MIN_PERIOD_INCLUDING_PORTS {
  report_clock_min_period -include_port_paths
}
section CHECK_SETUP {
  check_setup -verbose
}
section CHECKS_MAX {
  report_checks -path_delay max -format full_clock_expanded -fields {slew cap input_pins fanout} -digits 4
}
section CHECKS_MIN {
  report_checks -path_delay min -format full_clock_expanded -fields {slew cap input_pins fanout} -digits 4
}
section UNCONSTRAINED {
  report_checks -unconstrained -path_delay max -digits 4
}
section CLOCK_SKEW {
  report_clock_skew
}
section CHECK_TYPES {
  report_check_types -max_slew -max_capacitance -max_fanout -violators
}
section PARASITICS {
  report_parasitic_annotation
}
section COVERAGE {
  puts "input_ports [llength [all_inputs]]"
  puts "output_ports [llength [all_outputs]]"
  puts "register_clock_pins [llength [all_registers -clock_pins]]"
  puts "registers [llength [all_registers]]"
  puts "clocks [llength [all_clocks]]"
  foreach clk [all_clocks] {
    puts "clock $clk period [get_property $clk period]"
  }
}
section LIBS {
  foreach lib [get_libs *] {
    puts "LIB $lib"
  }
}
puts "===== AUDIT_DONE ====="
