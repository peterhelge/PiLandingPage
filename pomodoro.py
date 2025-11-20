import tkinter as tk
import config
from components import RoundedButton

class PomodoroWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.BG_COLOR, bd=0)
        self.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        self.state = "STOPPED"
        self.minutes = 25
        self.seconds = 0
        
        tk.Label(self, text="Focus Timer", font=config.FONT_MED, 
                 bg=config.BG_COLOR, fg=config.POMODORO_BLUE).pack(pady=(10,5))
        
        self.status_lbl = tk.Label(self, text="Ready", font=config.FONT_LARGE, 
                                   bg=config.BG_COLOR, fg="gray")
        self.status_lbl.pack(pady=10)

        self.time_lbl = tk.Label(self, text=f"{self.minutes:02d}:{self.seconds:02d}", 
                                 font=("Verdana", 90, "bold"), # Changed to Verdana
                                 bg=config.BG_COLOR, fg=config.POMODORO_BLUE)
        self.time_lbl.pack(expand=True)
        
        # Button Container
        btn_frame = tk.Frame(self, bg=config.BG_COLOR)
        btn_frame.pack(pady=40)

        # Modern Rounded Buttons
        RoundedButton(btn_frame, text="Start", command=self.start_timer, 
                      width=80, height=45, bg_color="#333").pack(side="left", padx=10)
        
        RoundedButton(btn_frame, text="Pause", command=self.pause_timer, 
                      width=80, height=45, bg_color="#333").pack(side="left", padx=10)
        
        RoundedButton(btn_frame, text="Reset", command=self.reset_timer, 
                      width=80, height=45, bg_color="#333").pack(side="left", padx=10)

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