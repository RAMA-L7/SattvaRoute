module sattva_macro_top (
  input [31:0] w_mask_in,
  input [31:0] wd_in,
  input [5:0] addr_in,
  input we_in,
  input ce_in,
  input clk,
  output [31:0] rd_out
);
  (* keep *) fakeram45_64x32 u_macro (
    .w_mask_in(w_mask_in),
    .wd_in(wd_in),
    .addr_in(addr_in),
    .we_in(we_in),
    .ce_in(ce_in),
    .clk(clk),
    .rd_out(rd_out)
  );
endmodule
