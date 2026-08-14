import cocotb

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_crc_known_vector(dut):

    clock = Clock(dut.clk, 10, unit="ns")
    clock.start()

    dut.reset.value = 1
    dut.clear.value = 0
    dut.data_valid.value = 0
    dut.data_in.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.reset.value = 0

    # Standard CRC-16/CCITT-FALSE test vector:
    # ASCII "123456789" -> CRC = 0x29B1

    test_data = b"123456789"

    for byte in test_data:

        dut.data_in.value = byte
        dut.data_valid.value = 1

        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        dut.data_valid.value = 0

    actual_crc = int(dut.crc_out.value)

    dut._log.info(
        f"Calculated CRC: 0x{actual_crc:04X}"
    )

    assert actual_crc == 0x29B1, (
        f"Expected CRC 0x29B1, got 0x{actual_crc:04X}"
    )


@cocotb.test()
async def test_crc_clear(dut):

    clock = Clock(dut.clk, 10, unit="ns")
    clock.start()

    dut.reset.value = 1
    dut.clear.value = 0
    dut.data_valid.value = 0
    dut.data_in.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.reset.value = 0

    dut.data_in.value = 0xA5
    dut.data_valid.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.data_valid.value = 0

    assert int(dut.crc_out.value) != 0xFFFF

    dut.clear.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.clear.value = 0

    assert int(dut.crc_out.value) == 0xFFFF
@cocotb.test()
async def test_crc_detects_corrupted_packet(dut):

    clock = Clock(dut.clk, 10, unit="ns")
    clock.start()

    async def calculate_crc(data):

        dut.clear.value = 1
        dut.data_valid.value = 0

        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        dut.clear.value = 0

        for byte in data:

            dut.data_in.value = byte
            dut.data_valid.value = 1

            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")

            dut.data_valid.value = 0

        return int(dut.crc_out.value)


    # Initial reset
    dut.reset.value = 1
    dut.clear.value = 0
    dut.data_valid.value = 0
    dut.data_in.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.reset.value = 0


    # Original telemetry packet
    original_packet = [
        0xA5,
        0x04,
        0x16,
        0x4E,
        0x0F,
        0x0F,
    ]

    original_crc = await calculate_crc(original_packet)

    dut._log.info(
        f"Original packet CRC: 0x{original_crc:04X}"
    )

    assert original_crc == 0xFE7C


    # Corrupt the temperature byte:
    #
    # 0x16 = 22 C
    # 0x17 = 23 C
    corrupted_packet = [
        0xA5,
        0x04,
        0x17,
        0x4E,
        0x0F,
        0x0F,
    ]

    corrupted_crc = await calculate_crc(corrupted_packet)

    dut._log.info(
        f"Corrupted packet CRC: 0x{corrupted_crc:04X}"
    )


    # CRC must change when packet data is corrupted.
    assert corrupted_crc != original_crc, (
        "CRC failed to detect corrupted telemetry data."
    )