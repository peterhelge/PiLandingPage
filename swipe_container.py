import tkinter as tk

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
        self.min_swipe_distance = 100 # Minimum pixels to register a swipe
        
        # Bind events to the whole container
        # Note: Event binding might need to be on the pages themselves if they consume events,
        # but binding_all usually catches it.
        self.bind_all("<Button-1>", self.on_touch_start)
        self.bind_all("<B1-Motion>", self.on_touch_move) 
        self.bind_all("<ButtonRelease-1>", self.on_touch_end)

    def show_page(self, index):
        if 0 <= index < len(self.pages):
            self.current_page_index = index
            page = self.pages[index]
            page.tkraise()
            
            # Optional: Visual feedback or animation hook could go here

    def next_page(self):
        new_index = (self.current_page_index + 1) % len(self.pages)
        self.show_page(new_index)

    def prev_page(self):
        new_index = (self.current_page_index - 1) % len(self.pages)
        self.show_page(new_index)

    # --- EVENT HANDLERS ---
    
    def on_touch_start(self, event):
        self.start_x = event.x

    def on_touch_move(self, event):
        # We can detect "dragging" here if we want continuous feedback,
        # but for simple page switching, we just wait for release.
        pass

    def on_touch_end(self, event):
        if self.start_x is None: return
        
        end_x = event.x
        diff_x = end_x - self.start_x
        
        # Reset start
        self.start_x = None
        
        # Detect Swipe
        if abs(diff_x) > self.min_swipe_distance:
            if diff_x < 0:
                # Swipe Left -> Next Page
                self.next_page()
            else:
                # Swipe Right -> Prev Page
                self.prev_page()
