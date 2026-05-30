import customtkinter as ctk
import webbrowser
import os
from PIL import Image

from config import COLORS, FONTS
import database as db


# favori ekranı
class FavoritesPage(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback, **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["bg"],
            corner_radius=0,
            **kwargs
        )

        self.navigate_callback = navigate_callback

        self._build()

    def _build(self):
        top = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_secondary"],
            corner_radius=0,
            height=52
        )
        top.pack(fill="x")
        top.pack_propagate(False)

        ctk.CTkLabel(
            top,
            text="Favori Ürünler",
            font=FONTS["subtitle"],
            text_color=COLORS["text"]
        ).pack(side="left", padx=20, pady=14)

        ctk.CTkButton(
            top,
            text="Yenile",
            font=FONTS["body"],
            fg_color=COLORS["button"],
            hover_color=COLORS["accent"],
            height=34,
            corner_radius=8,
            command=self.refresh
        ).pack(side="right", padx=16, pady=9)

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["button"]
        )
        self.scroll.pack(fill="both", expand=True, padx=0)

        for c in range(3):
            self.scroll.columnconfigure(c, weight=1)

        self.refresh()

    def _load_product_image(self, product_id, size=(100, 100)):
        """
        Ürün ID'sine göre pics klasöründen resmi yükler.
        """

        base_dir = os.path.dirname(os.path.abspath(__file__))
        pics_dir = os.path.join(base_dir, '..', 'pics')

        img_filename = f"k{product_id}.jpg"
        img_path = os.path.join(pics_dir, img_filename)

        if os.path.exists(img_path):
            try:
                return ctk.CTkImage(
                    light_image=Image.open(img_path),
                    size=size
                )
            except Exception:
                return None

        return None

    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        try:
            favs = db.get_favorites()
        except Exception:
            favs = []

        if not favs:
            empty_frame = ctk.CTkFrame(
                self.scroll,
                fg_color="transparent"
            )

            empty_frame.grid(
                row=0,
                column=0,
                columnspan=3,
                pady=80
            )

            ctk.CTkLabel(
                empty_frame,
                text="Henüz favoriniz yok",
                font=FONTS["subtitle"],
                text_color=COLORS["accent"]
            ).pack(pady=8)

            ctk.CTkLabel(
                empty_frame,
                text="Ürün detayında ❤ ikonuna basarak favorilere ekleyin",
                font=FONTS["body"],
                text_color=COLORS["button"]
            ).pack()

            ctk.CTkButton(
                empty_frame,
                text="Ürünlere Git",
                font=FONTS["body"],
                fg_color=COLORS["highlight"],
                hover_color=COLORS["highlight_hover"],
                height=38,
                corner_radius=8,
                command=lambda: self.navigate_callback("products")
            ).pack(pady=16)

            return

        for idx, p in enumerate(favs):
            row, col = divmod(idx, 3)

            card = ctk.CTkFrame(
                self.scroll,
                fg_color=COLORS["bg_secondary"],
                corner_radius=14
            )

            card.grid(
                row=row,
                column=col,
                padx=10,
                pady=10,
                sticky="nsew"
            )

            # RESİM
            img = self._load_product_image(
                p["id"],
                size=(100, 100)
            )

            if img:
                img_label = ctk.CTkLabel(
                    card,
                    image=img,
                    text=""
                )

                img_label.image = img
                img_label.pack(pady=(16, 2))

            else:
                icon = p.get("category_icon", "📦")

                ctk.CTkLabel(
                    card,
                    text=icon,
                    font=("Segoe UI", 44)
                ).pack(pady=(16, 2))

            # MARKA
            ctk.CTkLabel(
                card,
                text=p.get("brand", ""),
                font=FONTS["small"],
                text_color=COLORS["accent"]
            ).pack()

            # ÜRÜN ADI
            ctk.CTkLabel(
                card,
                text=p["name"],
                font=FONTS["heading"],
                text_color=COLORS["text"],
                wraplength=220,
                justify="center"
            ).pack(padx=12, pady=(2, 4))

            # PUAN
            ctk.CTkLabel(
                card,
                text=f"⭐ {p['rating']}",
                font=FONTS["small"],
                text_color="#FFD700"
            ).pack()

            # FİYAT
            ctk.CTkLabel(
                card,
                text=f"₺{float(p['price']):,.0f}" if p['price'] else "—",
                font=("Segoe UI", 18, "bold"),
                text_color="#5C6BC0"
            ).pack(pady=(4, 0))

            # BUTONLAR
            btn_row = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )

            btn_row.pack(pady=(8, 16))

            ctk.CTkButton(
                btn_row,
                text="❌",
                font=("Segoe UI", 14),
                fg_color=COLORS["button"],
                hover_color=COLORS["error"],
                width=36,
                height=34,
                corner_radius=8,
                command=lambda pid=p["id"]: self._remove_favorite(pid)
            ).pack(side="left", padx=4)

            ctk.CTkButton(
                btn_row,
                text="Detay",
                font=FONTS["small"],
                fg_color=COLORS["highlight"],
                hover_color=COLORS["highlight_hover"],
                height=34,
                corner_radius=8,
                width=80,
                command=lambda pid=p["id"]: self.navigate_callback("detail", pid)
            ).pack(side="left", padx=4)

            if p.get("purchase_link"):
                ctk.CTkButton(
                    btn_row,
                    text="🛒",
                    font=("Segoe UI", 16),
                    fg_color=COLORS["button"],
                    hover_color=COLORS["success"],
                    width=36,
                    height=34,
                    corner_radius=8,
                    command=lambda url=p["purchase_link"]: webbrowser.open(url)
                ).pack(side="left", padx=4)

    def _remove_favorite(self, product_id):
        db.toggle_favorite(product_id)
        self.refresh()