"""Paleta y estilos inspirados en la interfaz de iOS."""

from tkinter import ttk


BACKGROUND = "#F2F2F7"
CARD = "#FFFFFF"
TEXT = "#1C1C1E"
SECONDARY_TEXT = "#6C6C70"
SEPARATOR = "#D1D1D6"
BLUE = "#007AFF"
BLUE_PRESSED = "#0069D9"
GREEN = "#34C759"
RED = "#FF3B30"
SOFT_BLUE = "#E8F2FF"
SOFT_GREEN = "#E8F8ED"
SOFT_RED = "#FDEBEA"
FONT = "Segoe UI"


def apply_theme(root) -> ttk.Style:
    """Configura los estilos ttk usados por toda la ventana."""
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("App.TFrame", background=BACKGROUND)
    style.configure("Card.TFrame", background=CARD)
    style.configure("Header.TLabel", background=BACKGROUND, foreground=TEXT, font=(FONT, 24, "bold"))
    style.configure("Subtitle.TLabel", background=BACKGROUND, foreground=SECONDARY_TEXT, font=(FONT, 10))
    style.configure("CardTitle.TLabel", background=CARD, foreground=TEXT, font=(FONT, 11, "bold"))
    style.configure("Body.TLabel", background=CARD, foreground=TEXT, font=(FONT, 10))
    style.configure("Muted.TLabel", background=CARD, foreground=SECONDARY_TEXT, font=(FONT, 9))
    style.configure("Section.TLabel", background=BACKGROUND, foreground=SECONDARY_TEXT, font=(FONT, 9, "bold"))
    style.configure("Value.TLabel", background=CARD, foreground=TEXT, font=(FONT, 10, "bold"))
    style.configure("Accent.TButton", background=BLUE, foreground="#FFFFFF", font=(FONT, 10, "bold"), borderwidth=0, padding=(16, 10))
    style.map("Accent.TButton", background=[("active", BLUE_PRESSED), ("pressed", BLUE_PRESSED)])
    style.configure("Secondary.TButton", background=SOFT_BLUE, foreground=BLUE, font=(FONT, 9, "bold"), borderwidth=0, padding=(10, 7))
    style.map("Secondary.TButton", background=[("active", "#D8E9FF")])
    style.configure("App.TEntry", fieldbackground=CARD, foreground=TEXT, bordercolor=SEPARATOR, lightcolor=SEPARATOR, darkcolor=SEPARATOR, padding=(10, 9))
    style.configure("App.TCombobox", fieldbackground=CARD, foreground=TEXT, padding=(8, 7))
    return style
