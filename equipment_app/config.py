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
    "bg": "#FFFFFF",
    "bg_secondary": "#0F172A",
    "bg_card": "#0F172A",
    "bg_input": "#334155",
    "text": "#F1F5F9",
    "text_secondary": "#94A3B8",
    "button": "#0C5777",
    "button_hover": "#073346",
    "accent": "#F1F5F9",
    "border": "#1E293B",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "error": "#F44336",
    "highlight": "#073346",
    "highlight_hover": "#0C5777",
}

#kullanılan fontlar
FONTS = {
    "title": ("Inter", 22, "bold"),
    "subtitle": ("Inter", 16, "bold"),
    "heading": ("Inter", 14, "bold"),
    "body": ("Inter", 12),
    "small": ("Inter", 10),
    "button": ("Inter", 12, "bold"),
    "mono": ("Fira", 12),
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