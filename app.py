from flask import Flask, render_template, request, jsonify
from weather_logic import (
    get_weather,
    composite_crop_recommendations,
    get_ph_neutralization,
    generate_next_day_advisory,
    fetch_telegram_ph
)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    city = "Delhi"
    data = None
    recs = None
    neutralization = None
    advisories = []
    current_ph = 6.8
    current_moisture = 45.0

    if request.method == "POST":
        city = request.form.get("city", "Delhi")
        current_ph = float(request.form.get("ph", 6.8))
        current_moisture = float(request.form.get("moisture", 45.0))

    try:
        data = get_weather(city)
        recs = composite_crop_recommendations(
            data["temp_c"],
            data["humidity"],
            soil_moisture=current_moisture,
            ph_val=current_ph
        )
        neutralization = get_ph_neutralization(current_ph)
        advisories = generate_next_day_advisory(data.get("hourly", {}), current_moisture=current_moisture)
    except Exception as e:
        data = {"error": str(e), "city": city}

    return render_template(
        "index.html",
        data=data,
        recs=recs,
        neutralization=neutralization,
        advisories=advisories,
        current_ph=current_ph,
        current_moisture=current_moisture
    )

@app.route("/api/telemetry")
def api_telemetry():
    import requests
    username = request.args.get("name", "SoilMoisture")
    mac = request.args.get("mac", "B4:E6:2D:30:77:55")
    url = f"https://www.projectiot.in/token/fetch.php?name={username}&mac={mac}"
    try:
        r = requests.get(url, timeout=5, headers={"User-Agent": "SmartFarmingLocalBackend/2.0"})
        return jsonify({"success": True, "raw": r.text.strip(), "status_code": r.status_code})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/weather")
def api_weather():
    city = request.args.get("city", "Delhi")
    moisture = request.args.get("moisture", 45.0)
    ph = request.args.get("ph", 6.8)

    try:
        data = get_weather(city)
        recs = composite_crop_recommendations(data["temp_c"], data["humidity"], soil_moisture=moisture, ph_val=ph)
        neutralization = get_ph_neutralization(ph)
        advisories = generate_next_day_advisory(data.get("hourly", {}), current_moisture=moisture)

        return jsonify({
            "success": True,
            "data": data,
            "recs": recs,
            "neutralization": neutralization,
            "advisories": advisories
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/ph/neutralize")
def api_neutralize():
    ph = request.args.get("ph", 7.0)
    try:
        result = get_ph_neutralization(ph)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/ph/telegram")
def api_telegram():
    token = request.args.get("token", "")
    if not token:
        return jsonify({"success": False, "error": "Token required"}), 400
    try:
        res = fetch_telegram_ph(token)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
