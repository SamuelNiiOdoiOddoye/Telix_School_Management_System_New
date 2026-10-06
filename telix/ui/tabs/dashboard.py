"""Dashboard tab: headline totals and quick navigation."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from telix.core.formatting import format_currency
from telix.finance.summary import calculate_financial_summary
from telix.ui.tabs.base import BaseTab, TabContext
from telix.ui.theme import HEADING_FONT

CARDS = (
    ("Students", "students"),
    ("Teachers", "teachers"),
    ("Expected Fee Income", "income"),
    ("Profit / Loss", "result"),
)
QUICK_ACTIONS = (
    ("Manage Students", "students"),
    ("Manage Teachers", "teachers"),
    ("Record Academic Score", "academics"),
)


class DashboardTab(BaseTab):
    key = "dashboard"
    title = "Dashboard"
    padding = 16

    def __init__(self, notebook: ttk.Notebook, context: TabContext) -> None:
        super().__init__(notebook, context)
        self.metrics = {
            "students": tk.StringVar(value="0"),
            "teachers": tk.StringVar(value="0"),
            "income": tk.StringVar(value=format_currency(0)),
            "result": tk.StringVar(value=format_currency(0)),
        }
        self._build_heading()
        self._build_cards()
        self._build_quick_actions()

    def _build_heading(self) -> None:
        ttk.Label(self.frame, text="School overview", font=HEADING_FONT).pack(anchor="w")
        ttk.Label(
            self.frame,
            text="Financial results use recorded student fees less recorded teacher salaries.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 16))

    def _build_cards(self) -> None:
        cards = ttk.Frame(self.frame)
        cards.pack(fill="x")
        for index, (label, metric_key) in enumerate(CARDS):
            card = ttk.LabelFrame(cards, text=label, padding=18)
            card.grid(
                row=0, column=index, padx=(0, 12) if index < len(CARDS) - 1 else 0, sticky="nsew"
            )
            ttk.Label(card, textvariable=self.metrics[metric_key], style="Metric.TLabel").pack()
            cards.columnconfigure(index, weight=1)

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
        summary = calculate_financial_summary(students, teachers)
        self.metrics["students"].set(str(len(students)))
        self.metrics["teachers"].set(str(len(teachers)))
        self.metrics["income"].set(format_currency(summary["fee_income"]))
        self.metrics["result"].set(format_currency(summary["profit_or_loss"]))
