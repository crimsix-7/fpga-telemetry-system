# Virtual CubeSat Telemetry Protocol

## Overview

The FPGA telemetry subsystem generates a fixed-length 8-byte telemetry packet.

Each packet contains:

- synchronization/header byte
- packet sequence number
- temperature measurement
- battery voltage measurement
- system status flags
- sensor status flags
- 16-bit CRC

## Packet Structure

| Byte | Field | Size | Description |
|---|---|---:|---|
| 0 | HEADER | 8 bits | Fixed value `0xA5` identifying the start of a packet |
| 1 | PACKET_COUNT | 8 bits | Sequence number from 0–255 |
| 2 | TEMPERATURE | 8 bits | Temperature in degrees Celsius |
| 3 | BATTERY | 8 bits | Battery voltage encoded in decivolts |
| 4 | SYSTEM_STATUS | 8 bits | System health/status bit field |
| 5 | SENSOR_STATUS | 8 bits | Sensor health bit field |
| 6 | CRC_HIGH | 8 bits | Upper byte of CRC-16 |
| 7 | CRC_LOW | 8 bits | Lower byte of CRC-16 |

Total packet size: **64 bits / 8 bytes**

## Header

The first byte of every telemetry packet is:

`0xA5`

Binary:

`10100101`

This allows the receiver to identify the beginning of a telemetry packet.

## Packet Counter

`PACKET_COUNT` is an unsigned 8-bit sequence number.

Range:

`0–255`

After packet 255, the counter wraps back to 0.

The sequence number allows the ground station to detect missing packets.

Example:

`41, 42, 43, 45`

indicates that packet `44` was not received.

## Temperature Encoding

Temperature is initially represented as an unsigned integer in degrees Celsius.

Example:

- `22 °C` → decimal `22`
- decimal `22` → hexadecimal `0x16`

Signed and fractional temperature support may be added later.

## Battery Voltage Encoding

Battery voltage is represented in decivolts.

Formula:

`encoded_battery = voltage × 10`

Example:

`7.8 V × 10 = 78`

Therefore:

- Physical voltage: `7.8 V`
- Encoded decimal value: `78`
- Encoded hexadecimal value: `0x4E`

The ground station reconstructs the physical value using:

`voltage = encoded_battery / 10`

## System Status

`SYSTEM_STATUS` is an 8-bit bit field.

| Bit | Meaning |
|---:|---|
| 0 | FPGA healthy |
| 1 | Sensor subsystem healthy |
| 2 | Communications healthy |
| 3 | Watchdog active |
| 4 | Low battery warning |
| 5 | Overtemperature warning |
| 6 | Reserved |
| 7 | Reserved |

Normal system status:

`00001111`

Hexadecimal:

`0x0F`

## Sensor Status

`SENSOR_STATUS` is an 8-bit bit field.

| Bit | Meaning |
|---:|---|
| 0 | Temperature sensor healthy |
| 1 | IMU healthy |
| 2 | GPS healthy |
| 3 | Power monitor healthy |
| 4 | Reserved |
| 5 | Reserved |
| 6 | Reserved |
| 7 | Reserved |

All sensors healthy:

`00001111`

Hexadecimal:

`0x0F`

## CRC

Bytes 6 and 7 contain a 16-bit CRC used to detect corrupted telemetry packets.

The CRC implementation and polynomial will be defined when the CRC subsystem is developed.

CRC calculation is not part of the initial packetizer implementation.

## Example Packet

Example spacecraft state:

- Packet number: `4`
- Temperature: `22 °C`
- Battery voltage: `7.8 V`
- System status: healthy
- Sensor status: healthy

The packet before CRC calculation is:

`A5 04 16 4E 0F 0F XX XX`

Where:

| Value | Meaning |
|---|---|
| `A5` | Header |
| `04` | Packet number 4 |
| `16` | 22 °C |
| `4E` | 7.8 V |
| `0F` | Normal system status |
| `0F` | All sensors healthy |
| `XX XX` | CRC to be implemented later |