import os
import unittest

import config
from home_assistant import sensor_number
from spotify import adjusted_volume, collect_pages, playback_summary
from ui_thread import IntervalPoll, call_on_ui, reset_ui_queue_for_tests


class IntervalPollTests(unittest.TestCase):
    def test_start_is_a_single_loop_and_refresh_does_not_add_one(self):
        class Widget:
            def __init__(self):
                self.scheduled = []

            def after(self, ms, fn):
                self.scheduled.append((ms, fn))
                return len(self.scheduled)

        widget = Widget()
        calls = []
        poll = IntervalPoll(widget, 5000, lambda: calls.append("poll"))
        poll.start()
        poll.start()
        poll.refresh_soon(200)
        poll.refresh_soon(2000)

        self.assertEqual(calls, ["poll"])
        self.assertEqual([ms for ms, _fn in widget.scheduled], [5000, 200, 2000])

        loop = widget.scheduled[0][1]
        loop()
        self.assertEqual(calls, ["poll", "poll"])
        self.assertEqual(widget.scheduled[-1][0], 5000)


class PlaybackTests(unittest.TestCase):
    def test_track_episode_without_item_and_volume(self):
        title, device, playing = playback_summary({
            "is_playing": True,
            "item": None,
            "device": {"name": "Kitchen", "volume_percent": None},
        })
        self.assertEqual(title, "Playing")
        self.assertEqual(device, "on Kitchen")
        self.assertTrue(playing)
        self.assertIsNone(adjusted_volume(None, 10))
        self.assertEqual(adjusted_volume(95, 10), 100)

    def test_paused_and_track_label(self):
        self.assertEqual(playback_summary(None), ("Paused / Idle", "", False))
        title, device, playing = playback_summary({
            "is_playing": True,
            "item": {"name": "Song", "artists": [{"name": "Band"}]},
            "device": {"name": "Pi"},
        })
        self.assertEqual(title, "Song\nBand")
        self.assertEqual(device, "on Pi")
        self.assertTrue(playing)

    def test_playlist_pages_follow_next(self):
        pages = {
            "p1": {"items": [{"name": "A"}], "next": "p2"},
            "p2": {"items": [{"name": "B"}], "next": None},
        }

        def follow(page):
            return pages[page["next"]] if page.get("next") else None

        items = collect_pages(pages["p1"], follow)
        self.assertEqual([item["name"] for item in items], ["A", "B"])


class SensorAndConfigTests(unittest.TestCase):
    def test_unavailable_sensor_is_not_a_number(self):
        self.assertIsNone(sensor_number({"state": "unavailable"}))
        self.assertIsNone(sensor_number({"state": "unknown"}))
        self.assertIsNone(sensor_number(None))
        self.assertEqual(sensor_number({"state": "21.5"}), 21.5)

    def test_bad_env_int_falls_back(self):
        previous = os.environ.get("TODO_MAX_MAJOR")
        os.environ["TODO_MAX_MAJOR"] = "lots"
        try:
            self.assertEqual(config.env_int("TODO_MAX_MAJOR", 4), 4)
            os.environ["TODO_MAX_MAJOR"] = "0"
            self.assertEqual(config.env_int("TODO_MAX_MAJOR", 4), 4)
            os.environ["TODO_MAX_MAJOR"] = "6"
            self.assertEqual(config.env_int("TODO_MAX_MAJOR", 4), 6)
        finally:
            if previous is None:
                os.environ.pop("TODO_MAX_MAJOR", None)
            else:
                os.environ["TODO_MAX_MAJOR"] = previous


class UiQueueTests(unittest.TestCase):
    def test_callback_runs_from_the_queue(self):
        import tkinter as tk

        reset_ui_queue_for_tests()
        root = tk.Tk()
        root.withdraw()
        seen = []
        try:
            call_on_ui(lambda: seen.append("ran"))
            root.update()
            self.assertEqual(seen, ["ran"])
        finally:
            root.destroy()
            reset_ui_queue_for_tests()


if __name__ == "__main__":
    unittest.main()
