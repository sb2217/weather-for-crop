from flask import Flask, render_template, request
from weather_logic import get_weather, crop_recommendations, check_alerts

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    data = None
    recs = None
    alerts = []

    if request.method == "POST":
        city = request.form.get("city")

        if city:
            try:
                data = get_weather(city)
                recs = crop_recommendations(data["temp_c"], data["humidity"])
                alerts = check_alerts(data["temp_c"])
            except Exception as e:
                data = {"error": str(e)}

    return render_template("index.html", data=data, recs=recs, alerts=alerts)


@app.route("/api/weather")
def api_weather():
    city = request.args.get("city", "Delhi")
    try:
        data = get_weather(city)
        recs = crop_recommendations(data["temp_c"], data["humidity"])
        alerts = check_alerts(data["temp_c"])
        return {"success": True, "data": data, "recs": recs, "alerts": alerts}
    except Exception as e:
        return {"success": False, "error": str(e)}, 400


if __name__ == "__main__":
    app.run(debug=True)
