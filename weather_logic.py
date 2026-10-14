import time
import json
import sqlite3
import requests

import os

API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
DB_FILE = "weather_cache.db"
OWM_URL = "https://api.openweathermap.org/data/2.5/weather"

# ---------------- Crop Rules ----------------

CROPS = {
    "wheat": {"min_temp": 10, "max_temp": 25, "min_humidity": 45, "notes": "Cool season cereal; requires cool vegetative growth and sunny grain filling."},
    "rice": {"min_temp": 20, "max_temp": 36, "min_humidity": 65, "notes": "Needs warm and humid climate with abundant irrigation/rainfall."},
    "maize": {"min_temp": 18, "max_temp": 32, "min_humidity": 45, "notes": "Moderate climate crop; thrives in warm soils with good drainage."},
    "cotton": {"min_temp": 21, "max_temp": 35, "min_humidity": 40, "notes": "Warm season cash crop; needs dry sunshine during boll opening."},
    "sugarcane": {"min_temp": 20, "max_temp": 35, "min_humidity": 60, "notes": "Tropical heavy feeder; needs warm humid climate."},
    "pulses": {"min_temp": 14, "max_temp": 28, "min_humidity": 35, "notes": "Drought-tolerant nitrogen fixer; sensitive to waterlogging."},
    "mustard": {"min_temp": 10, "max_temp": 25, "min_humidity": 40, "notes": "Cool winter oilseed; thrives under dry, cool sunshine."},
    "potato": {"min_temp": 14, "max_temp": 24, "min_humidity": 55, "notes": "Cool season tuber; tuberization impeded above 24°C."},
    "soybean": {"min_temp": 20, "max_temp": 32, "min_humidity": 50, "notes": "Warm season legume; ideal for crop rotation in fertile loams."},
}

HEATWAVE = 40
FROST = 5

# ---------------- Database Caching ----------------

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS weather_cache (
            city TEXT PRIMARY KEY,
            timestamp INTEGER,
            data TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_cache(city, data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO weather_cache VALUES (?, ?, ?)",
        (city.lower(), int(time.time()), json.dumps(data))
    )
    conn.commit()
    conn.close()

def load_cache(city):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT timestamp, data FROM weather_cache WHERE city=?", (city.lower(),))
    row = c.fetchone()
    conn.close()

    if row:
        ts, txt = row
        data = json.loads(txt)
        data["source"] = "cache"
        data["timestamp"] = ts
        return data
    return None

# ---------------- Weather ----------------

def kelvin_to_c(k):
    return round(k - 273.15, 2)

def fetch_online(city):
    # If OpenWeather API key is provided in environment, try it
    if API_KEY:
        try:
            r = requests.get(OWM_URL, params={"q": city, "appid": API_KEY}, timeout=10)
            if r.status_code == 200:
                j = r.json()
                return {
                    "city": j["name"],
                    "temp_c": kelvin_to_c(j["main"]["temp"]),
                    "humidity": j["main"]["humidity"],
                    "wind_speed": j["wind"]["speed"],
                    "desc": j["weather"][0]["description"],
                    "source": "OpenWeatherMap",
                    "timestamp": int(time.time())
                }
        except Exception:
            pass

    # Public Open-Meteo API (Free, global, no API key required)
    geo_res = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=10
    )
    geo_res.raise_for_status()
    geo_data = geo_res.json()
    if not geo_data.get("results"):
        raise ValueError(f"City '{city}' not found")

    loc = geo_data["results"][0]
    lat, lon = loc["latitude"], loc["longitude"]
    display_name = f"{loc.get('name')}, {loc.get('country', '')}"

    w_res = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "timezone": "auto"
        },
        timeout=10
    )
    w_res.raise_for_status()
    cur = w_res.json().get("current", {})

    return {
        "city": display_name,
        "temp_c": round(cur.get("temperature_2m", 25.0), 1),
        "humidity": round(cur.get("relative_humidity_2m", 60)),
        "wind_speed": round(cur.get("wind_speed_10m", 0.0), 1),
        "desc": "Live Agro Feed",
        "source": "Open-Meteo",
        "timestamp": int(time.time())
    }

def get_weather(city):
    try:
        data = fetch_online(city)
        save_cache(city, data)
        return data
    except:
        cached = load_cache(city)
        if cached:
            return cached
        raise RuntimeError("Weather data not available")

# ---------------- Crop Advisory ----------------

def crop_recommendations(temp_c, humidity):
    recs = {}

    for crop, r in CROPS.items():
        if r["min_temp"] <= temp_c <= r["max_temp"] and humidity >= r["min_humidity"]:
            recs[crop] = "Recommended - " + r["notes"]
        elif r["min_temp"] <= temp_c <= r["max_temp"]:
            recs[crop] = "Maybe (low humidity) - " + r["notes"]
        else:
            recs[crop] = "Not recommended - " + r["notes"]

    return recs

def check_alerts(temp_c):
    alerts = []
    if temp_c >= HEATWAVE:
        alerts.append(f"🔥 Heatwave alert! {temp_c}°C")
    if temp_c <= FROST:
        alerts.append(f"❄ Frost alert! {temp_c}°C")
    return alerts
