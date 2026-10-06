"""Linked student, teacher, academic, attendance, and finance reports."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Any

from telix.attendance.rules import ATTENDANCE_STATUSES
from telix.authentication.roles import (
    REPORTS_OPERATIONAL,
    REPORTS_FINANCE,
    REPORTS_OWN,
    REPORTS_TEACHING,
    STUDENT,
)
from telix.core.errors import StorageError, ValidationError
from telix.core.formatting import format_currency
from telix.core.numbers import as_amount
from telix.reports.csv_export import write_csv_report
from telix.students.schema import STUDENT_STATUSES
from telix.ui.tabs.base import BaseTab, TabContext
from telix.ui.widgets.tables import create_tree, render_records, replace_rows

STUDENT_COLUMNS = (
    "student_id",
    "name",
    "class_name",
    "status",
    "parent_name",
    "parent_phone",
    "email",
)
STUDENT_WIDTHS = (120, 180, 90, 90, 170, 130, 190)
TEACHER_COLUMNS = ("teacher_id", "name", "class_name", "phone", "email", "emergency_contact")
TEACHER_WIDTHS = (140, 200, 150, 140, 240, 160)
ACADEMIC_COLUMNS = (
    "student_id",
    "student_name",
    "current_class",
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
        self.student_status_filter = tk.StringVar(value="All")
        self.student_id_filter = tk.StringVar()
        self.teacher_filter = tk.StringVar()
        self.academic_query = tk.StringVar()
        self.attendance_status_filter = tk.StringVar(value="All")
        self.attendance_start = tk.StringVar()
        self.attendance_end = tk.StringVar()
        self.finance_category_filter = tk.StringVar(value="All")
        self.finance_start = tk.StringVar()
        self.finance_end = tk.StringVar()
        self.attendance_summary = tk.StringVar(value="No attendance records.")
        self.finance_summary = tk.StringVar(value="No financial ledger entries.")
        self._build_toolbar()
        self._build_report_tables()

    def _build_toolbar(self) -> None:
        tools = ttk.Frame(self.frame)
        self.toolbar = tools
        tools.pack(fill="x", pady=(0, 10))
        ttk.Label(tools, text="Filter student and academic reports by class").grid(
            row=0, column=0, sticky="w"
        )
        self.class_filter_box = ttk.Combobox(
            tools, textvariable=self.class_filter, width=20, state="readonly"
        )
        self.class_filter_box.grid(row=0, column=1, padx=(8, 8))
        ttk.Label(tools, text="Student status").grid(row=0, column=2, sticky="w")
        self.student_status_box = ttk.Combobox(
            tools,
            textvariable=self.student_status_filter,
            values=("All", *STUDENT_STATUSES),
            state="readonly",
            width=14,
        )
        self.student_status_box.grid(row=0, column=3, padx=(8, 8))
        ttk.Button(tools, text="Refresh Reports", command=self.refresh).grid(
            row=0, column=4, sticky="w"
        )
        student_id_entry = ttk.Entry(tools, textvariable=self.student_id_filter, width=16)
        teacher_entry = ttk.Entry(tools, textvariable=self.teacher_filter, width=18)
        ttk.Label(tools, text="Student ID").grid(row=1, column=0, sticky="w", pady=(8, 0))
        student_id_entry.grid(row=1, column=1, sticky="w", padx=(6, 16), pady=(8, 0))
        ttk.Label(tools, text="Teacher ID/name").grid(row=1, column=2, sticky="w", pady=(8, 0))
        teacher_entry.grid(row=1, column=3, sticky="w", padx=(6, 0), pady=(8, 0))
        ttk.Label(tools, text="Academic subject/term/year").grid(
            row=2, column=0, sticky="w", pady=(8, 0)
        )
        ttk.Entry(tools, textvariable=self.academic_query, width=36).grid(
            row=2, column=1, columnspan=3, sticky="w", padx=(8, 8), pady=(8, 0)
        )
        ttk.Label(tools, text="Attendance status").grid(row=3, column=0, sticky="w", pady=(8, 0))
        ttk.Combobox(
            tools,
            textvariable=self.attendance_status_filter,
            values=("All", *ATTENDANCE_STATUSES),
            state="readonly",
            width=12,
        ).grid(row=3, column=1, sticky="w", padx=(6, 16), pady=(8, 0))
        ttk.Label(tools, text="From").grid(row=3, column=2, sticky="e", pady=(8, 0))
        ttk.Entry(tools, textvariable=self.attendance_start, width=12).grid(
            row=3, column=3, sticky="w", padx=(6, 16), pady=(8, 0)
        )
        ttk.Label(tools, text="To").grid(row=3, column=4, sticky="e", pady=(8, 0))
        ttk.Entry(tools, textvariable=self.attendance_end, width=12).grid(
            row=3, column=5, sticky="w", padx=(6, 0), pady=(8, 0)
        )
        ttk.Label(tools, text="Finance category").grid(row=4, column=0, sticky="w", pady=(8, 0))
        self.finance_category_box = ttk.Combobox(
            tools, textvariable=self.finance_category_filter, state="readonly", width=18
        )
        self.finance_category_box.grid(row=4, column=1, sticky="w", padx=(8, 16), pady=(8, 0))
        ttk.Label(tools, text="From").grid(row=4, column=2, sticky="e", pady=(8, 0))
        ttk.Entry(tools, textvariable=self.finance_start, width=12).grid(
            row=4, column=3, sticky="w", padx=(6, 16), pady=(8, 0)
        )
        ttk.Label(tools, text="To").grid(row=4, column=4, sticky="e", pady=(8, 0))
        ttk.Entry(tools, textvariable=self.finance_end, width=12).grid(
            row=4, column=5, sticky="w", padx=(6, 0), pady=(8, 0)
        )

    def _build_report_tables(self) -> None:
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True)
        authorization = self.context.services.authorization
        if any(
            authorization.allows(capability)
            for capability in (REPORTS_OPERATIONAL, REPORTS_TEACHING, REPORTS_OWN)
        ):
            self.student_columns = (
                ("student_id", "name", "class_name", "status")
                if authorization.role == STUDENT
                else ("student_id", "name", "class_name", "status")
                if authorization.allows(REPORTS_TEACHING)
                and not authorization.allows(REPORTS_OPERATIONAL)
                else STUDENT_COLUMNS
            )
            self.student_widths = (
                (140, 220, 120, 120) if len(self.student_columns) == 4 else STUDENT_WIDTHS
            )
            self.student_tree = self._build_page(
                "Student Details", self.student_columns, self.student_widths, "students"
            )
        if authorization.allows(REPORTS_OPERATIONAL):
            self.teacher_tree = self._build_page(
                "Teacher Details", TEACHER_COLUMNS, TEACHER_WIDTHS, "teachers"
            )
        if any(
            authorization.allows(capability)
            for capability in (REPORTS_OPERATIONAL, REPORTS_TEACHING, REPORTS_OWN)
        ):
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
        if authorization.allows(REPORTS_FINANCE):
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
            authorization = services.authorization
            if authorization.allows(REPORTS_FINANCE) and not authorization.allows(
                REPORTS_OPERATIONAL
            ):
                if authorization.allows(REPORTS_FINANCE):
                    categories = sorted(
                        {row["category"] for row in services.finance.list("expense")}
                    )
                    category_options = ["All", *categories]
                    self.finance_category_box["values"] = category_options
                    if self.finance_category_filter.get() not in category_options:
                        self.finance_category_filter.set("All")
                self._render_finance()
                return
            self.class_filter_box["values"] = ["All", *services.students.classes()]
            if self.class_filter.get() not in self.class_filter_box["values"]:
                self.class_filter.set("All")
            if self.student_status_filter.get() not in self.student_status_box["values"]:
                self.student_status_filter.set("All")
            selected_class = (
                "" if self.class_filter.get() in {"", "All"} else self.class_filter.get()
            )
            selected_status = (
                ""
                if self.student_status_filter.get() == "All"
                else self.student_status_filter.get()
            )
            students = services.students.by_status(selected_status)
            student_query = self.student_id_filter.get().strip().casefold()
            if student_query:
                students = [
                    student
                    for student in students
                    if student_query in student["student_id"].casefold()
                ]
            if selected_class:
                students = [
                    student
                    for student in students
                    if student["class_name"].casefold() == selected_class.casefold()
                ]
            if authorization.allows(REPORTS_OPERATIONAL):
                teachers = services.teachers.list()
                teacher_query = self.teacher_filter.get().strip().casefold()
                if teacher_query:
                    teachers = [
                        teacher
                        for teacher in teachers
                        if teacher_query in teacher["teacher_id"].casefold()
                        or teacher_query in teacher["name"].casefold()
                    ]
                render_records(self.teacher_tree, teachers, TEACHER_COLUMNS)
            if hasattr(self, "student_tree"):
                render_records(self.student_tree, students, self.student_columns)
            academic_query = self.academic_query.get().strip().casefold()
            self._render_academic_report(students, academic_query)
            self._render_assessments(students, academic_query)
            self._render_attendance(
                students,
                selected_class,
                self.attendance_start.get().strip(),
                self.attendance_end.get().strip(),
                ""
                if self.attendance_status_filter.get() == "All"
                else self.attendance_status_filter.get(),
            )
            if authorization.allows(REPORTS_FINANCE):
                categories = sorted({row["category"] for row in services.finance.list("expense")})
                category_options = ["All", *categories]
                self.finance_category_box["values"] = category_options
                if self.finance_category_filter.get() not in category_options:
                    self.finance_category_filter.set("All")
                self._render_finance()
        except (StorageError, ValidationError) as error:
            self.context.feedback.error(str(error))

    def _render_academic_report(self, students: list[dict[str, Any]], query: str = "") -> None:
        students_by_id = {str(student["student_id"]).casefold(): student for student in students}
        rows = (
            (
                record["academic_id"],
                self._academic_row(record, students_by_id[str(record["student_id"]).casefold()]),
            )
            for record in self.context.services.academics.list()
            if str(record["student_id"]).casefold() in students_by_id
            and (
                not query
                or any(
                    query in str(record.get(field, "")).casefold()
                    for field in ("subject", "term", "academic_year")
                )
            )
        )
        replace_rows(self.academic_tree, rows)

    def _render_assessments(self, students: list[dict[str, Any]], query: str = "") -> None:
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
                and (
                    not query
                    or any(
                        query in str(record.get(field, "")).casefold()
                        for field in ("subject", "term", "academic_year")
                    )
                )
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

    def _render_attendance(
        self,
        students: list[dict[str, Any]],
        class_name: str,
        start_date: str = "",
        end_date: str = "",
        status: str = "",
    ) -> None:
        student_names = {
            str(student["student_id"]).casefold(): student["name"] for student in students
        }
        classes = {
            str(item["class_id"]).casefold(): item["name"]
            for item in self.context.services.academic_structure.list("class")
        }
        records = self.context.services.attendance.list(
            start_date=start_date,
            end_date=end_date,
            status=status,
        )
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
        start_date = self.finance_start.get().strip()
        end_date = self.finance_end.get().strip()
        category = (
            ""
            if self.finance_category_filter.get() == "All"
            else self.finance_category_filter.get()
        )
        student_id = self.student_id_filter.get().strip()
        payments = ledger.list(
            "payment",
            student_id=student_id,
            start_date=start_date,
            end_date=end_date,
        )
        expenses = ledger.list(
            "expense",
            start_date=start_date,
            end_date=end_date,
            category=category,
        )
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
            self.context.services.students.list(),
            self.context.services.teachers.salary_records(),
        )
        self.finance_summary.set(
            f"School-to-date expected: {format_currency(summary['expected_fee_income'])} · "
            f"Received: {format_currency(summary['received_income'])} · "
            f"Outstanding: {format_currency(summary['outstanding_balances'])} · "
            f"Credit: {format_currency(summary['student_credit'])} · "
            f"Profit / Loss: {format_currency(summary['profit_or_loss'])}"
        )

    def export(self, report_name: str) -> None:
        tree_by_name = {
            name: getattr(self, attribute)
            for name, attribute in (
                ("students", "student_tree"),
                ("teachers", "teacher_tree"),
                ("academic-records", "academic_tree"),
                ("assessments", "assessment_tree"),
                ("attendance", "attendance_tree"),
                ("finance", "finance_tree"),
            )
            if hasattr(self, attribute)
        }
        tree = tree_by_name[report_name]
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
                (
                    tree.item(item_id, "values")
                    for item_id in tree.get_children()
                    if "empty" not in tree.item(item_id, "tags")
                ),
            )
        except OSError as error:
            self.context.feedback.error(f"Could not export this report: {error}")
            return
        self.context.feedback.success("Report exported successfully.")
