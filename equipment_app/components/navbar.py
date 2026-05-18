
import customtkinter as ctk
from config import COLORS, FONTS


class Navbar(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_secondary"], corner_radius=0, height=60, **kwargs)
        self.navigate_callback = navigate_callback
        self.pack_propagate(False)
        self._active_btn = None
        self._buttons = {}
        self._build()

    def _build(self):
        logo = ctk.CTkLabel(
            self, text="⚡ GearTECH",
            font=("Segoe UI", 18, "bold"),
            text_color="#E0E0E0"
        )
        logo.pack(side="left", padx=20)

        sep = ctk.CTkFrame(self, width=1, fg_color=COLORS["border"])
        sep.pack(side="left", fill="y", pady=10, padx=5)

        nav_items = [
            ("🏠  Ana Sayfa", "home"),
            ("📦  Ürünler", "products"),
            ("⚖  Karşılaştır", "compare"),
            ("🔬  Test Et", "test"),
            ("💡  Öneri Al", "recommend"),
            ("❤  Favoriler", "favorites"),
            ("⚙  Yönet", "manage"),
        ]

        for label, page in nav_items:
            btn = ctk.CTkButton(
                self, text=label,
                font=FONTS["body"],
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["button"],
                corner_radius=8,
                height=36,
                command=lambda p=page: self.navigate_callback(p)
            )
            btn.pack(side="left", padx=3, pady=10)
            self._buttons[page] = btn

    def set_active(self, page):
        if self._active_btn:
            self._active_btn.configure(
                fg_color="transparent",
                text_color=COLORS["text_secondary"]
            )
        btn = self._buttons.get(page)
        if btn:
            btn.configure(fg_color=COLORS["highlight"], text_color=COLORS["text"])
            self._active_btn = btn
