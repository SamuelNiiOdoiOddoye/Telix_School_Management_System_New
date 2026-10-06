"""Finance tab: expected fee income, salary expense, and profit or loss."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from telix.core.formatting import format_currency
from telix.finance.summary import calculate_financial_summary
from telix.ui.tabs.base import BaseTab, TabContext
from telix.ui.theme import HEADING_FONT

CARDS = (
    ("Expected Fee Income", "fee_income"),
    ("Teacher Salary Expense", "salary_expense"),
    ("Profit / Loss", "profit_or_loss"),
)


class FinanceTab(BaseTab):
    key = "finance"
    title = "Finance"
    padding = 16

    def __init__(self, notebook: ttk.Notebook, context: TabContext) -> None:
        super().__init__(notebook, context)
        self.values = {key: tk.StringVar(value=format_currency(0)) for _, key in CARDS}
        self._build_heading()
        self._build_cards()
        ttk.Button(self.frame, text="Recalculate", command=self.refresh).pack(anchor="w", pady=20)

    def _build_heading(self) -> None:
        ttk.Label(self.frame, text="Profit / Loss Calculation", font=HEADING_FONT).pack(anchor="w")
        ttk.Label(
            self.frame,
            text="Expected fee income minus total recorded teacher salaries.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 16))

    def _build_cards(self) -> None:
        grid = ttk.Frame(self.frame)
        grid.pack(fill="x")
        for index, (label, key) in enumerate(CARDS):
            card = ttk.LabelFrame(grid, text=label, padding=20)
            card.grid(
                row=0, column=index, padx=(0, 12) if index < len(CARDS) - 1 else 0, sticky="nsew"
            )
            ttk.Label(card, textvariable=self.values[key], style="Metric.TLabel").pack()
            grid.columnconfigure(index, weight=1)

    def refresh(self) -> None:
        summary = calculate_financial_summary(
            self.context.services.students.list(), self.context.services.teachers.list()
        )
        for key, variable in self.values.items():
            variable.set(format_currency(summary[key]))
