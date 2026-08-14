# Telemetry Protocol

## Overview

The project uses a fixed-length **8-byte telemetry packet**.

```text
Byte 0   Byte 1   Byte 2   Byte 3   Byte 4   Byte 5   Byte 6   Byte 7
HEADER   COUNT    TEMP     BATTERY  SYS      SENSOR   CRC_H    CRC_L
```

Total length: **8 bytes / 64 bits**

## Packet Definition

| Byte | Field | Width | Encoding |
|---:|---|---:|---|
| 0 | `HEADER` | 8 bits | Fixed `0xA5` |
| 1 | `PACKET_COUNT` | 8 bits | Unsigned sequence field, `0–255` |
| 2 | `TEMPERATURE` | 8 bits | Unsigned integer °C |
| 3 | `BATTERY` | 8 bits | Battery voltage × 10 |
| 4 | `SYSTEM_STATUS` | 8 bits | System-health bit field |
| 5 | `SENSOR_STATUS` | 8 bits | Sensor-health bit field |
| 6 | `CRC_HIGH` | 8 bits | CRC bits `[15:8]` |
| 7 | `CRC_LOW` | 8 bits | CRC bits `[7:0]` |

## Header

Every packet begins with:

```text
0xA5
```

Binary:

```text
1010 0101
```

The header provides a fixed synchronization marker for the packet format.

## Packet Count

`PACKET_COUNT` is an 8-bit sequence field.

```text
0 ... 255
```

A producer may increment it once per packet and wrap from `255` to `0`. Missing sequence values can therefore be used by a receiver to identify potential packet loss.

In the current integrated RTL, `packet_count` is supplied as an input to `telemetry_system`; the top-level telemetry system does not increment it internally.

## Temperature

`TEMPERATURE` is currently an **unsigned 8-bit integer in degrees Celsius**.

Example:

```text
22 °C = decimal 22 = 0x16
```

Current representable range:

```text
0 ... 255 °C
```

Negative and fractional temperatures are outside the current protocol version.

## Battery Voltage

Battery voltage is encoded in **decivolts**:

```text
encoded = voltage × 10
```

Example:

```text
7.8 V -> 78 -> 0x4E
```

The decoder reconstructs the displayed value with:

```text
voltage = encoded / 10
```

With one unsigned byte, the representable range is `0.0–25.5 V`.

## System Status

`SYSTEM_STATUS` uses individual bits:

| Bit | Meaning | `1` means |
|---:|---|---|
| 0 | FPGA healthy | Healthy |
| 1 | Sensor subsystem healthy | Healthy |
| 2 | Communications healthy | Healthy |
| 3 | Watchdog active | Active |
| 4 | Low battery | Warning active |
| 5 | Overtemperature | Warning active |
| 6 | Reserved | — |
| 7 | Reserved | — |

Nominal status:

```text
0000 1111 = 0x0F
```

Low battery and overtemperature simultaneously asserted:

```text
0011 1111 = 0x3F
```

## Sensor Status

`SENSOR_STATUS` uses:

| Bit | Meaning | `1` means |
|---:|---|---|
| 0 | Temperature sensor | Healthy |
| 1 | IMU | Healthy |
| 2 | GPS | Healthy |
| 3 | Power monitor | Healthy |
| 4–7 | Reserved | — |

All sensors healthy:

```text
0000 1111 = 0x0F
```

GPS failed while the other defined sensors remain healthy:

```text
0000 1011 = 0x0B
```

## CRC-16

CRC is calculated over **bytes 0 through 5 only**. Bytes 6 and 7 carry the resulting CRC and are not included in the calculation.

The implementation uses **CRC-16/CCITT-FALSE**:

| Parameter | Value |
|---|---|
| Width | 16 bits |
| Polynomial | `0x1021` |
| Initial value | `0xFFFF` |
| Reflect input | No |
| Reflect output | No |
| Final XOR | `0x0000` |

The CRC is transmitted high byte first:

```text
CRC_HIGH, CRC_LOW
```

Reference vector:

```text
ASCII "123456789" -> 0x29B1
```

## UART Framing

Each packet byte is serialized using UART **8-N-1** framing:

```text
Idle HIGH
Start bit: 0
Data bits: 8, LSB first
Parity: none
Stop bit: 1
```

## Example: Nominal Packet

Input values:

```text
Packet Count:   4
Temperature:    22 °C
Battery:        7.8 V
System Status:  0x0F
Sensor Status:  0x0F
```

Payload:

```text
A5 04 16 4E 0F 0F
```

CRC:

```text
0xFE7C
```

Complete packet:

```text
A5 04 16 4E 0F 0F FE 7C
```

## Example: Fault Packet

Input values:

```text
Packet Count:       5
Temperature:        30 °C
Battery:            7.9 V
System Status:      0x3F
Sensor Status:      0x0B
```

CRC:

```text
0xA3CF
```

Complete packet:

```text
A5 05 1E 4F 3F 0B A3 CF
```
