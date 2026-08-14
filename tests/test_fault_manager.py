import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_normal_status(dut):

    dut.fpga_healthy.value = 1
    dut.sensor_subsystem_healthy.value = 1
    dut.comms_healthy.value = 1
    dut.watchdog_active.value = 1

    dut.low_battery.value = 0
    dut.overtemperature.value = 0

    dut.temp_sensor_healthy.value = 1
    dut.imu_healthy.value = 1
    dut.gps_healthy.value = 1
    dut.power_monitor_healthy.value = 1

    await Timer(1, unit="ns")

    assert int(dut.system_status.value) == 0x0F
    assert int(dut.sensor_status.value) == 0x0F


@cocotb.test()
async def test_fault_status(dut):

    dut.fpga_healthy.value = 1
    dut.sensor_subsystem_healthy.value = 1
    dut.comms_healthy.value = 1
    dut.watchdog_active.value = 1

    dut.low_battery.value = 1
    dut.overtemperature.value = 1

    dut.temp_sensor_healthy.value = 1
    dut.imu_healthy.value = 1

    # Simulate GPS failure.
    dut.gps_healthy.value = 0

    dut.power_monitor_healthy.value = 1

    await Timer(1, unit="ns")

    assert int(dut.system_status.value) == 0x3F
    assert int(dut.sensor_status.value) == 0x0B

    dut._log.info(
        f"System status: 0x{int(dut.system_status.value):02X}"
    )

    dut._log.info(
        f"Sensor status: 0x{int(dut.sensor_status.value):02X}"
    )