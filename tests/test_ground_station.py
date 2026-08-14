import pytest

from ground_station.protocol import (
    crc16_ccitt,
    decode_packet,
)


def test_normal_packet():

    packet = [
        0xA5,
        0x04,
        0x16,
        0x4E,
        0x0F,
        0x0F,
        0xFE,
        0x7C,
    ]

    data = decode_packet(packet)

    assert data["packet_count"] == 4
    assert data["temperature_c"] == 22
    assert data["battery_v"] == 7.8

    assert data["system"]["fpga_healthy"] is True
    assert data["system"]["sensor_subsystem_healthy"] is True
    assert data["system"]["comms_healthy"] is True
    assert data["system"]["watchdog_active"] is True

    assert data["system"]["low_battery"] is False
    assert data["system"]["overtemperature"] is False

    assert data["sensors"]["temperature_sensor"] is True
    assert data["sensors"]["imu"] is True
    assert data["sensors"]["gps"] is True
    assert data["sensors"]["power_monitor"] is True


def test_fault_packet():

    packet = [
        0xA5,
        0x05,
        0x1E,
        0x4F,
        0x3F,
        0x0B,
        0xA3,
        0xCF,
    ]

    data = decode_packet(packet)

    assert data["packet_count"] == 5
    assert data["temperature_c"] == 30
    assert data["battery_v"] == 7.9

    assert data["system"]["low_battery"] is True
    assert data["system"]["overtemperature"] is True

    assert data["sensors"]["gps"] is False


def test_corrupted_packet():

    packet = [
        0xA5,
        0x04,
        0x17,  # Corrupted temperature byte
        0x4E,
        0x0F,
        0x0F,
        0xFE,
        0x7C,
    ]

    with pytest.raises(ValueError, match="CRC mismatch"):
        decode_packet(packet)


def test_invalid_header():

    packet = [
        0x00,
        0x04,
        0x16,
        0x4E,
        0x0F,
        0x0F,
        0xFE,
        0x7C,
    ]

    with pytest.raises(ValueError, match="Invalid header"):
        decode_packet(packet)


def test_crc_matches_fpga():

    packet_data = [
        0xA5,
        0x04,
        0x16,
        0x4E,
        0x0F,
        0x0F,
    ]

    assert crc16_ccitt(packet_data) == 0xFE7C