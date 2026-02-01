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

        # Load Icons
        from PIL import Image, ImageTk
        self.icon_power = None
        self.icon_reboot = None
        self.icon_exit = None

        try:
            sz = (40, 40)
            self.icon_power = ImageTk.PhotoImage(Image.open("assets/power.png").resize(sz))
            self.icon_reboot = ImageTk.PhotoImage(Image.open("assets/reboot.png").resize(sz))
            self.icon_exit = ImageTk.PhotoImage(Image.open("assets/exit.png").resize(sz))
        except Exception as e:
            print(f"Error loading icons: {e}")

        # Shutdown Button (Red)
        RoundedButton(btn_frame, text="Power Off", subtitle="Turn off the system", command=self.shutdown, 
                      width=350, height=90, bg_color="#C62828", hover_color="#B71C1C", # Slightly Darker Red
                      icon=self.icon_power).pack(pady=15)

        # Reboot Button (Darker Orange for better contrast)
        RoundedButton(btn_frame, text="Reboot System", subtitle="Restart the Raspberry Pi", command=self.reboot, 
                      width=350, height=90, bg_color="#E65100", hover_color="#EF6C00",
                      icon=self.icon_reboot).pack(pady=15)
        
        # Exit App Button (Blue/Gray) - Maintenance
        RoundedButton(btn_frame, text="Exit Kiosk", subtitle="Close app to desktop", command=self.exit_app, 
                      width=350, height=90, bg_color="#455A64", hover_color="#37474F",
                      icon=self.icon_exit).pack(pady=15)

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
