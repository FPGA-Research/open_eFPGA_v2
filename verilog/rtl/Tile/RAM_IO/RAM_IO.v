/// sta-blackbox
/* verilator lint_off UNDRIVEN */
/* verilator lint_off UNUSEDPARAM */

/* verilator lint_off UNUSEDSIGNAL */
//
module RAM_IO #(
`ifdef EMULATION
    parameter [639:0] Emulate_Bitstream = 640'b0,
`endif
    parameter MaxFramesPerCol = 20,
    parameter FrameBitsPerRow = 32,
    parameter NoConfigBits = 328
) (
`ifdef USE_POWER_PINS
    inout vccd1,  // User area 1 1.8V supply
    inout vssd1,  // User area 1 digital ground
`endif
    //Side.NORTH
    output [3:0] N1BEG,        //Port(Name=N1BEG, IO=OUTPUT, XOffset=0, YOffset=-1, WireCount=4, Side=NORTH)
    output [7:0] N2BEG,        //Port(Name=N2BEG, IO=OUTPUT, XOffset=0, YOffset=-1, WireCount=8, Side=NORTH)
    output [7:0] N2BEGb,        //Port(Name=N2BEGb, IO=OUTPUT, XOffset=0, YOffset=-1, WireCount=8, Side=NORTH)
    output [15:0] N4BEG,        //Port(Name=N4BEG, IO=OUTPUT, XOffset=0, YOffset=-4, WireCount=4, Side=NORTH)
    input [3:0] S1END,  //Port(Name=S1END, IO=INPUT, XOffset=0, YOffset=1, WireCount=4, Side=NORTH)
    input [7:0] S2MID,  //Port(Name=S2MID, IO=INPUT, XOffset=0, YOffset=1, WireCount=8, Side=NORTH)
    input [7:0] S2END,  //Port(Name=S2END, IO=INPUT, XOffset=0, YOffset=1, WireCount=8, Side=NORTH)
    input [15:0] S4END,  //Port(Name=S4END, IO=INPUT, XOffset=0, YOffset=4, WireCount=4, Side=NORTH)
    //Side.WEST
    input [3:0] E1END,  //Port(Name=E1END, IO=INPUT, XOffset=1, YOffset=0, WireCount=4, Side=WEST)
    input [7:0] E2MID,  //Port(Name=E2MID, IO=INPUT, XOffset=1, YOffset=0, WireCount=8, Side=WEST)
    input [7:0] E2END,  //Port(Name=E2END, IO=INPUT, XOffset=1, YOffset=0, WireCount=8, Side=WEST)
    input [15:0] EE4END,        //Port(Name=EE4END, IO=INPUT, XOffset=4, YOffset=0, WireCount=4, Side=WEST)
    input [11:0] E6END,  //Port(Name=E6END, IO=INPUT, XOffset=6, YOffset=0, WireCount=2, Side=WEST)
    output [3:0] W1BEG,        //Port(Name=W1BEG, IO=OUTPUT, XOffset=-1, YOffset=0, WireCount=4, Side=WEST)
    output [7:0] W2BEG,        //Port(Name=W2BEG, IO=OUTPUT, XOffset=-1, YOffset=0, WireCount=8, Side=WEST)
    output [7:0] W2BEGb,        //Port(Name=W2BEGb, IO=OUTPUT, XOffset=-1, YOffset=0, WireCount=8, Side=WEST)
    output [15:0] WW4BEG,        //Port(Name=WW4BEG, IO=OUTPUT, XOffset=-4, YOffset=0, WireCount=4, Side=WEST)
    output [11:0] W6BEG,        //Port(Name=W6BEG, IO=OUTPUT, XOffset=-6, YOffset=0, WireCount=2, Side=WEST)
    //Side.SOUTH
    input [3:0] N1END,  //Port(Name=N1END, IO=INPUT, XOffset=0, YOffset=-1, WireCount=4, Side=SOUTH)
    input [7:0] N2MID,  //Port(Name=N2MID, IO=INPUT, XOffset=0, YOffset=-1, WireCount=8, Side=SOUTH)
    input [7:0] N2END,  //Port(Name=N2END, IO=INPUT, XOffset=0, YOffset=-1, WireCount=8, Side=SOUTH)
    input [15:0] N4END,        //Port(Name=N4END, IO=INPUT, XOffset=0, YOffset=-4, WireCount=4, Side=SOUTH)
    output [3:0] S1BEG,        //Port(Name=S1BEG, IO=OUTPUT, XOffset=0, YOffset=1, WireCount=4, Side=SOUTH)
    output [7:0] S2BEG,        //Port(Name=S2BEG, IO=OUTPUT, XOffset=0, YOffset=1, WireCount=8, Side=SOUTH)
    output [7:0] S2BEGb,        //Port(Name=S2BEGb, IO=OUTPUT, XOffset=0, YOffset=1, WireCount=8, Side=SOUTH)
    output [15:0] S4BEG,        //Port(Name=S4BEG, IO=OUTPUT, XOffset=0, YOffset=4, WireCount=4, Side=SOUTH)
    input RAM2FAB_D0_I0,
    input RAM2FAB_D0_I1,
    input RAM2FAB_D0_I2,
    input RAM2FAB_D0_I3,
    input RAM2FAB_D1_I0,
    input RAM2FAB_D1_I1,
    input RAM2FAB_D1_I2,
    input RAM2FAB_D1_I3,
    input RAM2FAB_D2_I0,
    input RAM2FAB_D2_I1,
    input RAM2FAB_D2_I2,
    input RAM2FAB_D2_I3,
    input RAM2FAB_D3_I0,
    input RAM2FAB_D3_I1,
    input RAM2FAB_D3_I2,
    input RAM2FAB_D3_I3,
    output FAB2RAM_D0_O0,
    output FAB2RAM_D0_O1,
    output FAB2RAM_D0_O2,
    output FAB2RAM_D0_O3,
    output FAB2RAM_D1_O0,
    output FAB2RAM_D1_O1,
    output FAB2RAM_D1_O2,
    output FAB2RAM_D1_O3,
    output FAB2RAM_D2_O0,
    output FAB2RAM_D2_O1,
    output FAB2RAM_D2_O2,
    output FAB2RAM_D2_O3,
    output FAB2RAM_D3_O0,
    output FAB2RAM_D3_O1,
    output FAB2RAM_D3_O2,
    output FAB2RAM_D3_O3,
    output FAB2RAM_A0_O0,
    output FAB2RAM_A0_O1,
    output FAB2RAM_A0_O2,
    output FAB2RAM_A0_O3,
    output FAB2RAM_A1_O0,
    output FAB2RAM_A1_O1,
    output FAB2RAM_A1_O2,
    output FAB2RAM_A1_O3,
    output FAB2RAM_C_O0,
    output FAB2RAM_C_O1,
    output FAB2RAM_C_O2,
    output FAB2RAM_C_O3,
    output Config_accessC_bit0,
    output Config_accessC_bit1,
    output Config_accessC_bit2,
    output Config_accessC_bit3,
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
/* verilator lint_on UNUSEDSIGNAL */
/* verilator lint_on UNDRIVEN */
/* verilator lint_on UNUSEDPARAM */
