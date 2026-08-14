`timescale 1ns/1ps

module telemetry_system (

    input  wire       clk,
    input  wire       reset,
    input  wire       start,

    input  wire [7:0] packet_count,
    input  wire [7:0] temperature,
    input  wire [7:0] battery,

    // Health / fault inputs
    input wire fpga_healthy,
    input wire sensor_subsystem_healthy,
    input wire comms_healthy,
    input wire watchdog_active,

    input wire low_battery,
    input wire overtemperature,

    input wire temp_sensor_healthy,
    input wire imu_healthy,
    input wire gps_healthy,
    input wire power_monitor_healthy,

    output wire tx,
    output reg  busy,
    output reg  done
);


    // ========================================================
    // Fault manager
    // ========================================================

    wire [7:0] system_status;
    wire [7:0] sensor_status;


    fault_manager fault_unit (

        .fpga_healthy(fpga_healthy),
        .sensor_subsystem_healthy(sensor_subsystem_healthy),
        .comms_healthy(comms_healthy),
        .watchdog_active(watchdog_active),

        .low_battery(low_battery),
        .overtemperature(overtemperature),

        .temp_sensor_healthy(temp_sensor_healthy),
        .imu_healthy(imu_healthy),
        .gps_healthy(gps_healthy),
        .power_monitor_healthy(power_monitor_healthy),

        .system_status(system_status),
        .sensor_status(sensor_status)

    );


    // ========================================================
    // Packetizer
    // ========================================================

    reg        packetizer_start;

    wire [7:0] packetizer_byte;
    wire       packetizer_valid;
    wire       packetizer_busy;
    wire       packetizer_done;


    telemetry_packetizer packetizer (

        .clk(clk),
        .reset(reset),
        .start(packetizer_start),

        .packet_count(packet_count),
        .temperature(temperature),
        .battery(battery),

        .system_status(system_status),
        .sensor_status(sensor_status),

        .byte_out(packetizer_byte),
        .byte_valid(packetizer_valid),
        .busy(packetizer_busy),
        .done(packetizer_done)

    );


    // ========================================================
    // CRC
    // ========================================================

    reg         crc_clear;
    wire [15:0] crc_value;


    crc16 crc_unit (

        .clk(clk),
        .reset(reset),
        .clear(crc_clear),

        .data_in(packetizer_byte),
        .data_valid(packetizer_valid),

        .crc_out(crc_value)

    );


    // ========================================================
    // UART
    // ========================================================

    reg  [7:0] uart_data;
    reg        uart_start;

    wire       uart_busy;
    wire       uart_done;


    uart_tx #(
        .CLKS_PER_BIT(4)
    ) uart_unit (

        .clk(clk),
        .reset(reset),

        .start(uart_start),
        .data_in(uart_data),

        .tx(tx),
        .busy(uart_busy),
        .done(uart_done)

    );


    // ========================================================
    // Packet storage
    // ========================================================

    reg [7:0] packet_memory [0:5];

    reg [2:0] capture_index;
    reg [3:0] tx_index;

    reg [15:0] saved_crc;


    // ========================================================
    // System FSM
    // ========================================================

    localparam STATE_IDLE    = 3'd0;
    localparam STATE_CAPTURE = 3'd1;
    localparam STATE_TX_LOAD = 3'd2;
    localparam STATE_TX_WAIT = 3'd3;
    localparam STATE_DONE    = 3'd4;

    reg [2:0] state;


    always @(posedge clk) begin

        if (reset) begin

            state            <= STATE_IDLE;

            packetizer_start <= 1'b0;
            crc_clear        <= 1'b0;
            uart_start       <= 1'b0;

            uart_data        <= 8'd0;

            capture_index    <= 3'd0;
            tx_index         <= 4'd0;

            saved_crc        <= 16'd0;

            busy             <= 1'b0;
            done             <= 1'b0;

        end

        else begin

            packetizer_start <= 1'b0;
            crc_clear        <= 1'b0;
            uart_start       <= 1'b0;
            done             <= 1'b0;


            case (state)

                STATE_IDLE: begin

                    busy <= 1'b0;

                    if (start) begin

                        busy             <= 1'b1;

                        capture_index    <= 3'd0;
                        tx_index         <= 4'd0;

                        crc_clear        <= 1'b1;
                        packetizer_start <= 1'b1;

                        state <= STATE_CAPTURE;

                    end
                end


                STATE_CAPTURE: begin

                    if (packetizer_valid) begin

                        if (capture_index < 6) begin

                            packet_memory[capture_index]
                                <= packetizer_byte;

                            capture_index
                                <= capture_index + 1'b1;

                        end
                    end


                    if (packetizer_done) begin

                        saved_crc <= crc_value;
                        tx_index  <= 4'd0;

                        state <= STATE_TX_LOAD;

                    end
                end


                STATE_TX_LOAD: begin

                    case (tx_index)

                        4'd0: uart_data <= packet_memory[0];
                        4'd1: uart_data <= packet_memory[1];
                        4'd2: uart_data <= packet_memory[2];
                        4'd3: uart_data <= packet_memory[3];
                        4'd4: uart_data <= packet_memory[4];
                        4'd5: uart_data <= packet_memory[5];

                        4'd6: uart_data <= saved_crc[15:8];
                        4'd7: uart_data <= saved_crc[7:0];

                        default:
                            uart_data <= 8'd0;

                    endcase

                    uart_start <= 1'b1;

                    state <= STATE_TX_WAIT;

                end


                STATE_TX_WAIT: begin

                    if (uart_done) begin

                        if (tx_index == 4'd7) begin

                            state <= STATE_DONE;

                        end

                        else begin

                            tx_index <= tx_index + 1'b1;

                            state <= STATE_TX_LOAD;

                        end
                    end
                end


                STATE_DONE: begin

                    busy <= 1'b0;
                    done <= 1'b1;

                    state <= STATE_IDLE;

                end


                default: begin

                    state <= STATE_IDLE;
                    busy  <= 1'b0;

                end

            endcase
        end
    end

endmodule