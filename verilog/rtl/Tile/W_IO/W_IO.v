/// sta-blackbox
/* verilator lint_off UNDRIVEN */
/* verilator lint_off UNUSEDPARAM */
/* verilator lint_off UNUSEDSIGNAL */

//
module W_IO #(
`ifdef EMULATION
    parameter [639:0] Emulate_Bitstream = 640'b0,
`endif
    parameter MaxFramesPerCol = 20,
    parameter FrameBitsPerRow = 32,
    parameter NoConfigBits = 114
) (
`ifdef USE_POWER_PINS
    inout vccd1,  // User area 1 1.8V supply
    inout vssd1,  // User area 1 digital ground
`endif
    //Side.EAST
    output [3:0] E1BEG,  //Port(Name=E1BEG, IO=OUTPUT, XOffset=1, YOffset=0, WireCount=4, Side=EAST)
    output [7:0] E2BEG,  //Port(Name=E2BEG, IO=OUTPUT, XOffset=1, YOffset=0, WireCount=8, Side=EAST)
    output [7:0] E2BEGb,        //Port(Name=E2BEGb, IO=OUTPUT, XOffset=1, YOffset=0, WireCount=8, Side=EAST)
    output [15:0] EE4BEG,        //Port(Name=EE4BEG, IO=OUTPUT, XOffset=4, YOffset=0, WireCount=4, Side=EAST)
    output [11:0] E6BEG,        //Port(Name=E6BEG, IO=OUTPUT, XOffset=6, YOffset=0, WireCount=2, Side=EAST)
    input [3:0] W1END,  //Port(Name=W1END, IO=INPUT, XOffset=-1, YOffset=0, WireCount=4, Side=EAST)
    input [7:0] W2MID,  //Port(Name=W2MID, IO=INPUT, XOffset=-1, YOffset=0, WireCount=8, Side=EAST)
    input [7:0] W2END,  //Port(Name=W2END, IO=INPUT, XOffset=-1, YOffset=0, WireCount=8, Side=EAST)
    input [15:0] WW4END,        //Port(Name=WW4END, IO=INPUT, XOffset=-4, YOffset=0, WireCount=4, Side=EAST)
    input [11:0] W6END,  //Port(Name=W6END, IO=INPUT, XOffset=-6, YOffset=0, WireCount=2, Side=EAST)
    input A_O_top,
    output A_I_top,
    output A_T_top,
    input B_O_top,
    output B_I_top,
    output B_T_top,
    output A_config_C_bit0,
    output A_config_C_bit1,
    output A_config_C_bit2,
    output A_config_C_bit3,
    output B_config_C_bit0,
    output B_config_C_bit1,
    output B_config_C_bit2,
    output B_config_C_bit3,
    //Tile IO ports from BELs
    input UserCLK,
    output UserCLKo,
    input [FrameBitsPerRow -1:0] FrameData,  //CONFIG_PORT
    output [FrameBitsPerRow -1:0] FrameData_O,
    input [MaxFramesPerCol -1:0] FrameStrobe,  //CONFIG_PORT
    output [MaxFramesPerCol -1:0] FrameStrobe_O
    //global
);
endmodule
/* verilator lint_off UNUSEDSIGNAL */
/* verilator lint_on UNUSEDSIGNAL */
/* verilator lint_on UNDRIVEN */
/* verilator lint_on UNUSEDPARAM */
