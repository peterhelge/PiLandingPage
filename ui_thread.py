"""Main-thread scheduling for a Tk kiosk.

Widget.after() is only safe on the thread that created the Tcl interpreter.
Background fetches queue their UI updates here, and each poll owns a single
repeating timer so a button press cannot start a second loop.
"""

import queue
import tkinter as tk

_queue = queue.Queue()
_installed = False


def call_on_ui(callback):
    """Run callback on the Tk main thread. Safe to call from a worker."""
    _queue.put(callback)
    _ensure_pump()


def _ensure_pump():
    global _installed
    root = tk._default_root
    if root is None or _installed:
        return
    _installed = True
    root.after(0, _drain)


def _drain():
    global _installed
    root = tk._default_root
    if root is None:
        _installed = False
        return
    try:
        while True:
            callback = _queue.get_nowait()
            try:
                callback()
            except Exception:
                from app_logging import logger
                logger.exception("UI callback failed")
    except queue.Empty:
        pass
    try:
        root.after(30, _drain)
    except tk.TclError:
        _installed = False


def reset_ui_queue_for_tests():
    global _installed
    _installed = False
    while True:
        try:
            _queue.get_nowait()
        except queue.Empty:
            break


class IntervalPoll:
    """One repeating poll. Extra refreshes do not start another loop."""

    def __init__(self, widget, interval_ms, poll_fn):
        self.widget = widget
        self.interval_ms = interval_ms
        self.poll_fn = poll_fn
        self.started = False

    def start(self):
        if self.started:
            return
        self.started = True
        self._fire_loop()

    def _fire_loop(self):
        self.poll_fn()
        self.widget.after(self.interval_ms, self._fire_loop)

    def refresh_soon(self, delay_ms):
        self.widget.after(delay_ms, self.poll_fn)
