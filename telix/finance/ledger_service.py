"""Validated payment and expense records plus school-finance summaries."""

from __future__ import annotations

import builtins
from datetime import date
from decimal import Decimal
from typing import Any, Callable, Mapping

from telix.core.errors import ValidationError
from telix.core.identifiers import generate_id
from telix.core.numbers import ZERO_AMOUNT, as_amount
from telix.core.search import find_index_by_id
from telix.core.validators import validate_amount
from telix.finance.repository import FinanceRepository, ID_FIELDS, LedgerKind

StudentExists = Callable[[str], bool]
CENT = Decimal("0.01")


def _iso_date(value: object, label: str) -> str:
    text = str(value or "").strip()
    try:
        parsed = date.fromisoformat(text)
    except ValueError as error:
        raise ValidationError(f"{label} must use the format YYYY-MM-DD.") from error
    if parsed.isoformat() != text:
        raise ValidationError(f"{label} must use the format YYYY-MM-DD.")
    return text


class FinanceLedgerService:
    def __init__(
        self,
        repository: FinanceRepository | None = None,
        student_exists: StudentExists | None = None,
    ) -> None:
        self._repository = repository or FinanceRepository()
        self._student_exists = student_exists or (lambda _student_id: False)

    def list(
        self, kind: LedgerKind, *, student_id: str = "", start_date: str = "", end_date: str = ""
    ) -> builtins.list[dict[str, Any]]:
        start = _iso_date(start_date, "Start date") if start_date else ""
        end = _iso_date(end_date, "End date") if end_date else ""
        if start and end and start > end:
            raise ValidationError("Start date must be on or before end date.")
        target_student = student_id.strip().casefold()
        date_field = "payment_date" if kind == "payment" else "expense_date"
        records = self._repository.list(kind)
        return [
            record
            for record in records
            if (
                not target_student or str(record.get("student_id", "")).casefold() == target_student
            )
            and (not start or str(record.get(date_field, "")) >= start)
            and (not end or str(record.get(date_field, "")) <= end)
        ]

    def add_payment(self, values: Mapping[str, object]) -> dict[str, Any]:
        record = self._prepare_payment(values)
        records = self._repository.list("payment")
        records.append(record)
        self._repository.save("payment", records)
        return record

    def update_payment(self, payment_id: str, values: Mapping[str, object]) -> dict[str, Any]:
        records = self._repository.list("payment")
        index = find_index_by_id(records, ID_FIELDS["payment"], payment_id)
        if index is None:
            raise ValidationError("Payment record not found.")
        record = self._prepare_payment(values, payment_id)
        records[index] = record
        self._repository.save("payment", records)
        return record

    def _prepare_payment(
        self, values: Mapping[str, object], payment_id: str | None = None
    ) -> dict[str, Any]:
        student_id = str(values.get("student_id", "")).strip().upper()
        if not student_id or not self._student_exists(student_id):
            raise ValidationError("Select an existing student for this payment.")
        return {
            "payment_id": payment_id or generate_id("PAY"),
            "student_id": student_id,
            "payment_date": _iso_date(values.get("payment_date"), "Payment date"),
            "amount": self._positive_amount(values.get("amount"), "Payment amount"),
            "description": str(values.get("description", "")).strip(),
        }

    def add_expense(self, values: Mapping[str, object]) -> dict[str, Any]:
        record = self._prepare_expense(values)
        records = self._repository.list("expense")
        records.append(record)
        self._repository.save("expense", records)
        return record

    def update_expense(self, expense_id: str, values: Mapping[str, object]) -> dict[str, Any]:
        records = self._repository.list("expense")
        index = find_index_by_id(records, ID_FIELDS["expense"], expense_id)
        if index is None:
            raise ValidationError("Expense record not found.")
        record = self._prepare_expense(values, expense_id)
        records[index] = record
        self._repository.save("expense", records)
        return record

    def _prepare_expense(
        self, values: Mapping[str, object], expense_id: str | None = None
    ) -> dict[str, Any]:
        category = str(values.get("category", "")).strip()
        description = str(values.get("description", "")).strip()
        if not category:
            raise ValidationError("Expense category is required.")
        if not description:
            raise ValidationError("Expense description is required.")
        return {
            "expense_id": expense_id or generate_id("EXP"),
            "expense_date": _iso_date(values.get("expense_date"), "Expense date"),
            "category": category,
            "description": description,
            "amount": self._positive_amount(values.get("amount"), "Expense amount"),
        }

    def delete(self, kind: LedgerKind, record_id: str) -> dict[str, Any]:
        records = self._repository.list(kind)
        index = find_index_by_id(records, ID_FIELDS[kind], record_id)
        if index is None:
            raise ValidationError(f"{kind.title()} record not found.")
        deleted = records.pop(index)
        self._repository.save(kind, records)
        return deleted

    def ensure_student_removable(self, student_id: str) -> None:
        if self.list("payment", student_id=student_id):
            raise ValidationError(
                "This student has payment history. Remove or retain the financial records "
                "before deleting the student."
            )

    def summary(
        self, students: builtins.list[dict[str, Any]], teachers: builtins.list[dict[str, Any]]
    ) -> dict[str, Decimal]:
        payments = self._repository.list("payment")
        expenses = self._repository.list("expense")
        paid_by_student: dict[str, Decimal] = {}
        for payment in payments:
            key = str(payment.get("student_id", "")).casefold()
            paid_by_student[key] = paid_by_student.get(key, ZERO_AMOUNT) + as_amount(
                payment.get("amount")
            )
        expected = ZERO_AMOUNT
        outstanding = ZERO_AMOUNT
        credit = ZERO_AMOUNT
        for student in students:
            fee = as_amount(student.get("fees"))
            expected += fee
            paid = paid_by_student.get(str(student.get("student_id", "")).casefold(), ZERO_AMOUNT)
            outstanding += max(fee - paid, ZERO_AMOUNT)
            credit += max(paid - fee, ZERO_AMOUNT)
        collected = sum((as_amount(row.get("amount")) for row in payments), ZERO_AMOUNT)
        salary_expense = sum(
            (as_amount(teacher.get("salary")) for teacher in teachers), ZERO_AMOUNT
        )
        other_expenses = sum((as_amount(row.get("amount")) for row in expenses), ZERO_AMOUNT)
        total_expenses = salary_expense + other_expenses
        return {
            "expected_fee_income": expected.quantize(CENT),
            "received_income": collected.quantize(CENT),
            "outstanding_balances": outstanding.quantize(CENT),
            "student_credit": credit.quantize(CENT),
            "salary_expense": salary_expense.quantize(CENT),
            "other_expenses": other_expenses.quantize(CENT),
            "total_expenses": total_expenses.quantize(CENT),
            "profit_or_loss": (collected - total_expenses).quantize(CENT),
        }

    @staticmethod
    def _positive_amount(value: object, label: str) -> Decimal:
        amount = validate_amount(str(value or ""), label)
        if amount <= 0:
            raise ValidationError(f"{label} must be greater than zero.")
        return amount
