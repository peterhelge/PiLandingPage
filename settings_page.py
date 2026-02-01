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
        
        # Edit Config Button (Gray/Teal)
        RoundedButton(btn_frame, text="Edit Configuration", subtitle="Update .env settings", command=self.open_env_editor, 
                      width=350, height=90, bg_color="#00695C", hover_color="#004D40",
                      icon=None).pack(pady=15)

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

    def open_env_editor(self):
        # Create Modal Window
        editor = tk.Toplevel(self)
        editor.title("Edit .env Configuration")
        editor.geometry("800x600")
        editor.configure(bg=config.BG_COLOR)
        # Remove window decorations for kiosk feel, or keep for close button?
        # Let's keep a standard window but full screen ish or centered.
        
        # Make it modal
        editor.transient(self)
        editor.grab_set()

        # Header
        tk.Label(editor, text="Edit .env File", font=config.FONT_LARGE, 
                 bg=config.BG_COLOR, fg="white").pack(pady=20)

        # Text Area
        text_area = tk.Text(editor, font=("Consolas", 14), bg="#222", fg="#EEE", 
                            insertbackground="white", relief="flat", padx=10, pady=10)
        text_area.pack(fill="both", expand=True, padx=20, pady=10)

        # Load content
        try:
            with open(".env", "r") as f:
                content = f.read()
                text_area.insert("1.0", content)
        except Exception as e:
            text_area.insert("1.0", f"# Error loading .env: {e}")

        # Action Buttons
        btn_frame = tk.Frame(editor, bg=config.BG_COLOR)
        btn_frame.pack(fill="x", pady=20, padx=20)

        def save_env():
            new_content = text_area.get("1.0", "end-1c") # Get all text
            try:
                with open(".env", "w") as f:
                    f.write(new_content)
                # Show success feedback (simple console print or label, avoiding popups for now if not needed)
                print("Saved .env successfully.")
                editor.destroy()
                # Determine how to notify user to restart.
                # Maybe just close the app? Or show a label.
                # Let's restart the app roughly if possible or just warn.
                # For now, just close editor. User can use "Reboot System" button.
            except Exception as e:
                print(f"Error saving .env: {e}")

        # Cancel Button
        RoundedButton(btn_frame, text="Cancel", subtitle="", command=editor.destroy, 
                      width=200, height=60, bg_color="#555", hover_color="#444").pack(side="left", padx=10)

        # Save Button
        RoundedButton(btn_frame, text="Save Actions", subtitle="", command=save_env, 
                      width=200, height=60, bg_color="#2E7D32", hover_color="#1B5E20").pack(side="right", padx=10)

    def exit_app(self):
        sys.exit(0)
