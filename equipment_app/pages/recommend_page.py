
import customtkinter as ctk
import webbrowser
from config import COLORS, FONTS
import database as db


class RecommendPage(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg"], corner_radius=0, **kwargs)
        self.navigate_callback = navigate_callback
        self._answers = {}
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=0, height=52)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text="💡 Akıllı Ekipman Önerisi", font=FONTS["subtitle"],
                     text_color=COLORS["text"]).pack(side="left", padx=20, pady=14)

        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"],
                                                   scrollbar_button_color=COLORS["button"])
        self.main_scroll.pack(fill="both", expand=True)
        self._render_form()
#pencere öneri ekranı
    def _render_form(self):
        for w in self.main_scroll.winfo_children():
            w.destroy()

        header = ctk.CTkFrame(self.main_scroll, fg_color=COLORS["bg_secondary"], corner_radius=14)
        header.pack(fill="x", padx=24, pady=(20, 8))
        ctk.CTkLabel(header, text="💡", font=("Segoe UI", 48)).pack(pady=(20, 4))
        ctk.CTkLabel(header, text="Size En Uygun Ekipmanı Bulalım",
                     font=FONTS["title"], text_color=COLORS["text"]).pack()
        ctk.CTkLabel(header, text="Birkaç soruyu yanıtlayarak size özel öneri alın",
                     font=FONTS["body"], text_color=COLORS["accent"]).pack(pady=(4, 20))

        questions = [
            {
                "key": "category",
                "question": "🔍 Hangi ekipman için öneri istiyorsunuz?",
                "type": "choice",
                "options": ["Klavye", "Mouse", "Kulaklık", "Hepsi"],
                "default": "Hepsi"
            },
            {
                "key": "usage",
                "question": "🎯 Temel kullanım amacınız nedir?",
                "type": "choice",
                "options": ["Oyun (Gaming)", "Ofis/İş", "Müzik/Ses", "Programlama", "Genel Kullanım"],
                "default": "Genel Kullanım"
            },
            {
                "key": "budget",
                "question": "💰 Bütçeniz nedir? (₺)",
                "type": "choice",
                "options": ["0 - 1500", "1500 - 2500", "2500 - 3500", "3500+"],
                "default": "1500 - 2500"
            },
            {
                "key": "wireless",
                "question": "📶 Kablosuz tercih eder misiniz?",
                "type": "choice",
                "options": ["Evet, kablosuz olsun", "Hayır, kablolu olsun", "Fark etmez"],
                "default": "Fark etmez"
            },
            {
                "key": "rgb",
                "question": "💡 RGB aydınlatma önemli mi?",
                "type": "choice",
                "options": ["Evet, RGB olmalı", "Hayır, gerek yok", "Fark etmez"],
                "default": "Fark etmez"
            },
            {
                "key": "priority",
                "question": "🏆 En çok önem verdiğiniz özellik?",
                "type": "choice",
                "options": ["Performans", "Konfor/Ergonomi", "Fiyat/Performans", "Ses Kalitesi", "Dayanıklılık"],
                "default": "Fiyat/Performans"
            },
        ]

        self._vars = {}
        for q in questions:
            qframe = ctk.CTkFrame(self.main_scroll, fg_color=COLORS["bg_secondary"], corner_radius=12)
            qframe.pack(fill="x", padx=24, pady=5)
            ctk.CTkLabel(qframe, text=q["question"], font=FONTS["heading"],
                         text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(14, 8))
            var = ctk.StringVar(value=q["default"])
            self._vars[q["key"]] = var
            opt_row = ctk.CTkFrame(qframe, fg_color="transparent")
            opt_row.pack(fill="x", padx=12, pady=(0, 14))
            for opt in q["options"]:
                rb = ctk.CTkRadioButton(opt_row, text=opt, variable=var, value=opt,
                                         font=FONTS["body"], text_color=COLORS["text"],
                                         fg_color=COLORS["highlight"],
                                         hover_color=COLORS["highlight_hover"],
                                         border_color=COLORS["accent"])
                rb.pack(side="left", padx=12)

        ctk.CTkButton(self.main_scroll, text="💡 Öneri Al",
                      font=("Segoe UI", 14, "bold"),
                      fg_color=COLORS["highlight"], hover_color=COLORS["highlight_hover"],
                      height=50, corner_radius=12,
                      command=self._run_algorithm).pack(fill="x", padx=24, pady=(10, 24))

