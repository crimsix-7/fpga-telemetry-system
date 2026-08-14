`timescale 1ns/1ps

module crc16 (
    input  wire        clk,
    input  wire        reset,
    input  wire        clear,
    input  wire [7:0]  data_in,
    input  wire        data_valid,
    output reg  [15:0] crc_out
);

    integer i;
    reg [15:0] crc_next;

    always @(posedge clk) begin

        if (reset || clear) begin
            crc_out <= 16'hFFFF;
        end

        else if (data_valid) begin

            crc_next = crc_out ^ (data_in << 8);

            for (i = 0; i < 8; i = i + 1) begin

                if (crc_next[15])
                    crc_next = (crc_next << 1) ^ 16'h1021;
                else
                    crc_next = crc_next << 1;

            end

            crc_out <= crc_next;

        end
    end

endmodule