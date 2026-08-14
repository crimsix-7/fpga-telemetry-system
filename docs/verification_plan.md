# Verification Plan

## Objective

Verify that each RTL block and the integrated telemetry chain satisfy the defined packet, CRC, UART, reset/recovery, and status-encoding behavior.

## Environment

- Verilator
- cocotb
- Python
- pytest
- GTKWave

## Verification Matrix

| ID | Requirement / Behavior | Test Suite |
|---|---|---|
| V-01 | Synchronous reset clears the basic counter | `test_telemetry.py` |
| V-02 | Counter increments only while enabled | `test_telemetry.py` |
| V-03 | Packetizer emits bytes in protocol order | `test_packetizer.py` |
| V-04 | Packetizer snapshots telemetry inputs at `start` | `test_packetizer.py` |
| V-05 | Mid-packet reset aborts transmission and permits recovery | `test_packetizer.py` |
| V-06 | CRC matches the CCITT-FALSE reference vector | `test_crc16.py` |
| V-07 | CRC clear restores the initial value | `test_crc16.py` |
| V-08 | Changed/corrupted packet data produces a different CRC | `test_crc16.py` |
| V-09 | UART idles HIGH and emits start, 8 LSB-first data bits, and stop bit | `test_uart_tx.py` |
| V-10 | Nominal health inputs encode `SYSTEM_STATUS=0x0F` and `SENSOR_STATUS=0x0F` | `test_fault_manager.py` |
| V-11 | Injected low battery, overtemperature, and GPS failure encode the expected status bytes | `test_fault_manager.py` |
| V-12 | Integrated RTL emits the expected nominal 8-byte UART packet | `test_telemetry_system.py` |
| V-13 | Integrated RTL emits the expected fault-state 8-byte UART packet | `test_telemetry_system.py` |
| V-14 | Ground decoder accepts and decodes valid packets | `test_ground_station.py` |
| V-15 | Ground decoder rejects corrupted packets by CRC | `test_ground_station.py` |
| V-16 | Ground decoder rejects an invalid header | `test_ground_station.py` |
| V-17 | Python CRC implementation matches the RTL/reference packet value | `test_ground_station.py` |

## Regression Procedure

Activate the project environment and run:

```bash
make regression
```

The Makefile executes the RTL suites for the counter, packetizer, CRC, UART, fault manager, and integrated system, followed by the Python ground-station tests.

A failed assertion stops or marks the affected suite as failed.

## Waveform Inspection

GTKWave is used as a supporting debug/inspection tool rather than the primary pass/fail mechanism.

Waveforms are useful for confirming:

- clock/reset timing
- packetizer FSM progression
- telemetry snapshot registers
- `byte_valid` and `byte_out`
- UART serialization
- fault/status signals

Automated assertions remain the source of regression pass/fail results.
