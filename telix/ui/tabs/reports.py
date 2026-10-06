"""Linked student, teacher, academic, attendance, and finance reports."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Any

from telix.core.errors import StorageError
from telix.core.formatting import format_currency
from telix.core.numbers import as_amount
from telix.reports.csv_export import write_csv_report
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
ATTENDANCE_COLUMNS = ("attendance_date", "student_id", "student_name", "class", "status")
ATTENDANCE_WIDTHS = (130, 140, 200, 160, 110)
FINANCE_COLUMNS = ("kind", "date", "student_or_category", "amount", "description")
FINANCE_WIDTHS = (120, 120, 220, 130, 340)
ASSESSMENT_COLUMNS = ("student_id", "subject", "component", "score", "term", "academic_year")
ASSESSMENT_WIDTHS = (140, 190, 150, 90, 110, 140)


class ReportsTab(BaseTab):
    key = "reports"
    title = "Reports"

    def __init__(self, notebook: ttk.Notebook, context: TabContext) -> None:
        super().__init__(notebook, context)
        self.class_filter = tk.StringVar()
        self.attendance_summary = tk.StringVar(value="No attendance records.")
        self.finance_summary = tk.StringVar(value="No financial ledger entries.")
        self._build_toolbar()
        self._build_report_tables()

    def _build_toolbar(self) -> None:
        tools = ttk.Frame(self.frame)
        tools.pack(fill="x", pady=(0, 10))
        ttk.Label(tools, text="Filter student and academic reports by class").grid(
            row=0, column=0, sticky="w"
        )
        self.class_filter_box = ttk.Combobox(
            tools, textvariable=self.class_filter, width=20, state="readonly"
        )
        self.class_filter_box.grid(row=0, column=1, padx=(8, 8))
        ttk.Button(tools, text="Refresh Reports", command=self.refresh).grid(row=0, column=2)

    def _build_report_tables(self) -> None:
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True)
        self.student_tree = self._build_page(
            "Student & Parent Details", STUDENT_COLUMNS, STUDENT_WIDTHS, "students"
        )
        self.teacher_tree = self._build_page(
            "Teacher Details", TEACHER_COLUMNS, TEACHER_WIDTHS, "teachers"
        )
        self.academic_tree = self._build_page(
            "Academic Records", ACADEMIC_COLUMNS, ACADEMIC_WIDTHS, "academic-records"
        )
        self.assessment_tree = self._build_page(
            "Assessments", ASSESSMENT_COLUMNS, ASSESSMENT_WIDTHS, "assessments"
        )
        self.attendance_tree = self._build_page(
            "Attendance",
            ATTENDANCE_COLUMNS,
            ATTENDANCE_WIDTHS,
            "attendance",
            self.attendance_summary,
        )
        self.finance_tree = self._build_page(
            "Finance", FINANCE_COLUMNS, FINANCE_WIDTHS, "finance", self.finance_summary
        )

    def _build_page(
        self,
        title: str,
        columns: tuple[str, ...],
        widths: tuple[int, ...],
        export_name: str,
        summary: tk.StringVar | None = None,
    ) -> ttk.Treeview:
        page = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(page, text=title)
        toolbar = ttk.Frame(page)
        toolbar.pack(fill="x", pady=(0, 8))

        def export_report(name: str = export_name) -> None:
            self.export(name)

        ttk.Button(
            toolbar,
            text=f"Export {title} CSV",
            command=export_report,
        ).pack(anchor="e")
        if summary is not None:
            ttk.Label(page, textvariable=summary, style="Subtitle.TLabel").pack(
                anchor="w", pady=(0, 8)
            )
        tree_frame = ttk.Frame(page)
        tree_frame.pack(fill="both", expand=True)
        return create_tree(tree_frame, columns, widths)

    def refresh(self) -> None:
        try:
            services = self.context.services
            students_all = services.students.list()
            self.class_filter_box["values"] = ["All", *services.students.classes()]
            if self.class_filter.get() not in self.class_filter_box["values"]:
                self.class_filter.set("All")
            selected_class = (
                "" if self.class_filter.get() in {"", "All"} else self.class_filter.get()
            )
            students = services.students.by_class(selected_class)
            render_records(self.student_tree, students, STUDENT_COLUMNS)
            render_records(self.teacher_tree, services.teachers.list(), TEACHER_COLUMNS)
            self._render_academic_report(students)
            self._render_assessments(students)
            self._render_attendance(students_all, selected_class)
            self._render_finance()
        except StorageError as error:
            self.context.feedback.error(str(error))

    def _render_academic_report(self, students: list[dict[str, Any]]) -> None:
        students_by_id = {str(student["student_id"]).casefold(): student for student in students}
        rows = (
            (
                record["academic_id"],
                self._academic_row(record, students_by_id[str(record["student_id"]).casefold()]),
            )
            for record in self.context.services.academics.list()
            if str(record["student_id"]).casefold() in students_by_id
        )
        replace_rows(self.academic_tree, rows)

    def _render_assessments(self, students: list[dict[str, Any]]) -> None:
        visible_ids = {str(student["student_id"]).casefold() for student in students}
        replace_rows(
            self.assessment_tree,
            (
                (
                    record["assessment_id"],
                    tuple(record[column] for column in ASSESSMENT_COLUMNS),
                )
                for record in self.context.services.assessments.list()
                if str(record["student_id"]).casefold() in visible_ids
            ),
        )

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

    def _render_attendance(self, students: list[dict[str, Any]], class_name: str) -> None:
        student_names = {
            str(student["student_id"]).casefold(): student["name"] for student in students
        }
        classes = {
            str(item["class_id"]).casefold(): item["name"]
            for item in self.context.services.academic_structure.list("class")
        }
        records = self.context.services.attendance.list()
        visible = [
            record
            for record in records
            if str(record["student_id"]).casefold() in student_names
            and (
                not class_name
                or classes.get(str(record["class_id"]).casefold(), "").casefold()
                == class_name.casefold()
            )
        ]
        replace_rows(
            self.attendance_tree,
            (
                (
                    record["attendance_id"],
                    (
                        record["attendance_date"],
                        record["student_id"],
                        student_names[str(record["student_id"]).casefold()],
                        classes.get(str(record["class_id"]).casefold(), "Unknown class"),
                        record["status"],
                    ),
                )
                for record in visible
            ),
        )
        summary = self.context.services.attendance.summary(visible)
        self.attendance_summary.set(
            f"Records: {summary['total']} · Present: {summary['present']} · "
            f"Absent: {summary['absent']} · Late: {summary['late']} · "
            f"Excused: {summary['excused']} · Attendance: "
            f"{summary['attendance_percentage']}%"
        )

    def _render_finance(self) -> None:
        ledger = self.context.services.finance
        payments = ledger.list("payment")
        expenses = ledger.list("expense")
        students = {
            str(student["student_id"]).casefold(): student["name"]
            for student in self.context.services.students.list()
        }
        records: list[tuple[str, tuple[Any, ...]]] = []
        for payment in payments:
            records.append(
                (
                    payment["payment_id"],
                    (
                        "Payment",
                        payment["payment_date"],
                        students.get(payment["student_id"].casefold(), "Unknown student"),
                        format_currency(as_amount(payment["amount"])),
                        payment.get("description", ""),
                    ),
                )
            )
        for expense in expenses:
            records.append(
                (
                    expense["expense_id"],
                    (
                        "Expense",
                        expense["expense_date"],
                        expense["category"],
                        format_currency(as_amount(expense["amount"])),
                        expense["description"],
                    ),
                )
            )
        replace_rows(self.finance_tree, sorted(records, key=lambda row: row[1][1], reverse=True))
        summary = ledger.summary(
            self.context.services.students.list(), self.context.services.teachers.list()
        )
        self.finance_summary.set(
            f"Expected: {format_currency(summary['expected_fee_income'])} · "
            f"Received: {format_currency(summary['received_income'])} · "
            f"Outstanding: {format_currency(summary['outstanding_balances'])} · "
            f"Credit: {format_currency(summary['student_credit'])} · "
            f"Profit / Loss: {format_currency(summary['profit_or_loss'])}"
        )

    def export(self, report_name: str) -> None:
        tree = {
            "students": self.student_tree,
            "teachers": self.teacher_tree,
            "academic-records": self.academic_tree,
            "assessments": self.assessment_tree,
            "attendance": self.attendance_tree,
            "finance": self.finance_tree,
        }[report_name]
        target = filedialog.asksaveasfilename(
            parent=self.frame,
            title="Export report",
            defaultextension=".csv",
            filetypes=(("CSV files", "*.csv"),),
            initialfile=f"telix-{report_name}.csv",
        )
        if not target:
            return
        try:
            write_csv_report(
                Path(target),
                [tree.heading(column, "text") for column in tree["columns"]],
                (tree.item(item_id, "values") for item_id in tree.get_children()),
            )
        except OSError as error:
            self.context.feedback.error(f"Could not export this report: {error}")
            return
        self.context.feedback.success("Report exported successfully.")
