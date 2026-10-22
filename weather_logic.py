import time
import json
import sqlite3
import requests
import re
import os

API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
DB_FILE = "weather_cache.db"
OWM_URL = "https://api.openweathermap.org/data/2.5/weather"

# ---------------- Agronomic Crop Database (Climate + Soil pH) ----------------

CROPS = {
    "wheat": {
        "name": "Wheat (गेंहू)",
        "season": "Rabi (Winter)",
        "min_temp": 10, "max_temp": 25, "min_humidity": 45,
        "min_ph": 6.0, "max_ph": 7.5,
        "notes": "Cool season cereal; requires cool vegetative growth and sunny grain filling. Highly sensitive to acid soils."
    },
    "rice": {
        "name": "Rice / Paddy (धान)",
        "season": "Kharif (Monsoon)",
        "min_temp": 20, "max_temp": 36, "min_humidity": 65,
        "min_ph": 5.5, "max_ph": 7.0,
        "notes": "Tolerates slightly acidic submerged soils; requires abundant water and warm humid conditions."
    },
    "maize": {
        "name": "Maize / Corn (मक्का)",
        "season": "Kharif / Spring",
        "min_temp": 18, "max_temp": 32, "min_humidity": 45,
        "min_ph": 5.8, "max_ph": 7.2,
        "notes": "Moderate climate crop; needs warm, well-drained fertile loam with neutral pH."
    },
    "cotton": {
        "name": "Cotton (कपास)",
        "season": "Cash Crop",
        "min_temp": 21, "max_temp": 35, "min_humidity": 40,
        "min_ph": 6.0, "max_ph": 7.8,
        "notes": "Deep rooted; tolerates mild alkalinity; requires dry sunny weather during boll opening."
    },
    "sugarcane": {
        "name": "Sugarcane (गन्ना)",
        "season": "Cash / Perennial",
        "min_temp": 20, "max_temp": 35, "min_humidity": 60,
        "min_ph": 6.0, "max_ph": 7.8,
        "notes": "Heavy feeder; thrives in warm humid climates; requires consistent soil moisture and nutrient availability."
    },
    "pulses": {
        "name": "Pulses & Gram (दालें / चना)",
        "season": "Rabi / Kharif",
        "min_temp": 14, "max_temp": 28, "min_humidity": 35,
        "min_ph": 6.0, "max_ph": 7.5,
        "notes": "Drought-tolerant nitrogen fixer. Sensitive to waterlogging and soil acidity (<6.0 harms root nodules)."
    },
    "mustard": {
        "name": "Mustard / Rapeseed (सरसों)",
        "season": "Rabi (Winter)",
        "min_temp": 10, "max_temp": 25, "min_humidity": 40,
        "min_ph": 6.0, "max_ph": 7.5,
        "notes": "Cool winter oilseed; thrives under dry cool sunshine; sensitive to heavy frost and prolonged fog."
    },
    "potato": {
        "name": "Potato (आलू)",
        "season": "Rabi (Winter)",
        "min_temp": 14, "max_temp": 24, "min_humidity": 55,
        "min_ph": 5.0, "max_ph": 6.5,
        "notes": "Prefers slightly acidic soil (pH 5.2-6.2 helps prevent Potato Scab disease). Tuberization stops above 24°C."
    },
    "soybean": {
        "name": "Soybean (सोयाबीन)",
        "season": "Kharif (Monsoon)",
        "min_temp": 20, "max_temp": 32, "min_humidity": 50,
        "min_ph": 6.0, "max_ph": 7.0,
        "notes": "Warm season legume; thrives in fertile, neutral soils; essential for soil nitrogen replenishment."
    }
}

HEATWAVE = 40
FROST = 4

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
        # 30-minute valid cache
        if time.time() - ts < 1800:
            data = json.loads(txt)
            data["source"] = "cache"
            data["timestamp"] = ts
            return data
    return None

# ---------------- Weather & Forecast Engine ----------------

def kelvin_to_c(k):
    return round(k - 273.15, 2)

def fetch_online(city):
    # Public Open-Meteo API (Free, global, hourly forecast included)
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
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,precipitation",
            "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
            "timezone": "auto"
        },
        timeout=10
    )
    w_res.raise_for_status()
    res_json = w_res.json()
    cur = res_json.get("current", {})
    hourly = res_json.get("hourly", {})
    daily = res_json.get("daily", {})

    return {
        "city": display_name,
        "lat": lat,
        "lon": lon,
        "temp_c": round(cur.get("temperature_2m", 25.0), 1),
        "humidity": round(cur.get("relative_humidity_2m", 60)),
        "wind_speed": round(cur.get("wind_speed_10m", 0.0), 1),
        "weather_code": cur.get("weather_code", 0),
        "desc": "Live Agro Meteorological Feed",
        "hourly": hourly,
        "daily": daily,
        "source": "Open-Meteo",
        "timestamp": int(time.time())
    }

def get_weather(city):
    cached = load_cache(city)
    if cached:
        return cached
    try:
        data = fetch_online(city)
        save_cache(city, data)
        return data
    except Exception as e:
        if cached:
            return cached
        raise RuntimeError(f"Weather data error: {e}")

# ---------------- Soil pH Neutralization & Prescription Engine ----------------

def get_ph_neutralization(ph_val):
    try:
        ph = float(ph_val)
    except (TypeError, ValueError):
        ph = 7.0

    if ph < 5.0:
        return {
            "ph": ph,
            "category": "Strongly Acidic (अत्यधिक अम्लीय)",
            "status_code": "strongly_acidic",
            "badge_color": "#ef4444",
            "remedy_title": "Apply Agricultural Limestone (CaCO3) or Slaked Lime",
            "dosage_acre": "1,000 - 1,400 kg per acre (2.5 - 3.5 tonnes/ha)",
            "dosage_sqm": "250 - 350 g/m²",
            "organic_remedy": "Hardwood wood ash (लकड़ी की राख) @ 150 g/m² + Well-decomposed farmyard manure.",
            "application_method": "Broadcast evenly across soil 3 to 4 weeks prior to sowing. Plough into top 15 cm soil and irrigate.",
            "nutrient_lockout": "Severe Phosphorus (P) fixation; high Aluminum/Manganese toxicity risk; poor Calcium availability.",
            "crop_impact": "Wheat, pulses, and mustard will suffer stunted growth. Only tea or acid-tolerant tubers survive."
        }
    elif ph < 6.0:
        return {
            "ph": ph,
            "category": "Moderately Acidic (मध्यम अम्लीय)",
            "status_code": "moderately_acidic",
            "badge_color": "#f97316",
            "remedy_title": "Apply Dolomitic Limestone (CaCO3 + MgCO3)",
            "dosage_acre": "500 - 800 kg per acre (1.2 - 2.0 tonnes/ha)",
            "dosage_sqm": "120 - 200 g/m²",
            "organic_remedy": "Bio-fertilizers, vermicompost, and poultry manure to gradually lift pH.",
            "application_method": "Apply during land preparation. Incorporate with rotavator before pre-sowing irrigation.",
            "nutrient_lockout": "Reduced Molybdenum and Magnesium availability. Slower Rhizobium nitrogen fixation.",
            "crop_impact": "Suitable for Rice and Potato. Sub-optimal for Wheat, Mustard, and Gram."
        }
    elif ph <= 7.5:
        return {
            "ph": ph,
            "category": "Optimal & Balanced (संतुलित / आदर्श)",
            "status_code": "optimal",
            "badge_color": "#10b981",
            "remedy_title": "Soil pH is in the Ideal Zone – No Chemical Neutralizer Needed",
            "dosage_acre": "0 kg chemical neutralizers",
            "dosage_sqm": "0 g/m²",
            "organic_remedy": "Maintain soil organic carbon with regular compost, green manuring (Dhaincha/Sunhemp), and crop residue mulch.",
            "application_method": "Standard agronomic practices; avoid excessive acidic chemical fertilizers (like Ammonium Sulfate).",
            "nutrient_lockout": "None. Maximum bioavailability of N, P, K, Ca, Mg, and essential trace elements.",
            "crop_impact": "Ideal for almost all commercial Indian crops including Wheat, Rice, Mustard, Sugarcane, and Cotton."
        }
    elif ph <= 8.5:
        return {
            "ph": ph,
            "category": "Moderately Alkaline (मध्यम क्षारीय)",
            "status_code": "moderately_alkaline",
            "badge_color": "#eab308",
            "remedy_title": "Apply Agricultural Gypsum (Calcium Sulfate - CaSO4·2H2O)",
            "dosage_acre": "800 - 1,200 kg per acre (2.0 - 3.0 tonnes/ha)",
            "dosage_sqm": "200 - 300 g/m²",
            "organic_remedy": "Press mud (sugar mill residue), green manure, and farmyard manure (FYM) to produce organic acids.",
            "application_method": "Apply gypsum before monsoon or pre-sowing irrigation. Calcium displaces sodium on clay particles.",
            "nutrient_lockout": "Micronutrient deficiencies: Iron (Fe), Zinc (Zn), Manganese (Mn), and Copper (Cu) become insoluble.",
            "crop_impact": "Foliar yellowing (chlorosis) in seedlings. Rice and Cotton can tolerate; pulses and oilseeds struggle."
        }
    else:
        return {
            "ph": ph,
            "category": "Strongly Alkaline / Sodic Soil (अत्यधिक क्षारीय / ऊसर भूमि)",
            "status_code": "strongly_alkaline",
            "badge_color": "#dc2626",
            "remedy_title": "Apply Elemental Sulfur or Iron Pyrite (FeS2) + Heavy Leaching",
            "dosage_acre": "400 - 600 kg per acre Elemental Sulfur OR 1,500 kg Pyrite",
            "dosage_sqm": "100 - 150 g/m² Elemental Sulfur",
            "organic_remedy": "Heavy green manuring with Sesbania (ढैंचा) followed by water inundation and drainage leaching.",
            "application_method": "Broadcast sulfur into moist soil. Soil bacteria (Thiobacillus) oxidize sulfur into sulfuric acid over 4-6 weeks.",
            "nutrient_lockout": "Severe soil deflocculation (soil crusting), total Phosphorus and Micronutrient lock. Sodium toxicity.",
            "crop_impact": "Crop failure for sensitive crops. Requires reclamation before sowing Wheat or sensitive vegetables."
        }

