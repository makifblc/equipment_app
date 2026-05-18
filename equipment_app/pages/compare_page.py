
import customtkinter as ctk
import webbrowser
from config import COLORS, FONTS
import database as db

#karşılaştırma sayfası
class ComparePage(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg"], corner_radius=0, **kwargs)
        self.navigate_callback = navigate_callback
        self._prod_a = None
        self._prod_b = None
        self._all_products = []
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=0, height=52)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text="⚖ Ürün Karşılaştırma", font=FONTS["subtitle"],
                     text_color=COLORS["text"]).pack(side="left", padx=20, pady=14)
        ctk.CTkButton(top, text="🔄 Temizle", font=FONTS["body"],
                      fg_color=COLORS["button"], hover_color=COLORS["accent"],
                      height=34, corner_radius=8, command=self._clear).pack(side="right", padx=16, pady=9)

        sel_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=0)
        sel_frame.pack(fill="x", padx=0, pady=(1, 0))

        for side in ["a", "b"]:
            f = ctk.CTkFrame(sel_frame, fg_color="transparent")
            f.pack(side="left", fill="x", expand=True, padx=20, pady=10)
            ctk.CTkLabel(f, text=f"Ürün {'1' if side=='a' else '2'}", font=FONTS["body"],
                         text_color=COLORS["accent"]).pack(side="left", padx=(0, 10))
            var = ctk.StringVar(value="Seçiniz...")
            opt = ctk.CTkOptionMenu(f, variable=var, values=["Seçiniz..."],
                                    fg_color=COLORS["button"], button_color=COLORS["accent"],
                                    text_color=COLORS["text"], font=FONTS["body"], width=320,
                                    command=lambda val, s=side: self._select_product(val, s))
            opt.pack(side="left")
            setattr(self, f"_var_{side}", var)
            setattr(self, f"_opt_{side}", opt)

        self.compare_scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"],
                                                      scrollbar_button_color=COLORS["button"])
        self.compare_scroll.pack(fill="both", expand=True)
        self.compare_scroll.columnconfigure(0, weight=1)
        self.compare_scroll.columnconfigure(1, weight=0)
        self.compare_scroll.columnconfigure(2, weight=1)

        self._refresh_product_list()
        self._render_placeholder()

    def _refresh_product_list(self):
        try:
            self._all_products = db.get_all_products()
        except Exception:
            self._all_products = []
        names = ["Seçiniz..."] + [f"{p.get('category_icon','')}{p['brand']} - {p['name']}" for p in self._all_products]
        self._opt_a.configure(values=names)
        self._opt_b.configure(values=names)

    def preselect_product(self, product_id):
        self._refresh_product_list()
        prod = next((p for p in self._all_products if p["id"] == product_id), None)
        if prod:
            val = f"{prod.get('category_icon','')}{prod['brand']} - {prod['name']}"
            self._var_a.set(val)
            self._select_product(val, "a")

    def _select_product(self, value, side):
        if value == "Seçiniz...":
            if side == "a":
                self._prod_a = None
            else:
                self._prod_b = None
        else:
            prod = next((p for p in self._all_products
                         if f"{p.get('category_icon','')}{p['brand']} - {p['name']}" == value), None)
            if side == "a":
                self._prod_a = prod
            else:
                self._prod_b = prod
        self._render_compare()

    def _clear(self):
        self._prod_a = None
        self._prod_b = None
        self._var_a.set("Seçiniz...")
        self._var_b.set("Seçiniz...")
        self._render_placeholder()

    def _render_placeholder(self):
        for w in self.compare_scroll.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.compare_scroll,
                     text="⚖ İki ürün seçerek karşılaştırın",
                     font=FONTS["subtitle"], text_color=COLORS["accent"]).pack(pady=80)
        ctk.CTkLabel(self.compare_scroll,
                     text="Yukarıdaki menülerden iki ürün seçin",
                     font=FONTS["body"], text_color=COLORS["button"]).pack()

    def _render_compare(self):
        for w in self.compare_scroll.winfo_children():
            w.destroy()

        if not self._prod_a and not self._prod_b:
            self._render_placeholder()
            return

        cols_frame = ctk.CTkFrame(self.compare_scroll, fg_color="transparent")
        cols_frame.pack(fill="both", expand=True, padx=16, pady=16)

        for col_idx, (prod, side_label) in enumerate([(self._prod_a, "Ürün 1"), (self._prod_b, "Ürün 2")]):
            col_frame = ctk.CTkFrame(cols_frame, fg_color=COLORS["bg_secondary"], corner_radius=14)
            if col_idx == 0:
                col_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))
            else:
                col_frame.pack(side="right", fill="both", expand=True, padx=(6, 0))

            if prod is None:
                ctk.CTkLabel(col_frame, text=f"{side_label}\nSeçilmedi",
                             font=FONTS["subtitle"], text_color=COLORS["accent"],
                             justify="center").pack(expand=True, pady=60)
                continue

            icon = prod.get("category_icon", "📦")
            ctk.CTkLabel(col_frame, text=icon, font=("Segoe UI", 60)).pack(pady=(20, 4))
            ctk.CTkLabel(col_frame, text=prod.get("brand", ""), font=FONTS["body"],
                         text_color=COLORS["accent"]).pack()
            ctk.CTkLabel(col_frame, text=prod["name"], font=FONTS["heading"],
                         text_color=COLORS["text"], wraplength=280, justify="center").pack(padx=12, pady=(2, 4))
            ctk.CTkLabel(col_frame, text=f"⭐ {prod['rating']}", font=FONTS["body"],
                         text_color="#FFD700").pack()
            ctk.CTkLabel(col_frame, text=f"₺{float(prod['price']):,.0f}" if prod['price'] else "—",
                         font=("Segoe UI", 22, "bold"), text_color="#5C6BC0").pack(pady=(4, 8))

            btn_row = ctk.CTkFrame(col_frame, fg_color="transparent")
            btn_row.pack(pady=(0, 12))
            ctk.CTkButton(btn_row, text="Detay", font=FONTS["small"],
                          fg_color=COLORS["highlight"], hover_color=COLORS["highlight_hover"],
                          height=32, corner_radius=8,
                          command=lambda pid=prod["id"]: self.navigate_callback("detail", pid)).pack(side="left", padx=4)
            if prod.get("purchase_link"):
                ctk.CTkButton(btn_row, text="🛒 Al", font=FONTS["small"],
                              fg_color=COLORS["button"], hover_color=COLORS["success"],
                              height=32, corner_radius=8,
                              command=lambda url=prod["purchase_link"]: webbrowser.open(url)).pack(side="left", padx=4)

            ctk.CTkFrame(col_frame, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=12, pady=4)
            ctk.CTkLabel(col_frame, text="Teknik Özellikler", font=FONTS["heading"],
                         text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(4, 8))

            specs = db.get_specifications(prod["id"])
            for i, s in enumerate(specs):
                row_bg = COLORS["bg_card"] if i % 2 == 0 else COLORS["bg_secondary"]
                row = ctk.CTkFrame(col_frame, fg_color=row_bg, corner_radius=6)
                row.pack(fill="x", padx=12, pady=1)
                ctk.CTkLabel(row, text=s["spec_name"], font=FONTS["small"],
                             text_color=COLORS["accent"], width=140, anchor="w").pack(side="left", padx=8, pady=5)
                val_text = s["spec_value"] + (f" {s['spec_unit']}" if s.get("spec_unit") else "")
                ctk.CTkLabel(row, text=val_text, font=FONTS["small"],
                             text_color=COLORS["text"], anchor="w").pack(side="left", padx=4)

            ctk.CTkFrame(col_frame, height=12, fg_color="transparent").pack()

        if self._prod_a and self._prod_b:
            verdict = ctk.CTkFrame(self.compare_scroll, fg_color=COLORS["bg_secondary"], corner_radius=14)
            verdict.pack(fill="x", padx=16, pady=(10, 16))
            ctk.CTkLabel(verdict, text="⚖ Karşılaştırma Özeti", font=FONTS["heading"],
                         text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(12, 6))

            pa, pb = self._prod_a, self._prod_b
            price_a = float(pa["price"] or 0)
            price_b = float(pb["price"] or 0)
            rating_a = float(pa["rating"] or 0)
            rating_b = float(pb["rating"] or 0)

            comparisons = [
                ("💰 Fiyat", f"₺{price_a:,.0f}", f"₺{price_b:,.0f}", "lower" if price_a < price_b else ("higher" if price_a > price_b else "equal")),
                ("⭐ Puan", str(rating_a), str(rating_b), "higher" if rating_a > rating_b else ("lower" if rating_a < rating_b else "equal")),
            ]

            tbl = ctk.CTkFrame(verdict, fg_color="transparent")
            tbl.pack(fill="x", padx=16, pady=(0, 12))
            for label, val_a, val_b, winner in comparisons:
                row = ctk.CTkFrame(tbl, fg_color=COLORS["bg_card"], corner_radius=6)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=label, font=FONTS["body"], text_color=COLORS["accent"], width=130, anchor="w").pack(side="left", padx=10, pady=6)
                color_a = COLORS["success"] if winner == "lower" else (COLORS["error"] if winner == "higher" else COLORS["text"])
                color_b = COLORS["success"] if winner == "higher" else (COLORS["error"] if winner == "lower" else COLORS["text"])
                ctk.CTkLabel(row, text=val_a, font=FONTS["body"], text_color=color_a, width=130, anchor="center").pack(side="left", padx=4, pady=6)
                ctk.CTkLabel(row, text="vs", font=FONTS["small"], text_color=COLORS["accent"]).pack(side="left")
                ctk.CTkLabel(row, text=val_b, font=FONTS["body"], text_color=color_b, width=130, anchor="center").pack(side="left", padx=4, pady=6)

            score_a = rating_a * 10 - (price_a / 1000)
            score_b = rating_b * 10 - (price_b / 1000)
            if score_a > score_b:
                winner_name = pa["name"]
                winner_reason = "Daha yüksek puan/fiyat dengesi"
            elif score_b > score_a:
                winner_name = pb["name"]
                winner_reason = "Daha yüksek puan/fiyat dengesi"
            else:
                winner_name = "Eşit"
                winner_reason = "Her iki ürün dengeli"

            rec_frame = ctk.CTkFrame(verdict, fg_color=COLORS["highlight"], corner_radius=10)
            rec_frame.pack(fill="x", padx=16, pady=(0, 14))
            ctk.CTkLabel(rec_frame, text=f"💡 Öneri: {winner_name}", font=FONTS["heading"],
                         text_color="white").pack(anchor="w", padx=16, pady=(10, 2))
            ctk.CTkLabel(rec_frame, text=winner_reason, font=FONTS["body"],
                         text_color="#D0D0FF").pack(anchor="w", padx=16, pady=(0, 10))
