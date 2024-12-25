/*
module \$_DLATCH_N_ (E, D, Q);
  //wire [1023:0] _TECHMAP_DO_ = "simplemap; opt";
  input E, D;
  output Q;
//  TLATNX1M _TECHMAP_REPLACE_ (
  sky130_fd_sc_hd__udp_dlatch_p _TECHMAP_REPLACE_ (
    .D(D),
    .GATE(E),
    .Q(Q)
  );
endmodule

module \$_DLATCH_P_ (E, D, Q);
  //wire [1023:0] _TECHMAP_DO_ = "simplemap; opt";
  input E, D;
  output Q;
//  TLATNX1M _TECHMAP_REPLACE_ (
  sky130_fd_sc_hd__udp_dlatch_p _TECHMAP_REPLACE_ (
    .D(D),
    .GATE(E),
    .Q(Q)
  );
endmodule
module \$_DLATCH_N_ (E, D, Q);
  input E, D;
  output Q;
  sky130_fd_sc_hd__dlrtp_1 _TECHMAP_REPLACE_ (
    .D(D),
    .GATE(E),
    .RESET_B(1'b1), //disable reset (active low)
    .Q(Q)
  );
endmodule

module \$_DLATCH_P_ (E, D, Q);
  input E, D;
  output Q;
  sky130_fd_sc_hd__dlrtp_1 _TECHMAP_REPLACE_ (
    .D(D),
    .GATE(E),
    .RESET_B(1'b1), //disable reset (active low)
    .Q(Q)
  );
endmodule
*/

/*
module \$_DLATCH_N_ (E, D, Q, QN);
  input E, D;
  output Q, QN;
  sky130_fd_sc_hd__dlxbn_1 _TECHMAP_REPLACE_ (
    .D(D),
    .GATE(E),
    .Q(Q),
    .Q_N(QN)
  );
endmodule

module \$_DLATCH_P_ (E, D, Q, QN);
  input E, D;
  output Q, QN;
  sky130_fd_sc_hd__dlxbp_1 _TECHMAP_REPLACE_ (
    .D(D),
    .GATE(E),
    .Q(Q),
    .Q_N(QN)
  );
endmodule
*/

module LHQD1 (E, D, Q, QN);
  input E, D;
  output Q, QN;
  sky130_fd_sc_hd__dlxbp_1 _TECHMAP_REPLACE_ (
    .D(D),
    .GATE(E),
    .Q(Q),
    .Q_N(QN)
  );
endmodule

/*
module cus_mux41_buf (A0, A1, A2, A3, S0, S0N, S1, S1N, X);
  input A0, A1, A2, A3, S0, S0N, S1, S1N;
  output X;
	cus_tg_mux41_buf _TECHMAP_REPLACE_ (
	.A0 (A0),
	.A1 (A1),
	.A2 (A2),
	.A3 (A3),
	.S0 (S0),
	.S0N (S0N),
	.S1 (S1),
	.S1N (S1N),
	.X (X)
	);
endmodule
*/

module cus_mux41_buf (A0, A1, A2, A3, S0, S0N, S1, S1N, X);
  input A0, A1, A2, A3, S0, S0N, S1, S1N;
  output X;
  sky130_fd_sc_hd__mux4_1 _TECHMAP_REPLACE_ (
      .X(X),
      .A0(A0),
      .A1(A1),
      .A2(A2),
      .A3(A3),
      .S0(S0),
      .S1(S1)
  );
endmodule
