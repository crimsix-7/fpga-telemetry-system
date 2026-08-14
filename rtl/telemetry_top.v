`timescale 1ns/1ps

module telemetry_top (
    input  wire       clk,
    input  wire       reset,
    input  wire       enable,
    output reg  [7:0] packet_count
);

    // Update the packet counter on every rising edge of the clock.
    always @(posedge clk) begin

        // Synchronous reset:
        // If reset is high when the clock rises,
        // return the packet counter to zero.
        if (reset) begin
            packet_count <= 8'd0;
        end

        // Otherwise, increment the counter when enabled.
        else if (enable) begin
            packet_count <= packet_count + 8'd1;
        end

        // If neither reset nor enable is active,
        // no assignment is made and packet_count
        // keeps its previous value.

    end

endmodule