"""Application paths and UI constants."""

from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DB_FILENAME = "media_tracker.db"
DB_PATH = APP_DIR / DB_FILENAME
APP_TITLE = "Personal Movies & Shows"

# Typography / spacing (tk uses pt loosely on Windows)
FONT_FAMILY_UI = "Segoe UI"
FONT_FAMILY_MONO = "Consolas"

COLORS = {
    "bg": "#f4f5f7",
    "surface": "#ffffff",
    "accent": "#2563eb",
    "accent_hover": "#1d4ed8",
    "text": "#111827",
    "muted": "#6b7280",
    "border": "#e5e7eb",
    "header": "#1e293b",
}
