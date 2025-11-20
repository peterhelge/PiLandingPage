import os
from dotenv import load_dotenv

# Load secrets from .env file
load_dotenv()

# --- API KEYS ---
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_LAT = os.getenv("WEATHER_LAT")
WEATHER_LON = os.getenv("WEATHER_LON")
WEATHER_UNITS = os.getenv("WEATHER_UNITS", "metric")

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SPOTIPY_SCOPE = "user-read-playback-state user-modify-playback-state playlist-read-private"

# --- UI THEME ---
BG_COLOR = "#121212"

# UPDATED: Softer Grey Text (easier on eyes)
FG_COLOR = "#CCCCCC" 
ACCENT_COLOR = "#1DB954" 
DIVIDER_COLOR = "#333333"

# --- UPDATED FONTS (Bigger to fill screen) ---
FONT_HUGE = ("Helvetica", 80, "bold")    # Was 50
FONT_LARGE = ("Helvetica", 30, "bold")   # Was 24
FONT_MED = ("Helvetica", 18)             # Was 14
FONT_SMALL = ("Helvetica", 12)           # Was 10