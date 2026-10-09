import unittest
from datetime import datetime, timedelta

from todo_page import TaskTimerPanel, overlay_local_edits
from todoist_sync import select_visible_tasks


def _task(task_id, done=False, pending=False, sessions=None):
    task = {
        "id": task_id,
        "text": task_id,
        "done": done,
        "pending_push": pending,
        "todoist_task_id": task_id,
    }
    if sessions is not None:
        task["sessions"] = sessions
    return task


class VisibleTaskTests(unittest.TestCase):
    def test_finished_tasks_do_not_block_new_ones(self):
        done = [_task(f"done-{i}", done=True) for i in range(4)]
        new = [_task("new-1"), _task("new-2")]
        visible, overflow = select_visible_tasks(done, new, max_items=4)
        ids = [task["id"] for task in visible]
        self.assertEqual(ids[:2], ["new-1", "new-2"])
        self.assertEqual(overflow, 0)
        self.assertEqual(len(visible), 4)

    def test_pending_push_is_never_dropped(self):
        pinned = [_task(f"pin-{i}", pending=True) for i in range(5)]
        visible, overflow = select_visible_tasks(pinned, [_task("extra")], max_items=4)
        self.assertEqual([task["id"] for task in visible], [f"pin-{i}" for i in range(5)])
        self.assertEqual(overflow, 1)


class OverlayTests(unittest.TestCase):
    def test_toggle_during_sync_survives_the_snapshot(self):
        snapshot = {
            "major_tasks": [_task("a", done=False)],
            "minor_tasks": [],
        }
        local = {
            "major_tasks": [_task("a", done=True, pending=True, sessions=[{"completed": False}])],
            "minor_tasks": [_task("local-only", pending=True)],
        }
        merged = overlay_local_edits(snapshot, local)
        major = merged["major_tasks"][0]
        self.assertTrue(major["done"])
        self.assertTrue(major["pending_push"])
        self.assertEqual(len(major["sessions"]), 1)
        self.assertEqual(merged["minor_tasks"][0]["id"], "local-only")


class TaskTimerTests(unittest.TestCase):
    def test_reset_arms_a_new_session_and_long_break_label(self):
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        sessions = []
        try:
            panel = TaskTimerPanel(root, on_session=lambda task_id, session: sessions.append(session))
            panel.select_task("t1", "Write")
            panel._session_start = datetime.now() - timedelta(seconds=20)
            panel._reset_clicked()
            self.assertEqual(panel.pause_btn.text_str, "Start")
            self.assertIsNone(panel._session_start)
            self.assertEqual(len(sessions), 1)

            panel._toggle_pause()
            self.assertEqual(panel.pause_btn.text_str, "Pause")
            self.assertIsNotNone(panel._session_start)

            panel.engine.pause()
            panel._phase_label = "long_break"
            panel.engine.timer_mode = "BREAK"
            panel._toggle_pause()
            self.assertEqual(panel.phase_lbl.cget("text"), "Long break")
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
