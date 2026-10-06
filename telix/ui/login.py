"""Login screen for local V1 accounts."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from telix.authentication.service import AuthenticatedUser, AuthenticationService
from telix.core.errors import StorageError
from telix.ui.window import apply_window_icon


class LoginScreen:
    def __init__(
        self,
        master: tk.Tk,
        authentication: AuthenticationService,
        on_authenticated: Callable[[AuthenticatedUser], None],
    ) -> None:
        self.master = master
        self.authentication = authentication
        self.on_authenticated = on_authenticated
        self.frame = ttk.Frame(master, padding=28)
        self.frame.pack(expand=True)
        self._icon_image = apply_window_icon(master)
        self.email = tk.StringVar()
        self.password = tk.StringVar()
        self.message = tk.StringVar()
        self._build()

    def _build(self) -> None:
        card = ttk.Frame(self.frame, padding=28)
        card.pack()
        ttk.Label(card, text="TELIX", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            card,
            text="School Management System · access follows your account role",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 22))
        ttk.Label(card, text="Email").grid(row=2, column=0, sticky="w", pady=6)
        email_entry = ttk.Entry(card, textvariable=self.email, width=36)
        email_entry.grid(row=2, column=1, sticky="ew", padx=(12, 0), pady=6)
        ttk.Label(card, text="Password").grid(row=3, column=0, sticky="w", pady=6)
        password_entry = ttk.Entry(card, textvariable=self.password, show="*", width=36)
        password_entry.grid(row=3, column=1, sticky="ew", padx=(12, 0), pady=6)
        password_entry.bind("<Return>", self._submit)
        email_entry.bind("<Return>", lambda _event: password_entry.focus_set())
        ttk.Button(card, text="Log in", command=self._submit).grid(
            row=4, column=1, sticky="e", pady=(14, 4)
        )
        ttk.Label(
            card,
            textvariable=self.message,
            foreground="#a32121",
            wraplength=350,
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 0))
        card.columnconfigure(1, weight=1)
        try:
            if not self.authentication.has_super_admin():
                self.message.set(
                    "No administrator is configured. Close Telix and run "
                    "`python -m telix.bootstrap_admin` to create one."
                )
        except StorageError:
            self.message.set("Could not read local account data. Check the users.json file.")
        email_entry.focus_set()

    def _submit(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        try:
            user = self.authentication.authenticate(self.email.get(), self.password.get())
        except StorageError:
            self.message.set("Unable to access local account data.")
            self.password.set("")
            return
        if user is None:
            self.message.set("Invalid email or password.")
            self.password.set("")
            return
        self.password.set("")
        self.frame.destroy()
        self.on_authenticated(user)
