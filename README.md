# 🌾 AgriWeather IoT – All-in-One Smart Farming, Soil pH & Crop Advisory

[![Live Demo](https://img.shields.io/badge/demo-online-brightgreen.svg)](https://sb2217.github.io/weather-for-crop/)
[![GitHub Pages](https://img.shields.io/badge/Hosted%20on-GitHub%20Pages-blue.svg)](https://sb2217.github.io/weather-for-crop/)
[![PWA](https://img.shields.io/badge/PWA-Installable-purple.svg)](https://sb2217.github.io/weather-for-crop/)
[![Python](https://img.shields.io/badge/Python-3.x-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **All-in-one Smart Farming Web App & Progressive Web App (PWA)** uniting live farm hardware telemetry (`base.apk` replacement), real-time soil pH monitoring via Telegram Bot, scientific pH neutralization prescriptions, precision next-day farming action advisories, and composite crop suitability matching.

---

## 🚀 Live Demo on GitHub Pages
Visit the live application directly in any smartphone or desktop browser:  
👉 **[https://sb2217.github.io/weather-for-crop/](https://sb2217.github.io/weather-for-crop/)**

*(On mobile Chrome/Safari, tap **"Add to Home Screen"** or **"Install App"** to use it fullscreen like a native Android APK!)*

---

## ✨ Unified Features

### 1. 📡 Live Farm Hardware Telemetry (Mobile APK Replacement)
- **Soil Moisture Sensor**: Live percentage ($0\% - 100\%$), visual progress bar, and dry/optimal/saturated status.
- **Relay Water Pump**: Live operational status (`ON` with green pulse / `OFF`) driven by automatic soil threshold logic.
- **Farm Lamp & Bulb**: Live status (`ON` with glowing amber / `OFF`) automated by LDR darkness sensor.
- **Cloud Ingestion**: Connects seamlessly with `projectiot.in` cloud polling using project `userName` and ESP8266 MAC address (`B4:E6:2D:30:77:55`).
- **Interactive Demo Stream Toggle**: Allows full demonstration of live telemetry even when physical microcontrollers are powered off.

### 2. 🧪 Live Soil pH & Telegram Bot Bridge (`Phsep2026 bot`)
- **Direct Telegram Bot API Integration**: Connects over mobile hotspot to the ESP8266 pH node without requiring any hardware reflashing.
- **Telegram `getUpdates` Engine**: Automatically extracts the latest `"PH value is X.XX"` message received by the bot.
- **Classification Spectrum**: Identifies whether the soil is *Strongly Acidic*, *Moderately Acidic*, *Balanced/Optimal*, *Moderately Alkaline*, or *Strongly Alkaline/Sodic*.

### 3. ⚖️ Scientific Soil pH Neutralization & Prescription Engine
- **Chemical Neutralizer Calculator**: Prescribes exact remedies based on live or manual pH:
  - **Acidic Soils ($< 6.0$)**: Agricultural Lime ($\text{CaCO}_3$), Dolomite, Slaked Lime.
  - **Alkaline Soils ($> 7.5$)**: Agricultural Gypsum ($\text{CaSO}_4 \cdot 2\text{H}_2\text{O}$), Elemental Sulfur, Iron Pyrite.
- **Dosage Calculator**: Displays specific application rates in **kg per acre** and **g per square meter**.
- **Organic Amendments**: Prescribes hardwood ash, well-decomposed cow dung manure, press mud, and green manure (Dhaincha/Sesbania).
- **Nutrient Lockout Warnings**: Flags bioavailability locks (Phosphorus fixation in acid soil; Zinc/Iron chlorosis in alkaline soil).
- **Interactive pH Slider**: Allows farmers or science exhibition judges to simulate any pH test report ($3.0 - 10.0$).

### 4. 🚜 Next-Day & Future Precision Action Planner ("What to do Tomorrow")
- **Fertilizer & Foliar Spray Advisory**: Analyzes next 24-48h rain probability and wind speed. Alerts the farmer to *Delay Spraying* if rain or wind drift will cause chemical runoff and waste.
- **Smart Irrigation Coordination**: Correlates live hardware soil moisture with tomorrow's predicted rainfall. If soil is dry but heavy rain is forecasted, it advises *Holding the Pump* to save water and electricity.
- **Pest & Fungal Disease Prevention**: Monitors sustained atmospheric humidity ($>80\%$) and temperature to alert farmers about fungal blight risks before outbreaks occur.
- **Thermal Stress & Frost Protection**: Alerts for extreme heatwaves ($\ge 40^\circ\text{C}$) or ground frost ($\le 4^\circ\text{C}$) with protective mulching/irrigation tips.

### 5. 🌾 Composite Crop Suitability Matrix (Weather + Soil pH)
Evaluates 9 major Indian crops (**Wheat, Rice, Maize, Cotton, Sugarcane, Pulses, Mustard, Potato, Soybean**) against **both atmospheric weather AND soil pH**:
- `Highly Recommended` (Both weather and soil pH are optimal).
- `Remedy Soil pH First` (Climate is ideal, but pH needs lime or gypsum before sowing).
- `Climate Sub-Optimal` (Soil matches, but temperature or humidity is out of season).
- `Not Recommended`.

---

## 📂 Repository Structure

```text
weather-for-crop/
├── index.html                  # Standalone GitHub Pages entry point (Client-side PWA)
├── manifest.json               # Progressive Web App manifest
├── sw.js                       # Service Worker for offline resilience
├── app.py                      # Flask backend application with REST API
├── weather_logic.py            # Python weather fetching, pH neutralization & advisory rules
├── static/
│   ├── crop_weather_bg.jpg     # Custom agricultural wallpaper background
│   └── w_bg.png                # App icon and visual asset
├── templates/
│   └── index.html              # Server-rendered Jinja2 template
├── .gitignore                  # Git ignore rules
└── README.md                   # Full documentation & project guide
```

---

## 🌐 Deploying Updates to GitHub Pages

To publish the new unified application to GitHub Pages:

```bash
git add .
git commit -m "Upgrade to unified Smart Farming PWA with IoT telemetry, Telegram pH bridge & next-day advisory"
git push origin main
```

Your live site will update automatically at:  
👉 **`https://sb2217.github.io/weather-for-crop/`**

---

## 💻 Running Locally with Python

```bash
# 1. Install dependencies
pip install flask requests

# 2. Run Flask server
python app.py

# 3. Open in browser
http://127.0.0.1:5000
```

*(You can also simply open `index.html` directly in Google Chrome, Microsoft Edge, or Safari!)*

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
