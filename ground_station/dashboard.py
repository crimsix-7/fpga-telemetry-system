from flask import Flask, jsonify, render_template

from ground_station.protocol import crc16_ccitt, decode_packet


app = Flask(__name__)


state = {
    "packet_count": 0,
    "temperature": 22,
    "battery": 78,

    "system_status": 0x0F,
    "sensor_status": 0x0F,

    "corrupt_packet": False,
}


def build_packet():

    packet_data = [
        0xA5,
        state["packet_count"],
        state["temperature"],
        state["battery"],
        state["system_status"],
        state["sensor_status"],
    ]

    crc = crc16_ccitt(packet_data)

    packet = packet_data + [
        (crc >> 8) & 0xFF,
        crc & 0xFF,
    ]

    # Corrupt temperature AFTER CRC generation.
    if state["corrupt_packet"]:
        packet[2] ^= 0x01

    return packet


@app.route("/")
def dashboard():

    return render_template("dashboard.html")


@app.route("/api/telemetry")
def telemetry():

    packet = build_packet()

    try:

        decoded = decode_packet(packet)

        response = {
            **decoded,

            "crc_valid": True,
            "error": None,

            "raw_packet": [
                f"{byte:02X}"
                for byte in packet
            ],
        }

    except ValueError as error:

        response = {
            "packet_count": state["packet_count"],
            "temperature_c": state["temperature"],
            "battery_v": state["battery"] / 10.0,

            "crc_valid": False,
            "error": str(error),

            "raw_packet": [
                f"{byte:02X}"
                for byte in packet
            ],
        }


    state["packet_count"] = (
        state["packet_count"] + 1
    ) % 256

    return jsonify(response)


@app.route("/api/fault/gps", methods=["POST"])
def toggle_gps():

    state["sensor_status"] ^= (1 << 2)

    return jsonify({
        "success": True
    })


@app.route("/api/fault/low-battery", methods=["POST"])
def toggle_low_battery():

    state["system_status"] ^= (1 << 4)

    return jsonify({
        "success": True
    })


@app.route("/api/fault/overtemperature", methods=["POST"])
def toggle_overtemperature():

    state["system_status"] ^= (1 << 5)

    return jsonify({
        "success": True
    })


@app.route("/api/fault/corruption", methods=["POST"])
def toggle_corruption():

    state["corrupt_packet"] = (
        not state["corrupt_packet"]
    )

    return jsonify({
        "success": True
    })


@app.route("/api/reset", methods=["POST"])
def reset_faults():

    state["system_status"] = 0x0F
    state["sensor_status"] = 0x0F
    state["corrupt_packet"] = False

    return jsonify({
        "success": True
    })


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )