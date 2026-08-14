# Verification Results

## Summary

**Local regression status: PASS**

The complete `make regression` run completed successfully across **17 test cases** covering six RTL/component suites, the integrated RTL system, and the Python ground-station decoder.

## Results by Suite

| Suite | Test Cases | Result |
|---|---:|---|
| Basic RTL counter | 1 | PASS |
| Telemetry packetizer | 3 | PASS |
| CRC-16 | 3 | PASS |
| UART transmitter | 1 | PASS |
| Fault manager | 2 | PASS |
| Integrated telemetry system | 2 | PASS |
| Ground-station protocol | 5 | PASS |
| **Total** | **17** | **PASS** |

## CRC Reference Check

CRC-16/CCITT-FALSE reference vector:

```text
Input:  "123456789"
Result: 0x29B1
Status: PASS
```

## Nominal Integrated Packet

The integrated RTL UART path produced:

```text
A5 04 16 4E 0F 0F FE 7C
```

Decoded fields:

| Field | Value |
|---|---|
| Header | `0xA5` |
| Packet Count | `4` |
| Temperature | `22 °C` |
| Battery | `7.8 V` |
| System Status | `0x0F` |
| Sensor Status | `0x0F` |
| CRC-16 | `0xFE7C` |

Result: **PASS**

## Fault-State Integrated Packet

With low battery, overtemperature, and GPS failure injected, the integrated RTL UART path produced:

```text
A5 05 1E 4F 3F 0B A3 CF
```

Expected status fields:

```text
SYSTEM_STATUS = 0x3F
SENSOR_STATUS = 0x0B
```

Result: **PASS**

## Ground-Station Protocol Tests

The Python ground-side tests verified:

- valid nominal packet decoding
- valid fault packet decoding
- CRC rejection of corrupted data
- invalid-header rejection
- Python CRC agreement with the expected FPGA/reference packet CRC

Result: **5/5 PASS**

## Interactive Dashboard Check

Manual dashboard testing confirmed:

- GPS fault indication
- low-battery fault indication
- overtemperature fault indication
- intentional post-CRC packet corruption
- visible CRC mismatch reporting
- recovery to nominal state

This manual UI check supplements, but does not replace, the automated regression tests.

## Scope of Results

These results verify the **simulated RTL and software behavior** implemented in this repository. They do not represent timing closure on a physical FPGA, RF testing, PCB validation, environmental qualification, or flight-hardware verification.
