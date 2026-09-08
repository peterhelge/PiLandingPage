import tkinter as tk
import config
from components import RoundedButton
from ha_api import ha_client
import mold_risk
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
                
class MoldRiskGauge(tk.Frame):
    """Circular meter combining a temperature + humidity sensor pair into a
    single at-a-glance mould-risk indicator, via mold_risk.mold_risk_ratio."""

    SIZE = 100
    RING_WIDTH = 10
    MAX_RATIO_FOR_FULL_RING = 1.2  # ring visually maxes out a bit past "high" (0.95) rather than clipping right at it

    def __init__(self, parent, temp_entity_id, humidity_entity_id):
        super().__init__(parent, bg=config.BG_COLOR)
        self.temp_entity_id = temp_entity_id
        self.humidity_entity_id = humidity_entity_id
        self.temp_val = None
        self.humidity_val = None

        self.canvas = tk.Canvas(self, width=self.SIZE, height=self.SIZE, bg=config.BG_COLOR, highlightthickness=0)
        self.canvas.pack()

        self.name_lbl = tk.Label(self, text="Attic Mould Risk", font=config.FONT_SMALL,
                                  bg=config.BG_COLOR, fg="#AAA", wraplength=100, justify="center")
        self.name_lbl.pack(fill="x")

        self.detail_lbl = tk.Label(self, text="", font=("Verdana", 10), bg=config.BG_COLOR, fg="#777777")
        self.detail_lbl.pack(fill="x")

        self._draw(None)
        self.update_state()

    def update_state(self):
        threading.Thread(target=self._fetch, daemon=True).start()
        self.after(5000, self.update_state)

    def _fetch(self):
        t_obj = ha_client.get_entity_state(self.temp_entity_id)
        h_obj = ha_client.get_entity_state(self.humidity_entity_id)
        self.after(0, lambda: self._update_ui(t_obj, h_obj))

    def _update_ui(self, t_obj, h_obj):
        try:
            if t_obj is not None:
                self.temp_val = float(t_obj['state'])
        except (ValueError, TypeError, KeyError):
            pass
        try:
            if h_obj is not None:
                self.humidity_val = float(h_obj['state'])
        except (ValueError, TypeError, KeyError):
            pass

        ratio = mold_risk.mold_risk_ratio(self.temp_val, self.humidity_val)
        self._draw(ratio)

        if self.temp_val is not None and self.humidity_val is not None:
            self.detail_lbl.config(text=f"{self.temp_val:.0f}°C  {self.humidity_val:.0f}%")
        else:
            self.detail_lbl.config(text="No data")

    def _draw(self, ratio):
        self.canvas.delete("all")
        pad = self.RING_WIDTH / 2 + 2
        bbox = (pad, pad, self.SIZE - pad, self.SIZE - pad)

        # Background ring (full circle, dim) - always shown as the track the value ring sits on
        self.canvas.create_oval(*bbox, outline="#2A2A2A", width=self.RING_WIDTH)

        level, color = mold_risk.risk_level(ratio)

        if ratio is not None:
            fraction = max(0.0, min(ratio, self.MAX_RATIO_FOR_FULL_RING)) / self.MAX_RATIO_FOR_FULL_RING
            # Start at 12 o'clock (90 deg in Tk's math convention), sweep clockwise
            # (negative extent) proportional to how far into the risk range we are.
            extent = -359.9 * fraction
            if fraction > 0:
                self.canvas.create_arc(*bbox, start=90, extent=extent, style="arc",
                                        outline=color, width=self.RING_WIDTH)
            label = f"{int(round(ratio * 100))}%"
        else:
            label = "--"

        self.canvas.create_text(self.SIZE / 2, self.SIZE / 2, text=label, fill=color,
                                 font=("Verdana", 15, "bold"))


class HomeAssistantPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.BG_COLOR)
        
        # Header
        tk.Label(self, text="Home Control", font=config.FONT_LARGE, 
                 bg=config.BG_COLOR, fg="white").pack(pady=30)

        # Entity Grid Container - Centered nicely
        self.grid_frame = tk.Frame(self, bg=config.BG_COLOR)
        self.grid_frame.pack(fill="both", expand=True, padx=40)

        has_mold_gauge = bool(config.MOLD_RISK_TEMP_ENTITY and config.MOLD_RISK_HUMIDITY_ENTITY)
        if not config.HA_ENTITIES and not has_mold_gauge:
            tk.Label(self.grid_frame,
                     text="No Entities Configured.\nAdd HA_ENTITIES to .env",
                     font=config.FONT_MED, bg=config.BG_COLOR, fg="gray").pack()
        else:
            self.create_widgets(has_mold_gauge)

    def create_widgets(self, has_mold_gauge):
        # App Icon Grid Layout
        cols = 4 # More dense
        index = 0
        for entity_id in config.HA_ENTITIES:
            try:
                row = index // cols
                col = index % cols

                # Container for cell (helps centering)
                frame_container = tk.Frame(self.grid_frame, bg=config.BG_COLOR)
                frame_container.grid(row=row, column=col, padx=15, pady=25) # More breathing room around icons

                # Actual Widget
                w = HAWidget(frame_container, entity_id=entity_id)
                w.pack()
                index += 1
            except Exception as e:
                print(f"Error creating widget: {e}")

        # Mould-risk gauge - combines the attic temp/humidity sensors (which
        # may also be listed individually above) into one at-a-glance meter.
        if has_mold_gauge:
            try:
                row = index // cols
                col = index % cols
                frame_container = tk.Frame(self.grid_frame, bg=config.BG_COLOR)
                frame_container.grid(row=row, column=col, padx=15, pady=25)
                MoldRiskGauge(frame_container, config.MOLD_RISK_TEMP_ENTITY,
                              config.MOLD_RISK_HUMIDITY_ENTITY).pack()
            except Exception as e:
                print(f"Error creating mold risk gauge: {e}")

        # Configure Grid Weights so it centers content if few items
        # OR: Just let them pack to top-left or center. 
        # For 'App Icon' feel, top-left alignment (like phone) is often preferred, 
        # but let's center the whole block horizontally if possible.
        # Current implementation just Grids them. To center whole grid block, we packed grid_frame with fill=both.
        # Let's simple-grid.
