`timescale 1ns/1ps
module sky130_fd_sc_hd__inv (A, Y);

input A;
output Y;

assign Y = ~A;

endmodule
