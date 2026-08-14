`timescale 1ns/1ps

module uart_tx #(
    parameter CLKS_PER_BIT = 4
)(
    input  wire       clk,
    input  wire       reset,
    input  wire       start,
    input  wire [7:0] data_in,

    output reg        tx,
    output reg        busy,
    output reg        done
);

    localparam STATE_IDLE  = 3'd0;
    localparam STATE_START = 3'd1;
    localparam STATE_DATA  = 3'd2;
    localparam STATE_STOP  = 3'd3;
    localparam STATE_DONE  = 3'd4;

    reg [2:0] state;
    reg [15:0] clk_count;
    reg [2:0] bit_index;
    reg [7:0] data_reg;

    always @(posedge clk) begin

        if (reset) begin

            state     <= STATE_IDLE;
            tx        <= 1'b1;
            busy      <= 1'b0;
            done      <= 1'b0;
            clk_count <= 16'd0;
            bit_index <= 3'd0;
            data_reg  <= 8'd0;

        end

        else begin

            done <= 1'b0;

            case (state)

                STATE_IDLE: begin

                    tx        <= 1'b1;
                    busy      <= 1'b0;
                    clk_count <= 16'd0;
                    bit_index <= 3'd0;

                    if (start) begin

                        data_reg <= data_in;
                        busy     <= 1'b1;
                        state    <= STATE_START;

                    end
                end


                STATE_START: begin

                    tx <= 1'b0;

                    if (clk_count == CLKS_PER_BIT - 1) begin
                        clk_count <= 16'd0;
                        state     <= STATE_DATA;
                    end
                    else begin
                        clk_count <= clk_count + 1'b1;
                    end

                end


                STATE_DATA: begin

                    tx <= data_reg[bit_index];

                    if (clk_count == CLKS_PER_BIT - 1) begin

                        clk_count <= 16'd0;

                        if (bit_index == 3'd7) begin
                            bit_index <= 3'd0;
                            state     <= STATE_STOP;
                        end
                        else begin
                            bit_index <= bit_index + 1'b1;
                        end

                    end
                    else begin
                        clk_count <= clk_count + 1'b1;
                    end

                end


                STATE_STOP: begin

                    tx <= 1'b1;

                    if (clk_count == CLKS_PER_BIT - 1) begin
                        clk_count <= 16'd0;
                        state     <= STATE_DONE;
                    end
                    else begin
                        clk_count <= clk_count + 1'b1;
                    end

                end


                STATE_DONE: begin

                    tx   <= 1'b1;
                    busy <= 1'b0;
                    done <= 1'b1;

                    state <= STATE_IDLE;

                end


                default: begin

                    state <= STATE_IDLE;
                    tx    <= 1'b1;
                    busy  <= 1'b0;

                end

            endcase
        end
    end

endmodule