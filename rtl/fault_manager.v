`timescale 1ns/1ps

module fault_manager (

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

    output wire [7:0] system_status,
    output wire [7:0] sensor_status
);

    assign system_status = {
        2'b00,
        overtemperature,
        low_battery,
        watchdog_active,
        comms_healthy,
        sensor_subsystem_healthy,
        fpga_healthy
    };

    assign sensor_status = {
        4'b0000,
        power_monitor_healthy,
        gps_healthy,
        imu_healthy,
        temp_sensor_healthy
    };

endmodule