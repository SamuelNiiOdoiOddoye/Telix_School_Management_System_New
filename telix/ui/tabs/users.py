"""User Management tab for authorized local V1 administrators."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from telix.authentication.roles import capabilities_for
from telix.core.errors import AuthorizationError, StorageError, ValidationError
from telix.ui.tabs.base import BaseTab, TabContext
from telix.ui.widgets.forms import add_button_row, add_search_entry
from telix.ui.widgets.tables import create_tree, replace_rows

USER_COLUMNS = ("user_id", "name", "email", "role", "status", "student_id", "created_at")
USER_WIDTHS = (210, 180, 250, 150, 90, 150, 220)


def role_access_summary(role: str) -> str:
    """Render the effective V1 capabilities without defining new permissions."""
    capabilities = capabilities_for(role)
    if "*" in capabilities:
        return f"Effective V1 access for {role}\n✓ All V1 capabilities"
    grouped: dict[str, list[str]] = {}
    for capability in sorted(capabilities):
        domain, _, actions = capability.partition(".")
        grouped.setdefault(domain.replace("_", " ").title(), []).append(
            actions.replace(".", " · ").replace("_", " ")
        )
    lines = [f"Effective V1 access for {role}"]
    lines.extend(f"✓ {domain}: {', '.join(actions)}" for domain, actions in grouped.items())
    return "\n".join(lines)


class UserManagementTab(BaseTab):
    key = "users"
    title = "User Management"

    def __init__(self, notebook: ttk.Notebook, context: TabContext) -> None:
        super().__init__(notebook, context)
        if context.services.user_management is None:
            raise ValueError("User Management requires an authenticated user-management service.")
        self.service = context.services.user_management
        self.values = {
            field: tk.StringVar()
            for field in ("name", "email", "phone", "role", "student_id", "password", "confirm")
        }
        self.search_query = tk.StringVar()
        self.selected_user_id: str | None = None
        self._users_by_id: dict[str, dict[str, Any]] = {}
        self._build_form()
        self._build_tools()
        self._build_table()

    def _build_form(self) -> None:
        form = ttk.LabelFrame(self.frame, text="Account details", padding=12)
        form.pack(fill="x")
        _name_label, self.name_entry = self._add_field(form, "Name", self.values["name"], 0)
        _email_label, self.email_entry = self._add_field(form, "Email", self.values["email"], 1)
        _phone_label, self.phone_entry = self._add_field(form, "Phone", self.values["phone"], 2)
        _role_label, self.role_box = self._add_field(
            form,
            "Role",
            self.values["role"],
            3,
            ("", *self.service.assignable_roles()),
        )
        self.role_box.bind("<<ComboboxSelected>>", self._role_changed)
        self.student_label, self.student_box = self._add_field(
            form, "Linked student", self.values["student_id"], 4, ("",)
        )
        _password_label, self.password_entry = self._add_field(
            form, "Initial password", self.values["password"], 5, password=True
        )
        _confirm_label, self.confirm_entry = self._add_field(
            form, "Confirm password", self.values["confirm"], 6, password=True
        )
        self.password_entry.configure(show="*")
        self.confirm_entry.configure(show="*")
        self._populate_student_choices()
        add_button_row(
            form,
            (
                ("Create Account", self.create),
                ("Save Changes", self.update),
                ("Activate", lambda: self.set_active(True)),
                ("Deactivate", lambda: self.set_active(False)),
                ("Clear", self.clear_form),
            ),
            row=4,
        )
        self.form = form
        self._role_changed()

    @staticmethod
    def _add_field(
        parent: ttk.LabelFrame,
        label: str,
        variable: tk.StringVar,
        position: int,
        choices: tuple[str, ...] | None = None,
        password: bool = False,
    ) -> tuple[ttk.Label, ttk.Entry | ttk.Combobox]:
        column = (position % 2) * 3
        grid_row = position // 2
        label_widget = ttk.Label(parent, text=label)
        label_widget.grid(row=grid_row, column=column, sticky="w", padx=(0, 6))
        widget: ttk.Entry | ttk.Combobox
        if choices is not None:
            widget = ttk.Combobox(
                parent,
                textvariable=variable,
                values=choices,
                state="readonly",
                width=28,
            )
        else:
            widget = ttk.Entry(
                parent,
                textvariable=variable,
                show="*" if password else "",
                width=30,
            )
        widget.grid(row=grid_row, column=column + 1, sticky="ew", padx=(0, 16), pady=4)
        parent.columnconfigure(column + 1, weight=1)
        return label_widget, widget

    def _build_tools(self) -> None:
        tools = ttk.Frame(self.frame)
        tools.pack(fill="x", pady=10)
        add_search_entry(tools, "Search users", self.search_query)
        ttk.Button(tools, text="Search", command=self.refresh).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(tools, text="Show All", command=self._show_all).grid(row=0, column=3)
        access = ttk.LabelFrame(self.frame, text="Selected account access profile", padding=8)
        access.pack(fill="x", pady=(0, 10))
        self.access_summary = tk.Text(access, height=4, wrap="word", state="disabled")
        self.access_summary.pack(fill="x", expand=True)
        self._set_access_summary("")

    def _build_table(self) -> None:
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill="both", expand=True)
        self.tree = create_tree(table_frame, USER_COLUMNS, USER_WIDTHS)
        self.tree.bind("<<TreeviewSelect>>", self._on_selected)

    def create(self) -> None:
        password = self.values["password"].get()
        if password != self.values["confirm"].get():
            self.context.feedback.error("The passwords do not match.")
            return
        self.context.runner.run(
            lambda: self.service.create(
                self.values["name"].get(),
                self.values["email"].get(),
                self.values["phone"].get(),
                password,
                self.values["role"].get(),
                student_id=self._selected_student_id(),
            ),
            "User account created successfully.",
            self._after_change,
        )

    def update(self) -> None:
        if not self.selected_user_id:
            self.context.feedback.error("Select an account before saving changes.")
            return
        user_id = self.selected_user_id
        self.context.runner.run(
            lambda: self.service.update(
                user_id,
                name=self.values["name"].get(),
                email=self.values["email"].get(),
                phone=self.values["phone"].get(),
                role=self.values["role"].get(),
                student_id=self._selected_student_id(),
            ),
            "User account updated successfully.",
            self._after_change,
        )

    def set_active(self, is_active: bool) -> None:
        if not self.selected_user_id:
            self.context.feedback.error("Select an account before changing its status.")
            return
        if not is_active and not self.context.feedback.confirm(
            "Deactivate User", "Deactivate this account? It will no longer be able to log in."
        ):
            return
        user_id = self.selected_user_id
        status = "activated" if is_active else "deactivated"
        self.context.runner.run(
            lambda: self.service.set_active(user_id, is_active),
            f"User account {status} successfully.",
            self._after_change,
        )

    def refresh(self) -> None:
        try:
            records = self.service.list(self.search_query.get())
            self._users_by_id = {str(record["user_id"]): record for record in records}
            replace_rows(
                self.tree,
                (
                    (
                        str(record["user_id"]),
                        (
                            record["user_id"],
                            record["name"],
                            record["email"],
                            record["role"],
                            "Active" if record["active"] else "Inactive",
                            record.get("student_id", ""),
                            record.get("created_at", ""),
                        ),
                    )
                    for record in records
                ),
            )
            self._populate_student_choices()
        except (AuthorizationError, StorageError, ValidationError) as error:
            self.context.feedback.error(str(error))

    def clear_form(self) -> None:
        self.selected_user_id = None
        for variable in self.values.values():
            variable.set("")
        self.role_box["values"] = ("", *self.service.assignable_roles())
        self.password_entry.state(["!disabled"])
        self.confirm_entry.state(["!disabled"])
        self._role_changed()

    def _populate_student_choices(self) -> None:
        students = self.context.services.students.list()
        self.student_box["values"] = (
            "",
            *(f"{student['name']} [{student['student_id']}]" for student in students),
        )

    def _selected_student_id(self) -> str:
        selected = self.values["student_id"].get().strip()
        if selected.endswith("]") and " [" in selected:
            return selected.rsplit(" [", 1)[1][:-1]
        return selected

    def _role_changed(self, _event: tk.Event[Any] | None = None) -> None:
        is_student = self.values["role"].get() == "STUDENT"
        self.student_box.state(["!disabled"] if is_student else ["disabled"])
        self.student_label.configure(state="normal" if is_student else "disabled")
        if hasattr(self, "access_summary"):
            self._set_access_summary(self.values["role"].get())

    def _set_access_summary(self, role: str) -> None:
        text = role_access_summary(role) if role else "Select or choose a role to view its access."
        self.access_summary.configure(state="normal")
        self.access_summary.delete("1.0", "end")
        self.access_summary.insert("1.0", text)
        self.access_summary.configure(state="disabled")

    def _on_selected(self, _event: tk.Event[Any]) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        record = self._users_by_id.get(selected[0])
        if record is None:
            return
        self.selected_user_id = str(record["user_id"])
        for field in ("name", "email", "phone", "role"):
            self.values[field].set(str(record.get(field, "")))
        student_id = str(record.get("student_id", ""))
        if student_id:
            student = self.context.services.students.get(student_id)
            self.values["student_id"].set(
                f"{student['name']} [{student_id}]" if student else student_id
            )
        else:
            self.values["student_id"].set("")
        self.values["password"].set("")
        self.values["confirm"].set("")
        self.password_entry.state(["disabled"])
        self.confirm_entry.state(["disabled"])
        self._role_changed()

    def _after_change(self) -> None:
        self.clear_form()
        self.refresh()

    def _show_all(self) -> None:
        self.search_query.set("")
        self.refresh()
