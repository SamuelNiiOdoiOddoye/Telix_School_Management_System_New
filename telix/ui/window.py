"""Window icon setup."""

from __future__ import annotations

import os
import tkinter as tk

from telix.config import TELIX_ICON_IMAGE_PATH, TELIX_ICON_PATH


def apply_window_icon(master: tk.Tk) -> tk.PhotoImage | None:
    """Set the title-bar and taskbar icons; returns the image so the caller can keep it alive."""
    icon_image = _apply_png_icon(master)
    _apply_windows_icon(master)
    return icon_image


def _apply_png_icon(master: tk.Tk) -> tk.PhotoImage | None:
    if not TELIX_ICON_IMAGE_PATH.exists():
        return None
    try:
        icon_image = tk.PhotoImage(file=str(TELIX_ICON_IMAGE_PATH))
        master.iconphoto(True, icon_image)
        return icon_image
    except tk.TclError:
        return None


def _apply_windows_icon(master: tk.Tk) -> None:
    if os.name != "nt" or not TELIX_ICON_PATH.exists():
        return
    try:
        master.iconbitmap(str(TELIX_ICON_PATH))
    except tk.TclError:
        pass
