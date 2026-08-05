"""Telix School Management System V1 desktop application."""

from __future__ import annotations

import os
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk
from typing import Any, Callable

from academic_records import AcademicRecordService
from config import TELIX_ICON_IMAGE_PATH, TELIX_ICON_PATH
from database import StorageError
from finance import calculate_financial_summary
from students import STUDENT_FIELD_LABELS, StudentService
from teachers import TEACHER_FIELD_LABELS, TeacherService
from utils import ValidationError, format_currency, generate_id


class SchoolManagementSystem:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title("Telix School Management System V1")
        self.master.geometry("1200x780")
        self.master.minsize(1080, 680)
        self._set_window_icon()

        self.student_service = StudentService()
        self.teacher_service = TeacherService()
        self.academic_service = AcademicRecordService()
        self.selected_student_id: str | None = None
        self.selected_teacher_id: str | None = None
        self.selected_academic_id: str | None = None

        self._configure_style()
        self._create_variables()
        self._create_layout()
        self.refresh_all()

    def _set_window_icon(self) -> None:
        if TELIX_ICON_IMAGE_PATH.exists():
            try:
                self.icon_image = tk.PhotoImage(file=str(TELIX_ICON_IMAGE_PATH))
                self.master.iconphoto(True, self.icon_image)
            except tk.TclError:
                pass
        if os.name == "nt" and TELIX_ICON_PATH.exists():
            try:
                self.master.iconbitmap(str(TELIX_ICON_PATH))
            except tk.TclError:
                pass

    def _configure_style(self) -> None:
        style = ttk.Style(self.master)
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="#12355B")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground="#506784")
        style.configure("Metric.TLabel", font=("Segoe UI", 16, "bold"), foreground="#12355B")
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TNotebook.Tab", padding=(14, 8), font=("Segoe UI", 10, "bold"))

    def _create_variables(self) -> None:
        self.student_vars = {
            field_name: tk.StringVar()
            for field_name in STUDENT_FIELD_LABELS
        }
        self.teacher_vars = {
            field_name: tk.StringVar()
            for field_name in TEACHER_FIELD_LABELS
        }
        self.academic_vars = {
            field_name: tk.StringVar()
            for field_name in ("student_id", "subject", "score", "term", "academic_year")
        }
        self.student_search_id = tk.StringVar()
        self.student_class_filter = tk.StringVar()
        self.teacher_search_id = tk.StringVar()
        self.academic_search_student_id = tk.StringVar()
        self.academic_student_name = tk.StringVar(value="Search by Student ID to confirm the student.")
        self.report_class_filter = tk.StringVar()
        self.dashboard_metrics = {
            "students": tk.StringVar(value="0"),
            "teachers": tk.StringVar(value="0"),
            "income": tk.StringVar(value=format_currency(0)),
            "result": tk.StringVar(value=format_currency(0)),
        }

    def _create_layout(self) -> None:
        container = ttk.Frame(self.master, padding=16)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Telix School Management System", style="Title.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            container,
            text="V1 · Student, teacher, academic, finance, and reporting workspace",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 12))

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)

        self.dashboard_tab = ttk.Frame(self.notebook, padding=16)
        self.students_tab = ttk.Frame(self.notebook, padding=12)
        self.teachers_tab = ttk.Frame(self.notebook, padding=12)
        self.academic_tab = ttk.Frame(self.notebook, padding=12)
        self.reports_tab = ttk.Frame(self.notebook, padding=12)
        self.finance_tab = ttk.Frame(self.notebook, padding=16)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.students_tab, text="Students")
        self.notebook.add(self.teachers_tab, text="Teachers")
        self.notebook.add(self.academic_tab, text="Academic Records")
        self.notebook.add(self.reports_tab, text="Reports")
        self.notebook.add(self.finance_tab, text="Finance")

        self._build_dashboard()
        self._build_student_page()
        self._build_teacher_page()
        self._build_academic_page()
        self._build_reports_page()
        self._build_finance_page()

    def _build_dashboard(self) -> None:
        ttk.Label(
            self.dashboard_tab,
            text="School overview",
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            self.dashboard_tab,
            text="Financial results use recorded student fees less recorded teacher salaries.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 16))

        cards = ttk.Frame(self.dashboard_tab)
        cards.pack(fill="x")
        card_details = (
            ("Students", "students"),
            ("Teachers", "teachers"),
            ("Expected Fee Income", "income"),
            ("Profit / Loss", "result"),
        )
        for index, (label, metric_key) in enumerate(card_details):
            card = ttk.LabelFrame(cards, text=label, padding=18)
            card.grid(row=0, column=index, padx=(0, 12) if index < 3 else 0, sticky="nsew")
            ttk.Label(card, textvariable=self.dashboard_metrics[metric_key], style="Metric.TLabel").pack()
            cards.columnconfigure(index, weight=1)

        actions = ttk.LabelFrame(self.dashboard_tab, text="Quick actions", padding=16)
        actions.pack(fill="x", pady=24)
        ttk.Button(
            actions,
            text="Manage Students",
            command=lambda: self.notebook.select(self.students_tab),
        ).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(
            actions,
            text="Manage Teachers",
            command=lambda: self.notebook.select(self.teachers_tab),
        ).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(
            actions,
            text="Record Academic Score",
            command=lambda: self.notebook.select(self.academic_tab),
        ).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(actions, text="Refresh Dashboard", command=self.refresh_all).grid(row=0, column=3)

    def _build_student_page(self) -> None:
        form = ttk.LabelFrame(self.students_tab, text="Student details", padding=12)
        form.pack(fill="x")
        student_fields = (
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
        for index, (field_name, label) in enumerate(student_fields):
            self._add_form_field(
                form,
                label,
                self.student_vars[field_name],
                index // 3,
                (index % 3) * 2,
                choices=("Female", "Male", "Other") if field_name == "gender" else None,
            )

        buttons = ttk.Frame(form)
        buttons.grid(row=4, column=0, columnspan=6, sticky="w", pady=(12, 0))
        ttk.Button(buttons, text="Add Student", command=self.add_student).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Update Selected", command=self.update_student).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(buttons, text="Delete Selected", command=self.delete_student).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(buttons, text="Clear Form", command=self.clear_student_form).grid(row=0, column=3)

        tools = ttk.Frame(self.students_tab)
        tools.pack(fill="x", pady=12)
        ttk.Label(tools, text="Search Student ID").grid(row=0, column=0, sticky="w")
        ttk.Entry(tools, textvariable=self.student_search_id, width=24).grid(row=0, column=1, padx=(6, 8))
        ttk.Button(tools, text="Search", command=self.search_student).grid(row=0, column=2, padx=(0, 20))
        ttk.Label(tools, text="View class").grid(row=0, column=3, sticky="w")
        self.student_class_filter_box = ttk.Combobox(
            tools, textvariable=self.student_class_filter, width=18
        )
        self.student_class_filter_box.grid(row=0, column=4, padx=(6, 8))
        ttk.Button(tools, text="Filter", command=self.filter_students_by_class).grid(row=0, column=5, padx=(0, 8))
        ttk.Button(tools, text="Show All", command=self.show_all_students).grid(row=0, column=6)

        tree_frame = ttk.Frame(self.students_tab)
        tree_frame.pack(fill="both", expand=True)
        self.student_tree = self._create_tree(
            tree_frame,
            ("student_id", "name", "class_name", "phone", "parent_name", "fees"),
            (140, 210, 90, 140, 200, 110),
        )
        self.student_tree.bind("<<TreeviewSelect>>", self._load_selected_student)

    def _build_teacher_page(self) -> None:
        form = ttk.LabelFrame(self.teachers_tab, text="Teacher details", padding=12)
        form.pack(fill="x")
        teacher_fields = (
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
        for index, (field_name, label) in enumerate(teacher_fields):
            self._add_form_field(
                form,
                label,
                self.teacher_vars[field_name],
                index // 3,
                (index % 3) * 2,
                choices=("Female", "Male", "Other") if field_name == "gender" else None,
            )

        buttons = ttk.Frame(form)
        buttons.grid(row=4, column=0, columnspan=6, sticky="w", pady=(12, 0))
        ttk.Button(buttons, text="Add Teacher", command=self.add_teacher).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Update Selected", command=self.update_teacher).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(buttons, text="Delete Selected", command=self.delete_teacher).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(buttons, text="Clear Form", command=self.clear_teacher_form).grid(row=0, column=3)

        tools = ttk.Frame(self.teachers_tab)
        tools.pack(fill="x", pady=12)
        ttk.Label(tools, text="Search Teacher ID").grid(row=0, column=0, sticky="w")
        ttk.Entry(tools, textvariable=self.teacher_search_id, width=24).grid(row=0, column=1, padx=(6, 8))
        ttk.Button(tools, text="Search", command=self.search_teacher).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(tools, text="Show All", command=self.refresh_teachers).grid(row=0, column=3)

        tree_frame = ttk.Frame(self.teachers_tab)
        tree_frame.pack(fill="both", expand=True)
        self.teacher_tree = self._create_tree(
            tree_frame,
            ("teacher_id", "name", "class_name", "phone", "email", "salary"),
            (140, 210, 150, 140, 240, 110),
        )
        self.teacher_tree.bind("<<TreeviewSelect>>", self._load_selected_teacher)

    def _build_academic_page(self) -> None:
        form = ttk.LabelFrame(self.academic_tab, text="Academic record", padding=12)
        form.pack(fill="x")
        academic_fields = (
            ("student_id", "Student ID"),
            ("subject", "Subject"),
            ("score", "Score (0-100)"),
            ("term", "Term"),
            ("academic_year", "Academic year"),
        )
        for index, (field_name, label) in enumerate(academic_fields):
            self._add_form_field(
                form,
                label,
                self.academic_vars[field_name],
                index // 3,
                (index % 3) * 2,
            )
        ttk.Label(form, textvariable=self.academic_student_name, style="Subtitle.TLabel").grid(
            row=2, column=0, columnspan=6, sticky="w", pady=(8, 0)
        )

        buttons = ttk.Frame(form)
        buttons.grid(row=3, column=0, columnspan=6, sticky="w", pady=(12, 0))
        ttk.Button(buttons, text="Add Score", command=self.add_academic_record).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Update Selected", command=self.update_academic_record).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(buttons, text="Delete Selected", command=self.delete_academic_record).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(buttons, text="Clear Form", command=self.clear_academic_form).grid(row=0, column=3)

        tools = ttk.Frame(self.academic_tab)
        tools.pack(fill="x", pady=12)
        ttk.Label(tools, text="Search Student ID").grid(row=0, column=0, sticky="w")
        ttk.Entry(tools, textvariable=self.academic_search_student_id, width=24).grid(row=0, column=1, padx=(6, 8))
        ttk.Button(tools, text="Search", command=self.search_academic_student).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(tools, text="Show All", command=self.refresh_academic_records).grid(row=0, column=3)

        tree_frame = ttk.Frame(self.academic_tab)
        tree_frame.pack(fill="both", expand=True)
        self.academic_tree = self._create_tree(
            tree_frame,
            ("academic_id", "student_id", "subject", "score", "term", "academic_year"),
            (140, 140, 220, 80, 110, 140),
        )
        self.academic_tree.bind("<<TreeviewSelect>>", self._load_selected_academic_record)

    def _build_reports_page(self) -> None:
        tools = ttk.Frame(self.reports_tab)
        tools.pack(fill="x", pady=(0, 10))
        ttk.Label(tools, text="Filter linked student and academic reports by class").grid(
            row=0, column=0, sticky="w"
        )
        self.report_class_filter_box = ttk.Combobox(
            tools, textvariable=self.report_class_filter, width=20
        )
        self.report_class_filter_box.grid(row=0, column=1, padx=(8, 8))
        ttk.Button(tools, text="Refresh Reports", command=self.refresh_reports).grid(row=0, column=2)

        report_notebook = ttk.Notebook(self.reports_tab)
        report_notebook.pack(fill="both", expand=True)
        student_report = ttk.Frame(report_notebook, padding=8)
        teacher_report = ttk.Frame(report_notebook, padding=8)
        academic_report = ttk.Frame(report_notebook, padding=8)
        report_notebook.add(student_report, text="Student & Parent Details")
        report_notebook.add(teacher_report, text="Teacher Details")
        report_notebook.add(academic_report, text="Academic Records")

        self.report_student_tree = self._create_tree(
            student_report,
            ("student_id", "name", "class_name", "parent_name", "parent_phone", "email"),
            (140, 200, 100, 200, 150, 230),
        )
        self.report_teacher_tree = self._create_tree(
            teacher_report,
            ("teacher_id", "name", "class_name", "phone", "email", "emergency_contact"),
            (140, 200, 150, 140, 240, 160),
        )
        self.report_academic_tree = self._create_tree(
            academic_report,
            ("student_id", "student_name", "class_name", "subject", "score", "term", "academic_year"),
            (140, 180, 100, 180, 80, 100, 130),
        )

    def _build_finance_page(self) -> None:
        ttk.Label(
            self.finance_tab,
            text="Profit / Loss Calculation",
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            self.finance_tab,
            text="Expected fee income minus total recorded teacher salaries.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 16))
        self.finance_values = {
            "fee_income": tk.StringVar(value=format_currency(0)),
            "salary_expense": tk.StringVar(value=format_currency(0)),
            "profit_or_loss": tk.StringVar(value=format_currency(0)),
        }
        finance_grid = ttk.Frame(self.finance_tab)
        finance_grid.pack(fill="x")
        for index, (label, key) in enumerate(
            (
                ("Expected Fee Income", "fee_income"),
                ("Teacher Salary Expense", "salary_expense"),
                ("Profit / Loss", "profit_or_loss"),
            )
        ):
            card = ttk.LabelFrame(finance_grid, text=label, padding=20)
            card.grid(row=0, column=index, padx=(0, 12) if index < 2 else 0, sticky="nsew")
            ttk.Label(card, textvariable=self.finance_values[key], style="Metric.TLabel").pack()
            finance_grid.columnconfigure(index, weight=1)
        ttk.Button(self.finance_tab, text="Recalculate", command=self.refresh_finance).pack(
            anchor="w", pady=20
        )

    def _add_form_field(
        self,
        parent: ttk.LabelFrame,
        label: str,
        variable: tk.StringVar,
        row: int,
        column: int,
        choices: tuple[str, ...] | None = None,
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", padx=(0, 6), pady=5)
        if choices:
            widget: ttk.Entry | ttk.Combobox = ttk.Combobox(
                parent, textvariable=variable, values=choices, state="readonly", width=24
            )
        else:
            widget = ttk.Entry(parent, textvariable=variable, width=27)
        widget.grid(row=row, column=column + 1, sticky="ew", padx=(0, 14), pady=5)
        parent.columnconfigure(column + 1, weight=1)

    @staticmethod
    def _create_tree(
        parent: ttk.Frame,
        columns: tuple[str, ...],
        widths: tuple[int, ...],
    ) -> ttk.Treeview:
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for column, width in zip(columns, widths, strict=True):
            tree.heading(column, text=column.replace("_", " ").title())
            tree.column(column, width=width, minwidth=80, anchor="w")
        vertical_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        horizontal_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
        tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )
        tree.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        return tree

    def _student_values(self) -> dict[str, str]:
        return {field_name: variable.get() for field_name, variable in self.student_vars.items()}

    def _teacher_values(self) -> dict[str, str]:
        return {field_name: variable.get() for field_name, variable in self.teacher_vars.items()}

    def _academic_values(self) -> dict[str, str]:
        return {field_name: variable.get() for field_name, variable in self.academic_vars.items()}

    def add_student(self) -> None:
        self._run_operation(
            lambda: self.student_service.add(self._student_values()),
            "Student added successfully.",
            self._after_student_change,
        )

    def update_student(self) -> None:
        if not self.selected_student_id:
            self._show_error("Select a student record from the table before updating it.")
            return
        self._run_operation(
            lambda: self.student_service.update(self.selected_student_id or "", self._student_values()),
            "Student record updated successfully.",
            self._after_student_change,
        )

    def delete_student(self) -> None:
        student_id = self.selected_student_id or self.student_vars["student_id"].get().strip()
        if not student_id:
            self._show_error("Select or search for a student by Student ID before deleting it.")
            return
        student = self.student_service.get(student_id)
        if not student:
            self._show_error("Student record not found. Search by Student ID first.")
            return
        if not messagebox.askyesno(
            "Delete Student",
            f"Delete {student['name']} ({student['student_id']}) and linked academic records?",
            parent=self.master,
        ):
            return

        def delete_record() -> None:
            self.academic_service.delete_for_student(student_id)
            self.student_service.delete(student_id)

        self._run_operation(delete_record, "Student record deleted successfully.", self._after_student_change)

    def search_student(self) -> None:
        student_id = self.student_search_id.get().strip()
        if not student_id:
            self._show_error("Enter a Student ID to search.")
            return
        try:
            student = self.student_service.get(student_id)
        except StorageError as error:
            self._show_error(str(error))
            return
        if not student:
            self._show_error("No student was found with that Student ID.")
            return
        self._populate_student_form(student)
        self._render_students([student])

    def filter_students_by_class(self) -> None:
        try:
            self._render_students(self.student_service.by_class(self.student_class_filter.get()))
        except StorageError as error:
            self._show_error(str(error))

    def show_all_students(self) -> None:
        self.student_class_filter.set("")
        self.refresh_students()

    def _load_selected_student(self, _: tk.Event[Any]) -> None:
        selected_items = self.student_tree.selection()
        if not selected_items:
            return
        student = self.student_service.get(selected_items[0])
        if student:
            self._populate_student_form(student)

    def _populate_student_form(self, student: dict[str, Any]) -> None:
        self.selected_student_id = student["student_id"]
        for field_name, variable in self.student_vars.items():
            variable.set(str(student.get(field_name, "")))

    def clear_student_form(self) -> None:
        self.selected_student_id = None
        for variable in self.student_vars.values():
            variable.set("")
        self.student_vars["student_id"].set(generate_id("STU"))
        self.student_vars["medical_info"].set("None")

    def _after_student_change(self) -> None:
        self.clear_student_form()
        self.refresh_all()

    def add_teacher(self) -> None:
        self._run_operation(
            lambda: self.teacher_service.add(self._teacher_values()),
            "Teacher added successfully.",
            self._after_teacher_change,
        )

    def update_teacher(self) -> None:
        if not self.selected_teacher_id:
            self._show_error("Select a teacher record from the table before updating it.")
            return
        self._run_operation(
            lambda: self.teacher_service.update(self.selected_teacher_id or "", self._teacher_values()),
            "Teacher record updated successfully.",
            self._after_teacher_change,
        )

    def delete_teacher(self) -> None:
        teacher_id = self.selected_teacher_id or self.teacher_vars["teacher_id"].get().strip()
        if not teacher_id:
            self._show_error("Select or search for a teacher by Teacher ID before deleting it.")
            return
        try:
            teacher = self.teacher_service.get(teacher_id)
        except StorageError as error:
            self._show_error(str(error))
            return
        if not teacher:
            self._show_error("Teacher record not found. Search by Teacher ID first.")
            return
        if not messagebox.askyesno(
            "Delete Teacher",
            f"Delete {teacher['name']} ({teacher['teacher_id']})?",
            parent=self.master,
        ):
            return
        self._run_operation(
            lambda: self.teacher_service.delete(teacher_id),
            "Teacher record deleted successfully.",
            self._after_teacher_change,
        )

    def search_teacher(self) -> None:
        teacher_id = self.teacher_search_id.get().strip()
        if not teacher_id:
            self._show_error("Enter a Teacher ID to search.")
            return
        try:
            teacher = self.teacher_service.get(teacher_id)
        except StorageError as error:
            self._show_error(str(error))
            return
        if not teacher:
            self._show_error("No teacher was found with that Teacher ID.")
            return
        self._populate_teacher_form(teacher)
        self._render_teachers([teacher])

    def _load_selected_teacher(self, _: tk.Event[Any]) -> None:
        selected_items = self.teacher_tree.selection()
        if not selected_items:
            return
        teacher = self.teacher_service.get(selected_items[0])
        if teacher:
            self._populate_teacher_form(teacher)

    def _populate_teacher_form(self, teacher: dict[str, Any]) -> None:
        self.selected_teacher_id = teacher["teacher_id"]
        for field_name, variable in self.teacher_vars.items():
            variable.set(str(teacher.get(field_name, "")))

    def clear_teacher_form(self) -> None:
        self.selected_teacher_id = None
        for variable in self.teacher_vars.values():
            variable.set("")
        self.teacher_vars["teacher_id"].set(generate_id("TCH"))
        self.teacher_vars["medical_info"].set("None")

    def _after_teacher_change(self) -> None:
        self.clear_teacher_form()
        self.refresh_all()

    def add_academic_record(self) -> None:
        self._run_operation(
            lambda: self.academic_service.add(
                self._academic_values(), lambda student_id: self.student_service.get(student_id) is not None
            ),
            "Academic record added successfully.",
            self._after_academic_change,
        )

    def update_academic_record(self) -> None:
        if not self.selected_academic_id:
            self._show_error("Select an academic record from the table before updating it.")
            return
        self._run_operation(
            lambda: self.academic_service.update(
                self.selected_academic_id or "",
                self._academic_values(),
                lambda student_id: self.student_service.get(student_id) is not None,
            ),
            "Academic record updated successfully.",
            self._after_academic_change,
        )

    def delete_academic_record(self) -> None:
        if not self.selected_academic_id:
            self._show_error("Select an academic record from the table before deleting it.")
            return
        if not messagebox.askyesno(
            "Delete Academic Record",
            "Delete the selected academic record?",
            parent=self.master,
        ):
            return
        self._run_operation(
            lambda: self.academic_service.delete(self.selected_academic_id or ""),
            "Academic record deleted successfully.",
            self._after_academic_change,
        )

    def search_academic_student(self) -> None:
        student_id = self.academic_search_student_id.get().strip()
        if not student_id:
            self._show_error("Enter a Student ID to search academic records.")
            return
        try:
            student = self.student_service.get(student_id)
            if not student:
                self._show_error("No student was found with that Student ID.")
                return
            self.academic_vars["student_id"].set(student["student_id"])
            self.academic_student_name.set(f"Student: {student['name']} · Class: {student['class_name']}")
            self._render_academic_records(self.academic_service.for_student(student_id))
        except StorageError as error:
            self._show_error(str(error))

    def _load_selected_academic_record(self, _: tk.Event[Any]) -> None:
        selected_items = self.academic_tree.selection()
        if not selected_items:
            return
        record = self.academic_service.get(selected_items[0])
        if record:
            self.selected_academic_id = record["academic_id"]
            for field_name, variable in self.academic_vars.items():
                variable.set(str(record.get(field_name, "")))
            student = self.student_service.get(record["student_id"])
            if student:
                self.academic_student_name.set(
                    f"Student: {student['name']} · Class: {student['class_name']}"
                )

    def clear_academic_form(self) -> None:
        self.selected_academic_id = None
        for variable in self.academic_vars.values():
            variable.set("")
        self.academic_vars["term"].set("Term 1")
        current_year = date.today().year
        self.academic_vars["academic_year"].set(f"{current_year}/{current_year + 1}")
        self.academic_student_name.set("Search by Student ID to confirm the student.")

    def _after_academic_change(self) -> None:
        self.clear_academic_form()
        self.refresh_all()

    def refresh_all(self) -> None:
        try:
            self.refresh_students()
            self.refresh_teachers()
            self.refresh_academic_records()
            self.refresh_reports()
            self.refresh_finance()
        except StorageError as error:
            self._show_error(str(error))

    def refresh_students(self) -> None:
        students = self.student_service.list()
        self._render_students(students)
        classes = self.student_service.classes()
        self.student_class_filter_box["values"] = classes
        self.report_class_filter_box["values"] = classes
        if not self.selected_student_id:
            self.clear_student_form()

    def refresh_teachers(self) -> None:
        self._render_teachers(self.teacher_service.list())
        if not self.selected_teacher_id:
            self.clear_teacher_form()

    def refresh_academic_records(self) -> None:
        self._render_academic_records(self.academic_service.list())
        if not self.selected_academic_id:
            self.clear_academic_form()

    def refresh_reports(self) -> None:
        students = self.student_service.by_class(self.report_class_filter.get())
        teachers = self.teacher_service.list()
        student_names = {record["student_id"]: record for record in students}
        academic_records = [
            record
            for record in self.academic_service.list()
            if record["student_id"] in student_names
        ]
        self._render_tree(
            self.report_student_tree,
            students,
            ("student_id", "name", "class_name", "parent_name", "parent_phone", "email"),
        )
        self._render_tree(
            self.report_teacher_tree,
            teachers,
            ("teacher_id", "name", "class_name", "phone", "email", "emergency_contact"),
        )
        self.report_academic_tree.delete(*self.report_academic_tree.get_children())
        for record in academic_records:
            student = student_names[record["student_id"]]
            self.report_academic_tree.insert(
                "",
                "end",
                iid=record["academic_id"],
                values=(
                    record["student_id"],
                    student["name"],
                    student["class_name"],
                    record["subject"],
                    record["score"],
                    record["term"],
                    record["academic_year"],
                ),
            )

    def refresh_finance(self) -> None:
        students = self.student_service.list()
        teachers = self.teacher_service.list()
        summary = calculate_financial_summary(students, teachers)
        self.finance_values["fee_income"].set(format_currency(summary["fee_income"]))
        self.finance_values["salary_expense"].set(format_currency(summary["salary_expense"]))
        self.finance_values["profit_or_loss"].set(format_currency(summary["profit_or_loss"]))
        self.dashboard_metrics["students"].set(str(len(students)))
        self.dashboard_metrics["teachers"].set(str(len(teachers)))
        self.dashboard_metrics["income"].set(format_currency(summary["fee_income"]))
        self.dashboard_metrics["result"].set(format_currency(summary["profit_or_loss"]))

    def _render_students(self, students: list[dict[str, Any]]) -> None:
        self.student_tree.delete(*self.student_tree.get_children())
        for student in students:
            self.student_tree.insert(
                "",
                "end",
                iid=student["student_id"],
                values=(
                    student["student_id"],
                    student["name"],
                    student["class_name"],
                    student["phone"],
                    student["parent_name"],
                    format_currency(float(student["fees"] or 0)),
                ),
            )

    def _render_teachers(self, teachers: list[dict[str, Any]]) -> None:
        self.teacher_tree.delete(*self.teacher_tree.get_children())
        for teacher in teachers:
            self.teacher_tree.insert(
                "",
                "end",
                iid=teacher["teacher_id"],
                values=(
                    teacher["teacher_id"],
                    teacher["name"],
                    teacher["class_name"],
                    teacher["phone"],
                    teacher["email"],
                    format_currency(float(teacher["salary"] or 0)),
                ),
            )

    def _render_academic_records(self, records: list[dict[str, Any]]) -> None:
        self._render_tree(
            self.academic_tree,
            records,
            ("academic_id", "student_id", "subject", "score", "term", "academic_year"),
        )

    @staticmethod
    def _render_tree(
        tree: ttk.Treeview,
        records: list[dict[str, Any]],
        fields: tuple[str, ...],
    ) -> None:
        tree.delete(*tree.get_children())
        for record in records:
            record_id = record.get(fields[0], "")
            if not record_id:
                continue
            tree.insert("", "end", iid=str(record_id), values=tuple(record.get(field, "") for field in fields))

    def _run_operation(
        self,
        operation: Callable[[], Any],
        success_message: str,
        on_success: Callable[[], None],
    ) -> None:
        try:
            operation()
        except (ValidationError, StorageError) as error:
            self._show_error(str(error))
            return
        except Exception as error:
            self._show_error(f"The operation could not be completed: {error}")
            return
        on_success()
        messagebox.showinfo("Success", success_message, parent=self.master)

    def _show_error(self, message: str) -> None:
        messagebox.showerror("Telix School Management System", message, parent=self.master)


def main() -> None:
    root = tk.Tk()
    SchoolManagementSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()
