"""Small text and dictionary helpers."""

from __future__ import annotations

from typing import Any


def clean_text(value: object) -> str:
    """Return ``value`` as a stripped string, treating falsy values as empty."""
    return str(value or "").strip()


def first_value(record: dict[str, Any], *keys: str, default: Any = "") -> Any:
    """Return the first non-empty value found under ``keys`` (used for legacy key names)."""
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return value
    return default
