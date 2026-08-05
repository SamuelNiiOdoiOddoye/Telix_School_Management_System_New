"""Validation and formatting helpers shared by the V1 modules."""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Mapping
from uuid import uuid4


class ValidationError(ValueError):
    """Raised when submitted form data does not meet application rules."""


def generate_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def clean_text(value: object) -> str:
    return str(value or "").strip()


def require_fields(values: Mapping[str, object], labels: Mapping[str, str]) -> dict[str, str]:
    cleaned = {field: clean_text(value) for field, value in values.items()}
    missing = [labels[field] for field, value in cleaned.items() if not value]
    if missing:
        raise ValidationError(f"Please complete: {', '.join(missing)}.")
    return cleaned


def validate_date_of_birth(value: str, minimum_age: int, maximum_age: int, label: str) -> str:
    try:
        birth_date = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as error:
        raise ValidationError(f"{label} must use the format YYYY-MM-DD.") from error

    today = date.today()
    age = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    if not minimum_age <= age <= maximum_age:
        raise ValidationError(
            f"{label} must describe an age between {minimum_age} and {maximum_age}."
        )
    return birth_date.isoformat()


def validate_phone(value: str, label: str) -> str:
    compact_phone = re.sub(r"[\s-]", "", value)
    if not re.fullmatch(r"\+?\d{10,15}", compact_phone):
        raise ValidationError(f"{label} must contain 10 to 15 digits, optionally starting with +.")
    return compact_phone


def validate_email(value: str) -> str:
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
        raise ValidationError("Email address is not valid.")
    return value


def validate_amount(value: str, label: str) -> float:
    try:
        amount = Decimal(value)
    except InvalidOperation as error:
        raise ValidationError(f"{label} must be a number.") from error
    if amount < 0:
        raise ValidationError(f"{label} cannot be negative.")
    return float(amount.quantize(Decimal("0.01")))


def validate_score(value: str) -> int:
    try:
        score = int(value)
    except ValueError as error:
        raise ValidationError("Score must be a whole number from 0 to 100.") from error
    if not 0 <= score <= 100:
        raise ValidationError("Score must be a whole number from 0 to 100.")
    return score


def format_currency(value: float) -> str:
    return f"GHS {value:,.2f}"
