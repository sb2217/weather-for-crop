# 🌾 AgriWeather – Weather & Crop Advisory System

[![Live Demo](https://img.shields.io/badge/demo-online-brightgreen.svg)](https://sb2217.github.io/weather-for-crop/)
[![GitHub Pages](https://img.shields.io/badge/Hosted%20on-GitHub%20Pages-blue.svg)](https://sb2217.github.io/weather-for-crop/)
[![Python](https://img.shields.io/badge/Python-3.x-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> A modern, responsive Agricultural Weather & Crop Suitability Advisory web application with real-time meteorological feeds, custom farm visuals, and agronomic crop recommendations.

---

## 🚀 Live Demo on GitHub Pages
Visit the live application directly in your browser:
👉 **[https://sb2217.github.io/weather-for-crop/](https://sb2217.github.io/weather-for-crop/)**

---

## ✨ Features

- **🌡️ Live Temperature & Conditions**: Real-time temperature (°C/°F toggle), apparent feels-like temperature, and daily min/max.
- **💧 Atmospheric Humidity**: Precision humidity percentage, moisture indexing, and soil evaporation indicators.
- **🌾 Smart Crop Advisory Engine**: Real-time suitability evaluation for major crops based on physiological agronomic thresholds:
  - **Wheat** (Rabi - Cool season cereal)
  - **Rice / Paddy** (Kharif - High heat & moisture)
  - **Maize / Corn** (Kharif - Moderate climate)
  - **Cotton** (Cash crop - Warm sunshine)
  - **Sugarcane** (Cash crop - Tropical heavy feeder)
  - **Pulses & Gram** (Rabi - Drought tolerant legume)
  - **Mustard** (Rabi - Winter oilseed)
  - **Potato** (Rabi - Cool tuber growth)
  - **Soybean** (Kharif - Nitrogen fixing legume)
- **⚠️ Agricultural Hazard Alerts**:
  - 🔥 **Heatwave Alert** ($\ge 40^\circ\text{C}$): Excessive evapotranspiration and wilting warning
  - ❄ **Ground Frost Warning** ($\le 4^\circ\text{C}$): Cell freeze and frost damage alert
  - 💧 **High Humidity & Fungal Risk** ($\ge 85\%$): Blight and fungal spore risk
  - 💨 **Strong Wind Advisory** ($\ge 32\text{ km/h}$): Crop lodging / stalk breakage warning
- **🎨 Custom Agricultural Background**:
  - High-definition panoramic farm landscape background (`static/crop_weather_bg.jpg`)
  - Optional **Dynamic Sky Mode** that adapts to live weather (clear, rain, clouds, mist)
  - Dark Glass Mode toggle
- **📍 Instant Geolocation**: 1-click "My Location" button with automatic GPS coordinates lookup.
- **⚡ Dual Mode**: Runs completely client-side on **GitHub Pages** (zero backend server required) and also supports local **Python Flask** server execution.

---

## 📂 Repository Structure

```text
weather-for-crop/
├── index.html                  # Standalone GitHub Pages entry point (Client-side app)
├── app.py                      # Flask backend application
├── weather_logic.py            # Python weather fetching and crop advisory rules
├── static/
│   ├── crop_weather_bg.jpg     # Custom agricultural wallpaper background
│   └── w_bg.png                # Pixel art desk wallpaper
├── templates/
│   └── index.html              # Jinja2 template for Flask deployment
├── .gitignore                  # Git ignore rules for cache and environment
└── README.md                   # Documentation and hosting guide
```

---

## 🌐 Hosting on GitHub Pages (Step-by-Step)

Because `index.html` is located directly at the root of the repository, enabling GitHub Pages takes less than a minute:

1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "Add GitHub Pages web app with live weather, crop advisory, and custom bg"
   git push -u origin main
   ```

2. Open your repository on GitHub:
   [https://github.com/sb2217/weather-for-crop](https://github.com/sb2217/weather-for-crop)

3. Click **Settings** (tab at the top right of the repository).

4. On the left sidebar, click **Pages**.

5. Under **Build and deployment**:
   - **Source**: Select `Deploy from a branch`
   - **Branch**: Select `main`
   - **Folder**: Select `/ (root)`
   - Click **Save**.

6. Wait ~30 to 60 seconds. Your live web app will be accessible at:
   👉 **`https://sb2217.github.io/weather-for-crop/`**

---

## 💻 Running Locally with Python (Optional)

If you wish to run the app locally with Flask:

1. **Install dependencies**:
   ```bash
   pip install flask requests
   ```

2. **Start the Flask server**:
   ```bash
   python app.py
   ```

3. **Open in browser**:
   Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000).

*(Alternatively, you can simply double-click `index.html` in your file explorer to open it in Chrome/Edge/Firefox!)*

---

## 📜 Agronomic Logic Reference

| Crop | Ideal Temp Range | Ideal Humidity | Agronomic Classification |
|---|---|---|---|
| **Wheat** | 10°C – 25°C | 45% – 70% | Rabi (Winter Cereal) |
| **Rice (Paddy)** | 20°C – 36°C | 65% – 95% | Kharif (Wetland Cereal) |
| **Maize (Corn)** | 18°C – 32°C | 45% – 75% | Kharif (Warm Cereal) |
| **Cotton** | 21°C – 35°C | 40% – 65% | Cash (Warm Fiber) |
| **Sugarcane** | 20°C – 35°C | 60% – 88% | Cash (Tropical Perennial) |
| **Pulses** | 14°C – 28°C | 35% – 65% | Rabi / Kharif (Legume) |
| **Mustard** | 10°C – 25°C | 40% – 65% | Rabi (Oilseed) |
| **Potato** | 14°C – 24°C | 55% – 85% | Rabi (Tuber) |
| **Soybean** | 20°C – 32°C | 50% – 75% | Kharif (Oilseed Legume) |

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
