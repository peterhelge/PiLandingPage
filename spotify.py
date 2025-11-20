import tkinter as tk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import config
from components import RoundedButton 

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

        # Title
        tk.Label(self, text="Spotify", font=config.FONT_MED, 
                 bg=config.BG_COLOR, fg=config.SPOTIFY_GREEN).pack(pady=(10,5))

        # Track Info
        self.track_info_frame = tk.Frame(self, bg=config.BG_COLOR)
        self.track_info_frame.pack(expand=True)

        self.track_lbl = tk.Label(self.track_info_frame, text="Not Playing", font=config.FONT_LARGE, 
                                  bg=config.BG_COLOR, fg=config.SPOTIFY_GREEN, wraplength=300, justify="center")
        self.track_lbl.pack()
        
        self.device_lbl = tk.Label(self.track_info_frame, text="", font=config.FONT_MED, bg=config.BG_COLOR, fg="gray")
        self.device_lbl.pack()

        # Playback Controls
        c_frame = tk.Frame(self, bg=config.BG_COLOR)
        c_frame.pack(pady=(10, 5))

        RoundedButton(c_frame, text="<<", command=self.prev_track, width=60, height=45, 
                      bg_color="#333", hover_color="#444").pack(side="left", padx=5)
        
        RoundedButton(c_frame, text="Play", command=self.play_pause, width=80, height=45, 
                      bg_color=config.SPOTIFY_GREEN, hover_color="#159045").pack(side="left", padx=5)
        
        RoundedButton(c_frame, text=">>", command=self.next_track, width=60, height=45, 
                      bg_color="#333", hover_color="#444").pack(side="left", padx=5)

        # --- NEW: Volume Controls ---
        v_frame = tk.Frame(self, bg=config.BG_COLOR)
        v_frame.pack(pady=(0, 10))

        # Volume Down
        RoundedButton(v_frame, text="-", command=lambda: self.change_vol(-10), width=40, height=40, 
                      bg_color="#222", hover_color="#333").pack(side="left", padx=10)
        
        # Label
        tk.Label(v_frame, text="VOL", font=config.FONT_SMALL, bg=config.BG_COLOR, fg="gray").pack(side="left")

        # Volume Up
        RoundedButton(v_frame, text="+", command=lambda: self.change_vol(10), width=40, height=40, 
                      bg_color="#222", hover_color="#333").pack(side="left", padx=10)

        
        # Playlists
        tk.Label(self, text="Quick Playlists", bg=config.BG_COLOR, fg="gray", 
                 font=config.FONT_SMALL).pack(pady=(5,0))
        
        self.playlist_box = tk.Listbox(self, bg="#1E1E1E", fg="#AAA", height=5, bd=0, 
                                       font=config.FONT_PLAYLIST, selectbackground=config.SPOTIFY_GREEN)
        self.playlist_box.pack(fill="x", padx=5, pady=5)
        self.playlist_box.bind('<<ListboxSelect>>', self.play_selected_playlist)
        
        self.playlists = []
        self.load_playlists()
        self.check_playback()

    def get_active_device_id(self):
        if not self.sp: return None
        try:
            devices = self.sp.devices()
            for d in devices['devices']:
                if d['is_active']: return d['id']
            if devices['devices']:
                return devices['devices'][0]['id']
        except: pass
        return None

    def load_playlists(self):
        if not self.sp: return
        try:
            results = self.sp.current_user_playlists(limit=20)
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
                else: 
                    dev_id = self.get_active_device_id()
                    self.sp.start_playback(device_id=dev_id)
                self.check_playback()
            except: pass

    def next_track(self): 
        if self.sp: self.sp.next_track()
        
    def prev_track(self): 
        if self.sp: self.sp.previous_track()

    def change_vol(self, step):
        if self.sp:
            try:
                pb = self.sp.current_playback()
                if pb: self.sp.volume(max(0, min(100, pb['device']['volume_percent'] + step)))
            except: pass

    def play_selected_playlist(self, event):
        selection = event.widget.curselection()
        if selection and self.sp:
            index = selection[0]
            uri = self.playlists[index][1]
            try:
                dev_id = self.get_active_device_id()
                self.sp.start_playback(context_uri=uri, device_id=dev_id)
            except Exception as e:
                print(f"Playlist Play Error: {e}")