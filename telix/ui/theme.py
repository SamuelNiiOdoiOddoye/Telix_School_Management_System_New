"""Fonts and ttk styles used across the interface."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

FONT_FAMILY = "Segoe UI"
HEADING_FONT = (FONT_FAMILY, 15, "bold")


def configure_style(master: tk.Tk) -> None:
    style = ttk.Style(master)
    style.theme_use("clam")
    style.configure("Title.TLabel", font=(FONT_FAMILY, 20, "bold"), foreground="#12355B")
    style.configure("Subtitle.TLabel", font=(FONT_FAMILY, 10), foreground="#506784")
    style.configure("Metric.TLabel", font=(FONT_FAMILY, 16, "bold"), foreground="#12355B")
    style.configure("Treeview", rowheight=28, font=(FONT_FAMILY, 10))
    style.configure("Treeview.Heading", font=(FONT_FAMILY, 10, "bold"))
    style.configure("TNotebook.Tab", padding=(14, 8), font=(FONT_FAMILY, 10, "bold"))
