///  sta-blackbox
/* verilator lint_off UNOPTFLAT *//* verilator lint_off UNUSEDSIGNAL */
/* verilator lint_off UNUSEDPARAM */

`timescale 1ns/1ps
module N_term_single_ConfigMem
    #(
`ifdef EMULATION
        parameter [639:0] Emulate_Bitstream=640'b0,
`endif
        parameter MaxFramesPerCol=20,
        parameter FrameBitsPerRow=32,
        parameter NoConfigBits=0
    )
    (
        input [FrameBitsPerRow - 1:0] FrameData,
        input [MaxFramesPerCol - 1:0] FrameStrobe,
        output [NoConfigBits - 1:0] ConfigBits,
        output [NoConfigBits - 1:0] ConfigBits_N
    );

`ifdef EMULATION
`else

 //instantiate frame latches
`endif
endmodule
/* verilator lint_on UNOPTFLAT *//* verilator lint_on UNUSEDSIGNAL */
/* verilator lint_on UNUSEDPARAM */

