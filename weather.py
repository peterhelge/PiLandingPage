import tkinter as tk
import requests
import os
from PIL import Image, ImageTk
import config 

class WeatherWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.BG_COLOR, bd=0)
        self.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        # TITLE: Yellow
        self.title_lbl = tk.Label(self, text="Weather", font=config.FONT_MED, 
                 bg=config.BG_COLOR, fg=config.WEATHER_YELLOW)
        self.title_lbl.pack(pady=(10,5))

        # LOCATION: Yellow
        self.location_lbl = tk.Label(self, text="Loading...", font=config.FONT_MED, 
                 bg=config.BG_COLOR, fg=config.WEATHER_YELLOW)
        self.location_lbl.pack(pady=(0,5))

        # Icon
        self.icon_lbl = tk.Label(self, bg=config.BG_COLOR)
        self.icon_lbl.pack(pady=10, expand=True)

        # Temperature
        self.temp_lbl = tk.Label(self, text="--°", font=config.FONT_HUGE, 
                                 bg=config.BG_COLOR, fg=config.FG_COLOR)
        self.temp_lbl.pack(expand=True)

        # Description
        self.desc_lbl = tk.Label(self, text="...", font=config.FONT_MED, 
                                 bg=config.BG_COLOR, fg="gray")
        self.desc_lbl.pack(pady=5)
        
        # Forecast
        self.forecast_lbl = tk.Label(self, text="H: --°  L: --°", font=config.FONT_MED, 
                                     bg=config.BG_COLOR, fg=config.FG_COLOR)
        self.forecast_lbl.pack(pady=(5, 20))

        self.update_weather()

    def get_icon_path(self, main_condition):
        condition = main_condition.lower()
        path = "assets/clouds.png"
        if "clear" in condition: path = "assets/clear.png"
        elif "rain" in condition or "drizzle" in condition: path = "assets/rain.png"
        elif "snow" in condition: path = "assets/snow.png"
        elif "thunder" in condition: path = "assets/thunderstorm.png"
        elif "mist" in condition or "fog" in condition: path = "assets/mist.png"
        return path

    def update_weather(self):
        # Start a thread to fetch data so the UI doesn't freeze
        import threading
        t = threading.Thread(target=self._fetch_weather_data, daemon=True)
        t.start()

        # Schedule the next update (every 1 hour)
        self.after(3600000, self.update_weather)

    def _fetch_weather_data(self):
        if not config.WEATHER_API_KEY:
            self.after(0, lambda: self.desc_lbl.config(text="No API Key"))
            return

        try:
            url = f"https://api.openweathermap.org/data/3.0/onecall?lat={config.WEATHER_LAT}&lon={config.WEATHER_LON}&exclude=minutely,alerts&appid={config.WEATHER_API_KEY}&units={config.WEATHER_UNITS}"
            res = requests.get(url, timeout=10) # Added timeout
            res.raise_for_status()
            data = res.json()
            
            # Schedule UI update on the main thread
            self.after(0, lambda: self._update_ui_with_data(data))

        except Exception as e:
            print(f"Weather Fetch Error: {e}")
            self.after(0, lambda: self.desc_lbl.config(text="Error"))

    def _update_ui_with_data(self, data):
        try:
            if "current" in data:
                # --- UPDATED LOCATION LOGIC ---
                if config.WEATHER_LOCATION_NAME:
                    city_name = config.WEATHER_LOCATION_NAME
                else:
                    # Fallback to timezone if .env value is missing
                    timezone_str = data.get("timezone", "Unknown")
                    city_name = timezone_str.split("/")[-1].replace("_", " ")
                
                self.location_lbl.config(text=city_name)

                current = data["current"]
                temp = int(current["temp"])
                condition = current["weather"][0]["main"]
                desc = current["weather"][0]["description"].title()

                daily = data["daily"][0]
                max_temp = int(daily["temp"]["max"])
                min_temp = int(daily["temp"]["min"])

                self.temp_lbl.config(text=f"{temp}°")
                self.desc_lbl.config(text=desc)
                self.forecast_lbl.config(text=f"H: {max_temp}°   L: {min_temp}°")

                icon_path = self.get_icon_path(condition)
                if os.path.exists(icon_path):
                    img = Image.open(icon_path)
                    img = img.resize((120, 120), Image.Resampling.LANCZOS)
                    self.photo = ImageTk.PhotoImage(img) # Keep reference
                    self.icon_lbl.config(image=self.photo)
        except Exception as e:
            print(f"Weather UI Update Error: {e}")