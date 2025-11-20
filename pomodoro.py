import tkinter as tk
import config

class PomodoroWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.BG_COLOR, bd=0)
        self.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.state = "STOPPED"
        self.minutes = 25
        self.seconds = 0
        
        tk.Label(self, text="Focus Timer", font=config.FONT_MED, 
                 bg=config.BG_COLOR, fg="gray").pack(pady=10)
        
        self.time_lbl = tk.Label(self, text=f"{self.minutes:02d}:{self.seconds:02d}", 
                                 font=("Helvetica", 45, "bold"), bg=config.BG_COLOR, fg=config.FG_COLOR)
        self.time_lbl.pack(pady=20)
        
        self.status_lbl = tk.Label(self, text="Ready", font=config.FONT_MED, 
                                   bg=config.BG_COLOR, fg=config.ACCENT_COLOR)
        self.status_lbl.pack(pady=5)

        btn_frame = tk.Frame(self, bg=config.BG_COLOR)
        btn_frame.pack(pady=20)

        # Button Styling
        style = {"bg": "#333", "fg": "white", "width": 6, "bd": 0, "font": config.FONT_SMALL}
        
        tk.Button(btn_frame, text="Start", command=self.start_timer, **style).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Pause", command=self.pause_timer, **style).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Reset", command=self.reset_timer, **style).grid(row=0, column=2, padx=5)

    def update_timer(self):
        if self.state == "RUNNING":
            if self.seconds == 0:
                if self.minutes == 0:
                    self.state = "STOPPED"
                    self.status_lbl.config(text="Time's Up!", fg="red")
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
        self.status_lbl.config(text="Ready", fg=config.ACCENT_COLOR)