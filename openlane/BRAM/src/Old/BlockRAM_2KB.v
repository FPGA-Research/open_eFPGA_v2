module BlockRAM_2KB (rd_clk, rd_addr, rd_data, wr_clk, wr_en, wr_addr, wr_data, C0, C1, C2, C3, C4);
    parameter ACTIVE_HIGH_ENABLE_BITS = 1;

    input rd_clk;
    input [10:0] rd_addr;
    output [31:0] rd_data;
    
    input wr_clk;
    input wr_en; // active low
    input [10:0] wr_addr;
    input [31:0] wr_data;
    
    input C0;//naming of these doesnt really matter
    input C1;// C0,C1 select read port width
    input C2;// C2,C3 select write port width
    input C3;
    input C4; //C4 selects register bypass
      // NOTE, the read enable is currently constantly ON
      // NOTE, the R/W port on the standard cell is used only in write mode
      // NOTE, enable ports are active lows
    wire [1:0] rd_port_configuration;
    wire [1:0] wr_port_configuration;
    wire optional_register_enabled_configuration;
    assign rd_port_configuration = {C0, C1};
    assign wr_port_configuration = {C2, C3};
    assign optional_register_enabled_configuration = C4;
    
    reg memWriteEnable;
    always @ (*) begin // write enable
        if(ACTIVE_HIGH_ENABLE_BITS == 1)
            memWriteEnable = (!wr_en);
        else
            memWriteEnable = wr_en;
    end
    reg [3:0] mem_wr_mask;
    always @ (*) begin //write port config -> mask
        if(wr_port_configuration == 0) begin
            mem_wr_mask = 4'b1111;
        end else if(wr_port_configuration == 1) begin
            if(wr_addr[9] == 0) begin
                mem_wr_mask = 4'b0011;
            end else begin
                mem_wr_mask = 4'b1100;
            end
        end else if(wr_port_configuration == 2) begin
            if(wr_addr[10:9] == 0) begin
                mem_wr_mask = 4'b0001;
            end else if(wr_addr[10:9] == 1) begin
                mem_wr_mask = 4'b0010;
            end else if(wr_addr[10:9] == 2) begin
                mem_wr_mask = 4'b0100;
            end else begin
                mem_wr_mask = 4'b1000;
            end
        end
    end
    wire [31:0] mem_dout;
//sram_1rw1r_32_256_8_sky130 memory_cell(                             //dout0 is unused
//    .clk0(wr_clk),.csb0(memWriteEnable),.web0(memWriteEnable),.wmask0(mem_wr_mask),.addr0(wr_addr[7:0]),.din0(wr_data),//.dout0(),
//    .clk1(rd_clk),.csb1(1'b0),.addr1(rd_addr[7:0]),.dout1(mem_dout)
//);
sky130_sram_2kbyte_1rw1r_32x512_8 memory_cell(                             //dout0 is unused
    .clk0(wr_clk),.csb0(memWriteEnable),.web0(memWriteEnable),.wmask0(mem_wr_mask),.addr0(wr_addr[8:0]),.din0(wr_data),//.dout0(),
    .clk1(rd_clk),.csb1(1'b0),.addr1(rd_addr[8:0]),.dout1(mem_dout)
);

    reg [1:0] rd_dout_sel;
    always @ (posedge rd_clk) begin
        rd_dout_sel <= rd_addr[10:9];
    end
    reg [31:0] rd_dout_muxed;
    always @ (*) begin
        rd_dout_muxed[31:0] = mem_dout[31:0]; // a default value. Could be 32'dx if tools support it for logic saving!
        if(rd_port_configuration == 0) begin
            rd_dout_muxed[31:0] = mem_dout[31:0];
        end else if(rd_port_configuration == 1) begin
            if(rd_dout_sel[0] == 0) begin
                rd_dout_muxed[15:0] = mem_dout[15:0];
            end else begin
                rd_dout_muxed[15:0] = mem_dout[31:16];
            end
        end else if(rd_port_configuration == 2) begin
            if(rd_dout_sel == 0) begin
                rd_dout_muxed[7:0] = mem_dout[7:0];
            end else if(rd_dout_sel == 1) begin
                rd_dout_muxed[7:0] = mem_dout[15:8];
            end else if(rd_dout_sel == 2) begin
                rd_dout_muxed[7:0] = mem_dout[23:16];
            end else begin
                rd_dout_muxed[7:0] = mem_dout[31:24];
            end
        end
    end
    reg [31:0] rd_dout_additional_register;
    always @ (posedge rd_clk) begin
        rd_dout_additional_register <= rd_dout_muxed;
    end
    reg [31:0] final_dout;
    assign rd_data = final_dout;
    always @ (*) begin
        if(optional_register_enabled_configuration) begin
            final_dout = rd_dout_additional_register;
        end else begin
            final_dout = rd_dout_muxed;
        end
    end
endmodule

//(* blackbox *)
//module sky130_sram_2kbyte_1rw1r_32x512_8(
//// Port 0: RW
//    clk0,csb0,web0,wmask0,addr0,din0,dout0,
//// Port 1: R
//    clk1,csb1,addr1,dout1
//  );
//
//  input  clk0; // clock
//  input   csb0; // active low chip select
//  input  web0; // active low write control
//  input [NUM_WMASKS-1:0]   wmask0; // write mask
//  input [ADDR_WIDTH-1:0]  addr0;
//  input [DATA_WIDTH-1:0]  din0;
//  output [DATA_WIDTH-1:0] dout0;
//  input  clk1; // clock
//  input   csb1; // active low chip select
//  input [ADDR_WIDTH-1:0]  addr1;
//  output [DATA_WIDTH-1:0] dout1;
//endmodule
