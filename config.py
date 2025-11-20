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
FG_COLOR = "#FFFFFF"
ACCENT_COLOR = "#1DB954" # Spotify Green
DIVIDER_COLOR = "#333333"

# --- FONTS ---
FONT_HUGE = ("Helvetica", 50, "bold")
FONT_LARGE = ("Helvetica", 24, "bold")
FONT_MED = ("Helvetica", 14)
FONT_SMALL = ("Helvetica", 10)