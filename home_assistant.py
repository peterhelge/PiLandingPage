import tkinter as tk
import config
from components import RoundedButton
from ha_api import ha_client
import threading

class HAWidget(tk.Frame):
    def __init__(self, parent, entity_id):
        super().__init__(parent, bg="#1E1E1E", highlightthickness=1, highlightbackground="#333")
        self.entity_id = entity_id
        
        # Determine name from ID roughly
        self.friendly_name = entity_id.split(".")[-1].replace("_", " ").title()
        
        # Layout
        self.pack_propagate(False)
        
        # Name Label
        self.name_lbl = tk.Label(self, text=self.friendly_name, font=config.FONT_SMALL,
                                 bg="#1E1E1E", fg="#AAA", anchor="w")
        self.name_lbl.pack(fill="x", padx=10, pady=(10, 0))
        
        # State/Icon Label
        self.state_lbl = tk.Label(self, text="...", font=config.FONT_MED,
                                  bg="#1E1E1E", fg="white", anchor="w")
        self.state_lbl.pack(fill="x", padx=10, pady=(5, 10))

        # Click to Toggle
        self.bind("<Button-1>", self.toggle)
        self.name_lbl.bind("<Button-1>", self.toggle)
        self.state_lbl.bind("<Button-1>", self.toggle)
        
        self.update_state()

    def toggle(self, event=None):
        ha_client.toggle_entity(self.entity_id)
        # Optimistic update
        current = self.state_lbl.cget("text")
        new_state = "Off" if current == "On" else "On"
        self.state_lbl.config(text=f"{new_state}...", fg="yellow")
        
        # Force refresh soon
        self.after(2000, self.update_state)

    def update_state(self):
        # Threaded fetch
        threading.Thread(target=self._fetch, daemon=True).start()
        # Schedule next poll (every 5s)
        self.after(5000, self.update_state)

    def _fetch(self):
        state_obj = ha_client.get_entity_state(self.entity_id)
        if state_obj:
            self.after(0, lambda: self._update_ui(state_obj))

    def _update_ui(self, state_obj):
        state = state_obj['state']
        # Try to use friendly name if available
        if 'attributes' in state_obj and 'friendly_name' in state_obj['attributes']:
            self.name_lbl.config(text=state_obj['attributes']['friendly_name'])
        
        # Color code
        fg_color = "white"
        if state.lower() == "on":
            fg_color = config.SPOTIFY_GREEN
        
        self.state_lbl.config(text=state.title(), fg=fg_color)
        
                
class HomeAssistantPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.BG_COLOR)
        
        # Header
        tk.Label(self, text="Home Control", font=config.FONT_LARGE, 
                 bg=config.BG_COLOR, fg="white").pack(pady=20)

        # Entity Grid Container
        self.grid_frame = tk.Frame(self, bg=config.BG_COLOR)
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=20)

        print(f"DEBUG: HA_ENTITIES = {config.HA_ENTITIES}") # Debugging

        if not config.HA_ENTITIES:
            tk.Label(self.grid_frame, 
                     text="No Entities Configured.\nAdd HA_ENTITIES to .env", 
                     font=config.FONT_MED, bg=config.BG_COLOR, fg="gray").pack()
        else:
            self.create_widgets()

    def create_widgets(self):
        # simple grid layout
        cols = 3
        for i, entity_id in enumerate(config.HA_ENTITIES):
            row = i // cols
            col = i % cols
            
            # Container for margin
            frame_container = tk.Frame(self.grid_frame, bg=config.BG_COLOR)
            frame_container.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
            
            # Actual Widget
            w = HAWidget(frame_container, entity_id=entity_id)
            w.pack(fill="both", expand=True)

        # Configure Grid Weights
        for i in range(cols):
            self.grid_frame.grid_columnconfigure(i, weight=1)
