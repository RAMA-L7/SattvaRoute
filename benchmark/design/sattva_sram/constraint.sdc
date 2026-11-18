# SattvaRoute benchmark timing constraints (task T-M1-002).
# Structure follows the ORFS ASAP7 reference designs (riscv32i/uart).
#   clk_period : 950 ps — the same target used for Phase-A synthesis
#                (scripts/abc_map_sattva.script, `if -D 950`, decision D-009)
#   clk_io_pct : 0.125 — 12.5% of period reserved for IO paths (riscv32i value)
# Ports: clk, rst_n (inputs) / done, error (outputs).
current_design sattva_ctrl

set clk_name clk
set clk_port_name clk
set clk_period 950
set clk_io_pct 0.125

set clk_port [get_ports $clk_port_name]

create_clock -name $clk_name -period $clk_period $clk_port
set clk_io_name vclk_$clk_name
create_clock -name $clk_io_name -period $clk_period

set non_clock_inputs [all_inputs -no_clocks]
set_input_delay [expr $clk_period * $clk_io_pct] -clock $clk_io_name $non_clock_inputs
set_output_delay [expr $clk_period * $clk_io_pct] -clock $clk_io_name [all_outputs]
