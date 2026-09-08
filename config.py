import os
from dotenv import load_dotenv

load_dotenv()

# --- API KEYS ---
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_LAT = os.getenv("WEATHER_LAT")
WEATHER_LON = os.getenv("WEATHER_LON")
WEATHER_UNITS = os.getenv("WEATHER_UNITS", "metric")
WEATHER_LOCATION_NAME = os.getenv("WEATHER_LOCATION_NAME")

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SPOTIPY_SCOPE = "user-read-playback-state user-modify-playback-state playlist-read-private"

# --- UI THEME ---
BG_COLOR = "#121212"
FG_COLOR = "#B0B0B0"      
DIVIDER_COLOR = "#222222"

# --- UPDATED DARKER COLORS ---
SPOTIFY_GREEN = "#107C41"   # Much darker, professional green
POMODORO_BLUE = "#0277BD"   # Deep Ocean Blue
WEATHER_YELLOW = "#F57F17"  # Dark Gold/Orange-Yellow

ACCENT_COLOR = SPOTIFY_GREEN

# --- UPDATED FONTS (Verdana is rounder) ---
FONT_HUGE = ("Verdana", 80, "bold")
FONT_LARGE = ("Verdana", 28, "bold")
FONT_MED = ("Verdana", 16)
FONT_SMALL = ("Verdana", 11)
FONT_PLAYLIST = ("Verdana", 14)

# --- HOME ASSISTANT ---
HA_BASE_URL = os.getenv("HA_BASE_URL", "http://homeassistant.local:8123")
HA_ACCESS_TOKEN = os.getenv("HA_ACCESS_TOKEN")
# Comma separated string in .env, converted to list here
_ha_entities_str = os.getenv("HA_ENTITIES", "")
HA_ENTITIES = [e.strip() for e in _ha_entities_str.split(",") if e.strip()]

# --- GOOGLE KEEP (Today's Todo sync) ---
GOOGLE_KEEP_EMAIL = os.getenv("GOOGLE_KEEP_EMAIL")
GOOGLE_KEEP_MASTER_TOKEN = os.getenv("GOOGLE_KEEP_MASTER_TOKEN")
GOOGLE_KEEP_MAJOR_NOTE_TITLE = os.getenv("GOOGLE_KEEP_MAJOR_NOTE_TITLE", "Today - Major")
GOOGLE_KEEP_MINOR_NOTE_TITLE = os.getenv("GOOGLE_KEEP_MINOR_NOTE_TITLE", "Today - Minor")
GOOGLE_KEEP_SYNC_INTERVAL_MS = int(os.getenv("GOOGLE_KEEP_SYNC_INTERVAL_MS", "120000"))

# --- TODO SCREEN ---
TODO_MAX_MAJOR = int(os.getenv("TODO_MAX_MAJOR", "4"))
TODO_MAX_MINOR = int(os.getenv("TODO_MAX_MINOR", "8"))
TODO_DATA_DIR = os.getenv("TODO_DATA_DIR", "todo_data")
TODO_ACCENT = "#00BFA5"    # Teal, distinct from SPOTIFY_GREEN/POMODORO_BLUE/WEATHER_YELLOW
TODO_DONE_COLOR = "#555555"