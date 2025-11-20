import tkinter as tk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import config

class SpotifyWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.BG_COLOR, bd=0)
        self.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        self.sp = None
        if config.SPOTIPY_CLIENT_ID:
            try:
                self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                    client_id=config.SPOTIPY_CLIENT_ID,
                    client_secret=config.SPOTIPY_CLIENT_SECRET,
                    redirect_uri=config.SPOTIPY_REDIRECT_URI,
                    scope=config.SPOTIPY_SCOPE
                ))
            except Exception: print("Spotify Auth Failed")

        tk.Label(self, text="Spotify", font=config.FONT_MED, bg=config.BG_COLOR, fg="gray").pack(pady=(10,5))

        # Track Info (Expands to fill upper area)
        self.track_info_frame = tk.Frame(self, bg=config.BG_COLOR)
        self.track_info_frame.pack(expand=True)

        self.track_lbl = tk.Label(self.track_info_frame, text="Not Playing", font=config.FONT_LARGE, 
                                  bg=config.BG_COLOR, fg=config.FG_COLOR, wraplength=300, justify="center")
        self.track_lbl.pack()
        
        self.device_lbl = tk.Label(self.track_info_frame, text="", font=config.FONT_MED, bg=config.BG_COLOR, fg="gray")
        self.device_lbl.pack()

        # Controls
        c_frame = tk.Frame(self, bg=config.BG_COLOR)
        c_frame.pack(pady=10)

        btn_conf = {"bg": "#333", "fg": "white", "bd": 0, "width": 5, "font": config.FONT_MED}
        tk.Button(c_frame, text="⏮", command=self.prev_track, **btn_conf).pack(side="left", padx=10, ipady=5)
        tk.Button(c_frame, text="⏯", command=self.play_pause, bg=config.ACCENT_COLOR, 
                  fg="white", bd=0, width=5, font=config.FONT_MED).pack(side="left", padx=10, ipady=5)
        tk.Button(c_frame, text="⏭", command=self.next_track, **btn_conf).pack(side="left", padx=10, ipady=5)
        
        # Playlist List - Made Taller and wider
        tk.Label(self, text="Quick Playlists", bg=config.BG_COLOR, fg="gray", 
                 font=config.FONT_SMALL).pack(pady=(15,0))
        
        # Height 6 means it will show 6 playlists at once, filling more space
        self.playlist_box = tk.Listbox(self, bg="#1E1E1E", fg="#AAA", height=6, bd=0, 
                                       font=config.FONT_MED, selectbackground=config.ACCENT_COLOR)
        self.playlist_box.pack(fill="x", padx=5, pady=5)
        self.playlist_box.bind('<<ListboxSelect>>', self.play_selected_playlist)
        
        self.playlists = []
        self.load_playlists()
        self.check_playback()

    def load_playlists(self):
        if not self.sp: return
        try:
            results = self.sp.current_user_playlists(limit=20) # Fetch more playlists
            for item in results['items']:
                self.playlists.append((item['name'], item['uri']))
                self.playlist_box.insert(tk.END, f" {item['name']}")
        except Exception: pass

    def check_playback(self):
        if self.sp:
            try:
                playback = self.sp.current_playback()
                if playback and playback['is_playing']:
                    track = playback['item']['name']
                    artist = playback['item']['artists'][0]['name']
                    device = playback['device']['name']
                    self.track_lbl.config(text=f"{track}\n{artist}")
                    self.device_lbl.config(text=f"on {device}")
                else:
                    self.track_lbl.config(text="Paused / Idle")
            except Exception: pass
        self.after(5000, self.check_playback)

    def play_pause(self):
        if self.sp:
            try:
                pb = self.sp.current_playback()
                if pb and pb['is_playing']: self.sp.pause_playback()
                else: self.sp.start_playback()
                self.check_playback()
            except: pass

    def next_track(self): 
        if self.sp: self.sp.next_track()
        
    def prev_track(self): 
        if self.sp: self.sp.previous_track()

    def play_selected_playlist(self, event):
        selection = event.widget.curselection()
        if selection and self.sp:
            index = selection[0]
            uri = self.playlists[index][1]
            try:
                self.sp.start_playback(context_uri=uri)
            except: pass