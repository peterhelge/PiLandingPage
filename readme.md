# PiLandingPage

A sleek, touch-friendly smart dashboard designed for the Raspberry Pi 4 and the Official Touch Display 2. Built with Python and Tkinter, it provides a unified interface for your daily workflow.

## 📱 Features

### 1. 🌦️ Weather Station
- **Real-time Data**: Fetches current temperature and weather conditions.
- **Forecast**: Displays daily High and Low temperatures.
- **Visuals**: Custom-generated, flat-design weather icons.
- **Source**: Powered by OpenWeatherMap One Call API 3.0.
- **Updates**: Refreshes automatically every hour.

### 2. 🍅 Pomodoro Timer
- **Focus Mode**: Standard 25-minute countdown timer.
- **Controls**: Start, Pause, and Reset functionality.
- **Visual Feedback**: Large, easy-to-read countdown for glanceability.

### 3. 🎵 Spotify Controller
- **Now Playing**: Shows Track, Artist, and Device name.
- **Controls**: Play/Pause, Next/Previous Track, Volume Up/Down.
- **Quick Playlists**: Scrollable list of your top 10 playlists for one-touch playback.
- **Status**: Polls playback state every 5 seconds.

---

## 🛠️ Hardware Requirements
- **Raspberry Pi** (Recommended: Pi 4 Model B or Pi 5)
- **Touch Screen** (Optimized for Raspberry Pi Touch Display 2)
- **Resolution**: Default set to `800x480` (Adjustable in `main.py`)

---

## ⚙️ Prerequisites

Before running the code, you need to set up accounts for the APIs.

### 1. OpenWeatherMap
1. Sign up at [openweathermap.org](https://openweathermap.org/).
2. Subscribe to the "One Call API 3.0" (Free tier available, but requires credit card).
3. Get your **API Key**.

### 2. Spotify Developer
1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Create a new App.
3. Get your **Client ID** and **Client Secret**.
4. **Important:** In the app settings, add `http://localhost:8888/callback` to the **Redirect URIs**.

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/PiLandingPage.git
cd PiLandingPage