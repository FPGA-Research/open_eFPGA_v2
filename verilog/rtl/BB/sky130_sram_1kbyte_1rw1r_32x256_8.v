/// sta-blackbox
/* verilator lint_off UNUSEDSIGNAL */
/* verilator lint_off UNDRIVEN */
/* verilator lint_off UNUSEDPARAM */
// OpenRAM SRAM model
// Words: 256
// Word size: 32
// Write size: 8

module sky130_sram_1kbyte_1rw1r_32x256_8 (
`ifdef USE_POWER_PINS
    vccd1,
    vssd1,
`endif
    // Port 0: RW
    clk0,
    csb0,
    web0,
    wmask0,
    addr0,
    din0,
    dout0,
    // Port 1: R
    clk1,
    csb1,
    addr1,
    dout1
);

    parameter NUM_WMASKS = 4;
    parameter DATA_WIDTH = 32;
    parameter ADDR_WIDTH = 8;

`ifdef USE_POWER_PINS
    inout vccd1;
    inout vssd1;
`endif
    input clk0;  // clock
    input csb0;  // active low chip select
    input web0;  // active low write control
    input [NUM_WMASKS-1:0] wmask0;  // write mask
    input [ADDR_WIDTH-1:0] addr0;
    input [DATA_WIDTH-1:0] din0;
    output [DATA_WIDTH-1:0] dout0;
    input clk1;  // clock
    input csb1;  // active low chip select
    input [ADDR_WIDTH-1:0] addr1;
    output [DATA_WIDTH-1:0] dout1;
endmodule
/* verilator lint_on UNUSEDSIGNAL */
/* verilator lint_on UNDRIVEN */
/* verilator lint_on UNUSEDPARAM */
