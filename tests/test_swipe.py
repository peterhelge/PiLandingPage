import unittest

from swipe_container import is_horizontal_swipe, widget_handles_press


class SwipeGestureTests(unittest.TestCase):
    def test_vertical_drift_is_not_a_page_change(self):
        self.assertTrue(is_horizontal_swipe(-140, 20, 100))
        self.assertTrue(is_horizontal_swipe(140, -10, 100))
        self.assertFalse(is_horizontal_swipe(-140, 180, 100))
        self.assertFalse(is_horizontal_swipe(40, 0, 100))
        self.assertFalse(is_horizontal_swipe(100, 100, 100))

    def test_press_on_a_button_does_not_start_a_swipe(self):
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        try:
            container = tk.Frame(root, bg="#121212")
            button = tk.Label(container, text="Power", bg="#121212")
            button.bind("<Button-1>", lambda _event: None)
            button.pack()
            label = tk.Label(container, text="Weather", bg="#121212")
            label.pack()
            root.update_idletasks()

            self.assertTrue(widget_handles_press(button, container))
            self.assertFalse(widget_handles_press(label, container))
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
