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
FG_COLOR = "#CCCCCC"      # Default Light Grey for normal text
DIVIDER_COLOR = "#333333"

# --- SECTION SPECIFIC COLORS ---
SPOTIFY_GREEN = "#1DB954" # Official Spotify Green
POMODORO_BLUE = "#4FC3F7" # A nice bright Light Blue

# --- FONTS ---
FONT_HUGE = ("Helvetica", 80, "bold")
FONT_LARGE = ("Helvetica", 30, "bold")
FONT_MED = ("Helvetica", 18)
FONT_SMALL = ("Helvetica", 12)