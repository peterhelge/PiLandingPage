import threading
import tkinter as tk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import config
from components import RoundedButton

PLAYLIST_FETCH_LIMIT = 50   # Spotify's max page size - covers virtually any real library
PLAYLIST_LIST_HEIGHT = 210  # visible height of the scrollable playlist area (~4 rows)


class TouchScrollableRow(RoundedButton):
    """A RoundedButton variant for rows that live inside a touch-scrollable
    list. Plain RoundedButton fires its command immediately on touch-DOWN,
    which would hijack every scroll gesture as a tap on whatever row happens
    to be under the finger. This instead fires on release, and only if the
    touch didn't move past a small drag threshold - and it drives the
    parent ScrollableList's scroll position directly, since a canvas's own
    bindings never see events that land on a child widget embedded in it."""

    DRAG_THRESHOLD = 10

    def __init__(self, parent, scroll_list, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.scroll_list = scroll_list
        self.unbind("<Button-1>")
        self.bind("<Button-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_motion)
        self.bind("<ButtonRelease-1>", self._on_release)
        self._press_y = None
        self._moved = False

    def _on_press(self, event):
        self._press_y = event.y_root
        self._moved = False
        self.scroll_list.begin_drag()
        return "break"

    def _on_motion(self, event):
        if self._press_y is None:
            return "break"
        dy = event.y_root - self._press_y
        if abs(dy) > self.DRAG_THRESHOLD:
            self._moved = True
        self.scroll_list.drag_to(dy)
        return "break"

    def _on_release(self, event):
        if not self._moved and self.command:
            self.command()
        self.scroll_list.end_drag()
        self._press_y = None
        return "break"


class ScrollableList(tk.Frame):
    """A vertically touch-scrollable container. Rows are TouchScrollableRow
    instances that relay their own drag events here (see above) since a
    canvas never sees events landing on a child widget embedded in it."""

    def __init__(self, parent, height, bg):
        super().__init__(parent, bg=bg)
        self.bg = bg
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, height=height)
        self.canvas.pack(fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self._window_id, width=e.width))

        self._drag_start_frac = None
        self._bg_press_y = None
        self.canvas.bind("<Button-1>", self._on_bg_press)
        self.canvas.bind("<B1-Motion>", self._on_bg_motion)
        self.canvas.bind("<ButtonRelease-1>", lambda e: self.end_drag())

    def _on_bg_press(self, event):
        self._bg_press_y = event.y_root
        self.begin_drag()

    def _on_bg_motion(self, event):
        if self._bg_press_y is None:
            return
        self.drag_to(event.y_root - self._bg_press_y)

    def clear(self):
        for child in self.inner.winfo_children():
            child.destroy()

    def add_row(self, text, command, height=46):
        row = TouchScrollableRow(
            self.inner, self, text=text, command=command,
            width=320, height=height, corner_radius=8,
            bg_color=config.SURFACE_COLOR, hover_color=config.SURFACE_COLOR, fg_color="white",
        )
        row.pack(fill="x", pady=3)
        return row

    def begin_drag(self):
        self._drag_start_frac = self.canvas.yview()[0]

    def drag_to(self, total_dy):
        if self._drag_start_frac is None:
            self.begin_drag()
        bbox = self.canvas.bbox("all")
        if not bbox:
            return
        content_h = bbox[3] - bbox[1]
        canvas_h = self.canvas.winfo_height()
        if content_h <= canvas_h:
            return
        frac_delta = -total_dy / content_h
        new_frac = max(0.0, min(1.0, self._drag_start_frac + frac_delta))
        self.canvas.yview_moveto(new_frac)

    def end_drag(self):
        self._drag_start_frac = None


class SpotifyWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.BG_COLOR, bd=0)
        self.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        self.sp = None
        self.is_playing = False
        self.playlists = []
        self._load_icons()

        if config.SPOTIPY_CLIENT_ID:
            try:
                self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                    client_id=config.SPOTIPY_CLIENT_ID,
                    client_secret=config.SPOTIPY_CLIENT_SECRET,
                    redirect_uri=config.SPOTIPY_REDIRECT_URI,
                    scope=config.SPOTIPY_SCOPE
                ))
            except Exception: print("Spotify Auth Failed")

        # Eyebrow title, muted - identifies the widget without competing visually
        tk.Label(self, text="SPOTIFY", font=("Verdana", 10, "bold"),
                 bg=config.BG_COLOR, fg="#5A5A5A").pack(pady=(4, 8))

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

        RoundedButton(c_frame, text="", command=self.prev_track, width=65, height=60,
                      bg_color="#2A2A2A", hover_color="#2A2A2A", icon=self.icon_prev).pack(side="left", padx=5)

        self.play_btn = RoundedButton(c_frame, text="", command=self.play_pause, width=90, height=60,
                                       bg_color=config.SPOTIFY_GREEN, hover_color=config.SPOTIFY_GREEN,
                                       icon=self.icon_play)
        self.play_btn.pack(side="left", padx=5)

        RoundedButton(c_frame, text="", command=self.next_track, width=65, height=60,
                      bg_color="#2A2A2A", hover_color="#2A2A2A", icon=self.icon_next).pack(side="left", padx=5)

        # Volume Controls
        v_frame = tk.Frame(self, bg=config.BG_COLOR)
        v_frame.pack(pady=(12, 10))

        if self.icon_vdown and self.icon_vup:
            RoundedButton(v_frame, text="", command=self.vol_down, width=90, height=50,
                          bg_color="#2A2A2A", hover_color="#2A2A2A", icon=self.icon_vdown).pack(side="left", padx=15)
            RoundedButton(v_frame, text="", command=self.vol_up, width=90, height=50,
                          bg_color="#2A2A2A", hover_color="#2A2A2A", icon=self.icon_vup).pack(side="left", padx=15)
        else:
            tk.Label(v_frame, text="Vol Error", bg="red").pack()

        # Playlists - big touch-friendly rows, sorted alphabetically, in a
        # touch-scrollable list instead of a native, small-print Listbox.
        tk.Label(self, text="PLAYLISTS", font=("Verdana", 10, "bold"),
                 bg=config.BG_COLOR, fg="#5A5A5A").pack(pady=(6, 6))

        self.playlist_list = ScrollableList(self, height=PLAYLIST_LIST_HEIGHT, bg=config.BG_COLOR)
        self.playlist_list.pack(fill="x", padx=5)

        self.load_playlists()
        self.check_playback()

    def _load_icons(self):
        self.icon_vdown = self.icon_vup = None
        self.icon_play = self.icon_pause = self.icon_prev = self.icon_next = None
        try:
            from PIL import Image, ImageTk
            sz = (28, 28)
            self.icon_vdown = ImageTk.PhotoImage(Image.open("assets/vol_down.png").resize(sz))
            self.icon_vup = ImageTk.PhotoImage(Image.open("assets/vol_up.png").resize(sz))
            self.icon_play = ImageTk.PhotoImage(Image.open("assets/play.png").resize((32, 32)))
            self.icon_pause = ImageTk.PhotoImage(Image.open("assets/pause.png").resize((32, 32)))
            self.icon_prev = ImageTk.PhotoImage(Image.open("assets/prev_track.png").resize((28, 28)))
            self.icon_next = ImageTk.PhotoImage(Image.open("assets/next_track.png").resize((28, 28)))
        except Exception as e:
            print(f"Icon Error: {e}")

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
        # Run in background to avoid freezing startup
        if self.sp:
             threading.Thread(target=self._fetch_playlists, daemon=True).start()

    def _fetch_playlists(self):
        try:
            results = self.sp.current_user_playlists(limit=PLAYLIST_FETCH_LIMIT)
            # Update UI on Main Thread
            self.after(0, lambda: self._update_playlist_ui(results))
        except Exception as e:
            print(f"Error fetching playlists: {e}")

    def _update_playlist_ui(self, results):
        if not results: return
        items = sorted(results['items'], key=lambda item: item['name'].casefold())
        self.playlist_list.clear()
        for item in items:
            uri = item['uri']
            self.playlists.append((item['name'], uri))
            self.playlist_list.add_row(item['name'], command=lambda u=uri: self._play_uri(u))

    def check_playback(self):
        # Poll in a background thread
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
                self._set_playing(True)
            else:
                self.track_lbl.config(text="Paused / Idle")
                self._set_playing(False)
        except Exception: pass

    def _set_playing(self, playing):
        if playing == self.is_playing:
            return
        self.is_playing = playing
        if self.icon_play and self.icon_pause:
            self.play_btn.set_text(icon=self.icon_pause if playing else self.icon_play)

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

    def _play_uri(self, uri):
        if self.sp:
            self._run_async(lambda: self._play_playlist_impl(uri))

    def _play_playlist_impl(self, uri):
        try:
            dev_id = self.get_active_device_id()
            self.sp.start_playback(context_uri=uri, device_id=dev_id)
        except Exception as e:
            print(f"Playlist Play Error: {e}")

    def _run_async(self, func):
        threading.Thread(target=func, daemon=True).start()
