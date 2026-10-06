"""Dashboard tab: headline totals and quick navigation."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from telix.core.formatting import format_currency
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
    ("Profit / Loss", "result"),
)
QUICK_ACTIONS = (
    ("Manage Students", "students"),
    ("Manage Teachers", "teachers"),
    ("Record Academic Score", "academics"),
    ("Manage Assessments", "assessments"),
    ("Record Attendance", "attendance"),
    ("Open Finance", "finance"),
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
            "result": tk.StringVar(value=format_currency(0)),
        }
        self._build_heading()
        self._build_cards()
        self._build_quick_actions()

    def _build_heading(self) -> None:
        ttk.Label(self.frame, text="School overview", font=HEADING_FONT).pack(anchor="w")
        ttk.Label(
            self.frame,
            text="Financial results show collected payments less salaries and recorded expenses.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 16))

    def _build_cards(self) -> None:
        cards = ttk.Frame(self.frame)
        cards.pack(fill="x")
        for index, (label, metric_key) in enumerate(CARDS):
            row, column = divmod(index, 4)
            card = ttk.LabelFrame(cards, text=label, padding=18)
            card.grid(row=row, column=column, padx=(0, 12), pady=(0, 8), sticky="nsew")
            ttk.Label(card, textvariable=self.metrics[metric_key], style="Metric.TLabel").pack()
            cards.columnconfigure(column, weight=1)

    def _build_quick_actions(self) -> None:
        actions = ttk.LabelFrame(self.frame, text="Quick actions", padding=16)
        actions.pack(fill="x", pady=24)
        for index, (text, tab_key) in enumerate(QUICK_ACTIONS):

            def navigate(key: str = tab_key) -> None:
                self.context.navigate(key)

            ttk.Button(actions, text=text, command=navigate).grid(row=0, column=index, padx=(0, 10))
        ttk.Button(actions, text="Refresh Dashboard", command=self.context.refresh_all).grid(
            row=0, column=len(QUICK_ACTIONS)
        )

    def refresh(self) -> None:
        students = self.context.services.students.list()
        teachers = self.context.services.teachers.list()
        summary = self.context.services.finance.summary(students, teachers)
        attendance = self.context.services.attendance.summary()
        self.metrics["students"].set(str(len(students)))
        self.metrics["active_students"].set(
            str(sum(student["status"] == "Active" for student in students))
        )
        self.metrics["teachers"].set(str(len(teachers)))
        self.metrics["attendance"].set(
            f"{attendance['attendance_percentage']}% ({attendance['total']} records)"
        )
        self.metrics["expected"].set(format_currency(summary["expected_fee_income"]))
        self.metrics["received"].set(format_currency(summary["received_income"]))
        self.metrics["outstanding"].set(format_currency(summary["outstanding_balances"]))
        self.metrics["salaries"].set(format_currency(summary["salary_expense"]))
        self.metrics["expenses"].set(format_currency(summary["other_expenses"]))
        self.metrics["result"].set(format_currency(summary["profit_or_loss"]))
