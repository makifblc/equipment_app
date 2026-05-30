import customtkinter as ctk
import webbrowser
from config import COLORS, FONTS
import database as db


class RecommendPage(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg"], corner_radius=0, **kwargs)
        self.navigate_callback = navigate_callback
        self._vars = {}
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], height=52, corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)

        ctk.CTkLabel(
            top,
            text="Akıllı Ekipman Önerisi",
            font=FONTS["subtitle"],
            text_color=COLORS["text"]
        ).pack(side="left", padx=20, pady=14)

        self.main_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["button"]
        )
        self.main_scroll.pack(fill="both", expand=True)

        self._render_form()

    # ---------------- FORM ----------------
    def _render_form(self):
        for w in self.main_scroll.winfo_children():
            w.destroy()

        header = ctk.CTkFrame(self.main_scroll, fg_color=COLORS["bg_secondary"], corner_radius=14)
        header.pack(fill="x", padx=24, pady=(20, 10))

        ctk.CTkLabel(header, text="Size En Uygun Ekipmanı Bulalım",
                     font=FONTS["title"], text_color=COLORS["text"]).pack()

        ctk.CTkLabel(header, text="Birkaç soruyu yanıtlayarak öneri alın",
                     font=FONTS["body"], text_color=COLORS["accent"]).pack(pady=(4, 16))

        questions = [
            ("category", "Hangi ekipman?", ["Klavye", "Mouse", "Kulaklık", "Hepsi"], "Hepsi"),
            ("usage", "Kullanım amacı?", ["Oyun (Gaming)", "Ofis/İş", "Müzik/Ses", "Programlama", "Genel Kullanım"], "Genel Kullanım"),
            ("budget", "Bütçe?", ["0 - 1500", "1500 - 2500", "2500 - 3500", "3500+"], "1500 - 2500"),
            ("wireless", "Kablosuz?", ["Evet, kablosuz olsun", "Hayır, kablolu olsun", "Fark etmez"], "Fark etmez"),
            ("rgb", "RGB?", ["Evet, RGB olmalı", "Hayır, gerek yok", "Fark etmez"], "Fark etmez"),
            ("priority", "Öncelik?", ["Performans", "Konfor/Ergonomi", "Fiyat/Performans", "Ses Kalitesi", "Dayanıklılık"], "Fiyat/Performans"),
        ]

        self._vars = {}

        for key, q, opts, default in questions:
            frame = ctk.CTkFrame(self.main_scroll, fg_color=COLORS["bg_secondary"], corner_radius=12)
            frame.pack(fill="x", padx=24, pady=6)

            ctk.CTkLabel(frame, text=q, font=FONTS["heading"], text_color=COLORS["text"]).pack(
                anchor="w", padx=16, pady=(12, 6)
            )

            var = ctk.StringVar(value=default)
            self._vars[key] = var

            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=(0, 12))

            for opt in opts:
                ctk.CTkRadioButton(
                    row,
                    text=opt,
                    variable=var,
                    value=opt,
                    font=FONTS["body"],
                    fg_color=COLORS["highlight"],
                    hover_color=COLORS["highlight_hover"],
                    text_color=COLORS["text"]
                ).pack(side="left", padx=10)

        ctk.CTkButton(
            self.main_scroll,
            text="Öneri Al",
            font=("Segoe UI", 14, "bold"),
            fg_color=COLORS["highlight"],
            hover_color=COLORS["highlight_hover"],
            height=45,
            command=self._run_algorithm
        ).pack(fill="x", padx=24, pady=20)

    # ---------------- ALGORITHM ----------------
    def _run_algorithm(self):
        answers = {k: v.get() for k, v in self._vars.items()}

        try:
            products = db.get_all_products()
        except:
            products = []

        # filtre
        if answers["category"] != "Hepsi":
            products = [p for p in products if p.get("category_name") == answers["category"]]

        # budget
        budget_map = {
            "0 - 1500": (0, 1500),
            "1500 - 2500": (1500, 2500),
            "2500 - 3500": (2500, 3500),
            "3500+": (3500, 999999),
        }

        bmin, bmax = budget_map.get(answers["budget"], (0, 999999))
        products = [
            p for p in products
            if bmin <= float(p.get("price") or 0) <= bmax
        ]

        scored = []

        for p in products:
            score = float(p.get("rating") or 0) * 10

            text = f"{p.get('name','')} {p.get('brand','')} {p.get('description','')}".lower()

            if "rgb" in text and answers["rgb"].startswith("Evet"):
                score += 10

            if "wireless" in text or "bluetooth" in text:
                if "Evet" in answers["wireless"]:
                    score += 15

            scored.append((score, p))

        scored.sort(reverse=True, key=lambda x: x[0])
        self._show_results(scored[:5], answers)

    # ---------------- RESULTS ----------------
    def _show_results(self, scored, answers):
        for w in self.main_scroll.winfo_children():
            w.destroy()

        header = ctk.CTkFrame(self.main_scroll, fg_color=COLORS["highlight"], corner_radius=14)
        header.pack(fill="x", padx=24, pady=16)

        ctk.CTkLabel(header, text="Size Özel Öneriler",
                     font=FONTS["title"], text_color="white").pack(pady=10)

        ctk.CTkLabel(
            header,
            text=f"{answers['usage']} | {answers['budget']} | {answers['priority']}",
            font=FONTS["body"],
            text_color="#E0E0FF"
        ).pack(pady=(0, 10))

        # TEKRAR DENE (SABİT)
        ctk.CTkButton(
            self.main_scroll,
            text="← Tekrar Dene",
            font=FONTS["body"],
            fg_color=COLORS["button"],
            command=self._render_form
        ).pack(anchor="w", padx=24, pady=10)

        if not scored:
            ctk.CTkLabel(
                self.main_scroll,
                text="Uygun ürün bulunamadı",
                font=FONTS["subtitle"],
                text_color=COLORS["accent"]
            ).pack(pady=50)
            return

        for i, (score, p) in enumerate(scored):
            card = ctk.CTkFrame(self.main_scroll, fg_color=COLORS["bg_secondary"], corner_radius=14)
            card.pack(fill="x", padx=24, pady=6)

            icon = p.get("category_icon") or "📦"

            ctk.CTkLabel(card, text=icon, font=("Segoe UI", 28)).pack(side="left", padx=10)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(info, text=p.get("name", ""),
                         font=FONTS["heading"], text_color=COLORS["text"]).pack(anchor="w")

            ctk.CTkLabel(info, text=f"₺{p.get('price','?')} | ⭐ {p.get('rating','?')}",
                         font=FONTS["body"], text_color=COLORS["accent"]).pack(anchor="w")

            right = ctk.CTkFrame(card, fg_color="transparent")
            right.pack(side="right", padx=10)

            ctk.CTkButton(
                right,
                text="Detay",
                command=lambda pid=p["id"]: self.navigate_callback("detail", pid)
            ).pack(pady=5)

            if p.get("purchase_link"):
                ctk.CTkButton(
                    right,
                    text="Satın Al",
                    fg_color=COLORS["success"],
                    command=lambda url=p["purchase_link"]: webbrowser.open(url)
                ).pack()