// SattvaRoute benchmark controller — genuinely instantiates the OpenFinRAM
// SRAM macro sram_x4x4x1 (see sram_x4x4x1_bb.v and docs/benchmark/macro-sram-x4x4x1.md).
//
// Function: deterministic self-test FSM
//   1. Writes a distinct 4-bit pattern to 4 addresses (one write cycle each)
//   2. Reads each address back and compares against the expected pattern
//   3. Raises `done`; raises `error` on first mismatch
//
// Notes:
// - Sync reset only (ASAP7 flow convention; no async-reset dependency).
// - Address is held stable during read+capture so Q is valid whether the
//   macro's read is registered (1-cycle) or asynchronous — required because
//   the macro Liberty is an estimated model with no read-latency arcs.
// - sdel tied to 0 (delay-select unused in benchmark; documented in macro doc).
module sattva_ctrl (
    input  wire       clk,      // matches macro clk (all Liberty arcs relate to it)
    input  wire       rst_n,    // synchronous, active low
    output reg        done,     // self-test sequence complete
    output reg        error     // readback mismatch detected
);

    // ---- SRAM interface (driven from FSM state) ----
    reg  [2:0]  state;
    reg  [1:0]  addr;
    reg  [3:0]  wdata;

    wire        ce_n;
    wire        oe_n;
    wire        we_n;
    wire [3:0]  A;
    wire [3:0]  D;
    wire [3:0]  Q;      // consumed in S_CAP
    wire [3:0]  sdel;

    localparam S_IDLE = 3'd0,
               S_WR   = 3'd1,   // one write cycle
               S_RD   = 3'd2,   // read cycle (address presented)
               S_CAP  = 3'd3,   // capture/compare, address held
               S_DONE = 3'd4;

    // Expected pattern: {addr, ~addr} — distinct for all 4 addresses
    wire [3:0] expected = {addr, ~addr};

    // Combinational macro controls from state
    assign ce_n = (state == S_WR || state == S_RD || state == S_CAP) ? 1'b0 : 1'b1;
    assign we_n = (state == S_WR) ? 1'b0 : 1'b1;
    assign oe_n = (state == S_RD || state == S_CAP) ? 1'b0 : 1'b1;
    assign A    = (state == S_WR || state == S_RD || state == S_CAP) ? {2'b00, addr} : 4'b0000;
    assign D    = wdata;
    assign sdel = 4'b0000;   // documented tie-off (macro doc)

    // ---- FSM ----
    always @(posedge clk) begin
        if (!rst_n) begin
            state <= S_IDLE;
            addr  <= 2'b00;
            wdata <= 4'b0000;
            done  <= 1'b0;
            error <= 1'b0;
        end else begin
            case (state)
                S_IDLE: begin
                    // start immediately; wdata for addr 0
                    addr  <= 2'b00;
                    wdata <= {2'b00, 2'b11};   // {addr, ~addr} for addr=0 -> 4'b0011
                    done  <= 1'b0;
                    state <= S_WR;
                end
                S_WR: begin
                    // macro latches {A,D} on clk edge while we_n low
                    state <= S_RD;
                end
                S_RD: begin
                    state <= S_CAP;
                end
                S_CAP: begin
                    // Q valid with address held (covers reg or async read)
                    if (Q !== expected)
                        error <= 1'b1;
                    if (addr == 2'b11) begin
                        done  <= 1'b1;
                        state <= S_DONE;
                    end else begin
                        addr  <= addr + 2'b01;
                        wdata <= {addr + 2'b01, ~(addr + 2'b01)};
                        state <= S_WR;
                    end
                end
                S_DONE: begin
                    state <= S_DONE;    // hold until reset
                end
                default: state <= S_IDLE;
            endcase
        end
    end

    // ---- SRAM macro instance (real OpenFinRAM hard macro) ----
    sram_x4x4x1 u_sram (
        .clk   (clk),
        .ce_n  (ce_n),
        .oe_n  (oe_n),
        .we_n  (we_n),
        .sdel  (sdel),
        .A     (A),
        .D     (D),
        .Q     (Q)
    );

endmodule
