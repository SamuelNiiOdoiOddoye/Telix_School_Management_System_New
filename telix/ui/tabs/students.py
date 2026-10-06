"""Students tab: form, ID search, class filter and table."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from telix.core.errors import StorageError
from telix.core.formatting import format_currency
from telix.core.identifiers import generate_id
from telix.core.numbers import as_amount
from telix.students.schema import STUDENT_FIELD_LABELS
from telix.ui.tabs.base import BaseTab, TabContext
from telix.ui.widgets.forms import add_button_row, add_search_entry, build_form_fields
from telix.ui.widgets.tables import create_tree, replace_rows

FORM_FIELDS = (
    ("student_id", "Student ID"),
    ("name", "Full name"),
    ("date_of_birth", "Date of birth (YYYY-MM-DD)"),
    ("class_name", "Class"),
    ("fees", "School fees (GHS)"),
    ("gender", "Gender"),
    ("address", "Address"),
    ("phone", "Student phone"),
    ("email", "Email"),
    ("medical_info", "Medical information"),
    ("parent_name", "Parent / guardian name"),
    ("parent_phone", "Parent / guardian phone"),
)
GENDER_CHOICES = ("Female", "Male", "Other")
TABLE_COLUMNS = ("student_id", "name", "class_name", "phone", "parent_name", "fees")
TABLE_WIDTHS = (140, 210, 90, 140, 200, 110)


class StudentsTab(BaseTab):
    key = "students"
    title = "Students"

    def __init__(self, notebook: ttk.Notebook, context: TabContext) -> None:
        super().__init__(notebook, context)
        self.variables = {name: tk.StringVar() for name in STUDENT_FIELD_LABELS}
        self.search_id = tk.StringVar()
        self.class_filter = tk.StringVar()
        self.selected_id: str | None = None
        self._build_form()
        self._build_tools()
        self._build_table()

    # --- layout -----------------------------------------------------------
    def _build_form(self) -> None:
        form = ttk.LabelFrame(self.frame, text="Student details", padding=12)
        form.pack(fill="x")
        rows = build_form_fields(form, FORM_FIELDS, self.variables, {"gender": GENDER_CHOICES})
        add_button_row(
            form,
            (
                ("Add Student", self.add),
                ("Update Selected", self.update),
                ("Delete Selected", self.delete),
                ("Clear Form", self.clear_form),
            ),
            row=rows,
        )

    def _build_tools(self) -> None:
        tools = ttk.Frame(self.frame)
        tools.pack(fill="x", pady=12)
        add_search_entry(tools, "Search Student ID", self.search_id)
        ttk.Button(tools, text="Search", command=self.search).grid(row=0, column=2, padx=(0, 20))
        ttk.Label(tools, text="View class").grid(row=0, column=3, sticky="w")
        self.class_filter_box = ttk.Combobox(tools, textvariable=self.class_filter, width=18)
        self.class_filter_box.grid(row=0, column=4, padx=(6, 8))
        ttk.Button(tools, text="Filter", command=self.filter_by_class).grid(
            row=0, column=5, padx=(0, 8)
        )
        ttk.Button(tools, text="Show All", command=self.show_all).grid(row=0, column=6)

    def _build_table(self) -> None:
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill="both", expand=True)
        self.tree = create_tree(tree_frame, TABLE_COLUMNS, TABLE_WIDTHS)
        self.tree.bind("<<TreeviewSelect>>", self._on_row_selected)

    # --- button handlers ---------------------------------------------------
    def add(self) -> None:
        self.context.runner.run(
            lambda: self.context.services.students.add(self._form_values()),
            "Student added successfully.",
            self._after_change,
        )

    def update(self) -> None:
        if not self.selected_id:
            self.context.feedback.error(
                "Select a student record from the table before updating it."
            )
            return
        selected_id = self.selected_id
        self.context.runner.run(
            lambda: self.context.services.students.update(selected_id, self._form_values()),
            "Student record updated successfully.",
            self._after_change,
        )

    def delete(self) -> None:
        student_id = self.selected_id or self.variables["student_id"].get().strip()
        if not student_id:
            self.context.feedback.error(
                "Select or search for a student by Student ID before deleting it."
            )
            return
        try:
            student = self.context.services.students.get(student_id)
        except StorageError as error:
            self.context.feedback.error(str(error))
            return
        if not student:
            self.context.feedback.error("Student record not found. Search by Student ID first.")
            return
        if not self.context.feedback.confirm(
            "Delete Student",
            f"Delete {student['name']} ({student['student_id']}) and linked academic, "
            "enrollment, and attendance records? Existing payment history prevents deletion.",
        ):
            return
        self.context.runner.run(
            lambda: self.context.services.student_removal.remove(student_id),
            "Student record deleted successfully.",
            self._after_change,
        )

    def search(self) -> None:
        student_id = self.search_id.get().strip()
        if not student_id:
            self.context.feedback.error("Enter a Student ID to search.")
            return
        try:
            student = self.context.services.students.get(student_id)
        except StorageError as error:
            self.context.feedback.error(str(error))
            return
        if not student:
            self.context.feedback.error("No student was found with that Student ID.")
            return
        self._populate_form(student)
        self._render([student])

    def filter_by_class(self) -> None:
        try:
            self._render(self.context.services.students.by_class(self.class_filter.get()))
        except StorageError as error:
            self.context.feedback.error(str(error))

    def show_all(self) -> None:
        self.class_filter.set("")
        self.refresh()

    def clear_form(self) -> None:
        self.selected_id = None
        for variable in self.variables.values():
            variable.set("")
        self.variables["student_id"].set(generate_id("STU"))
        self.variables["medical_info"].set("None")

    # --- internals ----------------------------------------------------------
    def _form_values(self) -> dict[str, str]:
        return {name: variable.get() for name, variable in self.variables.items()}

    def _on_row_selected(self, _: tk.Event[Any]) -> None:
        selected_items = self.tree.selection()
        if not selected_items:
            return
        student = self.context.services.students.get(selected_items[0])
        if student:
            self._populate_form(student)

    def _populate_form(self, student: dict[str, Any]) -> None:
        self.selected_id = student["student_id"]
        for name, variable in self.variables.items():
            variable.set(str(student.get(name, "")))

    def _after_change(self) -> None:
        self.clear_form()
        self.context.refresh_all()

    def _render(self, students: list[dict[str, Any]]) -> None:
        replace_rows(
            self.tree,
            (
                (
                    student["student_id"],
                    (
                        student["student_id"],
                        student["name"],
                        student["class_name"],
                        student["phone"],
                        student["parent_name"],
                        format_currency(as_amount(student["fees"])),
                    ),
                )
                for student in students
            ),
        )

    def refresh(self) -> None:
        self._render(self.context.services.students.list())
        self.class_filter_box["values"] = self.context.services.students.classes()
        if not self.selected_id:
            self.clear_form()
