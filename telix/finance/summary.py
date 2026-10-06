"""Finance calculations derived from student fees and teacher salaries."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable

from telix.core.numbers import ZERO_AMOUNT, as_amount


def calculate_financial_summary(
    students: Iterable[dict[str, Any]], teachers: Iterable[dict[str, Any]]
) -> dict[str, Decimal]:
    fee_income = sum((as_amount(student.get("fees")) for student in students), ZERO_AMOUNT)
    salary_expense = sum((as_amount(teacher.get("salary")) for teacher in teachers), ZERO_AMOUNT)
    return {
        "fee_income": fee_income,
        "salary_expense": salary_expense,
        "profit_or_loss": fee_income - salary_expense,
    }
