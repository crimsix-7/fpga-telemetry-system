`timescale 1ns/1ps

module telemetry_packetizer (

    // Clock and control

    input  wire       clk,
    input  wire       reset,
    input  wire       start,

    // Telemetry inputs

    input  wire [7:0] packet_count,
    input  wire [7:0] temperature,
    input  wire [7:0] battery,
    input  wire [7:0] system_status,
    input  wire [7:0] sensor_status,

    // Packetizer outputs

    output reg  [7:0] byte_out,
    output reg        byte_valid,
    output reg        busy,
    output reg        done
);


    // FSM state definitions

    localparam STATE_IDLE          = 4'd0;
    localparam STATE_HEADER        = 4'd1;
    localparam STATE_COUNT         = 4'd2;
    localparam STATE_TEMP          = 4'd3;
    localparam STATE_BATTERY       = 4'd4;
    localparam STATE_SYSTEM_STATUS = 4'd5;
    localparam STATE_SENSOR_STATUS = 4'd6;
    localparam STATE_DONE          = 4'd7;


    reg [3:0] state;


    // Latched telemetry values
    // These registers capture a snapshot of the telemetry inputs when a new packet starts.

    reg [7:0] saved_packet_count;
    reg [7:0] saved_temperature;
    reg [7:0] saved_battery;
    reg [7:0] saved_system_status;
    reg [7:0] saved_sensor_status;


    // Packetizer state machine

    always @(posedge clk) begin

        if (reset) begin

            state               <= STATE_IDLE;

            byte_out            <= 8'd0;
            byte_valid          <= 1'b0;
            busy                <= 1'b0;
            done                <= 1'b0;

            saved_packet_count  <= 8'd0;
            saved_temperature   <= 8'd0;
            saved_battery       <= 8'd0;
            saved_system_status <= 8'd0;
            saved_sensor_status <= 8'd0;

        end

        else begin

            // These are one-cycle pulse signals.
            // Individual states set them high when required.
            byte_valid <= 1'b0;
            done       <= 1'b0;


            case (state)

                // IDLE
                // Wait for a request to generate a packet.

                STATE_IDLE: begin

                    busy <= 1'b0;

                    if (start) begin

                        // Capture one consistent snapshot of all
                        // telemetry data.

                        saved_packet_count  <= packet_count;
                        saved_temperature   <= temperature;
                        saved_battery       <= battery;
                        saved_system_status <= system_status;
                        saved_sensor_status <= sensor_status;

                        busy  <= 1'b1;
                        state <= STATE_HEADER;

                    end
                end


                // Byte 0: Header

                STATE_HEADER: begin

                    byte_out   <= 8'hA5;
                    byte_valid <= 1'b1;

                    state <= STATE_COUNT;

                end


                // Byte 1: Packet sequence number

                STATE_COUNT: begin

                    byte_out   <= saved_packet_count;
                    byte_valid <= 1'b1;

                    state <= STATE_TEMP;

                end


                // Byte 2: Temperature

                STATE_TEMP: begin

                    byte_out   <= saved_temperature;
                    byte_valid <= 1'b1;

                    state <= STATE_BATTERY;

                end


                // ------------------------------------------------
                // Byte 3: Battery voltage
                // ------------------------------------------------

                STATE_BATTERY: begin

                    byte_out   <= saved_battery;
                    byte_valid <= 1'b1;

                    state <= STATE_SYSTEM_STATUS;

                end


                // ------------------------------------------------
                // Byte 4: System status
                // ------------------------------------------------

                STATE_SYSTEM_STATUS: begin

                    byte_out   <= saved_system_status;
                    byte_valid <= 1'b1;

                    state <= STATE_SENSOR_STATUS;

                end

                // Byte 5: Sensor status

                STATE_SENSOR_STATUS: begin

                    byte_out   <= saved_sensor_status;
                    byte_valid <= 1'b1;

                    state <= STATE_DONE;

                end

                // Packet complete

                STATE_DONE: begin

                    busy <= 1'b0;
                    done <= 1'b1;

                    state <= STATE_IDLE;

                end


                // Safety fallback

                default: begin

                    state <= STATE_IDLE;
                    busy  <= 1'b0;

                end

            endcase
        end
    end

endmodule