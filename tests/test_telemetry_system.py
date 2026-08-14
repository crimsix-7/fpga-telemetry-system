import cocotb

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer


BIT_TIME_NS = 40


async def receive_uart_byte(dut):

    await FallingEdge(dut.tx)

    await Timer(BIT_TIME_NS // 2, unit="ns")

    value = 0

    for bit_index in range(8):

        await Timer(BIT_TIME_NS, unit="ns")

        bit = int(dut.tx.value)

        value |= bit << bit_index

    await Timer(BIT_TIME_NS, unit="ns")

    return value


async def reset_dut(dut):

    dut.reset.value = 1
    dut.start.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.reset.value = 0


async def transmit_packet(dut):

    dut.start.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.start.value = 0

    packet = []

    for _ in range(8):

        byte = await receive_uart_byte(dut)

        packet.append(byte)

        dut._log.info(
            f"UART byte: 0x{byte:02X}"
        )

    return packet


@cocotb.test()
async def test_normal_system(dut):

    clock = Clock(dut.clk, 10, unit="ns")
    clock.start()

    await reset_dut(dut)

    dut.packet_count.value = 4
    dut.temperature.value = 22
    dut.battery.value = 78

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

    received_packet = await transmit_packet(dut)

    expected_packet = [
        0xA5,
        0x04,
        0x16,
        0x4E,
        0x0F,
        0x0F,
        0xFE,
        0x7C,
    ]

    assert received_packet == expected_packet


@cocotb.test()
async def test_fault_packet(dut):

    clock = Clock(dut.clk, 10, unit="ns")
    clock.start()

    await reset_dut(dut)

    dut.packet_count.value = 5
    dut.temperature.value = 30
    dut.battery.value = 79

    dut.fpga_healthy.value = 1
    dut.sensor_subsystem_healthy.value = 1
    dut.comms_healthy.value = 1
    dut.watchdog_active.value = 1

    # Inject faults
    dut.low_battery.value = 1
    dut.overtemperature.value = 1

    dut.temp_sensor_healthy.value = 1
    dut.imu_healthy.value = 1

    # GPS failure
    dut.gps_healthy.value = 0

    dut.power_monitor_healthy.value = 1

    received_packet = await transmit_packet(dut)

    expected_packet = [
        0xA5,
        0x05,
        0x1E,
        0x4F,
        0x3F,
        0x0B,
        0xA3,
        0xCF,
    ]

    assert received_packet == expected_packet