import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from config import COLORS, FONTS, APP_TITLE, APP_SIZE, APP_MIN_SIZE
from components.navbar import Navbar
from pages.home_page import HomePage
from pages.products_page import ProductsPage
from pages.detail_page import DetailPage
from pages.compare_page import ComparePage
from pages.test_page import TestPage
from pages.recommend_page import RecommendPage
from pages.favorites_page import FavoritesPage
from pages.manage_page import ManagePage
import database as db

#uygulama başlangıc
#ana pencere
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.minsize(*APP_MIN_SIZE)
        self.configure(fg_color=COLORS["bg"])
        self.iconbitmap("equipment_app/assets/logo.ico")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self._init_db()
        self._build_ui()
        self.navigate("home")

    def _init_db(self):
        try:
            db.init_database()
        except Exception as e:
            self._show_db_error(str(e))

    def _show_db_error(self, msg):
        error_win = ctk.CTkToplevel(self)
        error_win.title("Veritabanı Hatası")
        error_win.geometry("540x300")
        error_win.configure(fg_color=COLORS["bg"])
        error_win.grab_set()

        ctk.CTkLabel(error_win, text="⚠ Veritabanı Bağlantı Hatası",
                     font=FONTS["title"], text_color=COLORS["error"]).pack(pady=(30, 8))
        ctk.CTkLabel(error_win, text=msg, font=FONTS["body"],
                     text_color=COLORS["text_secondary"], wraplength=480, justify="center").pack(pady=8)
        ctk.CTkLabel(error_win, text="MySQL sunucunuzun çalıştığından emin olun:\n• Kullanıcı: root\n• Şifre: 1234\n• Port: 3306",
                     font=FONTS["body"], text_color=COLORS["accent"], justify="left").pack(pady=8)
        ctk.CTkButton(error_win, text="Tamam", font=FONTS["button"],
                      fg_color=COLORS["highlight"], height=38, corner_radius=8,
                      command=error_win.destroy).pack(pady=16)

    def _build_ui(self):
        self.navbar = Navbar(self, navigate_callback=self.navigate)
        self.navbar.pack(fill="x", side="top")

        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self.content.pack(fill="both", expand=True)

        self._pages = {}
        self._current_page = None

    def _get_page(self, name):
        if name not in self._pages:
            page_map = {
                "home": lambda: HomePage(self.content, navigate_callback=self.navigate),
                "products": lambda: ProductsPage(self.content, navigate_callback=self.navigate),
                "detail": lambda: DetailPage(self.content, navigate_callback=self.navigate),
                "compare": lambda: ComparePage(self.content, navigate_callback=self.navigate),
                "test": lambda: TestPage(self.content, navigate_callback=self.navigate),
                "recommend": lambda: RecommendPage(self.content, navigate_callback=self.navigate),
                "favorites": lambda: FavoritesPage(self.content, navigate_callback=self.navigate),
                "manage": lambda: ManagePage(self.content, navigate_callback=self.navigate),
            }
            if name in page_map:
                self._pages[name] = page_map[name]()
            else:
                return None
        return self._pages[name]

    def navigate(self, page, extra=None):
        if self._current_page:
            self._current_page.pack_forget()

        target = self._get_page(page)
        if target is None:
            target = self._get_page("home")
            page = "home"

        nav_pages = {"home", "products", "compare", "test", "recommend", "favorites", "manage"}
        if page in nav_pages:
            self.navbar.set_active(page)

        if page == "detail" and extra is not None:
            target.load_product(extra)
        elif page == "compare" and extra is not None:
            target.preselect_product(extra)
        elif page == "products":
            try:
                target.refresh()
            except Exception:
                pass
        elif page == "favorites":
            try:
                target.refresh()
            except Exception:
                pass

        target.pack(fill="both", expand=True)
        self._current_page = target


def main():
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()