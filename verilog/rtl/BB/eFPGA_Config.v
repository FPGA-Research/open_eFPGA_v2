/// sta-blackbox
/* verilator lint_off UNUSEDSIGNAL */
/* verilator lint_off UNDRIVEN */
/* verilator lint_off UNUSEDPARAM */
module eFPGA_Config (
`ifdef USE_POWER_PINS
    vccd1,
    vssd1,
`endif
    CLK,
    resetn,
    Rx,
    ComActive,
    ReceiveLED,
    s_clk,
    s_data,
    SelfWriteData,
    SelfWriteStrobe,
    ConfigWriteData,
    ConfigWriteStrobe,
    FrameAddressRegister,
    LongFrameStrobe,
    RowSelect
);
    parameter NumberOfRows = 16;
    parameter RowSelectWidth = 5;
    parameter FrameBitsPerRow = 32;
    parameter desync_flag = 20;
`ifdef USE_POWER_PINS
    inout vccd1;
    inout vssd1;
`endif
    input CLK;
    input resetn;
    // UART configuration port
    input Rx;
    output ComActive;
    output ReceiveLED;
    // BitBang configuration port
    input s_clk;
    input s_data;
    // CPU configuration port
    input [32-1:0] SelfWriteData;  // configuration data write port
    input SelfWriteStrobe;  // must decode address and write enable

    output [32-1:0] ConfigWriteData;
    output ConfigWriteStrobe;

    output [FrameBitsPerRow-1:0] FrameAddressRegister;
    output LongFrameStrobe;
    output [RowSelectWidth-1:0] RowSelect;
endmodule
/* verilator lint_on UNUSEDSIGNAL */
/* verilator lint_on UNDRIVEN */
/* verilator lint_on UNUSEDPARAM */
