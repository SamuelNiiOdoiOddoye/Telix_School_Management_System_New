"""Attendance recording, history filtering, and summary display."""

from __future__ import annotations

from datetime import date
import tkinter as tk
from tkinter import ttk
from typing import Any

from telix.attendance.rules import ATTENDANCE_STATUSES
from telix.core.errors import StorageError, ValidationError
from telix.ui.tabs.base import BaseTab, TabContext
from telix.ui.widgets.forms import add_button_row, add_form_field
from telix.ui.widgets.tables import create_tree, replace_rows

COLUMNS = (
    "attendance_id",
    "attendance_date",
    "student_id",
    "student_name",
    "class_name",
    "status",
)
WIDTHS = (130, 120, 130, 180, 150, 100)


class AttendanceTab(BaseTab):
    key = "attendance"
    title = "Attendance"

    def __init__(self, notebook: ttk.Notebook, context: TabContext) -> None:
        super().__init__(notebook, context)
        self.selected_id: str | None = None
        self.variables = {
            "student_id": tk.StringVar(),
            "attendance_date": tk.StringVar(value=date.today().isoformat()),
            "status": tk.StringVar(value=ATTENDANCE_STATUSES[0]),
        }
        self.student_filter = tk.StringVar()
        self.class_filter = tk.StringVar()
        self.date_filter = tk.StringVar(value=date.today().isoformat())
        self.summary_text = tk.StringVar(value="No attendance records for this filter.")
        self._build_form()
        self._build_filters()
        self._build_table()

    def _build_form(self) -> None:
        form = ttk.LabelFrame(self.frame, text="Record attendance", padding=12)
        form.pack(fill="x")
        fields = (
            ("student_id", "Student"),
            ("attendance_date", "Date (YYYY-MM-DD)"),
            ("status", "Status"),
        )
        self.student_box = self._add_selector(form, fields[0], 0)
        self.student_box.configure(textvariable=self.variables["student_id"])
        add_form_field(form, fields[1][1], self.variables[fields[1][0]], 0, 2)
        add_form_field(form, fields[2][1], self.variables[fields[2][0]], 0, 4, ATTENDANCE_STATUSES)
        add_button_row(
            form,
            (
                ("Record", self.add),
                ("Update Selected", self.update),
                ("Delete Selected", self.delete),
                ("Clear", self.clear),
            ),
            row=1,
        )

    @staticmethod
    def _add_selector(form: ttk.LabelFrame, field: tuple[str, str], column: int) -> ttk.Combobox:
        ttk.Label(form, text=field[1]).grid(row=0, column=column, sticky="w", padx=(0, 6), pady=5)
        box = ttk.Combobox(form, state="readonly", width=24)
        box.grid(row=0, column=column + 1, sticky="ew", padx=(0, 14), pady=5)
        form.columnconfigure(column + 1, weight=1)
        return box

    def _build_filters(self) -> None:
        filters = ttk.LabelFrame(self.frame, text="Attendance history filters", padding=10)
        filters.pack(fill="x", pady=(12, 8))
        ttk.Label(filters, text="Date (optional)").grid(row=0, column=0, sticky="w")
        ttk.Entry(filters, textvariable=self.date_filter, width=16).grid(
            row=0, column=1, padx=(6, 12)
        )
        ttk.Label(filters, text="Student").grid(row=0, column=2, sticky="w")
        self.student_filter_box = ttk.Combobox(
            filters, textvariable=self.student_filter, state="readonly", width=22
        )
        self.student_filter_box.grid(row=0, column=3, padx=(6, 12))
        ttk.Label(filters, text="Class").grid(row=0, column=4, sticky="w")
        self.class_filter_box = ttk.Combobox(
            filters, textvariable=self.class_filter, state="readonly", width=20
        )
        self.class_filter_box.grid(row=0, column=5, padx=(6, 12))
        ttk.Button(filters, text="Apply Filters", command=self.refresh).grid(row=0, column=6)
        ttk.Label(self.frame, textvariable=self.summary_text, style="Subtitle.TLabel").pack(
            anchor="w", pady=(0, 8)
        )

    def _build_table(self) -> None:
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill="both", expand=True)
        self.tree = create_tree(table_frame, COLUMNS, WIDTHS)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def add(self) -> None:
        self.context.runner.run(
            lambda: self.context.services.attendance.add(self._form_values()),
            "Attendance recorded successfully.",
            self._after_change,
        )

    def update(self) -> None:
        if not self.selected_id:
            self.context.feedback.error("Select an attendance record before updating it.")
            return
        selected_id = self.selected_id
        self.context.runner.run(
            lambda: self.context.services.attendance.update(selected_id, self._form_values()),
            "Attendance record updated successfully.",
            self._after_change,
        )

    def delete(self) -> None:
        if not self.selected_id:
            self.context.feedback.error("Select an attendance record before deleting it.")
            return
        if not self.context.feedback.confirm(
            "Delete Attendance", "Delete the selected attendance record?"
        ):
            return
        selected_id = self.selected_id
        self.context.runner.run(
            lambda: self.context.services.attendance.delete(selected_id),
            "Attendance record deleted successfully.",
            self._after_change,
        )

    def clear(self) -> None:
        self.selected_id = None
        self.student_box.set("")
        self.variables["attendance_date"].set(date.today().isoformat())
        self.variables["status"].set(ATTENDANCE_STATUSES[0])
        self.tree.selection_remove(*self.tree.selection())

    def _form_values(self) -> dict[str, str]:
        return {
            "student_id": self._reference_id(self.variables["student_id"].get()),
            "attendance_date": self.variables["attendance_date"].get().strip(),
            "status": self.variables["status"].get(),
        }

    def _after_change(self) -> None:
        self.clear()
        self.context.refresh_all()

    def _on_select(self, _event: tk.Event[Any]) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        try:
            record = self.context.services.attendance.get(selection[0])
            if record is None:
                return
            self.selected_id = record["attendance_id"]
            self.student_box.set(self._student_label(record["student_id"]))
            self.variables["attendance_date"].set(record["attendance_date"])
            self.variables["status"].set(record["status"])
        except (StorageError, ValidationError) as error:
            self.context.feedback.error(str(error))

    def refresh(self) -> None:
        try:
            students = self.context.services.students.list()
            classes = self.context.services.academic_structure.list("class")
            student_options = [
                self._student_label(str(student["student_id"]), students)
                for student in students
                if student.get("student_id")
            ]
            class_options = [
                f"{record['name']} [{record['class_id']}]"
                for record in classes
                if record.get("name") and record.get("class_id")
            ]
            self.student_box["values"] = student_options
            self.student_filter_box["values"] = ["All"] + student_options
            self.class_filter_box["values"] = ["All"] + class_options
            filters = {
                "attendance_date": self.date_filter.get().strip(),
                "student_id": self._reference_id(self.student_filter.get()),
                "class_id": self._reference_id(self.class_filter.get()),
            }
            records = self.context.services.attendance.list(
                attendance_date=filters["attendance_date"],
                student_id="" if filters["student_id"] == "All" else filters["student_id"],
                class_id="" if filters["class_id"] == "All" else filters["class_id"],
            )
            students_by_id = {
                str(student.get("student_id", "")).casefold(): student for student in students
            }
            classes_by_id = {record["class_id"]: record for record in classes}
            rows = []
            for record in records:
                student = students_by_id.get(str(record["student_id"]).casefold(), {})
                classroom = classes_by_id.get(record["class_id"], {})
                rows.append(
                    (
                        record["attendance_id"],
                        (
                            record["attendance_id"],
                            record["attendance_date"],
                            record["student_id"],
                            student.get("name", "Unknown student"),
                            classroom.get("name", "Unknown class"),
                            record["status"],
                        ),
                    )
                )
            replace_rows(self.tree, rows)
            summary = self.context.services.attendance.summary(records)
            if summary["total"]:
                self.summary_text.set(
                    "Records: {total} · Present: {present} · Absent: {absent} · "
                    "Late: {late} · Excused: {excused} · Attendance: {attendance_percentage}%".format(
                        **summary
                    )
                )
            else:
                self.summary_text.set("No attendance records for this filter.")
        except (StorageError, ValidationError) as error:
            self.context.feedback.error(str(error))

    def _student_label(self, student_id: str, students: list[dict[str, Any]] | None = None) -> str:
        records = students if students is not None else self.context.services.students.list()
        target = student_id.casefold()
        student = next(
            (
                record
                for record in records
                if str(record.get("student_id", "")).casefold() == target
            ),
            None,
        )
        return f"{student.get('name', student_id)} [{student_id}]" if student else student_id

    @staticmethod
    def _reference_id(value: str) -> str:
        if value == "All":
            return value
        if " [" in value and value.endswith("]"):
            return value.rsplit(" [", 1)[1][:-1]
        return value
