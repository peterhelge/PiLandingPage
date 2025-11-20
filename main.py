import tkinter as tk
import config
from weather import WeatherWidget
from pomodoro import PomodoroWidget
from spotify import SpotifyWidget

class DashboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PiLandingPage")
        self.configure(bg=config.BG_COLOR)
        
        # ================= KIOSK SETTINGS =================
        
        # 1. Remove the Window Title Bar and Borders immediately
        # This prevents the "X" and "-" buttons from appearing
        self.overrideredirect(True)
        
        # 2. Hide the Mouse Cursor
        # Essential for a clean touch-screen experience
        self.config(cursor="none")
        
        # 3. Get Screen Dimensions dynamically
        # This ensures it works in both Portrait and Landscape without hardcoding numbers
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # 4. Force Fullscreen with a slight delay
        # The 'after(100)' waits 100ms. This gives the Raspberry Pi OS window manager
        # time to register the window before we force it to take over the screen.
        # This fixes the issue where the taskbar might stay visible.
        self.after(100, lambda: self.attributes('-fullscreen', True))
        
        # 5. Emergency Exit
        # Press 'ESC' on a keyboard to close the app (useful for maintenance)
        self.bind("<Escape>", lambda event: self.destroy())

        # ================= LAYOUT =================

        # Main Container
        container = tk.Frame(self, bg=config.BG_COLOR)
        container.pack(fill="both", expand=True)

        # Create 3 Columns
        # We use expand=True so they share the width equally
        col1 = tk.Frame(container, bg=config.BG_COLOR)
        col1.pack(side="left", fill="both", expand=True)
        
        col2 = tk.Frame(container, bg=config.BG_COLOR)
        col2.pack(side="left", fill="both", expand=True)
        
        col3 = tk.Frame(container, bg=config.BG_COLOR)
        col3.pack(side="left", fill="both", expand=True)
        
        # --- ADD WIDGETS ---
        
        # Left Column: Weather
        WeatherWidget(col1)
        
        # Divider Line 1
        tk.Frame(container, width=1, bg=config.DIVIDER_COLOR).pack(side="left", fill="y")
        
        # Middle Column: Pomodoro Timer
        PomodoroWidget(col2)
        
        # Divider Line 2
        tk.Frame(container, width=1, bg=config.DIVIDER_COLOR).pack(side="left", fill="y")
        
        # Right Column: Spotify
        SpotifyWidget(col3)

if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()