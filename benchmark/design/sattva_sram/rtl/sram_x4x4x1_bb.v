// SattvaRoute benchmark — blackbox stub for the OpenFinRAM SRAM macro.
// Derived from LEF sram_x4x4x1.lef (2026-11-18) and results/.../sram_x4x4x1.lib.
// Supply pins vdd/vss are omitted per ORFS convention (see fakeram7_*.v);
// they exist in LEF (M3, POWER/GROUND) and are handled by PDN.
// NEVER edit by hand without regenerating from the LEF — see docs/benchmark/macro-sram-x4x4x1.md
(* blackbox *)
module sram_x4x4x1 (
    input  wire        clk,
    input  wire        ce_n,
    input  wire        oe_n,
    input  wire        we_n,
    input  wire [3:0]  sdel,
    input  wire [3:0]  A,
    input  wire [3:0]  D,
    output wire [3:0]  Q
);
endmodule
