import tkinter as tk
import config
from components import RoundedButton
from datetime import datetime
import locale

# Try to set locale for date formatting (e.g. "Thursday" instead of "Thu")
try:
    locale.setlocale(locale.LC_TIME, '')
except:
    pass

class PomodoroWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.BG_COLOR, bd=0)
        self.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        self.state = "STOPPED"
        self.minutes = 25
        self.seconds = 0
        
        # ================= REAL TIME CLOCK =================
        
        # ================= REAL TIME CLOCK =================
        
        # Clock Container (to align Clock and Power Button)
        self.clock_frame = tk.Frame(self, bg=config.BG_COLOR)
        self.clock_frame.pack(pady=(0, 0))
        
        # 1. Time Label (Big, Bright)
        self.clock_lbl = tk.Label(self.clock_frame, text="--:--", font=("Verdana", 45, "bold"), 
                                  bg=config.BG_COLOR, fg="white")
        self.clock_lbl.pack(side="left")
        
        # Power Button (Next to Clock)
        # Using a small, subtle RoundedButton with Red Icon
        def quick_shutdown():
            import platform
            if platform.system() == "Linux":
                import os
                os.system("sudo shutdown -h now")
            else:
                print("Simulating Shutdown...")
        
        # Load icon if possible
        try:
            from PIL import Image, ImageTk
            self.power_icon = ImageTk.PhotoImage(Image.open("assets/power.png").resize((40, 40)))
            RoundedButton(self.clock_frame, text="", icon=self.power_icon, command=quick_shutdown, 
                          width=50, height=50, bg_color=config.BG_COLOR, hover_color="#330000").pack(side="left", padx=(20, 0))
        except:
             # Fallback text
             RoundedButton(self.clock_frame, text="OFF", command=quick_shutdown, 
                          width=50, height=50, bg_color="#440000").pack(side="left", padx=(20, 0))
        
        # 2. Date Label (Smaller, Modern Grey)
        self.date_lbl = tk.Label(self, text="...", font=("Verdana", 14), 
                                 bg=config.BG_COLOR, fg="#888888")
        self.date_lbl.pack(pady=(0, 20)) # 20px gap before the focus timer starts

        # ================= FOCUS TIMER =================

        # Divider (Optional, but helps separate Real Time from Focus Time)
        tk.Frame(self, height=2, bg=config.DIVIDER_COLOR, width=200).pack(pady=10)

        # Title (Blue)
        tk.Label(self, text="Focus Timer", font=config.FONT_MED, 
                 bg=config.BG_COLOR, fg=config.POMODORO_BLUE).pack(pady=(20,5))
        
        # Status Text
        self.status_lbl = tk.Label(self, text="Ready", font=config.FONT_LARGE, 
                                   bg=config.BG_COLOR, fg="gray")
        self.status_lbl.pack(pady=5)

        # Countdown Numbers
        self.time_lbl = tk.Label(self, text=f"{self.minutes:02d}:{self.seconds:02d}", 
                                 font=("Verdana", 80, "bold"), 
                                 bg=config.BG_COLOR, fg=config.POMODORO_BLUE)
        self.time_lbl.pack(expand=True)
        
        # Button Container
        btn_frame = tk.Frame(self, bg=config.BG_COLOR)
        btn_frame.pack(pady=30)

        # Buttons
        RoundedButton(btn_frame, text="Start", command=self.start_timer, 
                      width=120, height=65, bg_color="#333").pack(side="left", padx=10)
        
        RoundedButton(btn_frame, text="Pause", command=self.pause_timer, 
                      width=120, height=65, bg_color="#333").pack(side="left", padx=10)
        
        RoundedButton(btn_frame, text="Reset", command=self.reset_timer, 
                      width=120, height=65, bg_color="#333").pack(side="left", padx=10)
        
        # Start the clock loop
        self.update_clock()

    def update_clock(self):
        """Updates the real-time clock every second"""
        now = datetime.now()
        
        # 24-Hour Format (HH:MM)
        current_time = now.strftime("%H:%M")
        
        # Date Format (e.g., "Thu 20 Nov")
        current_date = now.strftime("%a %d %b")
        
        # Update Labels
        if self.clock_lbl.cget("text") != current_time:
            self.clock_lbl.config(text=current_time)
        
        if self.date_lbl.cget("text") != current_date:
            self.date_lbl.config(text=current_date)

        # Schedule next update (every 1 second)
        self.after(1000, self.update_clock)

    def update_timer(self):
        if self.state == "RUNNING":
            if self.seconds == 0:
                if self.minutes == 0:
                    self.state = "STOPPED"
                    self.status_lbl.config(text="Done!", fg="red")
                    return
                self.minutes -= 1
                self.seconds = 59
            else:
                self.seconds -= 1
            
            self.time_lbl.config(text=f"{self.minutes:02d}:{self.seconds:02d}")
            self.after(1000, self.update_timer)

    def start_timer(self):
        if self.state != "RUNNING":
            self.state = "RUNNING"
            self.status_lbl.config(text="Focusing...", fg=config.FG_COLOR)
            self.update_timer()

    def pause_timer(self):
        self.state = "PAUSED"
        self.status_lbl.config(text="Paused", fg="orange")

    def reset_timer(self):
        self.state = "STOPPED"
        self.minutes = 25
        self.seconds = 0
        self.time_lbl.config(text=f"{self.minutes:02d}:{self.seconds:02d}")
        self.status_lbl.config(text="Ready", fg="gray")