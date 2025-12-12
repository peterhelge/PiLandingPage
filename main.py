import tkinter as tk
import os
import config
from weather import WeatherWidget
from pomodoro import PomodoroWidget
from spotify import SpotifyWidget
import create_icons
from swipe_container import SwipeableContainer
from home_assistant import HomeAssistantPage

# ... imports ...

# Check for assets and generate if missing
if not os.path.exists("assets") or not os.listdir("assets"):
    create_icons.generate_icons()

class DashboardPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.BG_COLOR)
        
        # Main Container
        # We don't need another container frame, simple pack colums directly into self
        # Create 3 Columns
        col1 = tk.Frame(self, bg=config.BG_COLOR)
        col1.pack(side="left", fill="both", expand=True)
        
        col2 = tk.Frame(self, bg=config.BG_COLOR)
        col2.pack(side="left", fill="both", expand=True)
        
        col3 = tk.Frame(self, bg=config.BG_COLOR)
        col3.pack(side="left", fill="both", expand=True)
        
        # --- ADD WIDGETS ---
        
        # Left Column: Weather
        WeatherWidget(col1)
        
        # Divider Line 1
        tk.Frame(self, width=1, bg=config.DIVIDER_COLOR).pack(side="left", fill="y")
        
        # Middle Column: Pomodoro Timer
        PomodoroWidget(col2)
        
        # Divider Line 2
        tk.Frame(self, width=1, bg=config.DIVIDER_COLOR).pack(side="left", fill="y")
        
        # Right Column: Spotify
        SpotifyWidget(col3)

class DashboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PiLandingPage")
        self.configure(bg=config.BG_COLOR)
        
        # ================= KIOSK SETTINGS =================
        self.overrideredirect(True)
        self.config(cursor="none")
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        
        self.after(100, lambda: self.attributes('-fullscreen', True))
        self.bind("<Escape>", lambda event: self.destroy())

        # ================= LAYOUT =================
        
        # Initialize the Swipe Container with our pages
        self.container = SwipeableContainer(self, pages=[DashboardPage, HomeAssistantPage])
        self.container.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()