#ayarlar

#database bilgileri
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "equipment_db",
    "charset": "utf8mb4"
}

#kullanlılan renkler
COLORS = {
    "bg": "#121212",
    "bg_secondary": "#1E1E1E",
    "bg_card": "#1A1A1A",
    "bg_input": "#2A2A2A",
    "text": "#E0E0E0",
    "text_secondary": "#AAAAAA",
    "button": "#444444",
    "button_hover": "#555555",
    "accent": "#888888",
    "border": "#333333",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "error": "#F44336",
    "highlight": "#5C6BC0",
    "highlight_hover": "#7986CB",
}

#kullanılan fontlar
FONTS = {
    "title": ("Segoe UI", 22, "bold"),
    "subtitle": ("Segoe UI", 16, "bold"),
    "heading": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 12),
    "small": ("Segoe UI", 10),
    "button": ("Segoe UI", 12, "bold"),
    "mono": ("Consolas", 12),
}

#pencere bilgileri
APP_TITLE = "EkipmanX - Bilgisayar Ekipman Merkezi"
APP_SIZE = "1280x780"
APP_MIN_SIZE = (1024, 680)

CATEGORIES = {
    1: {"name": "Klavye", "icon": "⌨"},
    2: {"name": "Mouse", "icon": "🖱"},
    3: {"name": "Kulaklık", "icon": "🎧"},
}
