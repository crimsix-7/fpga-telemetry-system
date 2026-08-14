import cocotb

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_basic_packet(dut):
    """
    Verify that the telemetry packetizer outputs the expected
    six-byte packet in the correct order.
    """

    # Start clock

    clock = Clock(dut.clk, 10, unit="ns")
    clock.start()


    # Reset DUT

    dut.reset.value = 1
    dut.start.value = 0

    dut.packet_count.value = 0
    dut.temperature.value = 0
    dut.battery.value = 0
    dut.system_status.value = 0
    dut.sensor_status.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.reset.value = 0


    # Set spacecraft telemetry

    dut.packet_count.value = 4
    dut.temperature.value = 22
    dut.battery.value = 78
    dut.system_status.value = 0x0F
    dut.sensor_status.value = 0x0F


    # Start packet generation
    

    dut.start.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.start.value = 0


    # Expected packet

    expected_packet = [
        0xA5,   # Header
        0x04,   # Packet number
        0x16,   # 22 degrees C
        0x4E,   # 7.8 V
        0x0F,   # System healthy
        0x0F,   # Sensors healthy
    ]


    # Capture packetizer output

    received_packet = []

    for _ in range(10):

        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        if int(dut.byte_valid.value) == 1:

            received_byte = int(dut.byte_out.value)

            received_packet.append(received_byte)

            dut._log.info(
                f"Received byte: 0x{received_byte:02X}"
            )

        if int(dut.done.value) == 1:
            break


    # Verify entire packet

    assert received_packet == expected_packet, (
        f"Packet mismatch.\n"
        f"Expected: {[hex(x) for x in expected_packet]}\n"
        f"Received: {[hex(x) for x in received_packet]}"
    )
@cocotb.test()
async def test_input_snapshot(dut):
    """
    Verify that telemetry inputs are captured when start is asserted.

    Changing the live telemetry inputs after packet generation begins
    must not modify the packet currently being transmitted.
    """

    # ---------------------------------------------------------
    # Start clock
    # ---------------------------------------------------------

    clock = Clock(dut.clk, 10, unit="ns")
    clock.start()


    # ---------------------------------------------------------
    # Reset DUT
    # ---------------------------------------------------------

    dut.reset.value = 1
    dut.start.value = 0

    dut.packet_count.value = 0
    dut.temperature.value = 0
    dut.battery.value = 0
    dut.system_status.value = 0
    dut.sensor_status.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.reset.value = 0


    # ---------------------------------------------------------
    # ORIGINAL spacecraft telemetry
    #
    # These values should be captured into the packet snapshot.
    # ---------------------------------------------------------

    dut.packet_count.value = 10
    dut.temperature.value = 22
    dut.battery.value = 78
    dut.system_status.value = 0x0F
    dut.sensor_status.value = 0x0F


    # ---------------------------------------------------------
    # Start packet generation
    # ---------------------------------------------------------

    dut.start.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.start.value = 0


    # ---------------------------------------------------------
    # Change the LIVE inputs AFTER the snapshot was captured.
    #
    # These values must NOT appear in the current packet.
    # ---------------------------------------------------------

    dut.packet_count.value = 99
    dut.temperature.value = 99
    dut.battery.value = 12
    dut.system_status.value = 0x00
    dut.sensor_status.value = 0x00


    # ---------------------------------------------------------
    # Expected packet must contain ORIGINAL values.
    # ---------------------------------------------------------

    expected_packet = [
        0xA5,
        0x0A,   # Original packet number = 10
        0x16,   # Original temperature = 22 C
        0x4E,   # Original battery = 7.8 V
        0x0F,   # Original system status
        0x0F,   # Original sensor status
    ]


    # ---------------------------------------------------------
    # Capture generated packet
    # ---------------------------------------------------------

    received_packet = []

    for _ in range(10):

        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        if int(dut.byte_valid.value) == 1:

            received_byte = int(dut.byte_out.value)

            received_packet.append(received_byte)

            dut._log.info(
                f"Snapshot test byte: 0x{received_byte:02X}"
            )

        if int(dut.done.value) == 1:
            break


    # ---------------------------------------------------------
    # Verify that changing the live inputs did not corrupt
    # the packet snapshot.
    # ---------------------------------------------------------

    assert received_packet == expected_packet, (
        f"Snapshot failed.\n"
        f"Expected: {[hex(x) for x in expected_packet]}\n"
        f"Received: {[hex(x) for x in received_packet]}"
    )
@cocotb.test()
async def test_reset_mid_packet(dut):

    clock = Clock(dut.clk, 10, unit="ns")
    clock.start()

    dut.reset.value = 1
    dut.start.value = 0

    dut.packet_count.value = 0
    dut.temperature.value = 0
    dut.battery.value = 0
    dut.system_status.value = 0
    dut.sensor_status.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.reset.value = 0

    dut.packet_count.value = 7
    dut.temperature.value = 25
    dut.battery.value = 82
    dut.system_status.value = 0x0F
    dut.sensor_status.value = 0x0F

    dut.start.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.start.value = 0

    partial_packet = []

    for _ in range(2):

        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        if int(dut.byte_valid.value) == 1:

            received_byte = int(dut.byte_out.value)
            partial_packet.append(received_byte)

            dut._log.info(
                f"Before reset: 0x{received_byte:02X}"
            )

    assert partial_packet == [0xA5, 0x07]

    dut.reset.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert int(dut.busy.value) == 0
    assert int(dut.byte_valid.value) == 0
    assert int(dut.done.value) == 0

    dut.reset.value = 0

    for _ in range(2):

        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        assert int(dut.byte_valid.value) == 0
        assert int(dut.busy.value) == 0

    dut.packet_count.value = 8
    dut.temperature.value = 30
    dut.battery.value = 79
    dut.system_status.value = 0x0F
    dut.sensor_status.value = 0x0F

    dut.start.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.start.value = 0

    expected_packet = [
        0xA5,
        0x08,
        0x1E,
        0x4F,
        0x0F,
        0x0F,
    ]

    recovered_packet = []

    for _ in range(10):

        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        if int(dut.byte_valid.value) == 1:

            received_byte = int(dut.byte_out.value)
            recovered_packet.append(received_byte)

            dut._log.info(
                f"After reset: 0x{received_byte:02X}"
            )

        if int(dut.done.value) == 1:
            break

    assert recovered_packet == expected_packet, (
        f"Expected: {[hex(x) for x in expected_packet]}\n"
        f"Received: {[hex(x) for x in recovered_packet]}"
    )