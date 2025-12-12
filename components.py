import tkinter as tk
import tkinter.font as tkfont

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=100, height=40, corner_radius=15, 
                 bg_color="#333333", fg_color="white", hover_color="#444444", icon=None):
        super().__init__(parent, borderwidth=0, relief="flat", highlightthickness=0, bg=parent["bg"])
        self.command = command
        self.text_str = text
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
        font = tkfont.Font(family="Verdana", size=12, weight="bold")
        
        if self.icon:
            # Icon + Text
            # Icon on left (approx 15% in), Text centered-ish relative to remaining space or just offset
            icon_x = self.width * 0.15
            text_x = self.width * 0.55
            if not self.text_str:
                icon_x = self.width / 2 # Center if no text
            
            self.create_image(icon_x, self.height/2, image=self.icon)
            
            if self.text_str:
                self.create_text(text_x, self.height / 2, text=self.text_str, fill=self.fg_color, font=font, anchor="center")
        else:
            # Text Only
            self.create_text(self.width / 2, self.height / 2, text=self.text_str, fill=self.fg_color, font=font)

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event):
        self._draw(self.hover_color)

    def _on_leave(self, event):
        self._draw(self.bg_color)