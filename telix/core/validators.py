"""Field validators. Each function checks one rule and returns the cleaned value."""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Mapping

from telix.core.errors import ValidationError
from telix.core.text import clean_text


def require_fields(values: Mapping[str, object], labels: Mapping[str, str]) -> dict[str, str]:
    """Strip every value and reject the submission if any field is empty."""
    cleaned = {field: clean_text(value) for field, value in values.items()}
    missing = [labels[field] for field, value in cleaned.items() if not value]
    if missing:
        raise ValidationError(f"Please complete: {', '.join(missing)}.")
    return cleaned


def _parse_iso_date(value: str, label: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as error:
        raise ValidationError(f"{label} must use the format YYYY-MM-DD.") from error


def calculate_age(birth_date: date, today: date) -> int:
    had_birthday = (today.month, today.day) >= (birth_date.month, birth_date.day)
    return today.year - birth_date.year - (0 if had_birthday else 1)


def validate_date_of_birth(
    value: str,
    minimum_age: int,
    maximum_age: int,
    label: str,
    today: date | None = None,
) -> str:
    birth_date = _parse_iso_date(value, label)
    age = calculate_age(birth_date, today or date.today())
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


def validate_amount(value: str, label: str) -> Decimal:
    try:
        amount = Decimal(value)
        amount = amount.quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError) as error:
        raise ValidationError(f"{label} must be a number.") from error
    if not amount.is_finite():
        raise ValidationError(f"{label} must be a finite number.")
    if amount < 0:
        raise ValidationError(f"{label} cannot be negative.")
    return amount


def validate_score(value: str) -> int:
    try:
        score = int(value)
    except ValueError as error:
        raise ValidationError("Score must be a whole number from 0 to 100.") from error
    if not 0 <= score <= 100:
        raise ValidationError("Score must be a whole number from 0 to 100.")
    return score
