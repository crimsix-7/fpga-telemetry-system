import cocotb

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_packet_counter(dut):
    """
    Verify the basic behaviour of the telemetry packet counter.

    Test:
        1. Reset clears the counter.
        2. Enable causes the counter to increment.
        3. Disabling enable causes the counter to hold its value.
        4. Reset clears the counter again.
    """

    # ---------------------------------------------------------
    # Start a 10 ns clock.
    # ---------------------------------------------------------

    clock = Clock(dut.clk, 10, unit="ns")
    clock.start()

    # ---------------------------------------------------------
    # TEST 1: RESET
    # ---------------------------------------------------------

    dut.reset.value = 1
    dut.enable.value = 0

    # Wait for a rising clock edge.
    await RisingEdge(dut.clk)

    # Allow the HDL logic triggered by the clock to finish.
    await Timer(1, unit="ns")

    assert int(dut.packet_count.value) == 0, (
        f"Reset failed: expected 0, "
        f"got {int(dut.packet_count.value)}"
    )

    # ---------------------------------------------------------
    # TEST 2: COUNTING
    # ---------------------------------------------------------

    dut.reset.value = 0
    dut.enable.value = 1

    for expected_count in range(1, 6):

        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        actual_count = int(dut.packet_count.value)

        assert actual_count == expected_count, (
            f"Counting failed: expected {expected_count}, "
            f"got {actual_count}"
        )

    # ---------------------------------------------------------
    # TEST 3: HOLD VALUE WHEN DISABLED
    # ---------------------------------------------------------

    dut.enable.value = 0

    for _ in range(3):

        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        actual_count = int(dut.packet_count.value)

        assert actual_count == 5, (
            f"Enable hold failed: expected 5, "
            f"got {actual_count}"
        )

    # ---------------------------------------------------------
    # TEST 4: RESET AGAIN
    # ---------------------------------------------------------

    dut.reset.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert int(dut.packet_count.value) == 0, (
        f"Final reset failed: expected 0, "
        f"got {int(dut.packet_count.value)}"
    )