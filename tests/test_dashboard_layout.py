import unittest


class DashboardDividerTests(unittest.TestCase):
    def test_rules_sit_between_the_three_columns(self):
        import tkinter as tk
        from main import DashboardPage

        root = tk.Tk()
        root.geometry("800x480")
        try:
            page = DashboardPage(root)
            page.pack(fill="both", expand=True)
            root.update()

            children = page.winfo_children()
            self.assertGreaterEqual(len(children), 5)
            # The narrow frames are the rules, and each one is between two columns.
            self.assertLessEqual(children[1].winfo_width(), 2)
            self.assertLessEqual(children[3].winfo_width(), 2)
            self.assertGreater(children[0].winfo_width(), 2)
            self.assertGreater(children[2].winfo_width(), 2)
            self.assertGreater(children[4].winfo_width(), 2)
            self.assertGreater(children[1].winfo_x(), children[0].winfo_x())
            self.assertLess(children[1].winfo_x(), children[2].winfo_x())
            self.assertGreater(children[3].winfo_x(), children[2].winfo_x())
            self.assertLess(children[3].winfo_x(), children[4].winfo_x())
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
