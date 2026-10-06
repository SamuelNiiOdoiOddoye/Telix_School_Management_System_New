"""Default values offered when the academic form is cleared."""

from __future__ import annotations

from datetime import date

DEFAULT_TERM = "Term 1"


def default_academic_year(today: date | None = None) -> str:
    """Return a label such as ``2026/2027`` for the calendar year of ``today``."""
    year = (today or date.today()).year
    return f"{year}/{year + 1}"