# ---------------- Next-Day & Future Precision Weather Action Planner ----------------

def generate_next_day_advisory(hourly_data, current_moisture=None):
    """
    Analyzes next 24-48h meteorology to generate actionable farming tasks:
    - Fertilizer spraying window
    - Fungal / Pest risk
    - Smart Irrigation synchronization
    """
    if not hourly_data or "precipitation_probability" not in hourly_data:
        return []

    # Extract next 24 hours
    probs = hourly_data.get("precipitation_probability", [])[:24]
    rains = hourly_data.get("precipitation", [])[:24]
    winds = hourly_data.get("wind_speed_10m", [])[:24]
    temps = hourly_data.get("temperature_2m", [])[:24]
    humids = hourly_data.get("relative_humidity_2m", [])[:24]

    max_rain_prob = max(probs) if probs else 0
    total_rain_mm = sum(rains) if rains else 0.0
    max_wind_kmh = max(winds) if winds else 0.0
    avg_humidity = sum(humids) / len(humids) if humids else 60.0
    min_temp = min(temps) if temps else 20.0
    max_temp = max(temps) if temps else 30.0

    advisories = []

    # 1. Fertilizer & Foliar Spraying Advisory
    if max_rain_prob > 40 or total_rain_mm > 2.0:
        advisories.append({
            "category": "Fertilizer / Foliar Spray",
            "status": "DELAY",
            "status_class": "badge-danger",
            "icon": "fa-solid fa-cloud-showers-heavy",
            "title": "Do Not Spray Fertilizer Tomorrow (खाद छिड़काव स्थगित करें)",
            "message": f"High rain probability ({max_rain_prob}%) with {total_rain_mm:.1f} mm rain predicted within 24h. Rain will wash expensive foliar urea/nutrients away into soil runoff."
        })
    elif max_wind_kmh > 18:
        advisories.append({
            "category": "Fertilizer / Foliar Spray",
            "status": "CAUTION",
            "status_class": "badge-warning",
            "icon": "fa-solid fa-wind",
            "title": "High Wind Spray Drift Warning (तेज हवा चेतावनी)",
            "message": f"Wind gusts will reach {max_wind_kmh:.1f} km/h. Spray droplet drift will blow chemicals away from crop leaves and cause uneven coverage."
        })
    else:
        advisories.append({
            "category": "Fertilizer / Foliar Spray",
            "status": "OPTIMAL",
            "status_class": "badge-success",
            "icon": "fa-solid fa-seedling",
            "title": "Ideal Window for Fertilizer & Pesticide Spray (छिड़काव के लिए आदर्श दिन)",
            "message": "Clear skies with gentle breeze (<15 km/h). Best application hours are early morning (7:00 AM – 10:00 AM) or late afternoon."
        })

    # 2. Smart Irrigation Coordination with Hardware Soil Sensor
    if current_moisture is not None:
        try:
            moist_val = float(current_moisture)
        except (ValueError, TypeError):
            moist_val = 50.0

        if moist_val < 30.0:
            if total_rain_mm > 8.0:
                advisories.append({
                    "category": "Smart Irrigation Scheduling",
                    "status": "HOLD",
                    "status_class": "badge-info",
                    "icon": "fa-solid fa-hourglass-half",
                    "title": "Hold Water Pump Operation (सिंचाई रोकें - बारिश संभावित)",
                    "message": f"Soil is currently dry ({moist_val:.0f}%), but significant rainfall ({total_rain_mm:.1f} mm) is predicted within 24 hours. Save electricity and prevent root waterlogging."
                })
            else:
                advisories.append({
                    "category": "Smart Irrigation Scheduling",
                    "status": "IRRIGATE",
                    "status_class": "badge-warning",
                    "icon": "fa-solid fa-faucet-drip",
                    "title": "Run Irrigation Water Pump (सिंचाई तुरंत करें)",
                    "message": f"Soil moisture is critically low ({moist_val:.0f}%) and no natural rainfall is forecasted. Activate irrigation pump to protect vegetative growth."
                })
        elif moist_val > 75.0:
            advisories.append({
                "category": "Smart Irrigation Scheduling",
                "status": "SATURATED",
                "status_class": "badge-info",
                "icon": "fa-solid fa-droplet",
                "title": "Soil Moisture Saturated (पर्याप्त नमी)",
                "message": f"Soil moisture is high ({moist_val:.0f}%). Ensure farm drainage channels are open if further rainfall occurs."
            })

    # 3. Pest & Fungal Disease Early Warning
    if avg_humidity > 80 and min_temp > 18:
        advisories.append({
            "category": "Pest & Disease Advisory",
            "status": "WARNING",
            "status_class": "badge-danger",
            "icon": "fa-solid fa-biohazard",
            "title": "High Fungal Blight / Rust Risk (फफूंद रोग चेतावनी)",
            "message": "Prolonged high atmospheric humidity (>80%) creates favorable conditions for fungal spores, powdery mildew, and leaf spot. Inspect crop leaves and consider preventive bio-fungicide spray."
        })

    # 4. Thermal / Frost Protection
    if min_temp <= FROST:
        advisories.append({
            "category": "Thermal Protection",
            "status": "CRITICAL",
            "status_class": "badge-danger",
            "icon": "fa-solid fa-snowflake",
            "title": "Ground Frost Alert (पाले की चेतावनी)",
            "message": f"Night temperature dropping to {min_temp:.1f}°C. Provide light evening irrigation or field smoke/mulching to protect tender crops from frost damage."
        })
    elif max_temp >= HEATWAVE:
        advisories.append({
            "category": "Thermal Protection",
            "status": "HEAT STRESS",
            "status_class": "badge-danger",
            "icon": "fa-solid fa-fire",
            "title": "Severe Heatwave Alert (भीषण लू चेतावनी)",
            "message": f"Peak daytime temperature reaching {max_temp:.1f}°C. Irrigate early in the morning to prevent midday transpiration shock and leaf wilting."
        })

    return advisories

