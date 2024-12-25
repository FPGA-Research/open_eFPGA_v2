// SPDX-FileCopyrightText: 2020 Efabless Corporation
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// SPDX-License-Identifier: Apache-2.0

`default_nettype none
/*
 *-------------------------------------------------------------
 *EFPGA_USED_NUM_IOS
 * user_project_wrapper
 *
 * This wrapper enumerates all of the pins available to the
 * user for the user project.
 *
 * An example user project is provided in this wrapper.  The
 * example should be removed and replaced with the actual
 * user project.
 *
 *-------------------------------------------------------------
 */

module user_project_wrapper #(
    /* verilator lint_off UNUSEDPARAM */
    parameter BITS = 32
    /* verilator lint_on UNUSEDPARAM */
) (
`ifdef USE_POWER_PINS
    inout vdda1,  // User area 1 3.3V supply
    inout vdda2,  // User area 2 3.3V supply
    inout vssa1,  // User area 1 analog ground
    inout vssa2,  // User area 2 analog ground
    inout vccd1,  // User area 1 1.8V supply
    inout vccd2,  // User area 2 1.8v supply
    inout vssd1,  // User area 1 digital ground
    inout vssd2,  // User area 2 digital ground
`endif

    // Wishbone Slave ports (WB MI A)
    input wb_clk_i,
    input wb_rst_i,
    input wbs_stb_i,
    input wbs_cyc_i,
    input wbs_we_i,
    /* verilator lint_off UNUSEDSIGNAL*/
    input [3:0] wbs_sel_i,
    /* verilator lint_off UNUSEDSIGNAL*/
    input [31:0] wbs_dat_i,
    input [31:0] wbs_adr_i,
    output reg wbs_ack_o,
    output [31:0] wbs_dat_o,

    // Logic Analyzer Signals
    input  [127:0] la_data_in,
    output [127:0] la_data_out,
    input  [127:0] la_oenb,

    // IOs
    input  [`MPRJ_IO_PADS-1:0] io_in,
    output [`MPRJ_IO_PADS-1:0] io_out,
    output [`MPRJ_IO_PADS-1:0] io_oeb,

    // Analog (direct connection to GPIO pad---use with caution)
    // Note that analog I/O is not available on the 7 lowest-numbered
    // GPIO pads, and so the analog_io indexing is offset from the
    // GPIO indexing by 7 (also upper 2 GPIOs do not have analog_io).
    inout [`MPRJ_IO_PADS-10:0] analog_io,

    // Independent clock (on independent integer divider)
    input user_clock2,

    // User maskable interrupt signals
    output [2:0] user_irq
);

    /*--------------------------------------*/
    /* User project is instantiated  here   */
    /*--------------------------------------*/

    localparam NUM_OF_CARAVEL_IOS = 7;

    // The number of IOs that can be used by the FPGA user design
    localparam NUM_FABRIC_USER_IOS = 24;
    localparam [31:0] BASE_WB_ADDRESS = 32'h3000_0000;
    localparam [31:0] CONFIG_DATA_WB_ADDRESS = BASE_WB_ADDRESS;

    // The Output enable input of the IO cell is inverted, so define parameters for increased readability
    localparam OUTPUT_ENABLE = 1'b0;
    localparam OUTPUT_DISABLE = 1'b1;

    // Fabric IOs
    localparam EXTERNAL_CLK_IO = 7;
    localparam CLK_SEL_0_IO = 8;
    localparam CLK_SEL_1_IO = 9;

    localparam S_CLK_IO = 10;
    localparam S_DATA_IO = 11;
    localparam EFPGA_UART_RX_IO = 12;
    localparam RECEIVE_LED_IO = 13;

    // Clock select definitions
    localparam CLK_SEL_0 = 0;
    localparam CLK_SEL_1 = 1;

    // eFPGA IOs
    localparam EFPGA_USED_NUM_IOS = 23;  // Due to pin count limitation, we don't use all eFPGA IOs
    localparam EFPGA_IO_LOWEST = RECEIVE_LED_IO + 1; // This maps to MPRJ_IO[14], which is io[0] on the FABulous board
    localparam EFPGA_IO_HIGHEST = EFPGA_IO_LOWEST + EFPGA_USED_NUM_IOS - 1;

    localparam RESETN_IO = EFPGA_IO_HIGHEST + 1;  // resetn is located after user IOs

    wire [NUM_FABRIC_USER_IOS-1:0] I_top;
    wire [NUM_FABRIC_USER_IOS-1:0] T_top;
    wire [NUM_FABRIC_USER_IOS-1:0] O_top;

    wire CLK;  // This clock can go to the CPU (connects to the fabric LUT output flops)
    wire resetn;
    wire external_clock;

    // CPU configuration port
    wire SelfWriteStrobe;  // must decode address and write enable
    wire [32-1:0] SelfWriteData;  // configuration data write port

    // Wishbone configuration signals
    wire config_strobe;
    reg [31:0] config_data;

    //Whishbone clock domain crossing signals
    reg wb_to_fpga;
    reg feedback0;
    reg feedback1;

    // UART configuration port
    wire efpga_uart_rx;
    wire ReceiveLED;

    // BitBang configuration port
    wire s_clk;
    wire s_data;

    wire [1:0] clk_sel;

    // Latch for config_strobe
    reg config_strobe_reg1 = 0;
    reg config_strobe_reg2 = 0;
    reg config_strobe_reg3 = 0;

    // Drive unused IOs low
    assign wbs_dat_o = 32'b0;


    eFPGA_top eFPGA_top_i (
`ifdef USE_POWER_PINS
        .vccd1(vccd1),  // User area 1 1.8V supply
        .vssd1(vssd1),  // User area 1 digital ground
`endif
        .CLK(CLK),
        .resetn(resetn),
        .SelfWriteStrobe(SelfWriteStrobe),
        .SelfWriteData(SelfWriteData),
        .Rx(efpga_uart_rx),
        /* verilator lint_off PINCONNECTEMPTY */
        .ComActive(),
        /* verilator lint_on PINCONNECTEMPTY */
        .ReceiveLED(ReceiveLED),
        .s_clk(s_clk),
        .s_data(s_data),
        /* verilator lint_off PINCONNECTEMPTY */
        .A_config_C(),
        .B_config_C(),
        .Config_accessC(),
        /* verilator lint_on PINCONNECTEMPTY */
        .I_top(I_top),
        .O_top(O_top),
        .T_top(T_top)
    );

    //TODO test behaviour of this clock domain crossing (assume condition is
    //true
    always @(posedge wb_clk_i or negedge resetn) begin
        if (!resetn) begin
            wb_to_fpga <= 1'b0;
        end else begin
            if (feedback1 && !(wbs_stb_i && wbs_cyc_i && wbs_we_i &&  (wbs_adr_i == CONFIG_DATA_WB_ADDRESS))) begin
                wb_to_fpga <= 1'b0;
            end else if (wbs_stb_i && wbs_cyc_i && wbs_we_i && (wbs_adr_i == CONFIG_DATA_WB_ADDRESS)) begin
                wb_to_fpga <= 1'b1;
            end else begin
                wb_to_fpga <= wb_to_fpga;
            end
        end
    end

    always @(posedge wb_clk_i or negedge resetn) begin
        if (!resetn) begin
            feedback0 <= 1'b0;
            feedback1 <= 1'b0;
        end else begin
            feedback0 <= config_strobe_reg2;
            feedback1 <= feedback0;
        end
    end

    always @(posedge CLK or negedge resetn) begin
        if (!resetn) begin
            config_strobe_reg1 <= 1'b0;
            config_strobe_reg2 <= 1'b0;
            config_strobe_reg3 <= 1'b0;
        end else begin
            config_strobe_reg1 <= wb_to_fpga;
            config_strobe_reg2 <= config_strobe_reg1;
            config_strobe_reg3 <= config_strobe_reg2;
        end
    end

    assign config_strobe = (!config_strobe_reg3 && (config_strobe_reg2)); //posedge pulse for config strobe

    // Write the config data register from the wishbone bus
    always @(posedge wb_clk_i) begin
        if (wb_rst_i) begin
            config_data <= 32'b0;
        end else begin
            if (wbs_stb_i && wbs_cyc_i && wbs_we_i && (wbs_adr_i == CONFIG_DATA_WB_ADDRESS)) begin
                config_data <= wbs_dat_i;
            end
        end
    end

    // NOTE: Taken from Matt Venns wishbone demo:
    // https://github.com/mattvenn/wishbone_buttons_leds/blob/master/wb_buttons_leds.v

    // acks
    always @(posedge wb_clk_i) begin
        if (wb_rst_i) wbs_ack_o <= 1'b0;
        else
            // return ack immediately
            wbs_ack_o <= (wbs_stb_i && (wbs_adr_i == CONFIG_DATA_WB_ADDRESS));
    end

    assign external_clock = io_in[EXTERNAL_CLK_IO];
    assign clk_sel = {io_in[CLK_SEL_1_IO], io_in[CLK_SEL_0_IO]};
    assign s_clk = io_in[S_CLK_IO];
    assign s_data = io_in[S_DATA_IO];
    assign efpga_uart_rx = io_in[EFPGA_UART_RX_IO];
    assign io_out[RECEIVE_LED_IO] = ReceiveLED;

    assign resetn = io_in[RESETN_IO];

    assign io_oeb[EXTERNAL_CLK_IO] = OUTPUT_DISABLE;
    assign io_oeb[CLK_SEL_0_IO] = OUTPUT_DISABLE;
    assign io_oeb[CLK_SEL_1_IO] = OUTPUT_DISABLE;
    assign io_oeb[S_CLK_IO] = OUTPUT_DISABLE;
    assign io_oeb[S_DATA_IO] = OUTPUT_DISABLE;
    assign io_oeb[EFPGA_UART_RX_IO] = OUTPUT_DISABLE;
    assign io_oeb[RECEIVE_LED_IO] = OUTPUT_ENABLE;  // The only fabric IO output

    assign io_oeb[RESETN_IO] = OUTPUT_DISABLE;

    // Drive all unused outputs low
    assign io_out[EXTERNAL_CLK_IO] = 1'b0;
    assign io_out[CLK_SEL_0_IO] = 1'b0;
    assign io_out[CLK_SEL_1_IO] = 1'b0;
    assign io_out[S_CLK_IO] = 1'b0;
    assign io_out[S_DATA_IO] = 1'b0;
    assign io_out[EFPGA_UART_RX_IO] = 1'b0;
    assign io_out[RESETN_IO] = 1'b0;

    // Config signals
    assign SelfWriteStrobe = config_strobe;
    assign SelfWriteData = config_data;

    // Debug signals
    assign la_data_out[127:126] = {ReceiveLED, efpga_uart_rx};
    assign la_data_out[125:0] = {126{1'b0}};

    // eFPGA external IOs
    assign O_top[EFPGA_USED_NUM_IOS-1:0] = io_in[EFPGA_IO_HIGHEST:EFPGA_IO_LOWEST];
    assign io_out[EFPGA_IO_HIGHEST:EFPGA_IO_LOWEST] = I_top[EFPGA_USED_NUM_IOS-1:0];
    assign io_oeb[EFPGA_IO_HIGHEST:EFPGA_IO_LOWEST] = T_top[EFPGA_USED_NUM_IOS-1:0];

    assign CLK = clk_sel[CLK_SEL_0] ? (clk_sel[CLK_SEL_1] ? user_clock2 : wb_clk_i) : external_clock;

    assign user_irq = {3{1'b0}};

    // This just drives the highest fabric IO to a constant 0
    assign O_top[EFPGA_USED_NUM_IOS] = 1'b0;
    assign io_out[NUM_OF_CARAVEL_IOS-1:0] = {NUM_OF_CARAVEL_IOS{1'b0}};
    assign io_oeb[NUM_OF_CARAVEL_IOS-1:0] = {NUM_OF_CARAVEL_IOS{1'b0}};

endmodule  // user_project_wrapper

`default_nettype wire
