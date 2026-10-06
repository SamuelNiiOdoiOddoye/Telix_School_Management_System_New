"""Finance overview, student payments, and school expenses."""

from __future__ import annotations

from datetime import date
import tkinter as tk
from tkinter import ttk
from typing import Any

from telix.core.errors import StorageError
from telix.core.formatting import format_currency
from telix.core.numbers import as_amount
from telix.ui.tabs.base import BaseTab, TabContext
from telix.ui.theme import HEADING_FONT
from telix.ui.widgets.forms import add_button_row, add_form_field
from telix.ui.widgets.tables import create_tree, replace_rows

SUMMARY_CARDS = (
    ("Expected Fee Income", "expected_fee_income"),
    ("Received Income", "received_income"),
    ("Outstanding Balance", "outstanding_balances"),
    ("Student Credit", "student_credit"),
    ("Teacher Salaries", "salary_expense"),
    ("Other Expenses", "other_expenses"),
    ("Total Expenses", "total_expenses"),
    ("Profit / Loss", "profit_or_loss"),
)
PAYMENT_COLUMNS = ("payment_id", "payment_date", "student_id", "amount", "description")
EXPENSE_COLUMNS = ("expense_id", "expense_date", "category", "description", "amount")


class FinanceTab(BaseTab):
    key = "finance"
    title = "Finance"
    padding = 16

    def __init__(self, notebook: ttk.Notebook, context: TabContext) -> None:
        super().__init__(notebook, context)
        self.values = {key: tk.StringVar(value=format_currency(0)) for _, key in SUMMARY_CARDS}
        self.payment_fields = {
            "student_id": tk.StringVar(),
            "payment_date": tk.StringVar(value=date.today().isoformat()),
            "amount": tk.StringVar(),
            "description": tk.StringVar(),
        }
        self.expense_fields = {
            "expense_date": tk.StringVar(value=date.today().isoformat()),
            "category": tk.StringVar(),
            "description": tk.StringVar(),
            "amount": tk.StringVar(),
        }
        self.selected_payment_id: str | None = None
        self.selected_expense_id: str | None = None
        self._build_heading()
        self._build_cards()
        self._build_ledgers()

    def _build_heading(self) -> None:
        ttk.Label(self.frame, text="Finance Overview", font=HEADING_FONT).pack(anchor="w")
        ttk.Label(
            self.frame,
            text="Expected fees come from student records; received income, expenses, "
            "balances, and credit use the local ledger.",
            style="Subtitle.TLabel",
            wraplength=980,
        ).pack(anchor="w", pady=(0, 12))

    def _build_cards(self) -> None:
        grid = ttk.Frame(self.frame)
        grid.pack(fill="x")
        for index, (label, key) in enumerate(SUMMARY_CARDS):
            row, column = divmod(index, 4)
            card = ttk.LabelFrame(grid, text=label, padding=12)
            card.grid(row=row, column=column, padx=(0, 8), pady=(0, 8), sticky="nsew")
            ttk.Label(card, textvariable=self.values[key], style="Metric.TLabel").pack()
            grid.columnconfigure(column, weight=1)

    def _build_ledgers(self) -> None:
        self.ledger_tabs = ttk.Notebook(self.frame)
        self.ledger_tabs.pack(fill="both", expand=True, pady=(8, 0))
        payment_page = ttk.Frame(self.ledger_tabs, padding=10)
        expense_page = ttk.Frame(self.ledger_tabs, padding=10)
        self.ledger_tabs.add(payment_page, text="Student Payments")
        self.ledger_tabs.add(expense_page, text="School Expenses")
        self._build_payment_page(payment_page)
        self._build_expense_page(expense_page)

    def _build_payment_page(self, page: ttk.Frame) -> None:
        form = ttk.LabelFrame(page, text="Payment details", padding=10)
        form.pack(fill="x")
        ttk.Label(form, text="Student").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=5)
        self.student_box = ttk.Combobox(
            form, textvariable=self.payment_fields["student_id"], state="readonly", width=26
        )
        self.student_box.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=5)
        form.columnconfigure(1, weight=1)
        add_form_field(form, "Date (YYYY-MM-DD)", self.payment_fields["payment_date"], 0, 2)
        add_form_field(form, "Amount (GHS)", self.payment_fields["amount"], 0, 4)
        add_form_field(form, "Description (optional)", self.payment_fields["description"], 1, 0)
        add_button_row(
            form,
            (
                ("Add Payment", self.add_payment),
                ("Update Selected", self.update_payment),
                ("Delete Selected", self.delete_payment),
                ("Clear", self.clear_payment),
            ),
            row=2,
        )
        table = ttk.Frame(page)
        table.pack(fill="both", expand=True, pady=(10, 0))
        self.payment_tree = create_tree(table, PAYMENT_COLUMNS, (150, 120, 140, 120, 300))
        self.payment_tree.bind("<<TreeviewSelect>>", self._select_payment)

    def _build_expense_page(self, page: ttk.Frame) -> None:
        form = ttk.LabelFrame(page, text="Expense details", padding=10)
        form.pack(fill="x")
        add_form_field(form, "Date (YYYY-MM-DD)", self.expense_fields["expense_date"], 0, 0)
        add_form_field(form, "Category", self.expense_fields["category"], 0, 2)
        add_form_field(form, "Amount (GHS)", self.expense_fields["amount"], 0, 4)
        add_form_field(form, "Description", self.expense_fields["description"], 1, 0)
        add_button_row(
            form,
            (
                ("Add Expense", self.add_expense),
                ("Update Selected", self.update_expense),
                ("Delete Selected", self.delete_expense),
                ("Clear", self.clear_expense),
            ),
            row=2,
        )
        table = ttk.Frame(page)
        table.pack(fill="both", expand=True, pady=(10, 0))
        self.expense_tree = create_tree(table, EXPENSE_COLUMNS, (150, 120, 160, 300, 120))
        self.expense_tree.bind("<<TreeviewSelect>>", self._select_expense)

    def add_payment(self) -> None:
        self.context.runner.run(
            lambda: self.context.services.finance.add_payment(self._payment_values()),
            "Payment saved successfully.",
            self._after_change,
        )

    def update_payment(self) -> None:
        if not self.selected_payment_id:
            self.context.feedback.error("Select a payment before updating it.")
            return
        payment_id = self.selected_payment_id
        self.context.runner.run(
            lambda: self.context.services.finance.update_payment(
                payment_id, self._payment_values()
            ),
            "Payment updated successfully.",
            self._after_change,
        )

    def delete_payment(self) -> None:
        if not self.selected_payment_id:
            self.context.feedback.error("Select a payment before deleting it.")
            return
        if not self.context.feedback.confirm(
            "Delete Payment", "Delete the selected payment record?"
        ):
            return
        payment_id = self.selected_payment_id
        self.context.runner.run(
            lambda: self.context.services.finance.delete("payment", payment_id),
            "Payment deleted successfully.",
            self._after_change,
        )

    def add_expense(self) -> None:
        self.context.runner.run(
            lambda: self.context.services.finance.add_expense(
                {key: value.get() for key, value in self.expense_fields.items()}
            ),
            "Expense saved successfully.",
            self._after_change,
        )

    def update_expense(self) -> None:
        if not self.selected_expense_id:
            self.context.feedback.error("Select an expense before updating it.")
            return
        expense_id = self.selected_expense_id
        self.context.runner.run(
            lambda: self.context.services.finance.update_expense(
                expense_id, {key: value.get() for key, value in self.expense_fields.items()}
            ),
            "Expense updated successfully.",
            self._after_change,
        )

    def delete_expense(self) -> None:
        if not self.selected_expense_id:
            self.context.feedback.error("Select an expense before deleting it.")
            return
        if not self.context.feedback.confirm(
            "Delete Expense", "Delete the selected expense record?"
        ):
            return
        expense_id = self.selected_expense_id
        self.context.runner.run(
            lambda: self.context.services.finance.delete("expense", expense_id),
            "Expense deleted successfully.",
            self._after_change,
        )

    def clear_payment(self) -> None:
        self.selected_payment_id = None
        for variable in self.payment_fields.values():
            variable.set("")
        self.payment_fields["payment_date"].set(date.today().isoformat())
        self.payment_tree.selection_remove(*self.payment_tree.selection())

    def clear_expense(self) -> None:
        self.selected_expense_id = None
        for variable in self.expense_fields.values():
            variable.set("")
        self.expense_fields["expense_date"].set(date.today().isoformat())
        self.expense_tree.selection_remove(*self.expense_tree.selection())

    def _payment_values(self) -> dict[str, str]:
        selected = self.student_box.get()
        student_id = (
            selected.rsplit(" [", 1)[1][:-1]
            if " [" in selected and selected.endswith("]")
            else selected
        )
        return {
            **{key: variable.get() for key, variable in self.payment_fields.items()},
            "student_id": student_id,
        }

    def _select_payment(self, _event: tk.Event[Any]) -> None:
        selected = self.payment_tree.selection()
        if not selected:
            return
        record = next(
            (
                item
                for item in self.context.services.finance.list("payment")
                if item["payment_id"] == selected[0]
            ),
            None,
        )
        if record is None:
            return
        self.selected_payment_id = record["payment_id"]
        self.student_box.set(self._student_label(record["student_id"]))
        self.payment_fields["payment_date"].set(record["payment_date"])
        self.payment_fields["amount"].set(str(as_amount(record["amount"])))
        self.payment_fields["description"].set(record.get("description", ""))

    def _select_expense(self, _event: tk.Event[Any]) -> None:
        selected = self.expense_tree.selection()
        if not selected:
            return
        record = next(
            (
                item
                for item in self.context.services.finance.list("expense")
                if item["expense_id"] == selected[0]
            ),
            None,
        )
        if record is None:
            return
        self.selected_expense_id = record["expense_id"]
        self.expense_fields["expense_date"].set(record["expense_date"])
        self.expense_fields["category"].set(record["category"])
        self.expense_fields["description"].set(record["description"])
        self.expense_fields["amount"].set(str(as_amount(record["amount"])))

    def _student_label(self, student_id: str) -> str:
        student = self.context.services.students.get(student_id)
        if student is None:
            return student_id
        return f"{student['name']} [{student_id}]"

    def _after_change(self) -> None:
        self.clear_payment()
        self.clear_expense()
        self.context.refresh_all()

    def refresh(self) -> None:
        try:
            students = self.context.services.students.list()
            teachers = self.context.services.teachers.salary_records()
            ledger = self.context.services.finance
            summary = ledger.summary(students, teachers)
            for key, variable in self.values.items():
                variable.set(format_currency(summary[key]))
            self.student_box["values"] = [
                f"{student['name']} [{student['student_id']}]" for student in students
            ]
            self._render_payments(ledger.list("payment"))
            self._render_expenses(ledger.list("expense"))
        except StorageError as error:
            self.context.feedback.error(str(error))

    def _render_payments(self, records: list[dict[str, Any]]) -> None:
        replace_rows(
            self.payment_tree,
            (
                (
                    record["payment_id"],
                    (
                        record["payment_id"],
                        record["payment_date"],
                        record["student_id"],
                        format_currency(as_amount(record["amount"])),
                        record.get("description", ""),
                    ),
                )
                for record in records
            ),
        )

    def _render_expenses(self, records: list[dict[str, Any]]) -> None:
        replace_rows(
            self.expense_tree,
            (
                (
                    record["expense_id"],
                    (
                        record["expense_id"],
                        record["expense_date"],
                        record["category"],
                        record["description"],
                        format_currency(as_amount(record["amount"])),
                    ),
                )
                for record in records
            ),
        )
