"""Pequeños componentes reutilizables para mantener la ventana ordenada."""

import tkinter as tk
from tkinter import ttk

from . import theme


class ScrollableFrame(ttk.Frame):
    """Contenedor vertical con desplazamiento para pantallas pequeñas."""

    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, style="App.TFrame", **kwargs)
        self.canvas = tk.Canvas(self, background=theme.BACKGROUND, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.content = ttk.Frame(self.canvas, style="App.TFrame")
        self._content_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.content.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._fit_content_width)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")

    def _update_scroll_region(self, _event=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _fit_content_width(self, event) -> None:
        self.canvas.itemconfigure(self._content_window, width=event.width)

    def _on_mousewheel(self, event) -> None:
        self.canvas.yview_scroll(int(-event.delta / 120), "units")


def card(parent, title: str, subtitle: str | None = None) -> ttk.Frame:
    """Crea una tarjeta blanca con título y devuelve su contenido interno."""
    outer = ttk.Frame(parent, style="Card.TFrame", padding=16)
    ttk.Label(outer, text=title, style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
    if subtitle:
        ttk.Label(outer, text=subtitle, style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(3, 0))

    content = ttk.Frame(outer, style="Card.TFrame")
    content.grid(row=2, column=0, sticky="ew", pady=(12, 0))
    outer.columnconfigure(0, weight=1)
    content.columnconfigure(0, weight=1)
    return outer


def info_row(parent, row: int, label: str, value: str) -> None:
    """Muestra una etiqueta y su valor alineados dentro de una tarjeta."""
    ttk.Label(parent, text=label, style="Muted.TLabel").grid(row=row, column=0, sticky="w", pady=3)
    ttk.Label(parent, text=value, style="Value.TLabel").grid(row=row, column=1, sticky="e", pady=3)
    parent.columnconfigure(1, weight=1)


def clear_children(parent) -> None:
    """Elimina el contenido dinámico de un contenedor sin borrar la tarjeta."""
    for child in parent.winfo_children():
        child.destroy()
