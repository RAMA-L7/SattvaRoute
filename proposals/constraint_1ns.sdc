# SattvaRoute control benchmark: 1 ns clock target (proposed, NOT applied).
# Identical structure to constraint.sdc; only the numeric period changes from
# 1000 ns to 1 ns. ORFS/OpenSTA Liberty time unit is 1ns; a bare number is
# nanoseconds. Original constraint.sdc is preserved unchanged.
# Intended provenance: original synth_provenance.txt says "1000 ps clock" =
# 1 ns; the executed constraint was 1000 ns (1000x unit error).
create_clock -name clk -period 1 [get_ports clk]
set clk_io_pct 0.1
set clk_period 1
set_input_delay  [expr {$clk_period*$clk_io_pct}] -clock clk [all_inputs]
set_output_delay [expr {$clk_period*$clk_io_pct}] -clock clk [all_outputs]
