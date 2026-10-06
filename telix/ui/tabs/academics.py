"""Academic Records tab: score form, student search and table."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from telix.academics.structure_repository import StructureKind
from telix.core.errors import StorageError
from telix.ui.tabs.base import BaseTab, TabContext
from telix.ui.widgets.forms import add_button_row, add_form_field, add_search_entry
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
        self.selectors: dict[str, ttk.Combobox] = {}
        self._build_form()
        self._build_tools()
        self._build_table()

    # --- layout -----------------------------------------------------------
    def _build_form(self) -> None:
        form = ttk.LabelFrame(self.frame, text="Academic record", padding=12)
        form.pack(fill="x")
        for index, (field, label) in enumerate(FORM_FIELDS):
            row, column = divmod(index, 3)
            choices = ("",) if field in {"subject", "term", "academic_year"} else None
            add_form_field(form, label, self.variables[field], row, column * 2, choices)
            if choices:
                widget = form.grid_slaves(row=row, column=column * 2 + 1)[0]
                if isinstance(widget, ttk.Combobox):
                    self.selectors[field] = widget
        rows = -(-len(FORM_FIELDS) // 3)
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
        self.student_summary.set(STUDENT_PROMPT)

    # --- internals ----------------------------------------------------------
    def _form_values(self) -> dict[str, str]:
        values = {name: variable.get().strip() for name, variable in self.variables.items()}
        for field, selector in self.selectors.items():
            selected = selector.get().strip()
            if " [" in selected and selected.endswith("]"):
                label, identifier = selected.rsplit(" [", 1)
                values[field] = label
                values[f"{field}_id"] = identifier[:-1]
            else:
                values[field] = selected
                values[f"{field}_id"] = ""
        return values

    def _on_row_selected(self, _: tk.Event[Any]) -> None:
        selected_items = self.tree.selection()
        if not selected_items:
            return
        record = self.context.services.academics.get(selected_items[0])
        if not record:
            return
        self.selected_id = record["academic_id"]
        reference_fields: dict[str, tuple[StructureKind, str]] = {
            "subject": ("subject", "subject_id"),
            "term": ("term", "term_id"),
            "academic_year": ("academic_year", "academic_year_id"),
        }
        for name, variable in self.variables.items():
            value = str(record.get(name, ""))
            if name in reference_fields:
                kind, id_field = reference_fields[name]
                value = self._reference_label(kind, str(record.get(id_field, "")), value)
            variable.set(value)
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
        try:
            records = self.context.services.academics.list()
            structure = self.context.services.academic_structure
            reference_fields: dict[str, tuple[StructureKind, str, str]] = {
                "subject": ("subject", "subject_id", "subject"),
                "term": ("term", "term_id", "term"),
                "academic_year": ("academic_year", "academic_year_id", "academic_year"),
            }
            for field, (kind, id_field, label_field) in reference_fields.items():
                options = [
                    f"{item['name']} [{item[id_field]}]"
                    for item in structure.list(kind)
                    if item.get("name") and item.get(id_field)
                ]
                options.extend(
                    str(record[label_field])
                    for record in records
                    if not record.get(id_field) and record.get(label_field)
                )
                self.selectors[field]["values"] = ("", *dict.fromkeys(options))
            self._render(records)
            if not self.selected_id:
                self.clear_form()
        except StorageError as error:
            self.context.feedback.error(str(error))

    def _reference_label(self, kind: StructureKind, entity_id: str, fallback: str) -> str:
        if not entity_id:
            return fallback
        records = self.context.services.academic_structure.list(kind)
        id_field = f"{kind}_id"
        match = next((item for item in records if item.get(id_field) == entity_id), None)
        return f"{match['name']} [{entity_id}]" if match else fallback
