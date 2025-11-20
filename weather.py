import tkinter as tk
import requests
import os
from PIL import Image, ImageTk
import config 

class WeatherWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.BG_COLOR, bd=0)
        self.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Title
        tk.Label(self, text="Today's Weather", font=config.FONT_MED, 
                 bg=config.BG_COLOR, fg="gray").pack(pady=(10,5))

        # Icon
        self.icon_lbl = tk.Label(self, bg=config.BG_COLOR)
        self.icon_lbl.pack(pady=5)

        # Temperature
        self.temp_lbl = tk.Label(self, text="--°", font=config.FONT_HUGE, 
                                 bg=config.BG_COLOR, fg=config.FG_COLOR)
        self.temp_lbl.pack()

        # Description
        self.desc_lbl = tk.Label(self, text="Loading...", font=config.FONT_MED, 
                                 bg=config.BG_COLOR, fg="gray")
        self.desc_lbl.pack()
        
        # Forecast High/Low
        self.forecast_lbl = tk.Label(self, text="H: --°  L: --°", font=config.FONT_SMALL, 
                                     bg=config.BG_COLOR, fg="white")
        self.forecast_lbl.pack(pady=5)

        self.update_weather()

    def get_icon_path(self, main_condition):
        condition = main_condition.lower()
        path = "assets/clouds.png" # Default
        if "clear" in condition: path = "assets/clear.png"
        elif "rain" in condition or "drizzle" in condition: path = "assets/rain.png"
        elif "snow" in condition: path = "assets/snow.png"
        elif "thunder" in condition: path = "assets/thunderstorm.png"
        elif "mist" in condition or "fog" in condition: path = "assets/mist.png"
        return path

    def update_weather(self):
        if not config.WEATHER_API_KEY:
            self.desc_lbl.config(text="No API Key")
            return

        try:
            # ONE CALL 3.0 API
            url = f"https://api.openweathermap.org/data/3.0/onecall?lat={config.WEATHER_LAT}&lon={config.WEATHER_LON}&exclude=minutely,alerts&appid={config.WEATHER_API_KEY}&units={config.WEATHER_UNITS}"
            res = requests.get(url)
            data = res.json()

            if "current" in data:
                # Current Temp
                current = data["current"]
                temp = int(current["temp"])
                condition = current["weather"][0]["main"]
                desc = current["weather"][0]["description"].title()

                # Daily Forecast (Index 0 is today)
                daily = data["daily"][0]
                max_temp = int(daily["temp"]["max"])
                min_temp = int(daily["temp"]["min"])

                # Update Text
                self.temp_lbl.config(text=f"{temp}°")
                self.desc_lbl.config(text=desc)
                self.forecast_lbl.config(text=f"H: {max_temp}°  L: {min_temp}°")

                # Update Icon
                icon_path = self.get_icon_path(condition)
                if os.path.exists(icon_path):
                    img = Image.open(icon_path)
                    img = img.resize((100, 100), Image.Resampling.LANCZOS)
                    self.photo = ImageTk.PhotoImage(img)
                    self.icon_lbl.config(image=self.photo)
            else:
                print("Weather API Error: Data format unexpected")

        except Exception as e:
            print(f"Weather Connection Error: {e}")

        # Update every hour (3600000 ms)
        self.after(3600000, self.update_weather)