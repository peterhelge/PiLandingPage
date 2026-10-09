import tkinter as tk


def is_horizontal_swipe(dx, dy, minimum):
    """A page change is a sideways gesture, not a vertical scroll that drifted."""
    return abs(dx) >= minimum and abs(dx) > abs(dy)


def widget_handles_press(widget, stop_at):
    """True when this widget or an ancestor already handles the press.

    Buttons, task rows, and the playlist scroller bind <Button-1> themselves.
    A gesture that starts there is a tap or a scroll, not a page swipe.
    """
    current = widget
    while current is not None and current is not stop_at:
        try:
            sequences = current.bind()
        except tk.TclError:
            sequences = ()
        if "<Button-1>" in sequences or "<ButtonRelease-1>" in sequences:
            return True
        current = getattr(current, "master", None)
    return False


class SwipeableContainer(tk.Frame):
    def __init__(self, parent, pages, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.pages = []
        self.current_page_index = 0
        
        # Container configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Initialize Pages
        for PageClass in pages:
            # Create the page instance
            page = PageClass(self)
            self.pages.append(page)
            # Stack them all in the same grid cell
            page.grid(row=0, column=0, sticky="nsew")
            
        # Raise the first page
        self.show_page(0)
        
        # --- SWIPE LOGIC ---
        self.start_x = None
        self.start_y = None
        self.min_swipe_distance = 100 # Minimum pixels to register a swipe
        
        # Bind events to the whole container
        # Note: Event binding might need to be on the pages themselves if they consume events,
        # but binding_all usually catches it.
        self.bind_all("<Button-1>", self.on_touch_start)
        self.bind_all("<B1-Motion>", self.on_touch_move) 
        self.bind_all("<ButtonRelease-1>", self.on_touch_end)

    def show_page(self, index):
        if 0 <= index < len(self.pages):
            old_index = self.current_page_index
            if old_index != index and 0 <= old_index < len(self.pages):
                old_page = self.pages[old_index]
                if hasattr(old_page, "on_page_hidden"):
                    old_page.on_page_hidden()

            self.current_page_index = index
            page = self.pages[index]
            page.tkraise()

            if hasattr(page, "on_page_shown"):
                page.on_page_shown()

    def next_page(self):
        new_index = (self.current_page_index + 1) % len(self.pages)
        self.show_page(new_index)

    def prev_page(self):
        new_index = (self.current_page_index - 1) % len(self.pages)
        self.show_page(new_index)

    # --- EVENT HANDLERS ---
    
    def on_touch_start(self, event):
        self.start_x = None
        self.start_y = None
        if widget_handles_press(event.widget, self):
            return
        self.start_x = event.x_root
        self.start_y = event.y_root

    def on_touch_move(self, event):
        # Page changes are decided on release.
        pass

    def on_touch_end(self, event):
        if self.start_x is None:
            return

        dx = event.x_root - self.start_x
        dy = event.y_root - (self.start_y or event.y_root)
        self.start_x = None
        self.start_y = None

        if not is_horizontal_swipe(dx, dy, self.min_swipe_distance):
            return
        if dx < 0:
            self.next_page()
        else:
            self.prev_page()
