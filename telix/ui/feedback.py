"""Message boxes: the only place the application talks to ``tkinter.messagebox``."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

APP_TITLE = "Telix School Management System"


class Feedback:
    def __init__(self, master: tk.Tk) -> None:
        self._master = master

    def error(self, message: str) -> None:
        messagebox.showerror(APP_TITLE, message, parent=self._master)

    def success(self, message: str) -> None:
        messagebox.showinfo("Success", message, parent=self._master)

    def confirm(self, title: str, message: str) -> bool:
        return messagebox.askyesno(title, message, parent=self._master)
