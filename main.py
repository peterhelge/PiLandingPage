import tkinter as tk
import config
from weather import WeatherWidget
from pomodoro import PomodoroWidget
from spotify import SpotifyWidget

class DashboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # 1. Set Fullscreen
        self.attributes('-fullscreen', True)
        
        # 2. Bind the "Escape" key to close the app (useful for testing)
        self.bind("<Escape>", lambda event: self.destroy())

        self.configure(bg=config.BG_COLOR)
        
        # Remove the specific geometry line, fullscreen handles it now
        # self.geometry("800x480")
        # self.attributes('-fullscreen', True) # Uncomment on Pi
        
        # Main Container
        container = tk.Frame(self, bg=config.BG_COLOR)
        container.pack(fill="both", expand=True)

        # Create 3 Columns
        col1 = tk.Frame(container, bg=config.BG_COLOR)
        col1.pack(side="left", fill="both", expand=True)
        
        col2 = tk.Frame(container, bg=config.BG_COLOR)
        col2.pack(side="left", fill="both", expand=True)
        
        col3 = tk.Frame(container, bg=config.BG_COLOR)
        col3.pack(side="left", fill="both", expand=True)
        
        # --- ADD WIDGETS ---
        WeatherWidget(col1)
        
        # Divider 1
        tk.Frame(container, width=1, bg=config.DIVIDER_COLOR).pack(side="left", fill="y")
        
        PomodoroWidget(col2)
        
        # Divider 2
        tk.Frame(container, width=1, bg=config.DIVIDER_COLOR).pack(side="left", fill="y")
        
        SpotifyWidget(col3)

if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()