#öneri algoritması
    def _run_algorithm(self):
        answers = {k: v.get() for k, v in self._vars.items()}
        try:
            all_prods = db.get_all_products()
        except Exception:
            all_prods = []

        category_filter = answers.get("category", "Hepsi")
        cat_map = {"Klavye": "Klavye", "Mouse": "Mouse", "Kulaklık": "Kulaklık"}

        if category_filter != "Hepsi":
            cat_name = cat_map.get(category_filter, category_filter)
            candidates = [p for p in all_prods if p.get("category_name") == cat_name]
        else:
            candidates = list(all_prods)

        budget_ranges = {
            "0 - 1500": (0, 1500),
            "1500 - 2500": (1500, 2500),
            "2500 - 3500": (2500, 3500),
            "3500+": (3500, 999999),
        }
        blo, bhi = budget_ranges.get(answers.get("budget", "1500 - 2500"), (0, 999999))
        candidates = [p for p in candidates if blo <= float(p.get("price") or 0) <= bhi]

        scored = []
        for p in candidates:
            score = 0.0
            rating = float(p.get("rating") or 0)
            price = float(p.get("price") or 1)
            name_lower = p["name"].lower()
            brand_lower = (p.get("brand") or "").lower()
            desc_lower = (p.get("description") or "").lower()
            combined = name_lower + " " + brand_lower + " " + desc_lower

            score += rating * 15
