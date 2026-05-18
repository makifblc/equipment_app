
import customtkinter as ctk
from config import COLORS, FONTS
import database as db

#yönetme ekranı başlangıç
class ManagePage(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg"], corner_radius=0, **kwargs)
        self.navigate_callback = navigate_callback
        self._selected_product = None
        self._all_products = []
        self._build()
#yönet-navbar
    def _build(self):
        top = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=0, height=52)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text="⚙ Ürün Yönetimi", font=FONTS["subtitle"],
                     text_color=COLORS["text"]).pack(side="left", padx=20, pady=14)
        ctk.CTkButton(top, text="➕ Yeni Ürün", font=FONTS["body"],
                      fg_color=COLORS["highlight"], hover_color=COLORS["highlight_hover"],
                      height=34, corner_radius=8,
                      command=self._new_product_form).pack(side="right", padx=8, pady=9)
        ctk.CTkButton(top, text="🔄 Yenile", font=FONTS["body"],
                      fg_color=COLORS["button"], hover_color=COLORS["accent"],
                      height=34, corner_radius=8,
                      command=self._refresh_list).pack(side="right", padx=4, pady=9)

        body = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        body.pack(fill="both", expand=True)

        list_panel = ctk.CTkFrame(body, fg_color=COLORS["bg_secondary"], corner_radius=0, width=360)
        list_panel.pack(side="left", fill="y")
        list_panel.pack_propagate(False)

        ctk.CTkLabel(list_panel, text="Ürün Listesi", font=FONTS["heading"],
                     text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=(14, 4))

        search_frame = ctk.CTkFrame(list_panel, fg_color=COLORS["bg_input"], corner_radius=8)
        search_frame.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(search_frame, text="🔍", font=("Segoe UI", 12)).pack(side="left", padx=(8, 2))
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter_list())
        ctk.CTkEntry(search_frame, textvariable=self._search_var,
                     placeholder_text="Ara...", fg_color="transparent",
                     border_width=0, text_color=COLORS["text"],
                     font=FONTS["body"]).pack(side="left", padx=4, pady=6)

        self._prod_list_scroll = ctk.CTkScrollableFrame(list_panel, fg_color=COLORS["bg_secondary"],
                                                         scrollbar_button_color=COLORS["button"])
        self._prod_list_scroll.pack(fill="both", expand=True, padx=4, pady=4)

        self.form_panel = ctk.CTkScrollableFrame(body, fg_color=COLORS["bg"],
                                                  scrollbar_button_color=COLORS["button"])
        self.form_panel.pack(fill="both", expand=True)

        self._refresh_list()
        self._show_placeholder()

    def _refresh_list(self):
        try:
            self._all_products = db.get_all_products()
        except Exception:
            self._all_products = []
        self._filter_list()

    def _filter_list(self):
        kw = self._search_var.get().lower()
        for w in self._prod_list_scroll.winfo_children():
            w.destroy()
        filtered = [p for p in self._all_products
                    if kw in p["name"].lower() or kw in (p.get("brand") or "").lower()] if kw else self._all_products
        for p in filtered:
            icon = p.get("category_icon", "📦")
            btn = ctk.CTkButton(
                self._prod_list_scroll,
                text=f"{icon} {p['brand']} - {p['name']}",
                font=FONTS["small"],
                fg_color="transparent",
                hover_color=COLORS["button"],
                text_color=COLORS["text"],
                anchor="w",
                corner_radius=6,
                height=36,
                command=lambda pid=p["id"]: self._select_product(pid)
            )
            btn.pack(fill="x", padx=4, pady=2)

    def _select_product(self, product_id):
        self._selected_product = product_id
        self._edit_product_form(product_id)

    def _show_placeholder(self):
        for w in self.form_panel.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.form_panel,
                     text="← Bir ürün seçin veya\nYeni Ürün ekleyin",
                     font=FONTS["subtitle"], text_color=COLORS["accent"],
                     justify="center").pack(pady=80)

    def _new_product_form(self):
        self._selected_product = None
        for w in self.form_panel.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.form_panel, text="➕ Yeni Ürün Ekle", font=FONTS["subtitle"],
                     text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(20, 4))

        try:
            cats = db.get_all_categories()
        except Exception:
            cats = []
        cat_names = [c["name"] for c in cats]
        cat_ids = {c["name"]: c["id"] for c in cats}

        fields = self._make_form(self.form_panel, cat_names)

        def _save():
            try:
                cat_id = cat_ids.get(fields["category"].get(), 1)
                pid = db.add_product(
                    category_id=cat_id,
                    name=fields["name"].get().strip(),
                    brand=fields["brand"].get().strip(),
                    price=float(fields["price"].get() or 0),
                    purchase_link=fields["link"].get().strip(),
                    description=fields["desc"].get("1.0", "end").strip(),
                    rating=float(fields["rating"].get() or 0)
                )
                self._show_feedback("✅ Ürün başarıyla eklendi!", "success")
                self._refresh_list()
                self._edit_product_form(pid)
            except Exception as e:
                self._show_feedback(f"❌ Hata: {e}", "error")

        ctk.CTkButton(self.form_panel, text="💾 Ürünü Kaydet",
                      fg_color=COLORS["highlight"], hover_color=COLORS["highlight_hover"],
                      height=44, corner_radius=10, font=FONTS["button"],
                      command=_save).pack(fill="x", padx=20, pady=(8, 4))
        self._feedback_var = ctk.StringVar()
        ctk.CTkLabel(self.form_panel, textvariable=self._feedback_var, font=FONTS["body"],
                     text_color=COLORS["success"]).pack(pady=4)

    def _edit_product_form(self, product_id):
        for w in self.form_panel.winfo_children():
            w.destroy()

        p = db.get_product_by_id(product_id)
        if not p:
            self._show_placeholder()
            return
        specs = db.get_specifications(product_id)

        ctk.CTkLabel(self.form_panel, text=f"✏ Düzenle: {p['name']}", font=FONTS["subtitle"],
                     text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(20, 4))

        try:
            cats = db.get_all_categories()
        except Exception:
            cats = []
        cat_names = [c["name"] for c in cats]
        cat_ids = {c["name"]: c["id"] for c in cats}
        cat_by_id = {c["id"]: c["name"] for c in cats}

        fields = self._make_form(self.form_panel, cat_names, prefill={
            "category": cat_by_id.get(p["category_id"], cat_names[0] if cat_names else ""),
            "name": p["name"],
            "brand": p.get("brand", ""),
            "price": str(p.get("price", "")),
            "link": p.get("purchase_link", ""),
            "desc": p.get("description", ""),
            "rating": str(p.get("rating", "")),
        })

        def _update():
            try:
                db.update_product(
                    product_id=product_id,
                    name=fields["name"].get().strip(),
                    brand=fields["brand"].get().strip(),
                    price=float(fields["price"].get() or 0),
                    purchase_link=fields["link"].get().strip(),
                    description=fields["desc"].get("1.0", "end").strip(),
                    rating=float(fields["rating"].get() or 0)
                )
                self._show_feedback("✅ Güncellendi!", "success")
                self._refresh_list()
            except Exception as e:
                self._show_feedback(f"❌ Hata: {e}", "error")

        def _delete():
            if ctk.CTkInputDialog(text=f"'{p['name']}' silinecek. Emin misiniz?\n'EVET' yazın:", title="Silme Onayı").get_input() == "EVET":
                db.delete_product(product_id)
                self._refresh_list()
                self._show_placeholder()

        btn_row = ctk.CTkFrame(self.form_panel, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(8, 4))
        ctk.CTkButton(btn_row, text="💾 Güncelle",
                      fg_color=COLORS["highlight"], hover_color=COLORS["highlight_hover"],
                      height=40, corner_radius=8, font=FONTS["button"],
                      command=_update).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="🗑 Sil",
                      fg_color=COLORS["error"], hover_color="#C62828",
                      height=40, corner_radius=8, font=FONTS["button"],
                      command=_delete).pack(side="left")

        self._feedback_label = ctk.CTkLabel(self.form_panel, text="", font=FONTS["body"],
                                             text_color=COLORS["success"])
        self._feedback_label.pack(pady=2)

        ctk.CTkFrame(self.form_panel, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=20, pady=12)
        ctk.CTkLabel(self.form_panel, text="🔧 Teknik Özellikler", font=FONTS["heading"],
                     text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(0, 8))

        spec_frame = ctk.CTkFrame(self.form_panel, fg_color=COLORS["bg_secondary"], corner_radius=10)
        spec_frame.pack(fill="x", padx=20, pady=(0, 8))

        for s in specs:
            sr = ctk.CTkFrame(spec_frame, fg_color=COLORS["bg_card"], corner_radius=6)
            sr.pack(fill="x", padx=10, pady=3)
            name_var = ctk.StringVar(value=s["spec_name"])
            val_var = ctk.StringVar(value=s["spec_value"])
            unit_var = ctk.StringVar(value=s.get("spec_unit", ""))
            ctk.CTkEntry(sr, textvariable=name_var, fg_color=COLORS["bg_input"],
                         text_color=COLORS["text"], border_width=0, width=160,
                         font=FONTS["small"]).pack(side="left", padx=4, pady=4)
            ctk.CTkEntry(sr, textvariable=val_var, fg_color=COLORS["bg_input"],
                         text_color=COLORS["text"], border_width=0, width=200,
                         font=FONTS["small"]).pack(side="left", padx=4)
            ctk.CTkEntry(sr, textvariable=unit_var, fg_color=COLORS["bg_input"],
                         text_color=COLORS["text"], border_width=0, width=70,
                         font=FONTS["small"], placeholder_text="birim").pack(side="left", padx=4)

            def _update_spec(sid=s["id"], nv=name_var, vv=val_var, uv=unit_var):
                db.update_specification(sid, nv.get(), vv.get(), uv.get())
            def _del_spec(sid=s["id"]):
                db.delete_specification(sid)
                self._edit_product_form(product_id)

            ctk.CTkButton(sr, text="💾", width=30, height=28, fg_color=COLORS["button"],
                          hover_color=COLORS["highlight"], font=("Segoe UI", 12),
                          command=_update_spec).pack(side="left", padx=2)
            ctk.CTkButton(sr, text="🗑", width=30, height=28, fg_color=COLORS["button"],
                          hover_color=COLORS["error"], font=("Segoe UI", 12),
                          command=_del_spec).pack(side="left", padx=2)

        add_spec_frame = ctk.CTkFrame(self.form_panel, fg_color=COLORS["bg_secondary"], corner_radius=10)
        add_spec_frame.pack(fill="x", padx=20, pady=(4, 16))
        ctk.CTkLabel(add_spec_frame, text="Yeni Özellik Ekle:", font=FONTS["body"],
                     text_color=COLORS["accent"]).pack(anchor="w", padx=12, pady=(10, 4))
        nr = ctk.CTkFrame(add_spec_frame, fg_color="transparent")
        nr.pack(fill="x", padx=12, pady=(0, 10))
        new_name = ctk.CTkEntry(nr, placeholder_text="Özellik adı", fg_color=COLORS["bg_input"],
                                 text_color=COLORS["text"], border_width=0, width=160, font=FONTS["small"])
        new_name.pack(side="left", padx=4)
        new_val = ctk.CTkEntry(nr, placeholder_text="Değer", fg_color=COLORS["bg_input"],
                                text_color=COLORS["text"], border_width=0, width=200, font=FONTS["small"])
        new_val.pack(side="left", padx=4)
        new_unit = ctk.CTkEntry(nr, placeholder_text="Birim", fg_color=COLORS["bg_input"],
                                 text_color=COLORS["text"], border_width=0, width=70, font=FONTS["small"])
        new_unit.pack(side="left", padx=4)

        def _add_spec():
            if new_name.get().strip():
                db.add_specification(product_id, new_name.get().strip(), new_val.get().strip(), new_unit.get().strip())
                self._edit_product_form(product_id)

        ctk.CTkButton(nr, text="➕ Ekle", font=FONTS["small"],
                      fg_color=COLORS["highlight"], hover_color=COLORS["highlight_hover"],
                      height=34, corner_radius=8, command=_add_spec).pack(side="left", padx=6)

    def _make_form(self, parent, cat_names, prefill=None):
        prefill = prefill or {}
        fields = {}
        form = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=12)
        form.pack(fill="x", padx=20, pady=8)

        grid_items = [
            ("Kategori", "category", "option", cat_names),
            ("Ürün Adı *", "name", "entry", None),
            ("Marka", "brand", "entry", None),
            ("Fiyat (₺)", "price", "entry", None),
            ("Satın Alma Linki", "link", "entry", None),
            ("Puan (0-5)", "rating", "entry", None),
        ]

        for label_text, key, field_type, extra in grid_items:
            row = ctk.CTkFrame(form, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=4)
            ctk.CTkLabel(row, text=label_text, font=FONTS["body"],
                         text_color=COLORS["text_secondary"], width=140, anchor="w").pack(side="left")
            if field_type == "option":
                var = ctk.StringVar(value=prefill.get(key, extra[0] if extra else ""))
                widget = ctk.CTkOptionMenu(row, variable=var, values=extra or [""],
                                           fg_color=COLORS["button"], button_color=COLORS["accent"],
                                           text_color=COLORS["text"], font=FONTS["body"])
                widget.pack(side="left", fill="x", expand=True)
                fields[key] = var
            else:
                var = ctk.StringVar(value=prefill.get(key, ""))
                widget = ctk.CTkEntry(row, textvariable=var, fg_color=COLORS["bg_input"],
                                       text_color=COLORS["text"], border_color=COLORS["border"],
                                       font=FONTS["body"])
                widget.pack(side="left", fill="x", expand=True)
                fields[key] = var

        desc_row = ctk.CTkFrame(form, fg_color="transparent")
        desc_row.pack(fill="x", padx=14, pady=4)
        ctk.CTkLabel(desc_row, text="Açıklama", font=FONTS["body"],
                     text_color=COLORS["text_secondary"], width=140, anchor="nw").pack(side="left", anchor="n")
        desc_text = ctk.CTkTextbox(desc_row, fg_color=COLORS["bg_input"],
                                    text_color=COLORS["text"], border_color=COLORS["border"],
                                    font=FONTS["body"], height=70)
        desc_text.pack(side="left", fill="x", expand=True)
        if prefill.get("desc"):
            desc_text.insert("1.0", prefill["desc"])
        fields["desc"] = desc_text
        ctk.CTkFrame(form, height=8, fg_color="transparent").pack()

        return fields

    def _show_feedback(self, msg, level="success"):
        color = COLORS["success"] if level == "success" else COLORS["error"]
        if hasattr(self, "_feedback_label"):
            self._feedback_label.configure(text=msg, text_color=color)
