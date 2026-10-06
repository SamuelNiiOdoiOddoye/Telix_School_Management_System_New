"""Teachers tab: form, ID search and table."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from telix.core.errors import StorageError
from telix.core.formatting import format_currency
from telix.core.identifiers import generate_id
from telix.core.numbers import as_amount
from telix.teachers.schema import TEACHER_FIELD_LABELS
from telix.ui.tabs.base import BaseTab, TabContext
from telix.ui.widgets.forms import add_button_row, add_search_entry, build_form_fields
from telix.ui.widgets.tables import create_tree, replace_rows

FORM_FIELDS = (
    ("teacher_id", "Teacher ID"),
    ("name", "Full name"),
    ("date_of_birth", "Date of birth (YYYY-MM-DD)"),
    ("class_name", "Class or subject"),
    ("salary", "Salary (GHS)"),
    ("gender", "Gender"),
    ("address", "Address"),
    ("phone", "Teacher phone"),
    ("email", "Email"),
    ("medical_info", "Medical information"),
    ("emergency_contact", "Emergency contact"),
)
GENDER_CHOICES = ("Female", "Male", "Other")
TABLE_COLUMNS = ("teacher_id", "name", "class_name", "phone", "email", "salary")
TABLE_WIDTHS = (140, 210, 150, 140, 240, 110)


class TeachersTab(BaseTab):
    key = "teachers"
    title = "Teachers"

    def __init__(self, notebook: ttk.Notebook, context: TabContext) -> None:
        super().__init__(notebook, context)
        self.variables = {name: tk.StringVar() for name in TEACHER_FIELD_LABELS}
        self.search_id = tk.StringVar()
        self.selected_id: str | None = None
        self._build_form()
        self._build_tools()
        self._build_table()

    # --- layout -----------------------------------------------------------
    def _build_form(self) -> None:
        form = ttk.LabelFrame(self.frame, text="Teacher details", padding=12)
        form.pack(fill="x")
        rows = build_form_fields(form, FORM_FIELDS, self.variables, {"gender": GENDER_CHOICES})
        add_button_row(
            form,
            (
                ("Add Teacher", self.add),
                ("Update Selected", self.update),
                ("Delete Selected", self.delete),
                ("Clear Form", self.clear_form),
            ),
            row=rows,
        )

    def _build_tools(self) -> None:
        tools = ttk.Frame(self.frame)
        tools.pack(fill="x", pady=12)
        add_search_entry(tools, "Search Teacher ID", self.search_id)
        ttk.Button(tools, text="Search", command=self.search).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(tools, text="Show All", command=self.refresh).grid(row=0, column=3)

    def _build_table(self) -> None:
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill="both", expand=True)
        self.tree = create_tree(tree_frame, TABLE_COLUMNS, TABLE_WIDTHS)
        self.tree.bind("<<TreeviewSelect>>", self._on_row_selected)

    # --- button handlers ---------------------------------------------------
    def add(self) -> None:
        self.context.runner.run(
            lambda: self.context.services.teachers.add(self._form_values()),
            "Teacher added successfully.",
            self._after_change,
        )

    def update(self) -> None:
        if not self.selected_id:
            self.context.feedback.error(
                "Select a teacher record from the table before updating it."
            )
            return
        selected_id = self.selected_id
        self.context.runner.run(
            lambda: self.context.services.teachers.update(selected_id, self._form_values()),
            "Teacher record updated successfully.",
            self._after_change,
        )

    def delete(self) -> None:
        teacher_id = self.selected_id or self.variables["teacher_id"].get().strip()
        if not teacher_id:
            self.context.feedback.error(
                "Select or search for a teacher by Teacher ID before deleting it."
            )
            return
        try:
            teacher = self.context.services.teachers.get(teacher_id)
        except StorageError as error:
            self.context.feedback.error(str(error))
            return
        if not teacher:
            self.context.feedback.error("Teacher record not found. Search by Teacher ID first.")
            return
        if not self.context.feedback.confirm(
            "Delete Teacher", f"Delete {teacher['name']} ({teacher['teacher_id']})?"
        ):
            return
        self.context.runner.run(
            lambda: self.context.services.teachers.delete(teacher_id),
            "Teacher record deleted successfully.",
            self._after_change,
        )

    def search(self) -> None:
        teacher_id = self.search_id.get().strip()
        if not teacher_id:
            self.context.feedback.error("Enter a Teacher ID to search.")
            return
        try:
            teacher = self.context.services.teachers.get(teacher_id)
        except StorageError as error:
            self.context.feedback.error(str(error))
            return
        if not teacher:
            self.context.feedback.error("No teacher was found with that Teacher ID.")
            return
        self._populate_form(teacher)
        self._render([teacher])

    def clear_form(self) -> None:
        self.selected_id = None
        for variable in self.variables.values():
            variable.set("")
        self.variables["teacher_id"].set(generate_id("TCH"))
        self.variables["medical_info"].set("None")

    # --- internals ----------------------------------------------------------
    def _form_values(self) -> dict[str, str]:
        return {name: variable.get() for name, variable in self.variables.items()}

    def _on_row_selected(self, _: tk.Event[Any]) -> None:
        selected_items = self.tree.selection()
        if not selected_items:
            return
        teacher = self.context.services.teachers.get(selected_items[0])
        if teacher:
            self._populate_form(teacher)

    def _populate_form(self, teacher: dict[str, Any]) -> None:
        self.selected_id = teacher["teacher_id"]
        for name, variable in self.variables.items():
            variable.set(str(teacher.get(name, "")))

    def _after_change(self) -> None:
        self.clear_form()
        self.context.refresh_all()

    def _render(self, teachers: list[dict[str, Any]]) -> None:
        replace_rows(
            self.tree,
            (
                (
                    teacher["teacher_id"],
                    (
                        teacher["teacher_id"],
                        teacher["name"],
                        teacher["class_name"],
                        teacher["phone"],
                        teacher["email"],
                        format_currency(as_amount(teacher["salary"])),
                    ),
                )
                for teacher in teachers
            ),
        )

    def refresh(self) -> None:
        self._render(self.context.services.teachers.list())
        if not self.selected_id:
            self.clear_form()
