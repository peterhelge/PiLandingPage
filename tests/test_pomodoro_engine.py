import unittest

from pomodoro_engine import FOCUS_MINUTES, LONG_BREAK_MINUTES, PomodoroEngine, SHORT_BREAK_MINUTES


class FakeScheduler:
    def __init__(self):
        self.pending = None
        self._next_id = 0

    def after(self, ms, fn):
        self._next_id += 1
        self.pending = (self._next_id, fn)
        return self._next_id

    def after_cancel(self, after_id):
        if self.pending and self.pending[0] == after_id:
            self.pending = None

    def fire(self):
        if self.pending is None:
            raise AssertionError("nothing scheduled")
        _after_id, fn = self.pending
        self.pending = None
        fn()


class PomodoroEngineTests(unittest.TestCase):
    def test_start_and_resume_keep_the_displayed_second(self):
        ticks = []
        engine = PomodoroEngine(FakeScheduler(), on_tick=lambda m, s, mode: ticks.append((m, s)))
        engine.start()
        self.assertEqual((engine.minutes, engine.seconds), (FOCUS_MINUTES, 0))
        self.assertEqual(ticks, [])

        engine.scheduler.fire()
        self.assertEqual((engine.minutes, engine.seconds), (24, 59))

        engine.pause()
        self.assertIsNone(engine.scheduler.pending)
        engine.start()
        self.assertEqual((engine.minutes, engine.seconds), (24, 59))

    def test_focus_block_lasts_full_length_then_shows_the_break(self):
        phases = []
        engine = PomodoroEngine(
            FakeScheduler(),
            on_phase_change=lambda mode, label, count: phases.append(label),
        )
        engine.minutes = 0
        engine.seconds = 1
        engine.start()
        engine.scheduler.fire()
        self.assertEqual(phases, ["short_break"])
        self.assertEqual((engine.minutes, engine.seconds), (SHORT_BREAK_MINUTES, 0))
        self.assertEqual(engine.phase_label, "short_break")

    def test_fourth_focus_opens_the_long_break(self):
        phases = []
        engine = PomodoroEngine(
            FakeScheduler(),
            on_phase_change=lambda mode, label, count: phases.append(label),
        )
        engine.pomodoro_count = 3
        engine.minutes = 0
        engine.seconds = 1
        engine.start()
        engine.scheduler.fire()
        self.assertEqual(phases, ["long_break"])
        self.assertEqual(engine.minutes, LONG_BREAK_MINUTES)


if __name__ == "__main__":
    unittest.main()
