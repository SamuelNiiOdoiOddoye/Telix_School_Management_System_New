"""Finance calculations derived from student fees and teacher salaries."""

from __future__ import annotations

from typing import Any, Iterable


def calculate_financial_summary(
    students: Iterable[dict[str, Any]], teachers: Iterable[dict[str, Any]]
) -> dict[str, float]:
    fee_income = sum(_as_amount(student.get("fees")) for student in students)
    salary_expense = sum(_as_amount(teacher.get("salary")) for teacher in teachers)
    return {
        "fee_income": fee_income,
        "salary_expense": salary_expense,
        "profit_or_loss": fee_income - salary_expense,
    }


def _as_amount(value: object) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0