# ---------------- Composite Crop Recommendations (Weather + Soil pH) ----------------

def composite_crop_recommendations(temp_c, humidity, soil_moisture=None, ph_val=None):
    recs = {}
    ph = float(ph_val) if ph_val is not None else 6.8

    for crop_id, r in CROPS.items():
        weather_ok = (r["min_temp"] <= temp_c <= r["max_temp"]) and (humidity >= r["min_humidity"])
        ph_ok = (r["min_ph"] <= ph <= r["max_ph"])

        if weather_ok and ph_ok:
            status = "Highly Recommended (सर्वोत्तम उपयुक्त)"
            badge = "optimal"
            reason = f"Ideal climate ({temp_c}°C, {humidity}%) and soil pH ({ph:.1f}) is within preferred range ({r['min_ph']}-{r['max_ph']})."
        elif weather_ok and not ph_ok:
            status = "Weather Suitable, but pH Amendment Required"
            badge = "ph_warning"
            if ph < r["min_ph"]:
                reason = f"Weather is perfect, but soil pH ({ph:.1f}) is too acidic for this crop (needs {r['min_ph']}-{r['max_ph']}). Apply lime before sowing."
            else:
                reason = f"Weather is perfect, but soil pH ({ph:.1f}) is too alkaline for this crop (needs {r['min_ph']}-{r['max_ph']}). Apply gypsum/sulfur before sowing."
        elif not weather_ok and ph_ok:
            status = "Soil Suitable, but Climate Sub-Optimal"
            badge = "climate_warning"
            reason = f"Soil pH ({ph:.1f}) matches, but current temperature ({temp_c}°C) or humidity ({humidity}%) is outside ideal range ({r['min_temp']}-{r['max_temp']}°C)."
        else:
            status = "Not Recommended (अनुशंसित नहीं)"
            badge = "not_recommended"
            reason = f"Neither climate ({temp_c}°C, {humidity}%) nor soil pH ({ph:.1f}) is suitable currently."

        recs[crop_id] = {
            "name": r["name"],
            "season": r["season"],
            "status": status,
            "badge": badge,
            "reason": reason,
            "notes": r["notes"],
            "ideal_temp": f"{r['min_temp']}°C – {r['max_temp']}°C",
            "ideal_humidity": f"{r['min_humidity']}%+",
            "ideal_ph": f"{r['min_ph']} – {r['max_ph']}"
        }

    return recs

