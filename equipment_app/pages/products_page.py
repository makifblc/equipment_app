
import customtkinter as ctk
import webbrowser
from config import COLORS, FONTS
import database as db


class ProductsPage(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg"], corner_radius=0, **kwargs)
        self.navigate_callback = navigate_callback
        self._selected_cat = None
        self._all_products = []
        self._filtered = []
        self._build()
        self.refresh()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=0, height=60)
        top.pack(fill="x")
        top.pack_propagate(False)

        ctk.CTkLabel(top, text="📦 Ürünler", font=FONTS["subtitle"],
                     text_color=COLORS["text"]).pack(side="left", padx=20, pady=14)

        search_frame = ctk.CTkFrame(top, fg_color=COLORS["bg_input"], corner_radius=8)
        search_frame.pack(side="left", padx=10, pady=12)
        ctk.CTkLabel(search_frame, text="🔍", font=("Segoe UI", 14)).pack(side="left", padx=(8, 2))
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._apply_filter())
        ctk.CTkEntry(search_frame, textvariable=self.search_var, placeholder_text="Ürün ara...",
                     fg_color="transparent", border_width=0, width=220,
                     text_color=COLORS["text"], font=FONTS["body"]).pack(side="left", padx=4, pady=6)

        body = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        body.pack(fill="both", expand=True)

        sidebar = ctk.CTkFrame(body, fg_color=COLORS["bg_secondary"], corner_radius=0, width=190)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="KATEGORİ", font=FONTS["small"],
                     text_color=COLORS["accent"]).pack(anchor="w", padx=16, pady=(18, 4))

        self._cat_buttons = {}
        btn_all = ctk.CTkButton(sidebar, text="🗂  Tümü", font=FONTS["body"],
                                 fg_color=COLORS["highlight"], hover_color=COLORS["highlight_hover"],
                                 anchor="w", corner_radius=8, height=38,
                                 command=lambda: self._set_category(None))
        btn_all.pack(fill="x", padx=10, pady=3)
        self._cat_buttons["all"] = btn_all

        try:
            cats = db.get_all_categories()
        except Exception:
            cats = []
        for cat in cats:
            icon = cat.get("icon", "")
            btn = ctk.CTkButton(sidebar, text=f"{icon}  {cat['name']}", font=FONTS["body"],
                                 fg_color="transparent", hover_color=COLORS["button"],
                                 text_color=COLORS["text_secondary"], anchor="w",
                                 corner_radius=8, height=38,
                                 command=lambda cid=cat["id"]: self._set_category(cid))
            btn.pack(fill="x", padx=10, pady=3)
            self._cat_buttons[cat["id"]] = btn

        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=10, pady=12)
        ctk.CTkLabel(sidebar, text="SIRALA", font=FONTS["small"],
                     text_color=COLORS["accent"]).pack(anchor="w", padx=16, pady=(0, 4))
        self.sort_var = ctk.StringVar(value="Puana Göre")
        ctk.CTkOptionMenu(sidebar, variable=self.sort_var,
                           values=["Puana Göre", "Fiyat (Artan)", "Fiyat (Azalan)", "İsme Göre"],
                           fg_color=COLORS["button"], button_color=COLORS["accent"],
                           text_color=COLORS["text"], font=FONTS["small"],
                           command=lambda _: self._apply_filter()).pack(fill="x", padx=10, pady=3)

        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=10, pady=12)
        ctk.CTkLabel(sidebar, text="Bütçe (₺)", font=FONTS["small"],
                     text_color=COLORS["accent"]).pack(anchor="w", padx=16, pady=(0, 4))
        self.budget_var = ctk.StringVar(value="Tümü")
        ctk.CTkOptionMenu(sidebar, variable=self.budget_var,
                           values=["Tümü", "0-1500", "1500-2500", "2500-4000", "4000+"],
                           fg_color=COLORS["button"], button_color=COLORS["accent"],
                           text_color=COLORS["text"], font=FONTS["small"],
                           command=lambda _: self._apply_filter()).pack(fill="x", padx=10, pady=3)

        self.prod_scroll = ctk.CTkScrollableFrame(body, fg_color=COLORS["bg"],
                                                   scrollbar_button_color=COLORS["button"])
        self.prod_scroll.pack(fill="both", expand=True, padx=0)
        for c in range(3):
            self.prod_scroll.columnconfigure(c, weight=1)

    def refresh(self):
        try:
            self._all_products = db.get_all_products()
        except Exception:
            self._all_products = []
        self._apply_filter()

    def _set_category(self, cat_id):
        self._selected_cat = cat_id
        for key, btn in self._cat_buttons.items():
            active = (key == "all" and cat_id is None) or (key == cat_id)
            btn.configure(fg_color=COLORS["highlight"] if active else "transparent",
                          text_color=COLORS["text"] if active else COLORS["text_secondary"])
        self._apply_filter()

    def _apply_filter(self):
        kw = self.search_var.get().lower()
        budget = self.budget_var.get()
        sort = self.sort_var.get()

        filtered = self._all_products
        if self._selected_cat is not None:
            filtered = [p for p in filtered if p["category_id"] == self._selected_cat]
        if kw:
            filtered = [p for p in filtered if
                        kw in p["name"].lower() or kw in (p["brand"] or "").lower()]
        if budget != "Tümü":
            lo, hi = {"0-1500": (0, 1500), "1500-2500": (1500, 2500),
                       "2500-4000": (2500, 4000), "4000+": (4000, 9999999)}.get(budget, (0, 9999999))
            filtered = [p for p in filtered if lo <= float(p["price"] or 0) <= hi]

        if sort == "Puana Göre":
            filtered = sorted(filtered, key=lambda x: float(x["rating"] or 0), reverse=True)
        elif sort == "Fiyat (Artan)":
            filtered = sorted(filtered, key=lambda x: float(x["price"] or 0))
        elif sort == "Fiyat (Azalan)":
            filtered = sorted(filtered, key=lambda x: float(x["price"] or 0), reverse=True)
        elif sort == "İsme Göre":
            filtered = sorted(filtered, key=lambda x: x["name"])

        self._filtered = filtered
        self._render_products()

    def _render_products(self):
        for w in self.prod_scroll.winfo_children():
            w.destroy()

        if not self._filtered:
            ctk.CTkLabel(self.prod_scroll, text="Ürün bulunamadı", font=FONTS["subtitle"],
                         text_color=COLORS["accent"]).grid(row=0, column=0, columnspan=3, pady=60)
            return

        for idx, p in enumerate(self._filtered):
            row, col = divmod(idx, 3)
            card = ctk.CTkFrame(self.prod_scroll, fg_color=COLORS["bg_secondary"],
                                corner_radius=14, cursor="hand2")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.prod_scroll.rowconfigure(row, weight=0)

            icon = p.get("category_icon", "📦")
            ctk.CTkLabel(card, text=icon, font=("Segoe UI", 44)).pack(pady=(16, 2))

            brand_lbl = ctk.CTkLabel(card, text=p.get("brand", ""), font=FONTS["small"],
                                      text_color=COLORS["accent"])
            brand_lbl.pack()

            name_lbl = ctk.CTkLabel(card, text=p["name"], font=FONTS["heading"],
                                     text_color=COLORS["text"], wraplength=220, justify="center")
            name_lbl.pack(padx=12, pady=(2, 4))

            ctk.CTkLabel(card, text=f"⭐ {p['rating']}", font=FONTS["small"],
                         text_color="#FFD700").pack()

            ctk.CTkLabel(card, text=f"₺{float(p['price']):,.0f}" if p['price'] else "—",
                         font=("Segoe UI", 18, "bold"), text_color="#5C6BC0").pack(pady=(4, 0))

            cat_name = p.get("category_name", "")
            ctk.CTkLabel(card, text=cat_name, font=FONTS["small"],
                         text_color=COLORS["button"]).pack()

            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.pack(pady=(8, 16))

            fav = db.is_favorite(p["id"])
            fav_btn = ctk.CTkButton(btn_row, text="❤" if fav else "🤍",
                                     fg_color=COLORS["button"], hover_color=COLORS["accent"],
                                     width=36, height=34, corner_radius=8, font=("Segoe UI", 16))
            fav_btn.configure(command=lambda pid=p["id"], b=fav_btn: self._toggle_fav(pid, b))
            fav_btn.pack(side="left", padx=4)

            ctk.CTkButton(btn_row, text="Detay", font=FONTS["small"],
                          fg_color=COLORS["highlight"], hover_color=COLORS["highlight_hover"],
                          height=34, corner_radius=8, width=80,
                          command=lambda pid=p["id"]: self.navigate_callback("detail", pid)).pack(side="left", padx=4)

            if p.get("purchase_link"):
                ctk.CTkButton(btn_row, text="🛒", font=("Segoe UI", 16),
                              fg_color=COLORS["button"], hover_color=COLORS["success"],
                              width=36, height=34, corner_radius=8,
                              command=lambda url=p["purchase_link"]: webbrowser.open(url)).pack(side="left", padx=4)

    def _toggle_fav(self, product_id, button):
        result = db.toggle_favorite(product_id)
        button.configure(text="❤" if result else "🤍")
