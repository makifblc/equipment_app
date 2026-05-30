
import customtkinter as ctk
from config import COLORS, FONTS
import database as db

#anasayfa
class HomePage(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg"], corner_radius=0, **kwargs)
        self.navigate_callback = navigate_callback
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"], scrollbar_button_color=COLORS["bg"])
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        header = ctk.CTkFrame(scroll, fg_color=COLORS["bg_secondary"], corner_radius=16)
        header.pack(fill="x", padx=24, pady=(24, 8))

        ctk.CTkLabel(header, text="Gear Tech", font=("Segoe UI", 32, "bold"),
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

        #orta bar veri gösterme
        stats = db.get_stats()
        stat_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        stat_frame.pack(fill="x", padx=24, pady=8)
        stat_items = [
            ("📦", str(stats["total"]), "Toplam Ürün"),
            ("⌨", str(next((x["cnt"] for x in stats["by_category"] if x["name"] == "Klavye"), 0)), "Klavye"),
            ("🖱", str(next((x["cnt"] for x in stats["by_category"] if x["name"] == "Mouse"), 0)), "Mouse"),
            ("🎧", str(next((x["cnt"] for x in stats["by_category"] if x["name"] == "Kulaklık"), 0)), "Kulaklık"),
        ]
        for icon, val, label in stat_items:
            card = ctk.CTkFrame(stat_frame, fg_color=COLORS["bg_card"], corner_radius=12)
            card.pack(side="left", fill="x", expand=True, padx=6)
            ctk.CTkLabel(card, text=icon, font=("Segoe UI", 28)).pack(pady=(14, 2))
            ctk.CTkLabel(card, text=val, font=FONTS["title"], text_color="#5C6BC0").pack()
            ctk.CTkLabel(card, text=label, font=FONTS["small"], text_color=COLORS["accent"]).pack(pady=(0, 14))

        ctk.CTkLabel(scroll, text="Kategoriler", font=FONTS["subtitle"],
                     text_color=COLORS["text"]).pack(anchor="w", padx=32, pady=(20, 6))
        
        #katagoriler 
        cat_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        cat_frame.pack(fill="x", padx=24, pady=10)
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

