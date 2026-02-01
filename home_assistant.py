import tkinter as tk
import config
from components import RoundedButton
from ha_api import ha_client
import threading

from PIL import Image, ImageTk

class HAWidget(tk.Frame):
    def __init__(self, parent, entity_id):
        # Transparent background (matches parent), no border
        super().__init__(parent, bg=config.BG_COLOR, highlightthickness=0)
        self.entity_id = entity_id
        
        # Determine name from ID roughly
        self.friendly_name = entity_id.split(".")[-1].replace("_", " ").title()
        
        # Determine type
        self.is_sensor = entity_id.startswith("sensor.")
        self.sensor_type = "generic"
        if "temp" in entity_id or "temperature" in entity_id: self.sensor_type = "temp"
        elif "hum" in entity_id or "humidity" in entity_id: self.sensor_type = "humidity"

        # Load Icons (Larger size: 80x80)
        try:
            if self.is_sensor:
                icon_name = "assets/thermometer.png" if self.sensor_type == "temp" else "assets/humidity.png"
                # If generic sensor, maybe use info icon? For now default to humidity shape or keep None?
                # Let's fallback to thermometer if unknown sensor
                if self.sensor_type == "generic": icon_name = "assets/thermometer.png"
                
                self.icon_main = ImageTk.PhotoImage(Image.open(icon_name).resize((80, 80)))
                self.icon_on = None
                self.icon_off = None
            else:
                self.icon_on = ImageTk.PhotoImage(Image.open("assets/bulb_on.png").resize((80, 80)))
                self.icon_off = ImageTk.PhotoImage(Image.open("assets/bulb_off.png").resize((80, 80)))
                self.icon_main = None
        except Exception as e:
            print(f"Error loading icons: {e}")
            self.icon_on = None
            self.icon_off = None
            self.icon_main = None
        
        # Icon Container
        self.icon_lbl = tk.Label(self, bg=config.BG_COLOR)
        if self.is_sensor and self.icon_main:
             self.icon_lbl.config(image=self.icon_main)
             
        self.icon_lbl.pack(pady=(0, 5))

        # Name Label (Centered)
        self.name_lbl = tk.Label(self, text=self.friendly_name, font=config.FONT_SMALL,
                                 bg=config.BG_COLOR, fg="#AAA", anchor="center", wraplength=100)
        self.name_lbl.pack(fill="x")

        # Value Label (For sensors)
        self.val_lbl = tk.Label(self, text="", font=("Verdana", 14, "bold"), 
                                bg=config.BG_COLOR, fg="white", anchor="center")
        if self.is_sensor:
            self.val_lbl.pack(fill="x")

        # Click to Toggle (Only for non-sensors)
        if not self.is_sensor:
            self.bind("<Button-1>", self.toggle)
            self.name_lbl.bind("<Button-1>", self.toggle)
            self.icon_lbl.bind("<Button-1>", self.toggle)
        
        self.update_state()

    def toggle(self, event=None):
        if self.is_sensor: return
        ha_client.toggle_entity(self.entity_id)
        # Optimistic update (Simple color swap simulation if needed, but we wait for update mostly)
        self.after(200, self.update_state)
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
        
        if self.is_sensor:
            # Display Value
            unit = state_obj.get('attributes', {}).get('unit_of_measurement', "")
            self.val_lbl.config(text=f"{state} {unit}")
            # Ensure name is gray
            self.name_lbl.config(fg="#AAA")
        else:
            # Update Icon for Switches
            if state.lower() == "on":
                if self.icon_on:
                    self.icon_lbl.config(image=self.icon_on)
                self.name_lbl.config(fg=config.SPOTIFY_GREEN) # Highlight text too
            else:
                if self.icon_off:
                    self.icon_lbl.config(image=self.icon_off)
                self.name_lbl.config(fg="#AAA")
                
class HomeAssistantPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.BG_COLOR)
        
        # Header
        tk.Label(self, text="Home Control", font=config.FONT_LARGE, 
                 bg=config.BG_COLOR, fg="white").pack(pady=30)

        # Entity Grid Container - Centered nicely
        self.grid_frame = tk.Frame(self, bg=config.BG_COLOR)
        self.grid_frame.pack(fill="both", expand=True, padx=40)
        
        if not config.HA_ENTITIES:
            tk.Label(self.grid_frame, 
                     text="No Entities Configured.\nAdd HA_ENTITIES to .env", 
                     font=config.FONT_MED, bg=config.BG_COLOR, fg="gray").pack()
        else:
            self.create_widgets()

    def create_widgets(self):
        # App Icon Grid Layout
        cols = 4 # More dense
        for i, entity_id in enumerate(config.HA_ENTITIES):
            try:
                row = i // cols
                col = i % cols
                
                # Container for cell (helps centering)
                frame_container = tk.Frame(self.grid_frame, bg=config.BG_COLOR)
                frame_container.grid(row=row, column=col, padx=15, pady=25) # More breathing room around icons
                
                # Actual Widget
                w = HAWidget(frame_container, entity_id=entity_id)
                w.pack()
            except Exception as e:
                print(f"Error creating widget: {e}")

        # Configure Grid Weights so it centers content if few items
        # OR: Just let them pack to top-left or center. 
        # For 'App Icon' feel, top-left alignment (like phone) is often preferred, 
        # but let's center the whole block horizontally if possible.
        # Current implementation just Grids them. To center whole grid block, we packed grid_frame with fill=both.
        # Let's simple-grid.
