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

### 4. 🏠 Home Assistant Control (New!)
- **Direct Integration**: Talk directly to your Home Assistant instance API.
- **Interactive Widgets**: graphical lightbulb icons showing live state (Yellow=On, Gray=Off).
- **Zero Lag**: Native Python implementation means instant response compared to loading web dashboards.
- **Page 2**: Accessible by swiping left.

### 5. ⚙️ System Settings
- **Shutdown & Reboot**: Gracefully power off or restart your Pi from the UI.
- **Exit Kiosk**: Easily close the app for maintenance.
- **Protection**: Located on Page 3 (Swipe left twice) to prevent accidental clicks.

---

## 🛠️ Hardware Requirements
- **Raspberry Pi** (Recommended: Pi 4 Model B or Pi 5)
- **Touch Screen** (Optimized for Raspberry Pi Touch Display 2)
- **Resolution**: Default set to `800x480` (Adjustable in `main.py`)

---

## ⚙️ Prerequisites

Before running the code, you need to set up keys for the APIs.

### 1. OpenWeatherMap
1. Sign up at [openweathermap.org](https://openweathermap.org/).
2. Get your **API Key**.

### 2. Spotify Developer
1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Create a new App to get **Client ID** and **Client Secret**.
3. **Important:** Add `http://localhost:8888/callback` to the **Redirect URIs**.

### 3. Home Assistant
1. In Home Assistant, go to your User Profile (bottom left) -> **Security**.
2. Create a **Long-Lived Access Token**.
3. Note down the **Entity IDs** you want to control (e.g., `light.living_room`).

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/PiLandingPage.git
cd PiLandingPage
```

### 2. Install Dependencies
```bash
# On Raspberry Pi (Bookworm or newer), you might need --break-system-packages
pip install -r requirements.txt --break-system-packages
```

### 3. Configure Secrets
Create a `.env` file in the project folder:
```bash
nano .env
```
Paste in your keys:
```bash
# Weather
OPENWEATHER_API_KEY=your_key_here
WEATHER_LAT=59.3293
WEATHER_LON=18.0686

# Spotify
SPOTIPY_CLIENT_ID=your_id
SPOTIPY_CLIENT_SECRET=your_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback

# Home Assistant
HA_BASE_URL=http://homeassistant.local:8123
HA_ACCESS_TOKEN=your_long_token_here
HA_ENTITIES=light.lamp1,switch.plug2
```

### 4. Run the App
To run on the display allowing graphical output from SSH:
```bash
DISPLAY=:0 python main.py
```