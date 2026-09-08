import threading
import tkinter as tk
from datetime import date, datetime

import config
import todo_store
from components import RoundedButton
from todoist_sync import todoist_sync, TodoistSyncError
from pomodoro_engine import PomodoroEngine


def _now_str():
    return datetime.now().isoformat(timespec="seconds")


def _minutes_logged(task):
    return sum(s.get("duration_seconds", 0) for s in task.get("sessions", [])) // 60


class CircleCheckbox(tk.Canvas):
    """A true circular checkbox - deliberately a different shape from the
    rectangular task cards, so it reads unambiguously as "tap to check off"
    versus "tap to act on this task"."""

    def __init__(self, parent, done=False, command=None, size=40):
        super().__init__(parent, width=size, height=size, bg=parent["bg"], highlightthickness=0)
        self.size = size
        self.done = done
        self.command = command
        self._draw()
        if command:
            self.bind("<Button-1>", lambda e: command())

    def _draw(self):
        self.delete("all")
        s = self.size
        pad = 3
        if self.done:
            self.create_oval(pad, pad, s - pad, s - pad, fill=config.SPOTIFY_GREEN, outline=config.SPOTIFY_GREEN)
            self.create_line(s * 0.27, s * 0.52, s * 0.43, s * 0.68, s * 0.75, s * 0.30,
                              fill="white", width=max(2, s // 14), capstyle="round", joinstyle="round")
        else:
            self.create_oval(pad, pad, s - pad, s - pad, outline="#5A5A5A", width=3)


class MajorTaskRow(tk.Frame):
    def __init__(self, parent, task, on_toggle=None, on_select=None, is_active=False, read_only=False):
        super().__init__(parent, bg=config.SURFACE_COLOR)
        done = task.get("done", False)

        checkbox_cmd = (lambda: on_toggle(task["id"])) if (on_toggle and not read_only) else None
        checkbox = CircleCheckbox(self, done=done, command=checkbox_cmd, size=38)
        checkbox.pack(side="left", padx=(14, 10), pady=13)

        minutes = _minutes_logged(task)
        if done:
            subtitle = "Done"
        elif is_active:
            subtitle = "Focusing now"
        elif minutes:
            subtitle = f"{minutes}m logged"
        else:
            subtitle = None

        body_bg = config.TODO_ACCENT if is_active else config.SURFACE_COLOR
        text_fg = "#666666" if done else "white"
        body_cmd = (lambda: on_select(task["id"], task["text"])) if (on_select and not read_only) else None
        body = RoundedButton(
            self, text=task["text"], subtitle=subtitle, command=body_cmd,
            width=270, height=64, corner_radius=10,
            bg_color=body_bg, hover_color=body_bg, fg_color=text_fg,
        )
        body.pack(side="left", pady=10, padx=(0, 14))


class MinorTaskRow(tk.Frame):
    def __init__(self, parent, task, on_toggle=None, read_only=False):
        super().__init__(parent, bg=config.SURFACE_COLOR)
        done = task.get("done", False)
        cmd = (lambda: on_toggle(task["id"])) if (on_toggle and not read_only) else None

        checkbox = CircleCheckbox(self, done=done, command=cmd, size=26)
        checkbox.pack(side="left", padx=(12, 8), pady=9)

        text_fg = "#666666" if done else "white"
        font = ("Verdana", 12, "overstrike") if done else ("Verdana", 12)
        lbl = tk.Label(self, text=task["text"], font=font, bg=config.SURFACE_COLOR, fg=text_fg, anchor="w")
        lbl.pack(side="left", fill="x", expand=True, padx=(0, 12), pady=9)

        if cmd:
            self.bind("<Button-1>", lambda e: cmd())
            lbl.bind("<Button-1>", lambda e: cmd())


class TaskTimerPanel(tk.Frame):
    """Embeds a PomodoroEngine, tracks which major task it's tied to, and
    records session entries via on_session callback. Created once and kept
    alive for the lifetime of the page - never rebuilt by TodoPage._render()."""

    PHASE_CAPTIONS = {"focus": "Focus", "short_break": "Short break", "long_break": "Long break"}
    PHASE_COLORS = {"focus": None, "short_break": "#66BB6A", "long_break": "#00E676"}  # None = TODO_ACCENT

    def __init__(self, parent, on_session=None, on_active_changed=None):
        super().__init__(parent, bg=config.SURFACE_COLOR)
        self.on_session = on_session
        self.on_active_changed = on_active_changed
        self.active_task_id = None
        self.active_task_text = None
        self._session_start = None

        self.engine = PomodoroEngine(self, on_tick=self._on_tick, on_phase_change=self._on_phase_change,
                                      on_focus_complete=self._on_focus_complete)

        self.task_lbl = tk.Label(self, text="No active task", font=("Verdana", 14, "bold"),
                                  bg=config.SURFACE_COLOR, fg=config.FG_COLOR)
        self.task_lbl.pack(pady=(18, 2))

        self.phase_lbl = tk.Label(self, text="Tap a task to start focusing", font=("Verdana", 11),
                                   bg=config.SURFACE_COLOR, fg="#777777")
        self.phase_lbl.pack(pady=(0, 8))

        self.time_lbl = tk.Label(self, text=f"{self.engine.minutes:02d}:{self.engine.seconds:02d}",
                                  font=("Verdana", 52, "bold"), bg=config.SURFACE_COLOR, fg=config.TODO_ACCENT)
        self.time_lbl.pack(pady=6)

        btn_frame = tk.Frame(self, bg=config.SURFACE_COLOR)
        btn_frame.pack(pady=(6, 18))
        self.pause_btn = RoundedButton(btn_frame, text="Pause", command=self._toggle_pause, width=90, height=42,
                                        bg_color="#2A2A2A")
        self.pause_btn.pack(side="left", padx=6)
        RoundedButton(btn_frame, text="Reset", command=self._reset_clicked, width=90, height=42,
                      bg_color="#2A2A2A").pack(side="left", padx=6)

    def select_task(self, task_id, text):
        if self.active_task_id == task_id:
            return  # already active, ignore re-tap - use Pause/Reset for control
        if self.active_task_id is not None:
            self._finalize_session(completed=False)
        self.active_task_id = task_id
        self.active_task_text = text
        self.engine.reset()
        self.task_lbl.config(text=text, fg="white")
        self._begin_focus_timing()
        self.engine.start()
        self.phase_lbl.config(text="Focus", fg="#AAAAAA")
        self.pause_btn.set_text(text="Pause")
        if self.on_active_changed:
            self.on_active_changed()

    def clear_active(self):
        """Stops timing without counting a completed session (e.g. task marked done)."""
        if self.active_task_id is not None:
            self._finalize_session(completed=False)
        self.engine.reset()
        self.active_task_id = None
        self.active_task_text = None
        self.task_lbl.config(text="No active task", fg=config.FG_COLOR)
        self.time_lbl.config(text=f"{self.engine.minutes:02d}:{self.engine.seconds:02d}", fg=config.TODO_ACCENT)
        self.phase_lbl.config(text="Tap a task to start focusing", fg="#777777")
        self.pause_btn.set_text(text="Pause")
        if self.on_active_changed:
            self.on_active_changed()

    def _toggle_pause(self):
        if self.active_task_id is None:
            return
        if self.engine.state == "RUNNING":
            self.engine.pause()
            self.phase_lbl.config(text="Paused", fg="orange")
            self.pause_btn.set_text(text="Resume")
        else:
            self.engine.start()
            phase = "short_break" if self.engine.timer_mode == "BREAK" else "focus"
            self.phase_lbl.config(text=self.PHASE_CAPTIONS.get(phase, "Focus"), fg="#AAAAAA")
            self.pause_btn.set_text(text="Pause")

    def _reset_clicked(self):
        self._finalize_session(completed=False)
        self.engine.reset()
        self.time_lbl.config(text=f"{self.engine.minutes:02d}:{self.engine.seconds:02d}", fg=config.TODO_ACCENT)
        self.phase_lbl.config(text="Focus", fg="#AAAAAA")
        self.pause_btn.set_text(text="Pause")

    def _begin_focus_timing(self):
        self._session_start = datetime.now()

    def _on_tick(self, minutes, seconds, mode):
        self.time_lbl.config(text=f"{minutes:02d}:{seconds:02d}")

    def _on_phase_change(self, mode, phase_label, count):
        color = self.PHASE_COLORS.get(phase_label) or config.TODO_ACCENT
        self.phase_lbl.config(text=self.PHASE_CAPTIONS.get(phase_label, "Focus"), fg="#AAAAAA")
        self.time_lbl.config(fg=color)
        if phase_label == "focus":
            self._begin_focus_timing()

    def _on_focus_complete(self, count):
        self._finalize_session(completed=True)

    def _finalize_session(self, completed):
        if self.active_task_id is None or self._session_start is None:
            self._session_start = None
            return
        if self.engine.timer_mode != "FOCUS":
            self._session_start = None
            return
        start_snapshot = self._session_start
        duration = (datetime.now() - start_snapshot).total_seconds()
        self._session_start = None
        if duration < 5:
            return
        session = {"start": start_snapshot.isoformat(timespec="seconds"),
                   "duration_seconds": int(duration), "completed": completed}
        if self.on_session:
            self.on_session(self.active_task_id, session)


class TodoPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.BG_COLOR)

        self.state = todo_store.load_state()
        self._sync_in_progress = False
        self._sync_debounce_id = None

        self._build_header()

        self.body_frame = tk.Frame(self, bg=config.BG_COLOR)
        self.body_frame.pack(fill="both", expand=True)

        self.today_frame = tk.Frame(self.body_frame, bg=config.BG_COLOR)
        self.today_frame.pack(fill="both", expand=True)
        self._build_today_scaffold()

        self.history_frame = None  # built lazily

        self._render()

        self.after(500, lambda: self.trigger_sync())
        self.after(60000, self._heartbeat)
        self.after(config.TODOIST_SYNC_INTERVAL_MS, self._sync_heartbeat)

    # ---------------- header ----------------

    def _build_header(self):
        header = tk.Frame(self, bg=config.BG_COLOR)
        header.pack(fill="x", pady=(15, 10), padx=20)

        left = tk.Frame(header, bg=config.BG_COLOR)
        left.pack(side="left")
        tk.Label(left, text="Today's Focus", font=config.FONT_LARGE, bg=config.BG_COLOR,
                 fg=config.TODO_ACCENT).pack(anchor="w")
        self.date_lbl = tk.Label(left, text=date.today().strftime("%a %d %b"), font=config.FONT_SMALL,
                                  bg=config.BG_COLOR, fg="#888888")
        self.date_lbl.pack(anchor="w")

        right = tk.Frame(header, bg=config.BG_COLOR)
        right.pack(side="right")
        RoundedButton(right, text="History", command=self._show_history, width=90, height=50,
                      bg_color="#2A2A2A").pack(side="right", padx=(8, 0))
        # The Refresh button doubles as the sync-status indicator (subtitle),
        # so status doesn't need its own separate label cluttering the header.
        self.refresh_btn = RoundedButton(right, text="Refresh", subtitle="Not synced",
                                          command=lambda: self.trigger_sync(manual=True),
                                          width=150, height=50, bg_color="#2A2A2A")
        self.refresh_btn.pack(side="right")

    def _update_sync_status_label(self):
        if self._sync_in_progress:
            subtitle, bg = "Syncing…", "#2A2A2A"
        elif self.state.get("last_sync_error"):
            subtitle, bg = "Sync failed", "#7A3B24"
        elif self.state.get("last_synced_at"):
            subtitle, bg = f"Synced {self.state['last_synced_at'][11:16]}", "#2A2A2A"
        else:
            subtitle, bg = "Not synced", "#2A2A2A"
        self.refresh_btn.set_text(subtitle=subtitle, bg_color=bg)

    # ---------------- persistent today scaffold ----------------

    def _build_today_scaffold(self):
        """Builds the parts of the today view that stay alive across renders:
        the two columns, the task-list containers, the overflow labels and the
        (single, persistent) TaskTimerPanel. _render() only ever repopulates
        the task-list containers - it never touches the timer panel, so an
        in-progress pomodoro survives every toggle/sync re-render untouched."""
        left_col = tk.Frame(self.today_frame, bg=config.BG_COLOR)
        left_col.pack(side="left", fill="both", expand=True, padx=15)

        tk.Frame(self.today_frame, width=1, bg=config.DIVIDER_COLOR).pack(side="left", fill="y")

        right_col = tk.Frame(self.today_frame, bg=config.BG_COLOR)
        right_col.pack(side="left", fill="both", expand=True, padx=15)

        tk.Label(left_col, text="MAJOR TASKS", font=("Verdana", 10, "bold"), bg=config.BG_COLOR,
                 fg="#5A5A5A").pack(anchor="w", pady=(6, 8))
        self.major_list = tk.Frame(left_col, bg=config.BG_COLOR)
        self.major_list.pack(fill="x")
        self.major_overflow_lbl = tk.Label(left_col, text="", font=config.FONT_SMALL,
                                            bg=config.BG_COLOR, fg="#666666")
        self.major_overflow_lbl.pack(anchor="w", pady=(4, 0))

        self.timer_panel = TaskTimerPanel(left_col, on_session=self.on_session_recorded,
                                           on_active_changed=self._render)
        self.timer_panel.pack(fill="x", pady=(14, 0))

        tk.Label(right_col, text="QUICK TASKS", font=("Verdana", 10, "bold"), bg=config.BG_COLOR,
                 fg="#5A5A5A").pack(anchor="w", pady=(6, 8))
        self.minor_list = tk.Frame(right_col, bg=config.BG_COLOR)
        self.minor_list.pack(fill="x")
        self.minor_overflow_lbl = tk.Label(right_col, text="", font=config.FONT_SMALL,
                                            bg=config.BG_COLOR, fg="#666666")
        self.minor_overflow_lbl.pack(anchor="w", pady=(4, 0))

    # ---------------- lifecycle hooks (called by SwipeableContainer) ----------------

    def on_page_shown(self):
        self._check_rollover()
        self.trigger_sync()

    def on_page_hidden(self):
        pass

    def _heartbeat(self):
        self._check_rollover()
        self.after(60000, self._heartbeat)

    def _sync_heartbeat(self):
        self.trigger_sync()
        self.after(config.TODOIST_SYNC_INTERVAL_MS, self._sync_heartbeat)

    def _check_rollover(self):
        if self.state.get("date") != date.today().isoformat():
            self.timer_panel.clear_active()
            todo_store.archive_and_reset(self.state)
            self.state = todo_store.load_state()
            self._render()
            self.trigger_sync()

    # ---------------- sync ----------------

    def trigger_sync(self, manual=False):
        if self._sync_in_progress:
            return
        if not config.TODOIST_API_TOKEN:
            self.state["last_sync_error"] = "Todoist not configured"
            self._update_sync_status_label()
            return
        self._sync_in_progress = True
        self._update_sync_status_label()
        threading.Thread(target=self._sync_worker, daemon=True).start()

    def _sync_worker(self):
        try:
            todoist_sync.sync(self.state)
            todo_store.save_state(self.state)
            self.after(0, self._on_sync_done)
        except TodoistSyncError:
            todo_store.save_state(self.state)
            self.after(0, self._on_sync_done)

    def _on_sync_done(self):
        self._sync_in_progress = False
        self._render()

    def _debounced_sync(self):
        if self._sync_debounce_id:
            self.after_cancel(self._sync_debounce_id)
        self._sync_debounce_id = self.after(1500, lambda: self.trigger_sync())

    # ---------------- task interactions ----------------

    def _find_task(self, section, task_id):
        for t in self.state.get(section, []):
            if t["id"] == task_id:
                return t
        return None

    def on_toggle_done(self, section, task_id):
        task = self._find_task(section, task_id)
        if task is None:
            return
        task["done"] = not task["done"]
        task["pending_push"] = True
        task["updated_at"] = _now_str()

        if section == "major_tasks" and task["done"] and self.timer_panel.active_task_id == task_id:
            self.timer_panel.clear_active()

        todo_store.save_state(self.state)
        self._render()
        self._debounced_sync()

    def on_major_task_tapped(self, task_id, text):
        task = self._find_task("major_tasks", task_id)
        if task is None or task.get("done"):
            return
        self.timer_panel.select_task(task_id, text)

    def on_session_recorded(self, task_id, session):
        task = self._find_task("major_tasks", task_id)
        if task is None:
            return
        task.setdefault("sessions", []).append(session)
        task["updated_at"] = _now_str()
        todo_store.save_state(self.state)
        self._render()

    # ---------------- rendering: today ----------------

    def _render(self):
        self._update_sync_status_label()

        for child in self.major_list.winfo_children():
            child.destroy()
        active_id = self.timer_panel.active_task_id
        for task in self.state.get("major_tasks", []):
            row = MajorTaskRow(self.major_list, task,
                                on_toggle=lambda tid: self.on_toggle_done("major_tasks", tid),
                                on_select=self.on_major_task_tapped,
                                is_active=(task["id"] == active_id))
            row.pack(fill="x", pady=4)
        overflow = self.state.get("major_overflow_count", 0)
        self.major_overflow_lbl.config(text=f"+{overflow} more in Todoist" if overflow else "")

        for child in self.minor_list.winfo_children():
            child.destroy()
        for task in self.state.get("minor_tasks", []):
            row = MinorTaskRow(self.minor_list, task, on_toggle=lambda tid: self.on_toggle_done("minor_tasks", tid))
            row.pack(fill="x", pady=3)
        overflow = self.state.get("minor_overflow_count", 0)
        self.minor_overflow_lbl.config(text=f"+{overflow} more in Todoist" if overflow else "")

    # ---------------- rendering: history ----------------

    def _show_history(self):
        self.today_frame.pack_forget()
        if self.history_frame is not None:
            self.history_frame.destroy()
        self.history_frame = tk.Frame(self.body_frame, bg=config.BG_COLOR)
        self.history_frame.pack(fill="both", expand=True)
        self._render_history_dates()

    def _render_history_dates(self):
        for child in self.history_frame.winfo_children():
            child.destroy()

        top = tk.Frame(self.history_frame, bg=config.BG_COLOR)
        top.pack(fill="x", pady=10, padx=20)
        tk.Label(top, text="History", font=config.FONT_LARGE, bg=config.BG_COLOR,
                 fg=config.TODO_ACCENT).pack(side="left")
        RoundedButton(top, text="Back to Today", command=self._back_to_today, width=160, height=50,
                      bg_color="#2A2A2A").pack(side="right")

        dates = todo_store.list_history_dates()
        if not dates:
            tk.Label(self.history_frame, text="No history yet", font=config.FONT_MED,
                     bg=config.BG_COLOR, fg="#888888").pack(pady=30)
            return

        list_frame = tk.Frame(self.history_frame, bg=config.BG_COLOR)
        list_frame.pack(fill="both", expand=True, padx=20)
        for d in dates:
            RoundedButton(list_frame, text=d, command=lambda d=d: self._show_history_detail(d),
                          width=300, height=55, bg_color="#2A2A2A").pack(anchor="w", pady=4)

    def _show_history_detail(self, date_str):
        snapshot = todo_store.load_history(date_str)
        for child in self.history_frame.winfo_children():
            child.destroy()

        top = tk.Frame(self.history_frame, bg=config.BG_COLOR)
        top.pack(fill="x", pady=10, padx=20)
        tk.Label(top, text=date_str, font=config.FONT_LARGE, bg=config.BG_COLOR,
                 fg=config.TODO_ACCENT).pack(side="left")
        RoundedButton(top, text="Back to Dates", command=self._render_history_dates, width=160, height=50,
                      bg_color="#2A2A2A").pack(side="right", padx=(10, 0))
        RoundedButton(top, text="Back to Today", command=self._back_to_today, width=160, height=50,
                      bg_color="#2A2A2A").pack(side="right")

        if snapshot is None:
            tk.Label(self.history_frame, text="Snapshot not found", font=config.FONT_MED,
                     bg=config.BG_COLOR, fg="#888888").pack(pady=30)
            return

        body = tk.Frame(self.history_frame, bg=config.BG_COLOR)
        body.pack(fill="both", expand=True)

        left_col = tk.Frame(body, bg=config.BG_COLOR)
        left_col.pack(side="left", fill="both", expand=True, padx=15)
        tk.Frame(body, width=1, bg=config.DIVIDER_COLOR).pack(side="left", fill="y")
        right_col = tk.Frame(body, bg=config.BG_COLOR)
        right_col.pack(side="left", fill="both", expand=True, padx=15)

        tk.Label(left_col, text="MAJOR TASKS", font=("Verdana", 10, "bold"), bg=config.BG_COLOR,
                 fg="#5A5A5A").pack(anchor="w", pady=(6, 8))
        for task in snapshot.get("major_tasks", []):
            MajorTaskRow(left_col, task, read_only=True).pack(fill="x", pady=4)

        tk.Label(right_col, text="QUICK TASKS", font=("Verdana", 10, "bold"), bg=config.BG_COLOR,
                 fg="#5A5A5A").pack(anchor="w", pady=(6, 8))
        for task in snapshot.get("minor_tasks", []):
            MinorTaskRow(right_col, task, read_only=True).pack(fill="x", pady=3)

    def _back_to_today(self):
        if self.history_frame is not None:
            self.history_frame.pack_forget()
        self.today_frame.pack(fill="both", expand=True)
