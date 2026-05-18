import customtkinter as ctk
import threading
import math
import struct
import wave
import os
import tempfile
from config import COLORS, FONTS

#klavye rotasyonları
KEYBOARD_LAYOUT = [
    ["Esc", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
    ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "BackSpace"],
    ["Tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\"],
    ["CapsLock", "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "Return"],
    ["Shift_L", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "Shift_R"],
    ["Control_L", "Win", "Alt_L", "space", "Alt_R", "Menu", "Control_R"],
]

KEY_LABELS = {
    "BackSpace": "⌫ Back", "Tab": "⇥ Tab", "CapsLock": "Caps", "Return": "Enter ↵",
    "Shift_L": "⇧ Shift", "Shift_R": "Shift ⇧", "Control_L": "Ctrl", "Control_R": "Ctrl",
    "Alt_L": "Alt", "Alt_R": "Alt", "Win": "⊞ Win", "Menu": "☰ Menu",
    "space": "─── Space ───", "Esc": "Esc",
}

KEY_WIDTHS = {
    "BackSpace": 90, "Tab": 70, "CapsLock": 80, "Return": 90,
    "Shift_L": 110, "Shift_R": 110, "Control_L": 70, "Control_R": 70,
    "Alt_L": 60, "Alt_R": 60, "Win": 60, "Menu": 60, "space": 300,
}

KEYSYM_MAP = {
    "BackSpace": "BackSpace", "Tab": "Tab", "Caps_Lock": "CapsLock",
    "Return": "Return", "Escape": "Esc",
    "Shift_L": "Shift_L", "Shift_R": "Shift_R",
    "Control_L": "Control_L", "Control_R": "Control_R",
    "Alt_L": "Alt_L", "Alt_R": "Alt_R",
    "Super_L": "Win", "Menu": "Menu",
    "space": "space",
    "minus": "-", "equal": "=", "bracketleft": "[", "bracketright": "]",
    "backslash": "\\", "semicolon": ";", "apostrophe": "'",
    "comma": ",", "period": ".", "slash": "/", "grave": "`",
    "F1": "F1", "F2": "F2", "F3": "F3", "F4": "F4", "F5": "F5", "F6": "F6",
    "F7": "F7", "F8": "F8", "F9": "F9", "F10": "F10", "F11": "F11", "F12": "F12",
}


class TestPage(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg"], corner_radius=0, **kwargs)
        self.navigate_callback = navigate_callback
        self._key_widgets = {}
        self._pressed_keys = set()
        self._key_counts = {}
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=0, height=52)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text="🔬 Ekipman Test Merkezi", font=FONTS["subtitle"],
                     text_color=COLORS["text"]).pack(side="left", padx=20, pady=14)

        tabs = ctk.CTkTabview(
            self,
            fg_color=COLORS["bg_secondary"],
            segmented_button_fg_color=COLORS["button"],
            segmented_button_selected_color=COLORS["highlight"],
            segmented_button_selected_hover_color=COLORS["highlight_hover"],
            segmented_button_unselected_color=COLORS["button"],
            segmented_button_unselected_hover_color=COLORS["accent"],
            text_color=COLORS["text"],
            border_color=COLORS["border"],
        )
        tabs.pack(fill="both", expand=True, padx=16, pady=10)

        tabs.add("⌨ Klavye Testi")
        tabs.add("🖱 Mouse Testi")
        tabs.add("🎧 Ses Testi")

        self._build_keyboard_tab(tabs.tab("⌨ Klavye Testi"))
        self._build_mouse_tab(tabs.tab("🖱 Mouse Testi"))
        self._build_audio_tab(tabs.tab("🎧 Ses Testi"))

    # klavye test
    def _build_keyboard_tab(self, parent):
        info = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=10)
        info.pack(fill="x", padx=16, pady=(12, 6))
        ctk.CTkLabel(info, text="⌨  Klavye Tuş Testi",
                     font=FONTS["heading"], text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=(10, 2))
        ctk.CTkLabel(
            info,
            text="Klavye simülasyonuna tıklayın → klavyenizden tuşlara basın. "
                 "Algılanan tuşlar yeşil yanar, bırakıldığında söner.",
            font=FONTS["body"], text_color=COLORS["text_secondary"],
            wraplength=860, justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 10))

        stat_row = ctk.CTkFrame(parent, fg_color="transparent")
        stat_row.pack(fill="x", padx=16, pady=(0, 8))

        self._total_var = ctk.StringVar(value="0")
        self._unique_var = ctk.StringVar(value="0")
        self._last_var  = ctk.StringVar(value="—")

        for label, var, color in [
            ("Toplam Basma",  self._total_var,  COLORS["highlight"]),
            ("Benzersiz Tuş", self._unique_var, "#43A047"),
            ("Son Tuş",       self._last_var,   "#FB8C00"),
        ]:
            card = ctk.CTkFrame(stat_row, fg_color=COLORS["bg_secondary"], corner_radius=10)
            card.pack(side="left", padx=5, pady=2)
            ctk.CTkLabel(card, textvariable=var, font=("Segoe UI", 20, "bold"),
                         text_color=color).pack(padx=20, pady=(8, 0))
            ctk.CTkLabel(card, text=label, font=FONTS["small"],
                         text_color=COLORS["accent"]).pack(padx=20, pady=(0, 8))

        # Görsel klavye
        kb_outer = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=14)
        kb_outer.pack(fill="x", padx=16, pady=(0, 8))
        ctk.CTkLabel(kb_outer, text="Aşağıdaki alana tıklayın ve tuşlara basmaya başlayın",
                     font=FONTS["small"], text_color=COLORS["accent"]).pack(pady=(10, 6))

        self._key_widgets = {}
        for row_keys in KEYBOARD_LAYOUT:
            row_frame = ctk.CTkFrame(kb_outer, fg_color="transparent")
            row_frame.pack(pady=2, padx=14)
            for key in row_keys:
                label = KEY_LABELS.get(key, key.upper() if len(key) == 1 else key)
                w = KEY_WIDTHS.get(key, 42)
                btn = ctk.CTkButton(
                    row_frame, text=label,
                    width=w, height=36, corner_radius=6,
                    fg_color=COLORS["button"], hover_color=COLORS["button"],
                    text_color=COLORS["text_secondary"], font=("Segoe UI", 10),
                    border_width=1, border_color=COLORS["border"], state="disabled",
                )
                btn.pack(side="left", padx=2)
                self._key_widgets[key] = btn

        # tuş tıklama (event yakalama)
        self._focus_entry = ctk.CTkEntry(
            kb_outer, width=1, height=1,
            fg_color=COLORS["bg_secondary"], border_width=0,
            text_color=COLORS["bg_secondary"],
        )
        self._focus_entry.pack()
        self._focus_entry.bind("<KeyPress>",   self._on_key_press)
        self._focus_entry.bind("<KeyRelease>", self._on_key_release)
        kb_outer.bind("<Button-1>", lambda e: self._focus_entry.focus_set())
        ctk.CTkFrame(kb_outer, height=8, fg_color="transparent").pack()

        # tuş geçmişi
        log_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=10)
        log_frame.pack(fill="x", padx=16, pady=(0, 4))
        top_log = ctk.CTkFrame(log_frame, fg_color="transparent")
        top_log.pack(fill="x", padx=12, pady=(8, 2))
        ctk.CTkLabel(top_log, text="Tuş Geçmişi", font=FONTS["body"],
                     text_color=COLORS["accent"]).pack(side="left")
        ctk.CTkButton(top_log, text="Temizle", font=FONTS["small"],
                      fg_color=COLORS["button"], hover_color=COLORS["accent"],
                      height=28, corner_radius=6,
                      command=self._clear_keyboard).pack(side="right")
        self._key_log = ctk.CTkTextbox(
            log_frame, font=("Consolas", 11),
            fg_color=COLORS["bg_card"], text_color=COLORS["text"],
            height=60, state="disabled",
        )
        self._key_log.pack(fill="x", padx=12, pady=(0, 10))

    def _resolve_key(self, event):
        sym = event.keysym
        if sym in KEYSYM_MAP:
            return KEYSYM_MAP[sym]
        ch = event.char
        if ch and ch.isalnum():
            return ch.lower()
        if sym and len(sym) == 1:
            return sym.lower()
        return sym

    def _on_key_press(self, event):
        key = self._resolve_key(event)
        if key in self._pressed_keys:
            return
        self._pressed_keys.add(key)
        self._key_counts[key] = self._key_counts.get(key, 0) + 1
        self._total_var.set(str(sum(self._key_counts.values())))
        self._unique_var.set(str(len(self._key_counts)))
        self._last_var.set(key)
        if key in self._key_widgets:
            self._key_widgets[key].configure(
                fg_color=COLORS["success"], text_color="white",
                border_color=COLORS["success"])
        self._key_log.configure(state="normal")
        self._key_log.insert("1.0", f"[{key}]  ")
        self._key_log.configure(state="disabled")

    def _on_key_release(self, event):
        key = self._resolve_key(event)
        self._pressed_keys.discard(key)
        if key in self._key_widgets:
            self._key_widgets[key].configure(
                fg_color=COLORS["highlight"], text_color="white",
                border_color=COLORS["highlight"])
            self.after(400, lambda k=key: self._reset_key_color(k))

    def _reset_key_color(self, key):
        if key not in self._pressed_keys and key in self._key_widgets:
            self._key_widgets[key].configure(
                fg_color=COLORS["button"], text_color=COLORS["text_secondary"],
                border_color=COLORS["border"])

    def _clear_keyboard(self):
        self._key_counts.clear()
        self._pressed_keys.clear()
        self._total_var.set("0")
        self._unique_var.set("0")
        self._last_var.set("—")
        for btn in self._key_widgets.values():
            btn.configure(fg_color=COLORS["button"], text_color=COLORS["text_secondary"],
                          border_color=COLORS["border"])
        self._key_log.configure(state="normal")
        self._key_log.delete("1.0", "end")
        self._key_log.configure(state="disabled")

    #  mouse test
    def _build_mouse_tab(self, parent):
        info = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=10)
        info.pack(fill="x", padx=16, pady=(12, 10))
        ctk.CTkLabel(info, text="🖱  Mouse Buton Testi",
                     font=FONTS["heading"], text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=(10, 2))
        ctk.CTkLabel(
            info,
            text="Sol, sağ ve orta tuşlara tıklayın. Tıklamalar algılanır ve sayılır.",
            font=FONTS["body"], text_color=COLORS["text_secondary"],
            wraplength=860, justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 10))

        self._mouse_counts = {"Sol Tık": 0, "Sağ Tık": 0, "Orta Tık": 0, "Çift Tık": 0}
        self._mouse_vars   = {}

        count_row  = ctk.CTkFrame(parent, fg_color="transparent")
        count_row.pack(fill="x", padx=16, pady=8)
        colors_map = {
            "Sol Tık": "#5C6BC0", "Sağ Tık": "#E53935",
            "Orta Tık": "#43A047", "Çift Tık": "#FB8C00",
        }
        for name, color in colors_map.items():
            card = ctk.CTkFrame(count_row, fg_color=COLORS["bg_secondary"], corner_radius=12)
            card.pack(side="left", fill="x", expand=True, padx=8)
            var = ctk.StringVar(value="0")
            self._mouse_vars[name] = var
            ctk.CTkLabel(card, textvariable=var, font=("Segoe UI", 42, "bold"),
                         text_color=color).pack(pady=(20, 4))
            ctk.CTkLabel(card, text=name, font=FONTS["heading"],
                         text_color=COLORS["text"]).pack(pady=(0, 20))

        click_area = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=14)
        click_area.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        ctk.CTkLabel(click_area, text="Bu alana mouse butonlarıyla tıklayın",
                     font=FONTS["body"], text_color=COLORS["accent"]).pack(pady=(16, 4))

        self._flash_label = ctk.CTkLabel(
            click_area, text="Tıklamayı Bekliyorum...",
            font=("Segoe UI", 26, "bold"), text_color=COLORS["button"])
        self._flash_label.pack(expand=True)

        self._flash_colors = colors_map
        for widget in (click_area, self._flash_label):
            widget.bind("<Button-1>",        lambda e: self._mouse_click("Sol Tık"))
            widget.bind("<Button-3>",        lambda e: self._mouse_click("Sağ Tık"))
            widget.bind("<Button-2>",        lambda e: self._mouse_click("Orta Tık"))
            widget.bind("<Double-Button-1>", lambda e: self._mouse_click("Çift Tık"))

        ctk.CTkButton(parent, text="🔄 Sıfırla", font=FONTS["body"],
                      fg_color=COLORS["button"], hover_color=COLORS["accent"],
                      height=34, corner_radius=8,
                      command=self._reset_mouse).pack(pady=(0, 12))

    def _mouse_click(self, btn_type):
        self._mouse_counts[btn_type] += 1
        self._mouse_vars[btn_type].set(str(self._mouse_counts[btn_type]))
        color = self._flash_colors.get(btn_type, COLORS["text"])
        self._flash_label.configure(
            text=f"✓  {btn_type}  ({self._mouse_counts[btn_type]})",
            text_color=color)
        self.after(400, lambda: self._flash_label.configure(
            text="Tıklamayı Bekliyorum...", text_color=COLORS["button"]))

    def _reset_mouse(self):
        for k in self._mouse_counts:
            self._mouse_counts[k] = 0
            self._mouse_vars[k].set("0")
        self._flash_label.configure(
            text="Tıklamayı Bekliyorum...", text_color=COLORS["button"])

    # ses test
    def _build_audio_tab(self, parent):
        info = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=10)
        info.pack(fill="x", padx=16, pady=(12, 10))
        ctk.CTkLabel(info, text="🎧  Kulaklık Kanal ve Frekans Testi",
                     font=FONTS["heading"], text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=(10, 2))
        ctk.CTkLabel(
            info,
            text="Sol / Sağ kanal testleri kulaklığın her iki tarafını ayrı ayrı kontrol eder. "
                 "Sesi duyamıyorsanız sistem ses seviyenizi kontrol edin.",
            font=FONTS["body"], text_color=COLORS["text_secondary"],
            wraplength=860, justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(parent, fg_color=COLORS["bg"],
                                         scrollbar_button_color=COLORS["button"])
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        # Frekans & ses seviyesi kontrolü
        freq_card = ctk.CTkFrame(scroll, fg_color=COLORS["bg_secondary"], corner_radius=12)
        freq_card.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(freq_card, text="Frekans ve Ses Seviyesi",
                     font=FONTS["heading"], text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(12, 4))

        ctrl_row = ctk.CTkFrame(freq_card, fg_color="transparent")
        ctrl_row.pack(fill="x", padx=16, pady=(0, 12))

        ctk.CTkLabel(ctrl_row, text="Frekans (Hz):", font=FONTS["body"],
                     text_color=COLORS["text"]).pack(side="left")
        self._freq_var = ctk.IntVar(value=440)
        ctk.CTkSlider(ctrl_row, from_=80, to=8000, variable=self._freq_var,
                      width=200, button_color=COLORS["highlight"],
                      progress_color=COLORS["highlight"]).pack(side="left", padx=10)
        self._freq_label = ctk.CTkLabel(ctrl_row, text="440 Hz", font=FONTS["body"],
                                         text_color=COLORS["accent"], width=70)
        self._freq_label.pack(side="left")
        self._freq_var.trace_add("write", lambda *_: self._freq_label.configure(
            text=f"{self._freq_var.get()} Hz"))

        ctk.CTkLabel(ctrl_row, text="  Ses:", font=FONTS["body"],
                     text_color=COLORS["text"]).pack(side="left", padx=(20, 0))
        self._vol_var = ctk.DoubleVar(value=0.7)
        ctk.CTkSlider(ctrl_row, from_=0.05, to=1.0, variable=self._vol_var,
                      width=150, button_color=COLORS["highlight"],
                      progress_color=COLORS["highlight"]).pack(side="left", padx=10)

        # ses test butonları
        tests = [
            ("🔵 Sol Kanal",    "Sol kanaldan ses gelmeli — sağ taraf sessiz",  "left",   "#3F51B5"),
            ("🔴 Sağ Kanal",    "Sağ kanaldan ses gelmeli — sol taraf sessiz",  "right",  "#E53935"),
            ("🟢 Her İki Kanal","Her iki kanaldan aynı anda ses gelmeli",        "both",   "#43A047"),
            ("🟠 Bass (80 Hz)", "Düşük frekanslı bas testi — her iki kanal",    "bass",   "#FB8C00"),
            ("🟣 Treble (6kHz)","Yüksek frekanslı tiz testi — her iki kanal",   "treble", "#9C27B0"),
        ]
        for btn_text, desc, test_type, btn_color in tests:
            card = ctk.CTkFrame(scroll, fg_color=COLORS["bg_secondary"], corner_radius=12)
            card.pack(fill="x", pady=4)
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=12)
            left_col = ctk.CTkFrame(row, fg_color="transparent")
            left_col.pack(side="left", fill="both", expand=True)
            ctk.CTkLabel(left_col, text=btn_text, font=FONTS["heading"],
                         text_color=COLORS["text"]).pack(anchor="w")
            ctk.CTkLabel(left_col, text=desc, font=FONTS["small"],
                         text_color=COLORS["accent"]).pack(anchor="w", pady=(2, 0))
            status_var = ctk.StringVar(value="⬜ Bekleniyor")
            ctk.CTkLabel(row, textvariable=status_var, font=FONTS["body"],
                         text_color=COLORS["text_secondary"], width=160).pack(side="right", padx=(10, 0))
            ctk.CTkButton(row, text="▶ Çal", font=FONTS["body"],
                          fg_color=btn_color, hover_color=COLORS["highlight_hover"],
                          height=38, corner_radius=8, width=90,
                          command=lambda tt=test_type, sv=status_var: self._play_channel(tt, sv)).pack(
                side="right", padx=6)

    def _play_channel(self, test_type, status_var):
        status_var.set("⏳ Çalınıyor...")
        threading.Thread(
            target=self._generate_and_play,
            args=(test_type, status_var),
            daemon=True,
        ).start()

    def _generate_and_play(self, test_type, status_var):
        try:
            sample_rate = 44100
            duration    = 2.0
            volume      = self._vol_var.get()

            freq_map = {"bass": 80, "treble": 6000}
            freq     = freq_map.get(test_type, self._freq_var.get())
            channel  = test_type if test_type in ("left", "right") else "both"

            samples  = self._build_stereo_wav(freq, duration, sample_rate, volume, channel)

            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp_path = tmp.name
            tmp.close()
            with wave.open(tmp_path, "w") as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(samples)

            played = False
            # 1) simpleaudio
            if not played:
                try:
                    import simpleaudio as sa
                    sa.WaveObject.from_wave_file(tmp_path).play().wait_done()
                    played = True
                except Exception:
                    pass
            # 2) playsound
            if not played:
                try:
                    import playsound
                    playsound.playsound(tmp_path, block=True)
                    played = True
                except Exception:
                    pass
            # 3) winsound (Windows)
            if not played:
                try:
                    import winsound
                    winsound.PlaySound(tmp_path, winsound.SND_FILENAME)
                    played = True
                except Exception:
                    pass
            # 4) aplay (Linux)
            if not played:
                try:
                    import subprocess
                    subprocess.run(["aplay", tmp_path], timeout=6, capture_output=True)
                    played = True
                except Exception:
                    pass
            # 5) os.startfile (son çare)
            if not played:
                try:
                    import time
                    os.startfile(tmp_path)
                    time.sleep(3)
                except Exception:
                    pass

            try:
                os.unlink(tmp_path)
            except Exception:
                pass

            self.after(0, lambda: status_var.set("✅ Tamamlandı"))
        except Exception as e:
            self.after(0, lambda: status_var.set(f"❌ {str(e)[:50]}"))

    @staticmethod
    def _build_stereo_wav(freq, duration, rate, volume, channel):
        n   = int(rate * duration)
        out = bytearray()
        for i in range(n):
            t    = i / rate
            fade = min(1.0, t / 0.05, (duration - t) / 0.05)
            val  = int(32767 * volume * fade * math.sin(2 * math.pi * freq * t))
            if channel == "left":
                out += struct.pack("<hh", val, 0)
            elif channel == "right":
                out += struct.pack("<hh", 0, val)
            else:
                out += struct.pack("<hh", val, val)
        return bytes(out)