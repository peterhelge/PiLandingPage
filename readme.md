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

### 4. ✅ Today's Todo
- **Major/Minor Tasks**: Two-tier todo list synced against dedicated Todoist projects.
- **Pomodoro Sessions**: Track focus sessions per major task.
- **Two-Way Sync**: Completing a task locally or in the Todoist app is reflected on both sides.
- **Page 2**: Accessible by swiping left.

### 5. 🏠 Home Assistant Control
- **Direct Integration**: Talk directly to your Home Assistant instance API.
- **Interactive Widgets**: graphical lightbulb icons showing live state (Yellow=On, Gray=Off).
- **Attic Mould-Risk Gauge**: Optional gauge computed from a temperature/humidity sensor pair.
- **Zero Lag**: Native Python implementation means instant response compared to loading web dashboards.
- **Page 3**: Accessible by swiping left twice.

### 6. ⚙️ System Settings
- **Shutdown & Reboot**: Power off or restart the Pi. Each button needs a second tap, and the command is non-interactive `sudo -n` so a password prompt cannot hang the screen.
- **Exit Kiosk**: Closes the app for maintenance. Also needs a second tap. The Escape key does not close the kiosk.
- **Protection**: Located on Page 4 (Swipe left three times) to prevent accidental clicks.

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
3. **Important:** Add `http://127.0.0.1:8080/callback` to the **Redirect URIs**. Spotify deprecated `localhost` as a redirect host (April 2025) — use the literal loopback IP `127.0.0.1` instead, and make sure the port here matches `SPOTIPY_REDIRECT_URI` in your `.env` exactly.

### 3. Home Assistant
1. In Home Assistant, go to your User Profile (bottom left) -> **Security**.
2. Create a **Long-Lived Access Token**.
3. Prefer an `https://` URL for the instance. Plain `http://` is allowed for local names (`homeassistant.local`, a single-label hostname) and private addresses, and the Home Control page warns that the token can be read on that network. HTTP to a public host is refused. Set `HA_ALLOW_INSECURE_HTTP=1` only if you accept that anyone on the path can read the token.
4. Note down the **Entity IDs** you want to control (e.g., `light.living_room`).
5. Optional - mould-risk gauges: if you have a temperature and humidity sensor pair (e.g. in an attic/crawlspace or a laundry room), note down their Entity IDs too for `MOLD_RISK_TEMP_ENTITY`/`MOLD_RISK_HUMIDITY_ENTITY` (attic) and/or `LAUNDRY_MOLD_RISK_TEMP_ENTITY`/`LAUNDRY_MOLD_RISK_HUMIDITY_ENTITY` (laundry) below. Each gauge simply doesn't appear if its pair isn't set.

### 4. Todoist
1. Go to Todoist **Settings -> Integrations -> Developer** and copy your **API token**.
2. Create two Todoist projects to sync against - one for major tasks, one for minor tasks (defaults: `Today - Major` and `Today - Minor`, or pick your own names and set them below).

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
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8080/callback

# Home Assistant
# Prefer https://. http:// is only kept for a local/private host.
HA_BASE_URL=http://homeassistant.local:8123
HA_ACCESS_TOKEN=your_long_token_here
# HA_ALLOW_INSECURE_HTTP=1
# Any entity here (lights, switches, or plain temp/humidity sensors) gets its own
# widget automatically. Name sensor entities with "temperature"/"humidity" in the
# id so the right icon is picked, e.g. sensor.laundry_temperature.
HA_ENTITIES=light.lamp1,switch.plug2,sensor.laundry_temperature,sensor.laundry_humidity

# Mould-risk gauges (optional - omit a pair to hide that gauge)
MOLD_RISK_TEMP_ENTITY=sensor.your_temperature_sensor
MOLD_RISK_HUMIDITY_ENTITY=sensor.your_humidity_sensor
LAUNDRY_MOLD_RISK_TEMP_ENTITY=sensor.your_laundry_temperature_sensor
LAUNDRY_MOLD_RISK_HUMIDITY_ENTITY=sensor.your_laundry_humidity_sensor

# Todoist (Today's Todo sync)
TODOIST_API_TOKEN=your_todoist_api_token
TODOIST_MAJOR_PROJECT_NAME=Today - Major
TODOIST_MINOR_PROJECT_NAME=Today - Minor
```

### 4. Run the App
To run on the display allowing graphical output from SSH:
```bash
DISPLAY=:0 python main.py
```

### 5. Logs
Errors (weather/Spotify/HA/Todoist fetch failures, etc.) are written to
`logs/app.log`, alongside the same output printed to the console. Log files
rotate daily and anything older than 30 days is deleted automatically.