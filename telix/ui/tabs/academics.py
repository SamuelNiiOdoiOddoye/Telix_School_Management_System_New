"""Academic Records tab: score form, student search and table."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from telix.academics.defaults import DEFAULT_TERM, default_academic_year
from telix.core.errors import StorageError
from telix.ui.tabs.base import BaseTab, TabContext
from telix.ui.widgets.forms import add_button_row, add_search_entry, build_form_fields
from telix.ui.widgets.tables import create_tree, render_records

FORM_FIELDS = (
    ("student_id", "Student ID"),
    ("subject", "Subject"),
    ("score", "Score (0-100)"),
    ("term", "Term"),
    ("academic_year", "Academic year"),
)
TABLE_COLUMNS = ("academic_id", "student_id", "subject", "score", "term", "academic_year")
TABLE_WIDTHS = (140, 140, 220, 80, 110, 140)
STUDENT_PROMPT = "Search by Student ID to confirm the student."


class AcademicsTab(BaseTab):
    key = "academics"
    title = "Academic Records"

    def __init__(self, notebook: ttk.Notebook, context: TabContext) -> None:
        super().__init__(notebook, context)
        self.variables = {name: tk.StringVar() for name, _ in FORM_FIELDS}
        self.search_student_id = tk.StringVar()
        self.student_summary = tk.StringVar(value=STUDENT_PROMPT)
        self.selected_id: str | None = None
        self._build_form()
        self._build_tools()
        self._build_table()

    # --- layout -----------------------------------------------------------
    def _build_form(self) -> None:
        form = ttk.LabelFrame(self.frame, text="Academic record", padding=12)
        form.pack(fill="x")
        rows = build_form_fields(form, FORM_FIELDS, self.variables)
        ttk.Label(form, textvariable=self.student_summary, style="Subtitle.TLabel").grid(
            row=rows, column=0, columnspan=6, sticky="w", pady=(8, 0)
        )
        add_button_row(
            form,
            (
                ("Add Score", self.add),
                ("Update Selected", self.update),
                ("Delete Selected", self.delete),
                ("Clear Form", self.clear_form),
            ),
            row=rows + 1,
        )

    def _build_tools(self) -> None:
        tools = ttk.Frame(self.frame)
        tools.pack(fill="x", pady=12)
        add_search_entry(tools, "Search Student ID", self.search_student_id)
        ttk.Button(tools, text="Search", command=self.search_student).grid(
            row=0, column=2, padx=(0, 8)
        )
        ttk.Button(tools, text="Show All", command=self.refresh).grid(row=0, column=3)

    def _build_table(self) -> None:
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill="both", expand=True)
        self.tree = create_tree(tree_frame, TABLE_COLUMNS, TABLE_WIDTHS)
        self.tree.bind("<<TreeviewSelect>>", self._on_row_selected)

    # --- button handlers ---------------------------------------------------
    def add(self) -> None:
        services = self.context.services
        self.context.runner.run(
            lambda: services.academics.add(self._form_values(), services.students.exists),
            "Academic record added successfully.",
            self._after_change,
        )

    def update(self) -> None:
        if not self.selected_id:
            self.context.feedback.error(
                "Select an academic record from the table before updating it."
            )
            return
        services = self.context.services
        selected_id = self.selected_id
        self.context.runner.run(
            lambda: services.academics.update(
                selected_id, self._form_values(), services.students.exists
            ),
            "Academic record updated successfully.",
            self._after_change,
        )

    def delete(self) -> None:
        if not self.selected_id:
            self.context.feedback.error(
                "Select an academic record from the table before deleting it."
            )
            return
        if not self.context.feedback.confirm(
            "Delete Academic Record", "Delete the selected academic record?"
        ):
            return
        selected_id = self.selected_id
        self.context.runner.run(
            lambda: self.context.services.academics.delete(selected_id),
            "Academic record deleted successfully.",
            self._after_change,
        )

    def search_student(self) -> None:
        student_id = self.search_student_id.get().strip()
        if not student_id:
            self.context.feedback.error("Enter a Student ID to search academic records.")
            return
        try:
            student = self.context.services.students.get(student_id)
            if not student:
                self.context.feedback.error("No student was found with that Student ID.")
                return
            self.variables["student_id"].set(student["student_id"])
            self._show_student(student)
            self._render(self.context.services.academics.for_student(student_id))
        except StorageError as error:
            self.context.feedback.error(str(error))

    def clear_form(self) -> None:
        self.selected_id = None
        for variable in self.variables.values():
            variable.set("")
        self.variables["term"].set(DEFAULT_TERM)
        self.variables["academic_year"].set(default_academic_year())
        self.student_summary.set(STUDENT_PROMPT)

    # --- internals ----------------------------------------------------------
    def _form_values(self) -> dict[str, str]:
        return {name: variable.get() for name, variable in self.variables.items()}

    def _on_row_selected(self, _: tk.Event[Any]) -> None:
        selected_items = self.tree.selection()
        if not selected_items:
            return
        record = self.context.services.academics.get(selected_items[0])
        if not record:
            return
        self.selected_id = record["academic_id"]
        for name, variable in self.variables.items():
            variable.set(str(record.get(name, "")))
        student = self.context.services.students.get(record["student_id"])
        if student:
            self._show_student(student)

    def _show_student(self, student: dict[str, Any]) -> None:
        self.student_summary.set(f"Student: {student['name']} · Class: {student['class_name']}")

    def _after_change(self) -> None:
        self.clear_form()
        self.context.refresh_all()

    def _render(self, records: list[dict[str, Any]]) -> None:
        render_records(self.tree, records, TABLE_COLUMNS)

    def refresh(self) -> None:
        self._render(self.context.services.academics.list())
        if not self.selected_id:
            self.clear_form()
