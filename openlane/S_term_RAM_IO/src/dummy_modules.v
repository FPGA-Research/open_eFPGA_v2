`timescale 1ns / 1ps
/* verilator lint_off UNOPTFLAT */
// These modules are just used as dummies since they are normally
// only used in the simulation, but still instantiated in the fabric

module clk_buf (
    input  A,
    output X
);
    assign X = A;
endmodule

module break_comb_loop (
    input  A,
    output X
);
    assign X = A;
endmodule
/* verilator lint_on UNOPTFLAT */
