import tkinter as tk
import os
import platform
import config
from components import RoundedButton
import sys

class SettingsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.BG_COLOR)
        
        # Header
        tk.Label(self, text="System Settings", font=config.FONT_LARGE, 
                 bg=config.BG_COLOR, fg="white").pack(pady=40)

        # Button Container
        btn_frame = tk.Frame(self, bg=config.BG_COLOR)
        btn_frame.pack(expand=True)

        # Shutdown Button
        RoundedButton(btn_frame, text="Shutdown System", command=self.shutdown, 
                      width=250, height=80, bg_color="#D32F2F", hover_color="#B71C1C").pack(pady=20)

        # Reboot Button
        RoundedButton(btn_frame, text="Reboot System", command=self.reboot, 
                      width=250, height=80, bg_color="#FBC02D", hover_color="#F9A825").pack(pady=20)
        
        # Exit App Button (Maintenance)
        RoundedButton(btn_frame, text="Exit App", command=self.exit_app, 
                      width=250, height=60, bg_color="#455A64", hover_color="#37474F").pack(pady=40)

    def shutdown(self):
        print("Shutting down...")
        if platform.system() == "Linux":
            os.system("sudo shutdown -h now")
        else:
            print("[Mock] sudo shutdown -h now")
            # In a real app we might want to confirm or just close, 
            # here we just print to console for safety on Windows

    def reboot(self):
        print("Rebooting...")
        if platform.system() == "Linux":
            os.system("sudo reboot")
        else:
            print("[Mock] sudo reboot")

    def exit_app(self):
        sys.exit(0)
