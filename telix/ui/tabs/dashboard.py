"""Dashboard tab: headline totals and quick navigation."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from telix.core.formatting import format_currency
from telix.authentication.roles import (
    DASHBOARD_FINANCE,
    DASHBOARD_OPERATIONAL,
    DASHBOARD_OWN,
    DASHBOARD_TEACHING,
    STUDENTS_WRITE,
    USERS_MANAGE,
)
from telix.ui.tabs.base import BaseTab, TabContext
from telix.ui.theme import HEADING_FONT

CARDS = (
    ("Students", "students"),
    ("Active Students", "active_students"),
    ("Teachers", "teachers"),
    ("Attendance", "attendance"),
    ("Expected Fee Income", "expected"),
    ("Received Income", "received"),
    ("Outstanding Balance", "outstanding"),
    ("Teacher Salaries", "salaries"),
    ("Other Expenses", "expenses"),
    ("Total Expenses", "total_expenses"),
    ("Profit / Loss", "result"),
    ("Academic History", "academic"),
)
QUICK_ACTIONS = (
    ("Manage Students", "students"),
    ("Manage Teachers", "teachers"),
    ("Record Academic Score", "academics"),
    ("Manage Assessments", "assessments"),
    ("Record Attendance", "attendance"),
    ("Open Finance", "finance"),
    ("Open Reports", "reports"),
    ("Manage Users", "users"),
)


class DashboardTab(BaseTab):
    key = "dashboard"
    title = "Dashboard"
    padding = 16

    def __init__(self, notebook: ttk.Notebook, context: TabContext) -> None:
        super().__init__(notebook, context)
        self.metrics = {
            "students": tk.StringVar(value="0"),
            "active_students": tk.StringVar(value="0"),
            "teachers": tk.StringVar(value="0"),
            "attendance": tk.StringVar(value="0%"),
            "expected": tk.StringVar(value=format_currency(0)),
            "received": tk.StringVar(value=format_currency(0)),
            "outstanding": tk.StringVar(value=format_currency(0)),
            "salaries": tk.StringVar(value=format_currency(0)),
            "expenses": tk.StringVar(value=format_currency(0)),
            "total_expenses": tk.StringVar(value=format_currency(0)),
            "result": tk.StringVar(value=format_currency(0)),
            "academic": tk.StringVar(value="No results"),
        }
        self._build_heading()
        self._build_cards()
        self._build_quick_actions()

    def _build_heading(self) -> None:
        ttk.Label(self.frame, text="School overview", font=HEADING_FONT).pack(anchor="w")
        subtitle = (
            "Your academic period history and attendance."
            if self.context.services.authorization.allows(DASHBOARD_OWN)
            else "Financial results show collected payments less salaries and recorded expenses."
            if self.context.services.authorization.allows(DASHBOARD_FINANCE)
            else "Current student and attendance overview."
        )
        ttk.Label(
            self.frame,
            text=subtitle,
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 16))

    def _build_cards(self) -> None:
        cards = ttk.Frame(self.frame)
        cards.pack(fill="x")
        for index, (label, metric_key) in enumerate(CARDS):
            required_capabilities = (
                (DASHBOARD_OPERATIONAL, DASHBOARD_TEACHING)
                if metric_key in {"students", "active_students"}
                else (DASHBOARD_OPERATIONAL,)
                if metric_key == "teachers"
                else (DASHBOARD_FINANCE,)
                if metric_key
                in {
                    "expected",
                    "received",
                    "outstanding",
                    "salaries",
                    "expenses",
                    "total_expenses",
                    "result",
                }
                else (DASHBOARD_OWN,)
                if metric_key == "academic"
                else (DASHBOARD_TEACHING, DASHBOARD_OWN)
            )
            if not any(
                self.context.services.authorization.allows(capability)
                for capability in required_capabilities
            ):
                continue
            row, column = divmod(index, 4)
            card = ttk.LabelFrame(cards, text=label, padding=18)
            card.grid(row=row, column=column, padx=(0, 12), pady=(0, 8), sticky="nsew")
            ttk.Label(card, textvariable=self.metrics[metric_key], style="Metric.TLabel").pack()
            cards.columnconfigure(column, weight=1)

    def _build_quick_actions(self) -> None:
        actions = ttk.LabelFrame(self.frame, text="Quick actions", padding=16)
        actions.pack(fill="x", pady=24)
        for index, (text, tab_key) in enumerate(QUICK_ACTIONS):
            if tab_key == "students" and not self.context.services.authorization.allows(
                STUDENTS_WRITE
            ):
                text = "View Students"
            required = {
                "students": (DASHBOARD_OPERATIONAL, DASHBOARD_TEACHING),
                "teachers": (DASHBOARD_OPERATIONAL,),
                "academics": (DASHBOARD_TEACHING,),
                "assessments": (DASHBOARD_TEACHING,),
                "attendance": (DASHBOARD_TEACHING,),
                "finance": (DASHBOARD_FINANCE,),
                "reports": (
                    DASHBOARD_OPERATIONAL,
                    DASHBOARD_TEACHING,
                    DASHBOARD_FINANCE,
                    DASHBOARD_OWN,
                ),
                "users": (USERS_MANAGE,),
            }.get(tab_key, ())
            if not any(
                self.context.services.authorization.allows(capability) for capability in required
            ):
                continue

            def navigate(key: str = tab_key) -> None:
                self.context.navigate(key)

            ttk.Button(actions, text=text, command=navigate).grid(row=0, column=index, padx=(0, 10))
        ttk.Button(actions, text="Refresh Dashboard", command=self.context.refresh_all).grid(
            row=0, column=len(QUICK_ACTIONS)
        )

    def refresh(self) -> None:
        authorization = self.context.services.authorization
        if authorization.allows(DASHBOARD_OWN):
            summaries = self.context.services.academics.period_summaries()
            records = self.context.services.attendance.list()
            attendance = self.context.services.attendance.summary(records)
            average = (
                sum((item["average_score"] for item in summaries), start=0) / len(summaries)
                if summaries
                else None
            )
            self.metrics["academic"].set(
                f"{len(summaries)} periods · {average:.2f} avg"
                if average is not None
                else "No results"
            )
            self.metrics["attendance"].set(
                f"{attendance['attendance_percentage']}% ({attendance['total']} records)"
            )
            if not authorization.allows(DASHBOARD_FINANCE):
                return
        students = self.context.services.students.list()
        if authorization.allows(DASHBOARD_OPERATIONAL):
            teachers = self.context.services.teachers.list()
            self.metrics["students"].set(str(len(students)))
            self.metrics["active_students"].set(
                str(sum(student["status"] == "Active" for student in students))
            )
            self.metrics["teachers"].set(str(len(teachers)))
            attendance = self.context.services.attendance.summary()
            self.metrics["attendance"].set(
                f"{attendance['attendance_percentage']}% ({attendance['total']} records)"
            )
            if not authorization.allows(DASHBOARD_FINANCE):
                return
        if authorization.allows(DASHBOARD_TEACHING):
            self.metrics["students"].set(str(len(students)))
            self.metrics["active_students"].set(
                str(sum(student["status"] == "Active" for student in students))
            )
            attendance = self.context.services.attendance.summary()
            self.metrics["attendance"].set(
                f"{attendance['attendance_percentage']}% ({attendance['total']} records)"
            )
            return
        salary_records = self.context.services.teachers.salary_records()
        summary = self.context.services.finance.summary(students, salary_records)
        for metric, key in (
            ("expected", "expected_fee_income"),
            ("received", "received_income"),
            ("outstanding", "outstanding_balances"),
            ("salaries", "salary_expense"),
            ("expenses", "other_expenses"),
            ("total_expenses", "total_expenses"),
            ("result", "profit_or_loss"),
        ):
            self.metrics[metric].set(format_currency(summary[key]))
