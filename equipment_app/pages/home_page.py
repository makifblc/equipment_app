
import customtkinter as ctk
from config import COLORS, FONTS
import database as db


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg"], corner_radius=0, **kwargs)
        self.navigate_callback = navigate_callback
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"], scrollbar_button_color=COLORS["button"])
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        header = ctk.CTkFrame(scroll, fg_color=COLORS["bg_secondary"], corner_radius=16)
        header.pack(fill="x", padx=24, pady=(24, 8))

        ctk.CTkLabel(header, text="⚡ Gear Tech", font=("Segoe UI", 32, "bold"),
                     text_color="#E0E0E0").pack(pady=(24, 4))
        ctk.CTkLabel(header, text="Bilgisayar Ekipmanlarını Keşfet, Karşılaştır ve Test Et",
                     font=FONTS["subtitle"], text_color=COLORS["text_secondary"]).pack()
        ctk.CTkLabel(header, text="Klavye · Mouse · Kulaklık",
                     font=FONTS["body"], text_color=COLORS["accent"]).pack(pady=(0, 24))

        btn_row = ctk.CTkFrame(header, fg_color="transparent")
        btn_row.pack(pady=(0, 24))
        for label, page in [("📦 Ürünleri İncele", "products"),
                             ("⚖ Karşılaştır", "compare"),
                             ("💡 Öneri Al", "recommend")]:
            ctk.CTkButton(btn_row, text=label, font=FONTS["button"],
                          fg_color=COLORS["highlight"], hover_color=COLORS["highlight_hover"],
                          height=42, corner_radius=10, width=180,
                          command=lambda p=page: self.navigate_callback(p)).pack(side="left", padx=8)

        stats = db.get_stats()
        stat_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        stat_frame.pack(fill="x", padx=24, pady=8)
        stat_items = [
            ("📦", str(stats["total"]), "Toplam Ürün"),
            ("⌨", str(next((x["cnt"] for x in stats["by_category"] if x["name"] == "Klavye"), 0)), "Klavye"),
            ("🖱", str(next((x["cnt"] for x in stats["by_category"] if x["name"] == "Mouse"), 0)), "Mouse"),
            ("🎧", str(next((x["cnt"] for x in stats["by_category"] if x["name"] == "Kulaklık"), 0)), "Kulaklık"),
            ("💰", f"₺{stats['prices']['avg_price']:.0f}" if stats['prices']['avg_price'] else "—", "Ort. Fiyat"),
        ]
        for icon, val, label in stat_items:
            card = ctk.CTkFrame(stat_frame, fg_color=COLORS["bg_card"], corner_radius=12)
            card.pack(side="left", fill="x", expand=True, padx=6)
            ctk.CTkLabel(card, text=icon, font=("Segoe UI", 28)).pack(pady=(14, 2))
            ctk.CTkLabel(card, text=val, font=FONTS["title"], text_color="#5C6BC0").pack()
            ctk.CTkLabel(card, text=label, font=FONTS["small"], text_color=COLORS["accent"]).pack(pady=(0, 14))

        ctk.CTkLabel(scroll, text="Kategoriler", font=FONTS["subtitle"],
                     text_color=COLORS["text"]).pack(anchor="w", padx=32, pady=(20, 6))

        cat_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        cat_frame.pack(fill="x", padx=24, pady=4)
        categories_info = [
            ("⌨", "Klavye", "Mekanik ve membran seçenekleri\nGaming ve ofis modelleri", "products", 1),
            ("🖱", "Mouse", "Yüksek DPI gaming fareler\nKablosuz ve kablolu seçenekler", "products", 2),
            ("🎧", "Kulaklık", "Surround ses, ANC teknolojisi\nKablosuz konfor", "products", 3),
        ]
        for icon, name, desc, page, cat_id in categories_info:
            card = ctk.CTkFrame(cat_frame, fg_color=COLORS["bg_secondary"], corner_radius=14,
                                cursor="hand2")
            card.pack(side="left", fill="both", expand=True, padx=8, pady=4)
            ctk.CTkLabel(card, text=icon, font=("Segoe UI", 48)).pack(pady=(20, 4))
            ctk.CTkLabel(card, text=name, font=FONTS["heading"], text_color=COLORS["text"]).pack()
            ctk.CTkLabel(card, text=desc, font=FONTS["small"], text_color=COLORS["accent"],
                         justify="center").pack(pady=(4, 8))
            ctk.CTkButton(card, text=f"{name} İncele", font=FONTS["small"],
                          fg_color=COLORS["button"], hover_color=COLORS["highlight"],
                          height=34, corner_radius=8,
                          command=lambda p=page: self.navigate_callback(p)).pack(pady=(0, 20))

        ctk.CTkLabel(scroll, text="Özellikler", font=FONTS["subtitle"],
                     text_color=COLORS["text"]).pack(anchor="w", padx=32, pady=(20, 6))
        feat_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        feat_frame.pack(fill="x", padx=24, pady=4)
        features = [
            ("🔬", "Ekipman Testi", "Klavye tuş, mouse buton\nve ses testleri yapın", "test"),
            ("⚖", "Karşılaştırma", "İki ürünü yan yana\ndetaylı karşılaştırın", "compare"),
            ("💡", "Akıllı Öneri", "Bütçe ve kullanım alışkanlığınıza\ngöre en iyi ekipmanı bulun", "recommend"),
            ("❤", "Favoriler", "Beğendiğiniz ürünleri\nfavorilere ekleyin", "favorites"),
        ]
        for icon, title, desc, page in features:
            card = ctk.CTkFrame(feat_frame, fg_color=COLORS["bg_card"], corner_radius=12)
            card.pack(side="left", fill="both", expand=True, padx=6, pady=4)
            ctk.CTkLabel(card, text=icon, font=("Segoe UI", 32)).pack(pady=(18, 4))
            ctk.CTkLabel(card, text=title, font=FONTS["heading"], text_color=COLORS["text"]).pack()
            ctk.CTkLabel(card, text=desc, font=FONTS["small"], text_color=COLORS["accent"],
                         justify="center").pack(pady=(2, 8))
            ctk.CTkButton(card, text="Git →", font=FONTS["small"],
                          fg_color=COLORS["highlight"], hover_color=COLORS["highlight_hover"],
                          height=30, corner_radius=8, width=90,
                          command=lambda p=page: self.navigate_callback(p)).pack(pady=(0, 18))

        ctk.CTkLabel(scroll, text="En Yüksek Puanlı Ürünler", font=FONTS["subtitle"],
                     text_color=COLORS["text"]).pack(anchor="w", padx=32, pady=(20, 6))

        top_frame = ctk.CTkScrollableFrame(scroll, fg_color="transparent", height=180,
                                           orientation="horizontal",
                                           scrollbar_button_color=COLORS["button"])
        top_frame.pack(fill="x", padx=24, pady=(0, 24))
        try:
            all_prods = db.get_all_products()
            top_prods = sorted(all_prods, key=lambda x: float(x["rating"] or 0), reverse=True)[:8]
            for p in top_prods:
                card = ctk.CTkFrame(top_frame, fg_color=COLORS["bg_secondary"], corner_radius=12, width=200)
                card.pack(side="left", padx=6, pady=4)
                card.pack_propagate(False)
                ctk.CTkLabel(card, text=p.get("category_icon", "📦"), font=("Segoe UI", 30)).pack(pady=(14, 2))
                ctk.CTkLabel(card, text=p["brand"], font=FONTS["small"],
                             text_color=COLORS["accent"]).pack()
                ctk.CTkLabel(card, text=p["name"], font=FONTS["body"],
                             text_color=COLORS["text"], wraplength=170, justify="center").pack(padx=8)
                ctk.CTkLabel(card, text=f"⭐ {p['rating']}", font=FONTS["small"],
                             text_color="#FFD700").pack()
                ctk.CTkLabel(card, text=f"₺{p['price']:,.0f}" if p['price'] else "—",
                             font=FONTS["heading"], text_color="#5C6BC0").pack(pady=(0, 14))
        except Exception:
            pass
