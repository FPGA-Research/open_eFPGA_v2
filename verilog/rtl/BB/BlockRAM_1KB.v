/// sta-blackbox
/* verilator lint_off UNUSEDSIGNAL */
/* verilator lint_off UNDRIVEN */
/* verilator lint_off UNUSEDPARAM */
/* verilator lint_off LATCH */
module BlockRAM_1KB (
`ifdef USE_POWER_PINS
    vccd1,
    vssd1,
`endif
    clk,
    rd_addr,
    rd_data,
    wr_addr,
    wr_data,
    C0,
    C1,
    C2,
    C3,
    C4,
    C5
);

    parameter READ_ADDRESS_MSB_FROM_DATALSB = 24; //default 24 means bits wr_data[25:24] will become bits [9:8] of read address
    parameter WRITE_ADDRESS_MSB_FROM_DATALSB = 16; //default 16 means bits wr_data[17:16] will become bits [9:8] of write address
    parameter WRITE_ENABLE_FROM_DATA = 20; //default 20 means bit wr_data[20] will become the dynamic writeEnable input
`ifdef USE_POWER_PINS
    inout vccd1;
    inout vssd1;
`endif
    input clk;
    input [7:0] rd_addr;
    output [31:0] rd_data;

    input [7:0] wr_addr;
    input [31:0] wr_data;

    input C0;  //naming of these doesnt really matter
    input C1;  // C0,C1 select write port width
    input C2;  // C2,C3 select read port width
    input C3;
    input C4;  //C4 selects the alwaysWriteEnable
    input C5;  //C5 selects register bypass
endmodule
/* verilator lint_on UNUSEDSIGNAL */
/* verilator lint_on UNDRIVEN */
/* verilator lint_on UNUSEDPARAM */
