FOCUS_MINUTES = 25
SHORT_BREAK_MINUTES = 5
LONG_BREAK_MINUTES = 15
LONG_BREAK_EVERY = 4


class PomodoroEngine:
    """Pure pomodoro cycle state machine (no widget creation).

    scheduler: anything with .after(ms, fn) / .after_cancel(id) - typically the
    owning tk.Frame. Mirrors the recursive .after() driven loop that used to
    live directly inside PomodoroWidget.update_timer().
    """

    def __init__(self, scheduler, on_tick=None, on_phase_change=None, on_focus_complete=None):
        self.scheduler = scheduler
        self.on_tick = on_tick
        self.on_phase_change = on_phase_change
        self.on_focus_complete = on_focus_complete

        self.state = "STOPPED"
        self.timer_mode = "FOCUS"
        self.pomodoro_count = 0
        self.minutes = FOCUS_MINUTES
        self.seconds = 0
        self._after_id = None

    def start(self):
        if self.state != "RUNNING":
            self.state = "RUNNING"
            self._tick()

    def pause(self):
        self.state = "PAUSED"
        if self._after_id is not None:
            self.scheduler.after_cancel(self._after_id)
            self._after_id = None

    def reset(self):
        if self._after_id is not None:
            self.scheduler.after_cancel(self._after_id)
            self._after_id = None
        self.state = "STOPPED"
        self.timer_mode = "FOCUS"
        self.pomodoro_count = 0
        self.minutes = FOCUS_MINUTES
        self.seconds = 0

    def _tick(self):
        if self.state != "RUNNING":
            return

        if self.seconds == 0:
            if self.minutes == 0:
                self._advance_phase()
                return
            self.minutes -= 1
            self.seconds = 59
        else:
            self.seconds -= 1

        if self.on_tick:
            self.on_tick(self.minutes, self.seconds, self.timer_mode)

        self._after_id = self.scheduler.after(1000, self._tick)

    def _advance_phase(self):
        # Fire on_focus_complete BEFORE mutating mode, so a consumer can still
        # attribute this boundary to "the focus block that just ended".
        if self.timer_mode == "FOCUS":
            self.pomodoro_count += 1
            if self.on_focus_complete:
                self.on_focus_complete(self.pomodoro_count)

            if self.pomodoro_count % LONG_BREAK_EVERY == 0:
                self.timer_mode = "BREAK"
                self.minutes = LONG_BREAK_MINUTES
                self.seconds = 0
                phase_label = "long_break"
            else:
                self.timer_mode = "BREAK"
                self.minutes = SHORT_BREAK_MINUTES
                self.seconds = 0
                phase_label = "short_break"
        else:
            self.timer_mode = "FOCUS"
            self.minutes = FOCUS_MINUTES
            self.seconds = 0
            phase_label = "focus"

        if self.on_phase_change:
            self.on_phase_change(self.timer_mode, phase_label, self.pomodoro_count)

        # Continue running immediately (auto-start next phase), no missed second.
        self._tick()
