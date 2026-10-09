import tkinter as tk
import config
from components import RoundedButton
from app_logging import logger
from security import ConfirmGate, run_power_action
import sys

_CONFIRM_MS = 5000


class SettingsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.BG_COLOR)
        self._gate = ConfirmGate()
        self._armed_button = None
        self._armed_snapshot = None
        self._arm_after = None

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
            logger.error(f"Error loading icons: {e}")

        # Shutdown Button (Red)
        self.power_btn = RoundedButton(
            btn_frame, text="Power Off", subtitle="Turn off the system", command=self.shutdown,
            width=350, height=90, bg_color="#C62828", hover_color="#B71C1C",
            icon=self.icon_power,
        )
        self.power_btn.pack(pady=15)

        # Reboot Button (Darker Orange for better contrast)
        self.reboot_btn = RoundedButton(
            btn_frame, text="Reboot System", subtitle="Restart the Raspberry Pi", command=self.reboot,
            width=350, height=90, bg_color="#E65100", hover_color="#EF6C00",
            icon=self.icon_reboot,
        )
        self.reboot_btn.pack(pady=15)

        # Exit App Button (Blue/Gray) - Maintenance
        self.exit_btn = RoundedButton(
            btn_frame, text="Exit Kiosk", subtitle="Close app to desktop", command=self.exit_app,
            width=350, height=90, bg_color="#455A64", hover_color="#37474F",
            icon=self.icon_exit,
        )
        self.exit_btn.pack(pady=15)

    def shutdown(self):
        self._require_confirm("shutdown", self.power_btn, self._do_shutdown)

    def reboot(self):
        self._require_confirm("reboot", self.reboot_btn, self._do_reboot)

    def exit_app(self):
        self._require_confirm("exit", self.exit_btn, self._do_exit)

    def _require_confirm(self, key, button, action):
        if self._gate.arm(key):
            self._restore_armed_button()
            action()
            return
        self._show_armed(button)

    def _show_armed(self, button):
        self._restore_armed_button()
        self._armed_button = button
        self._armed_snapshot = (button.text_str, button.subtitle, button.bg_color)
        button.set_text(text="Confirm?", subtitle="Tap again", bg_color="#6D4C41")
        self._arm_after = self.after(_CONFIRM_MS, self._expire_confirm)

    def _expire_confirm(self):
        self._gate.clear()
        self._restore_armed_button()

    def _restore_armed_button(self):
        if self._arm_after is not None:
            self.after_cancel(self._arm_after)
            self._arm_after = None
        if self._armed_button is not None and self._armed_snapshot is not None:
            text, subtitle, color = self._armed_snapshot
            self._armed_button.set_text(text=text, subtitle=subtitle, bg_color=color)
        self._armed_button = None
        self._armed_snapshot = None

    def _do_shutdown(self):
        self._finish_power("shutdown", self.power_btn)

    def _do_reboot(self):
        self._finish_power("reboot", self.reboot_btn)

    def _finish_power(self, action, button):
        ok, message = run_power_action(action)
        if ok:
            logger.info("Power action started: %s", action)
            return
        button.set_text(subtitle=message or "Failed")

    def _do_exit(self):
        logger.info("Exiting kiosk")
        sys.exit(0)
