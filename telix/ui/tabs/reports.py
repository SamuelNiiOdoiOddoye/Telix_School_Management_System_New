"""Reports tab: linked student, teacher and academic views."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from telix.ui.tabs.base import BaseTab, TabContext
from telix.ui.widgets.tables import create_tree, render_records, replace_rows

STUDENT_COLUMNS = ("student_id", "name", "class_name", "parent_name", "parent_phone", "email")
STUDENT_WIDTHS = (140, 200, 100, 200, 150, 230)
TEACHER_COLUMNS = ("teacher_id", "name", "class_name", "phone", "email", "emergency_contact")
TEACHER_WIDTHS = (140, 200, 150, 140, 240, 160)
ACADEMIC_COLUMNS = (
    "student_id",
    "student_name",
    "class_name",
    "subject",
    "score",
    "term",
    "academic_year",
)
ACADEMIC_WIDTHS = (140, 180, 100, 180, 80, 100, 130)


class ReportsTab(BaseTab):
    key = "reports"
    title = "Reports"

    def __init__(self, notebook: ttk.Notebook, context: TabContext) -> None:
        super().__init__(notebook, context)
        self.class_filter = tk.StringVar()
        self._build_toolbar()
        self._build_report_tables()

    def _build_toolbar(self) -> None:
        tools = ttk.Frame(self.frame)
        tools.pack(fill="x", pady=(0, 10))
        ttk.Label(tools, text="Filter linked student and academic reports by class").grid(
            row=0, column=0, sticky="w"
        )
        self.class_filter_box = ttk.Combobox(tools, textvariable=self.class_filter, width=20)
        self.class_filter_box.grid(row=0, column=1, padx=(8, 8))
        ttk.Button(tools, text="Refresh Reports", command=self.refresh).grid(row=0, column=2)

    def _build_report_tables(self) -> None:
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill="both", expand=True)
        student_page = ttk.Frame(notebook, padding=8)
        teacher_page = ttk.Frame(notebook, padding=8)
        academic_page = ttk.Frame(notebook, padding=8)
        notebook.add(student_page, text="Student & Parent Details")
        notebook.add(teacher_page, text="Teacher Details")
        notebook.add(academic_page, text="Academic Records")
        self.student_tree = create_tree(student_page, STUDENT_COLUMNS, STUDENT_WIDTHS)
        self.teacher_tree = create_tree(teacher_page, TEACHER_COLUMNS, TEACHER_WIDTHS)
        self.academic_tree = create_tree(academic_page, ACADEMIC_COLUMNS, ACADEMIC_WIDTHS)

    def refresh(self) -> None:
        services = self.context.services
        self.class_filter_box["values"] = services.students.classes()
        students = services.students.by_class(self.class_filter.get())
        render_records(self.student_tree, students, STUDENT_COLUMNS)
        render_records(self.teacher_tree, services.teachers.list(), TEACHER_COLUMNS)
        self._render_academic_report(students)

    def _render_academic_report(self, students: list[dict[str, Any]]) -> None:
        students_by_id = {student["student_id"]: student for student in students}
        rows = (
            (
                record["academic_id"],
                self._academic_row(record, students_by_id[record["student_id"]]),
            )
            for record in self.context.services.academics.list()
            if record["student_id"] in students_by_id
        )
        replace_rows(self.academic_tree, rows)

    @staticmethod
    def _academic_row(record: dict[str, Any], student: dict[str, Any]) -> tuple[Any, ...]:
        return (
            record["student_id"],
            student["name"],
            student["class_name"],
            record["subject"],
            record["score"],
            record["term"],
            record["academic_year"],
        )
