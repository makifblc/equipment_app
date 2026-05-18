
import customtkinter as ctk
import webbrowser
from config import COLORS, FONTS
import database as db

#ürüler detay ekranı
class DetailPage(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg"], corner_radius=0, **kwargs)
        self.navigate_callback = navigate_callback
        self._product_id = None
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=0, height=52)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkButton(top, text="← Geri", font=FONTS["body"],
                      fg_color="transparent", hover_color=COLORS["button"],
                      text_color=COLORS["text_secondary"], width=90,
                      command=lambda: self.navigate_callback("products")).pack(side="left", padx=16, pady=10)
        self.page_title = ctk.CTkLabel(top, text="Ürün Detayı", font=FONTS["subtitle"],
                                       text_color=COLORS["text"])
        self.page_title.pack(side="left", padx=8)

        self.content_scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"],
                                                      scrollbar_button_color=COLORS["button"])
        self.content_scroll.pack(fill="both", expand=True)

    def load_product(self, product_id):
        self._product_id = product_id
        for w in self.content_scroll.winfo_children():
            w.destroy()

        p = db.get_product_by_id(product_id)
        if not p:
            ctk.CTkLabel(self.content_scroll, text="Ürün bulunamadı",
                         font=FONTS["subtitle"], text_color=COLORS["accent"]).pack(pady=60)
            return

        self.page_title.configure(text=p["name"])
        specs = db.get_specifications(product_id)
        is_fav = db.is_favorite(product_id)
        ratings = db.get_user_ratings(product_id)

        header = ctk.CTkFrame(self.content_scroll, fg_color=COLORS["bg_secondary"], corner_radius=14)
        header.pack(fill="x", padx=24, pady=(20, 10))

        icon_col = ctk.CTkFrame(header, fg_color="transparent", width=200)
        icon_col.pack(side="left", padx=20, pady=20)
        icon_col.pack_propagate(False)
        cat_icon = p.get("category_icon", "📦") if "category_icon" in p else "📦"
        try:
            prods_with_icon = db.get_all_products()
            prod_icon_map = {x["id"]: x.get("category_icon", "📦") for x in prods_with_icon}
            cat_icon = prod_icon_map.get(product_id, "📦")
        except Exception:
            cat_icon = "📦"
        ctk.CTkLabel(icon_col, text=cat_icon, font=("Segoe UI", 72)).pack(pady=(20, 0))
        ctk.CTkLabel(icon_col, text=p.get("category_name", ""), font=FONTS["small"],
                     text_color=COLORS["accent"]).pack()

        info_col = ctk.CTkFrame(header, fg_color="transparent")
        info_col.pack(side="left", fill="both", expand=True, padx=(0, 20), pady=20)

        ctk.CTkLabel(info_col, text=p.get("brand", ""), font=FONTS["body"],
                     text_color=COLORS["accent"]).pack(anchor="w")
        ctk.CTkLabel(info_col, text=p["name"], font=("Segoe UI", 22, "bold"),
                     text_color=COLORS["text"], wraplength=500, justify="left").pack(anchor="w", pady=(2, 8))
        ctk.CTkLabel(info_col, text=f"⭐ {p['rating']}  ({len(ratings)} değerlendirme)",
                     font=FONTS["body"], text_color="#FFD700").pack(anchor="w")
        ctk.CTkLabel(info_col, text=f"₺{float(p['price']):,.0f}" if p['price'] else "—",
                     font=("Segoe UI", 28, "bold"), text_color="#5C6BC0").pack(anchor="w", pady=(8, 12))

        if p.get("description"):
            ctk.CTkLabel(info_col, text=p["description"], font=FONTS["body"],
                         text_color=COLORS["text_secondary"], wraplength=500, justify="left").pack(anchor="w")

        btn_row = ctk.CTkFrame(info_col, fg_color="transparent")
        btn_row.pack(anchor="w", pady=(16, 0))

        self._fav_btn = ctk.CTkButton(btn_row,
                                       text="❤ Favorilerden Çıkar" if is_fav else "🤍 Favorilere Ekle",
                                       fg_color=COLORS["button"], hover_color=COLORS["accent"],
                                       height=38, corner_radius=8, font=FONTS["body"],
                                       command=self._toggle_fav)
        self._fav_btn.pack(side="left", padx=(0, 10))

        if p.get("purchase_link"):
            ctk.CTkButton(btn_row, text="🛒 Satın Al",
                          fg_color=COLORS["highlight"], hover_color=COLORS["highlight_hover"],
                          height=38, corner_radius=8, font=FONTS["body"],
                          command=lambda: webbrowser.open(p["purchase_link"])).pack(side="left", padx=(0, 10))

        ctk.CTkButton(btn_row, text="⚖ Karşılaştırmaya Ekle",
                      fg_color=COLORS["button"], hover_color=COLORS["highlight"],
                      height=38, corner_radius=8, font=FONTS["body"],
                      command=lambda: self.navigate_callback("compare", product_id)).pack(side="left")

        body = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        body.pack(fill="x", padx=24, pady=10)

        spec_col = ctk.CTkFrame(body, fg_color=COLORS["bg_secondary"], corner_radius=12)
        spec_col.pack(side="left", fill="both", expand=True, padx=(0, 8))

        ctk.CTkLabel(spec_col, text="Teknik Özellikler", font=FONTS["heading"],
                     text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(14, 8))
        ctk.CTkFrame(spec_col, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=12, pady=(0, 8))

        if specs:
            for i, s in enumerate(specs):
                row_bg = COLORS["bg_card"] if i % 2 == 0 else COLORS["bg_secondary"]
                row = ctk.CTkFrame(spec_col, fg_color=row_bg, corner_radius=6)
                row.pack(fill="x", padx=12, pady=1)
                ctk.CTkLabel(row, text=s["spec_name"], font=FONTS["body"],
                             text_color=COLORS["text_secondary"], width=180, anchor="w").pack(side="left", padx=10, pady=6)
                val_text = s["spec_value"] + (f" {s['spec_unit']}" if s.get("spec_unit") else "")
                ctk.CTkLabel(row, text=val_text, font=FONTS["body"],
                             text_color=COLORS["text"], anchor="w").pack(side="left", padx=4)
        else:
            ctk.CTkLabel(spec_col, text="Teknik özellik girilmemiş",
                         font=FONTS["body"], text_color=COLORS["accent"]).pack(pady=20)
        ctk.CTkFrame(spec_col, height=12, fg_color="transparent").pack()

        right_col = ctk.CTkFrame(body, fg_color="transparent", width=340)
        right_col.pack(side="left", fill="y", padx=(8, 0))
        right_col.pack_propagate(False)

        rating_card = ctk.CTkFrame(right_col, fg_color=COLORS["bg_secondary"], corner_radius=12)
        rating_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(rating_card, text="Değerlendirme Ekle", font=FONTS["heading"],
                     text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(14, 6))
        ctk.CTkFrame(rating_card, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=12, pady=(0, 8))

        self._star_var = ctk.IntVar(value=5)
        star_row = ctk.CTkFrame(rating_card, fg_color="transparent")
        star_row.pack(padx=16)
        ctk.CTkLabel(star_row, text="Puan:", font=FONTS["body"], text_color=COLORS["text"]).pack(side="left")
        self._star_btns = []
        for i in range(1, 6):
            b = ctk.CTkButton(star_row, text="★", width=28, height=28,
                              fg_color="transparent", text_color="#FFD700",
                              hover_color=COLORS["button"], font=("Segoe UI", 18),
                              command=lambda v=i: self._set_star(v))
            b.pack(side="left", padx=1)
            self._star_btns.append(b)

        self._comment_entry = ctk.CTkEntry(rating_card, placeholder_text="Yorum yazın (isteğe bağlı)...",
                                            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
                                            text_color=COLORS["text"], font=FONTS["body"], height=50)
        self._comment_entry.pack(fill="x", padx=12, pady=8)

        ctk.CTkButton(rating_card, text="Değerlendirmeyi Gönder",
                      fg_color=COLORS["highlight"], hover_color=COLORS["highlight_hover"],
                      font=FONTS["body"], height=36, corner_radius=8,
                      command=self._submit_rating).pack(fill="x", padx=12, pady=(0, 14))

        if ratings:
            ctk.CTkLabel(right_col, text=f"Kullanıcı Yorumları ({len(ratings)})", font=FONTS["heading"],
                         text_color=COLORS["text"]).pack(anchor="w", pady=(10, 4))
            for r in ratings[:5]:
                rcard = ctk.CTkFrame(right_col, fg_color=COLORS["bg_secondary"], corner_radius=10)
                rcard.pack(fill="x", pady=3)
                stars = "★" * int(r["rating"]) + "☆" * (5 - int(r["rating"]))
                ctk.CTkLabel(rcard, text=stars, font=("Segoe UI", 13),
                             text_color="#FFD700").pack(anchor="w", padx=12, pady=(8, 0))
                if r.get("comment"):
                    ctk.CTkLabel(rcard, text=r["comment"], font=FONTS["small"],
                                 text_color=COLORS["text_secondary"], wraplength=280,
                                 justify="left").pack(anchor="w", padx=12, pady=(2, 8))

    def _toggle_fav(self):
        if not self._product_id:
            return
        result = db.toggle_favorite(self._product_id)
        self._fav_btn.configure(
            text="❤ Favorilerden Çıkar" if result else "🤍 Favorilere Ekle"
        )

    def _set_star(self, value):
        self._star_var.set(value)
        for i, b in enumerate(self._star_btns):
            b.configure(text_color="#FFD700" if i < value else COLORS["accent"])

    def _submit_rating(self):
        if not self._product_id:
            return
        rating = self._star_var.get()
        comment = self._comment_entry.get().strip()
        db.add_user_rating(self._product_id, rating, comment)
        self._comment_entry.delete(0, "end")
        self.load_product(self._product_id)
