"""Login screen for local V1 accounts."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from telix.authentication.service import AuthenticatedUser, AuthenticationService
from telix.core.errors import StorageError, ValidationError
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
        self.registration_window: tk.Toplevel | None = None
        self.email_entry: ttk.Entry
        self.demo_registration_button: ttk.Button | None = None
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
        self.email_entry = email_entry
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
        if self.authentication.demo_registration_enabled():
            self.demo_registration_button = ttk.Button(
                card,
                text="Create Local Demo Account",
                command=self.open_demo_registration,
            )
            self.demo_registration_button.grid(
                row=6, column=0, columnspan=2, sticky="ew", pady=(16, 0)
            )
            ttk.Label(
                card,
                text="Development/demo use only. New accounts receive the Teacher role.",
                wraplength=350,
            ).grid(row=7, column=0, columnspan=2, sticky="w", pady=(6, 0))
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

    def open_demo_registration(self) -> None:
        if not self.authentication.demo_registration_enabled():
            self.message.set("Local demo account registration is disabled.")
            return
        if self.registration_window is not None and self.registration_window.winfo_exists():
            self.registration_window.lift()
            return

        window = tk.Toplevel(self.master)
        self.registration_window = window
        window.title("Create Local Demo Account")
        window.transient(self.master)
        window.resizable(False, False)
        content = ttk.Frame(window, padding=20)
        content.pack(fill="both", expand=True)
        ttk.Label(content, text="Create Local Demo Account", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            content,
            text="Development/demo only · Access is limited to the Teacher role.",
            wraplength=380,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 12))

        full_name = tk.StringVar()
        email = tk.StringVar()
        password = tk.StringVar()
        confirmation = tk.StringVar()
        fields = (
            ("Full name", full_name, False),
            ("Email", email, False),
            ("Password", password, True),
            ("Confirm password", confirmation, True),
        )
        entries: list[ttk.Entry] = []
        for row, (label, variable, hidden) in enumerate(fields, start=2):
            ttk.Label(content, text=label).grid(row=row, column=0, sticky="w", pady=5)
            entry = ttk.Entry(
                content,
                textvariable=variable,
                width=38,
                show="*" if hidden else "",
            )
            entry.grid(row=row, column=1, sticky="ew", padx=(12, 0), pady=5)
            entries.append(entry)
        message = tk.StringVar()
        ttk.Label(
            content,
            textvariable=message,
            foreground="#a32121",
            wraplength=380,
        ).grid(row=6, column=0, columnspan=2, sticky="w", pady=(6, 0))

        def create_account() -> None:
            try:
                user = self.authentication.register_demo_account(
                    full_name.get(),
                    email.get(),
                    password.get(),
                    confirmation.get(),
                )
            except (StorageError, ValidationError) as error:
                message.set(str(error))
                password.set("")
                confirmation.set("")
                entries[2].focus_set()
                return
            self.email.set(user.email)
            self.password.set("")
            self.message.set(
                "Demo Teacher account created. Log in with the email and password you chose."
            )
            password.set("")
            confirmation.set("")
            window.destroy()
            self.registration_window = None
            self.email_entry.focus_set()

        actions = ttk.Frame(content)
        actions.grid(row=7, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(actions, text="Cancel", command=self._close_registration).pack(side="right")
        ttk.Button(actions, text="Create Account", command=create_account).pack(
            side="right", padx=(0, 8)
        )
        window.protocol("WM_DELETE_WINDOW", self._close_registration)
        window.bind("<Return>", lambda _event: create_account())
        entries[0].focus_set()
        window.grab_set()

    def _close_registration(self) -> None:
        if self.registration_window is not None:
            self.registration_window.destroy()
            self.registration_window = None

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