#öneri soruları
            usage = answers.get("usage", "")
            if usage == "Oyun (Gaming)":
                gaming_kw = ["gaming", "game", "pro", "rgb", "wireless", "hz", "dpi", "mechanical", "mekanik"]
                score += sum(6 for kw in gaming_kw if kw in combined)
            elif usage == "Ofis/İş":
                office_kw = ["office", "silent", "quiet", "wireless", "ergonomic", "ergonomik", "plug", "compact"]
                score += sum(5 for kw in office_kw if kw in combined)
            elif usage == "Müzik/Ses":
                audio_kw = ["hi-fi", "audio", "anc", "noise", "spatial", "atmos", "thx", "titanium", "frequency"]
                score += sum(6 for kw in audio_kw if kw in combined)
            elif usage == "Programlama":
                prog_kw = ["tkl", "compact", "mechanical", "mekanik", "silent", "ergonomik"]
                score += sum(5 for kw in prog_kw if kw in combined)

            wireless_pref = answers.get("wireless", "Fark etmez")
            is_wireless = any(kw in combined for kw in ["wireless", "kablosuz", "lightspeed", "2.4ghz", "bluetooth"])
            if wireless_pref == "Evet, kablosuz olsun":
                score += 20 if is_wireless else -10
            elif wireless_pref == "Hayır, kablolu olsun":
                score += 20 if not is_wireless else -10

            rgb_pref = answers.get("rgb", "Fark etmez")
            has_rgb = any(kw in combined for kw in ["rgb", "chroma", "lightsync", "aura"])
            if rgb_pref == "Evet, RGB olmalı":
                score += 15 if has_rgb else -5
            elif rgb_pref == "Hayır, gerek yok":
                score += 10 if not has_rgb else 0

            priority = answers.get("priority", "Fiyat/Performans")
            if priority == "Performans":
                score += rating * 8
            elif priority == "Fiyat/Performans":
                ratio = rating / (price / 1000) if price > 0 else 0
                score += ratio * 5
            elif priority == "Konfor/Ergonomi":
                comfort_kw = ["ergonomik", "ergonomic", "foam", "memory", "kumaş", "yumuşak", "hafif"]
                score += sum(8 for kw in comfort_kw if kw in combined)
            elif priority == "Ses Kalitesi":
                audio_kw = ["hi-fi", "titanium", "spatial", "atmos", "thx", "anc", "frequency", "driver"]
                score += sum(8 for kw in audio_kw if kw in combined)
            elif priority == "Dayanıklılık":
                durability_kw = ["braided", "aluminum", "metal", "aircraft"]
                score += sum(6 for kw in durability_kw if kw in combined)

            scored.append((score, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        self._show_results(scored[:5], answers)
#sonuc gösterme
    def _show_results(self, scored, answers):
        for w in self.main_scroll.winfo_children():
            w.destroy()

        header = ctk.CTkFrame(self.main_scroll, fg_color=COLORS["highlight"], corner_radius=14)
        header.pack(fill="x", padx=24, pady=(20, 8))
        ctk.CTkLabel(header, text="✨ Size Özel Öneriler Hazır!", font=FONTS["title"],
                     text_color="white").pack(pady=(20, 4))
        ctk.CTkLabel(header, text=f"Kullanım: {answers.get('usage', '—')}  |  Bütçe: {answers.get('budget', '—')} ₺  |  Öncelik: {answers.get('priority', '—')}",
                     font=FONTS["body"], text_color="#D0D0FF").pack(pady=(0, 16))

        ctk.CTkButton(self.main_scroll, text="← Tekrar Dene", font=FONTS["body"],
                      fg_color=COLORS["button"], hover_color=COLORS["accent"],
                      height=36, corner_radius=8, width=160,
                      command=self._render_form).pack(anchor="w", padx=24, pady=(8, 0))

        if not scored:
            ctk.CTkLabel(self.main_scroll,
                         text="Seçtiğiniz kriterlere uygun ürün bulunamadı.\nBütçeyi veya kategoriyi değiştirmeyi deneyin.",
                         font=FONTS["subtitle"], text_color=COLORS["accent"],
                         justify="center").pack(pady=60)
            return

        ctk.CTkLabel(self.main_scroll, text="🏆 En İyi Öneriler", font=FONTS["subtitle"],
                     text_color=COLORS["text"]).pack(anchor="w", padx=28, pady=(14, 6))

        for rank, (score, p) in enumerate(scored):
            card = ctk.CTkFrame(self.main_scroll, fg_color=COLORS["bg_secondary"], corner_radius=14)
            card.pack(fill="x", padx=24, pady=5)

            rank_colors = {0: "#FFD700", 1: "#C0C0C0", 2: "#CD7F32"}
            rank_icons = {0: "🥇", 1: "🥈", 2: "🥉"}
            rank_icon = rank_icons.get(rank, f"#{rank+1}")
            rank_color = rank_colors.get(rank, COLORS["text"])

            left = ctk.CTkFrame(card, fg_color="transparent", width=80)
            left.pack(side="left", fill="y", padx=(16, 0), pady=16)
            left.pack_propagate(False)
            ctk.CTkLabel(left, text=rank_icon, font=("Segoe UI", 36)).pack()
            ctk.CTkLabel(left, text=f"{score:.0f}p", font=FONTS["small"],
                         text_color=rank_color).pack()

            ctk.CTkFrame(card, width=1, fg_color=COLORS["border"]).pack(side="left", fill="y", pady=16, padx=10)

            icon = p.get("category_icon", "📦")
            ctk.CTkLabel(card, text=icon, font=("Segoe UI", 44)).pack(side="left", padx=8, pady=16)

            info_col = ctk.CTkFrame(card, fg_color="transparent")
            info_col.pack(side="left", fill="both", expand=True, pady=16)

            ctk.CTkLabel(info_col, text=p.get("brand", ""), font=FONTS["small"],
                         text_color=COLORS["accent"]).pack(anchor="w")
            ctk.CTkLabel(info_col, text=p["name"], font=FONTS["heading"],
                         text_color=COLORS["text"], wraplength=380, justify="left").pack(anchor="w")
            ctk.CTkLabel(info_col, text=p.get("description", "")[:100] + "..." if len(p.get("description","")) > 100 else p.get("description",""),
                         font=FONTS["small"], text_color=COLORS["text_secondary"],
                         wraplength=380, justify="left").pack(anchor="w", pady=(2, 6))

            match_tags = self._get_match_tags(p, answers)
            if match_tags:
                tag_row = ctk.CTkFrame(info_col, fg_color="transparent")
                tag_row.pack(anchor="w")
                for tag in match_tags[:4]:
                    ctk.CTkLabel(tag_row, text=tag, font=FONTS["small"],
                                 fg_color=COLORS["highlight"], corner_radius=6,
                                 text_color="white").pack(side="left", padx=3)

            right_col = ctk.CTkFrame(card, fg_color="transparent", width=160)
            right_col.pack(side="right", fill="y", padx=16, pady=16)
            right_col.pack_propagate(False)
            ctk.CTkLabel(right_col, text=f"₺{float(p['price']):,.0f}" if p['price'] else "—",
                         font=("Segoe UI", 20, "bold"), text_color="#5C6BC0").pack()
            ctk.CTkLabel(right_col, text=f"⭐ {p['rating']}", font=FONTS["body"],
                         text_color="#FFD700").pack(pady=(2, 10))
            ctk.CTkButton(right_col, text="Detaylar", font=FONTS["small"],
                          fg_color=COLORS["highlight"], hover_color=COLORS["highlight_hover"],
                          height=32, corner_radius=8,
                          command=lambda pid=p["id"]: self.navigate_callback("detail", pid)).pack(fill="x", pady=2)
            if p.get("purchase_link"):
                ctk.CTkButton(right_col, text="🛒 Satın Al", font=FONTS["small"],
                              fg_color=COLORS["button"], hover_color=COLORS["success"],
                              height=32, corner_radius=8,
                              command=lambda url=p["purchase_link"]: webbrowser.open(url)).pack(fill="x", pady=2)

    def _get_match_tags(self, p, answers):
        tags = []
        combined = (p["name"] + " " + (p.get("brand") or "") + " " + (p.get("description") or "")).lower()
        usage = answers.get("usage", "")
        wireless_pref = answers.get("wireless", "Fark etmez")

        if usage == "Oyun (Gaming)":
            tags.append("✓ Gaming")
        elif usage == "Ofis/İş":
            tags.append("✓ Ofis")
        elif usage == "Müzik/Ses":
            tags.append("✓ Ses")

        if wireless_pref == "Evet, kablosuz olsun" and any(kw in combined for kw in ["wireless", "lightspeed", "2.4ghz"]):
            tags.append("✓ Kablosuz")
        if any(kw in combined for kw in ["rgb", "chroma", "lightsync"]):
            tags.append("✓ RGB")

        priority = answers.get("priority", "")
        if priority == "Fiyat/Performans":
            tags.append("✓ Değerli")
        elif priority == "Performans":
            tags.append("✓ Yüksek Performans")

        return tags
