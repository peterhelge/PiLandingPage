import tkinter as tk
import tkinter.font as tkfont

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=100, height=40, corner_radius=15, 
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
        # Draw Rounded Rectangle
        self.create_polygon(
            (0, self.height / 2),
            (0, 0),
            (self.width, 0),
            (self.width, self.height),
            (0, self.height),
            (0, self.height / 2),
            smooth=True, fill=color, outline="")
        
        # Draw Content
        
        if self.icon:
            # Layout: [ Icon ]  Title
            #                   Subtitle
            
            # Icon centered in left 25% zone
            icon_center_x = self.width * 0.15
            self.create_image(icon_center_x, self.height/2, image=self.icon)
            
            text_x = self.width * 0.30  # Start text at 30% width
            
            if self.subtitle:
                # Title (Top half)
                title_font = tkfont.Font(family="Verdana", size=14, weight="bold")
                self.create_text(text_x, self.height * 0.35, text=self.text_str, fill=self.fg_color, font=title_font, anchor="w")
                
                # Subtitle (Bottom half)
                sub_font = tkfont.Font(family="Verdana", size=10)
                self.create_text(text_x, self.height * 0.65, text=self.subtitle, fill="#DDDDDD", font=sub_font, anchor="w")
            else:
                # Centered Title (Vertically)
                font = tkfont.Font(family="Verdana", size=12, weight="bold")
                self.create_text(text_x, self.height / 2, text=self.text_str, fill=self.fg_color, font=font, anchor="w")
                
        else:
            # Text Only (Centered)
            font = tkfont.Font(family="Verdana", size=12)
            self.create_text(self.width / 2, self.height / 2, text=self.text_str, fill=self.fg_color, font=font)

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event):
        self._draw(self.hover_color)

    def _on_leave(self, event):
        self._draw(self.bg_color)