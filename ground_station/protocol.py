HEADER = 0xA5
PACKET_LENGTH = 8


def crc16_ccitt(data):
    crc = 0xFFFF

    for byte in data:
        crc ^= byte << 8

        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF

    return crc


def decode_packet(packet):

    if len(packet) != PACKET_LENGTH:
        raise ValueError(
            f"Expected {PACKET_LENGTH} bytes, got {len(packet)}"
        )

    if packet[0] != HEADER:
        raise ValueError(
            f"Invalid header: 0x{packet[0]:02X}"
        )

    received_crc = (packet[6] << 8) | packet[7]
    calculated_crc = crc16_ccitt(packet[:6])

    if received_crc != calculated_crc:
        raise ValueError(
            f"CRC mismatch: received 0x{received_crc:04X}, "
            f"calculated 0x{calculated_crc:04X}"
        )

    system_status = packet[4]
    sensor_status = packet[5]

    return {
        "packet_count": packet[1],

        "temperature_c": packet[2],

        "battery_v": packet[3] / 10.0,

        "system": {
            "fpga_healthy": bool(system_status & (1 << 0)),
            "sensor_subsystem_healthy": bool(system_status & (1 << 1)),
            "comms_healthy": bool(system_status & (1 << 2)),
            "watchdog_active": bool(system_status & (1 << 3)),
            "low_battery": bool(system_status & (1 << 4)),
            "overtemperature": bool(system_status & (1 << 5)),
        },

        "sensors": {
            "temperature_sensor": bool(sensor_status & (1 << 0)),
            "imu": bool(sensor_status & (1 << 1)),
            "gps": bool(sensor_status & (1 << 2)),
            "power_monitor": bool(sensor_status & (1 << 3)),
        },

        "crc": received_crc,
    }