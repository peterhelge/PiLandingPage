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

        # Playback Controls (Compacted to fit screen)
        c_frame = tk.Frame(self, bg=config.BG_COLOR)
        c_frame.pack(pady=(10, 5))

        RoundedButton(c_frame, text="<<", command=self.prev_track, width=65, height=60, 
                      bg_color="#333", hover_color="#444").pack(side="left", padx=5)
        
        RoundedButton(c_frame, text="Play", command=self.play_pause, width=100, height=60, 
                      bg_color=config.SPOTIFY_GREEN, hover_color="#159045").pack(side="left", padx=5)
        
        RoundedButton(c_frame, text=">>", command=self.next_track, width=65, height=60, 
                      bg_color="#333", hover_color="#444").pack(side="left", padx=5)

        # Volume Controls
        v_frame = tk.Frame(self, bg=config.BG_COLOR)
        v_frame.pack(pady=(15, 10))

        # Load Icons
        try:
            from PIL import Image, ImageTk
            sz = (30, 30)
            self.icon_vdown = ImageTk.PhotoImage(Image.open("assets/vol_down.png").resize(sz))
            self.icon_vup = ImageTk.PhotoImage(Image.open("assets/vol_up.png").resize(sz))
            
            # Vol Down
            RoundedButton(v_frame, text="", command=self.vol_down, width=110, height=60, 
                          bg_color="#333", hover_color="#444", icon=self.icon_vdown).pack(side="left", padx=20)
            
            # Vol Up
            RoundedButton(v_frame, text="", command=self.vol_up, width=110, height=60, 
                          bg_color="#333", hover_color="#444", icon=self.icon_vup).pack(side="left", padx=20)
            
        except Exception as e:
             print(f"Vol Icon Error: {e}")
             tk.Label(v_frame, text="Vol Error", bg="red").pack()

        
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
        # Poll in a background thread
        import threading
        t = threading.Thread(target=self._poll_spotify, daemon=True)
        t.start()
        
        # Schedule next poll
        self.after(5000, self.check_playback)

    def _poll_spotify(self):
        if not self.sp: return
        try:
            playback = self.sp.current_playback()
            # Update UI on main thread
            self.after(0, lambda: self._update_ui_playback(playback))
        except Exception: 
            pass

    def _update_ui_playback(self, playback):
        try:
            if playback and playback['is_playing']:
                track = playback['item']['name']
                artist = playback['item']['artists'][0]['name']
                device = playback['device']['name']
                self.track_lbl.config(text=f"{track}\n{artist}")
                self.device_lbl.config(text=f"on {device}")
                
                # No need to sync slider anymore, maybe just update label?
                # For now, just keeping track/artist is enough.
                pass
            else:
                self.track_lbl.config(text="Paused / Idle")
        except Exception: pass

    # Refactor play/pause/next/prev/vol to run in background too to be safe
    # although they are less frequent, they can still hang.
    
    def play_pause(self):
        self._run_async(self._play_pause_impl)

    def _play_pause_impl(self):
        if not self.sp: return
        try:
            pb = self.sp.current_playback()
            if pb and pb['is_playing']: self.sp.pause_playback()
            else: 
                dev_id = self.get_active_device_id()
                self.sp.start_playback(device_id=dev_id)
            # Trigger an immediate check (optional, or just wait for next poll)
            self.after(500, self.check_playback) 
        except: pass

    def next_track(self): 
        self._run_async(lambda: self.sp.next_track() if self.sp else None)
        
    def prev_track(self): 
        self._run_async(lambda: self.sp.previous_track() if self.sp else None)

    def vol_up(self):
        self._change_vol(10)

    def vol_down(self):
        self._change_vol(-10)

    def _change_vol(self, delta):
        if not self.sp: return
        self._run_async(lambda: self._vol_change_impl(delta))

    def _vol_change_impl(self, delta):
        try:
            # We need current volume first. 
            # Optimistic update is hard without current state, so we fetch playback
            pb = self.sp.current_playback()
            if pb and pb['device']:
                curr = pb['device']['volume_percent']
                new_vol = max(0, min(100, curr + delta))
                self.sp.volume(new_vol)
        except: pass

    def play_selected_playlist(self, event):
        selection = event.widget.curselection()
        if selection and self.sp:
            index = selection[0]
            uri = self.playlists[index][1]
            self._run_async(lambda: self._play_playlist_impl(uri))

    def _play_playlist_impl(self, uri):
        try:
            dev_id = self.get_active_device_id()
            self.sp.start_playback(context_uri=uri, device_id=dev_id)
        except Exception as e:
            print(f"Playlist Play Error: {e}")

    def _run_async(self, func):
        import threading
        threading.Thread(target=func, daemon=True).start()