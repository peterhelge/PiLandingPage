import tkinter as tk
import tkinter.font as tkfont

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=100, height=40, corner_radius=8, 
                 bg_color="#333333", fg_color="white", hover_color="#444444", icon=None, subtitle=None):
        super().__init__(parent, borderwidth=0, relief="flat", highlightthickness=0, bg=parent["bg"])
        self.command = command
        self.text_str = text
        self.subtitle = subtitle
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.icon = icon

        # Set dimensions
        self.config(width=self.width, height=self.height)

        # Bind events
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        self._draw(self.bg_color)

    def _draw(self, color):
        self.delete("all")
        # Draw Rounded Rectangle (Now sharper)
        self.create_polygon(
            (0, self.height), 
            (0, 0), 
            (self.width, 0), 
            (self.width, self.height),
            smooth=True, fill=color, outline="")
        
        # NOTE: Tkinter 'smooth=True' on polygon makes it very round if few points. 
        # For precise rounded rect, we need arcs + lines. 
        # But 'create_polygon' with smooth=True is a "hack" for pill shapes.
        # For sharper corners (Material), we real arcs.
        # Let's switch to a proper implementation using arcs and rectangles for better control.
        # Actually, simpler: just use 'create_line' with width=height... no, that's pill.
        # Let's write a proper rounded_rect helper.
        
        radius = self.corner_radius
        # Ensure radius isn't too big for size
        radius = min(radius, self.width/2, self.height/2)
        
        # Top Left
        self.create_arc((0, 0, 2*radius, 2*radius), start=90, extent=90, fill=color, outline=color)
        # Top Right
        self.create_arc((self.width-2*radius, 0, self.width, 2*radius), start=0, extent=90, fill=color, outline=color)
        # Bottom Right
        self.create_arc((self.width-2*radius, self.height-2*radius, self.width, self.height), start=270, extent=90, fill=color, outline=color)
        # Bottom Left
        self.create_arc((0, self.height-2*radius, 2*radius, self.height), start=180, extent=90, fill=color, outline=color)
        
        # Rectangles to fill gaps
        self.create_rectangle((radius, 0, self.width-radius, self.height), fill=color, outline=color)
        self.create_rectangle((0, radius, self.width, self.height-radius), fill=color, outline=color)

        
        # Draw Content
        
        if self.icon:
            if not self.text_str and not self.subtitle:
                # Icon ONLY -> Center it completely
                self.create_image(self.width / 2, self.height / 2, image=self.icon)
            else:
                # Layout: [ Icon ]  Title
                #                   Subtitle
                
                # Icon centered in left 15% zone (approx)
                icon_center_x = self.width * 0.15
                self.create_image(icon_center_x, self.height/2, image=self.icon)
                
                text_x = self.width * 0.30  # Start text at 30% width
                
                if self.subtitle:
                    # Title (Top half)
                    title_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
                    self.create_text(text_x, self.height * 0.35, text=self.text_str, fill=self.fg_color, font=title_font, anchor="w")
                    
                    # Subtitle (Bottom half)
                    sub_font = tkfont.Font(family="Helvetica", size=10)
                    self.create_text(text_x, self.height * 0.65, text=self.subtitle, fill="#DDDDDD", font=sub_font, anchor="w")
                else:
                    # Centered Title (Vertically)
                    font = tkfont.Font(family="Helvetica", size=12, weight="bold")
                    self.create_text(text_x, self.height / 2, text=self.text_str, fill=self.fg_color, font=font, anchor="w")
                
        else:
            # Text Only (Centered)
            font = tkfont.Font(family="Helvetica", size=12)
            self.create_text(self.width / 2, self.height / 2, text=self.text_str, fill=self.fg_color, font=font)

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event):
        self._draw(self.hover_color)

    def _on_leave(self, event):
        self._draw(self.bg_color)