# ---------------- Telegram Bot Bridge for pH Node ----------------

def fetch_telegram_ph(bot_token="8764275901:AAFbCOGIOqnNyLkqLqdLMTp-vWJTt5bIx7A"):
    """
    Polls the Telegram Bot getUpdates endpoint to retrieve the latest pH reading.
    e.g. ESP8266 sent: "PH value is 5.40"
    """
    if not bot_token:
        bot_token = "8764275901:AAFbCOGIOqnNyLkqLqdLMTp-vWJTt5bIx7A"

    url = f"https://api.telegram.org/bot{bot_token}/getUpdates?offset=-1"
    res = requests.get(url, timeout=8)
    res.raise_for_status()
    data = res.json()

    if data.get("ok") and data.get("result"):
        last_item = data["result"][-1]
        msg_text = last_item.get("message", {}).get("text", "")
        # Extract numeric float
        match = re.search(r"([0-9]+\.[0-9]+)", msg_text)
        if match:
            return {
                "success": True,
                "ph": float(match.group(1)),
                "raw_text": msg_text,
                "timestamp": last_item.get("message", {}).get("date", int(time.time()))
            }
        # Fallback to integer
        int_match = re.search(r"(\b[0-9]{1,2}\b)", msg_text)
        if int_match:
            return {
                "success": True,
                "ph": float(int_match.group(1)),
                "raw_text": msg_text,
                "timestamp": last_item.get("message", {}).get("date", int(time.time()))
            }

    return {"success": False, "error": "No pH message found in Telegram Bot updates"}
