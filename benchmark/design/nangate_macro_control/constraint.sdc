create_clock -name clk -period 1000 [get_ports clk]
set clk_io_pct 0.1
set clk_period 1000
set_input_delay  [expr {$clk_period*$clk_io_pct}] -clock clk [all_inputs]
set_output_delay [expr {$clk_period*$clk_io_pct}] -clock clk [all_outputs]
