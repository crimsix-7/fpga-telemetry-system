import cocotb

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


CLKS_PER_BIT = 4


async def wait_clocks(dut, count):

    for _ in range(count):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")


@cocotb.test()
async def test_uart_transmit_byte(dut):

    clock = Clock(dut.clk, 10, unit="ns")
    clock.start()

    dut.reset.value = 1
    dut.start.value = 0
    dut.data_in.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.reset.value = 0

    # UART idle line must be HIGH.
    assert int(dut.tx.value) == 1


    # Transmit 0xA5.
    dut.data_in.value = 0xA5
    dut.start.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.start.value = 0


    # Move into start bit.
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert int(dut.tx.value) == 0


    # UART sends data LSB first.
    expected_bits = [
        1,  # bit 0
        0,  # bit 1
        1,  # bit 2
        0,  # bit 3
        0,  # bit 4
        1,  # bit 5
        0,  # bit 6
        1,  # bit 7
    ]

    received_bits = []

    for expected_bit in expected_bits:

        await wait_clocks(dut, CLKS_PER_BIT)

        actual_bit = int(dut.tx.value)

        received_bits.append(actual_bit)

        assert actual_bit == expected_bit, (
            f"Expected UART bit {expected_bit}, "
            f"got {actual_bit}"
        )


    # Stop bit.
    await wait_clocks(dut, CLKS_PER_BIT)

    assert int(dut.tx.value) == 1


    dut._log.info(
        f"UART data bits: {received_bits}"
    )


    # Wait for transmission completion.
    for _ in range(CLKS_PER_BIT + 3):

        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        if int(dut.done.value) == 1:
            break

    assert int(dut.done.value) == 1
    assert int(dut.busy.value) == 0
    assert int(dut.tx.value) == 1