"""Business rules for academic records."""

from __future__ import annotations

from typing import Any, Callable

from telix.core.errors import ValidationError


def uniqueness_key(record: dict[str, Any]) -> tuple[str, str, str, str]:
    """One score per student, subject, term and academic year (case-insensitive)."""
    return (
        record["student_id"].casefold(),
        record["subject"].casefold(),
        record["term"].casefold(),
        record["academic_year"].casefold(),
    )


def ensure_student_exists(student_id: str, student_exists: Callable[[str], bool]) -> None:
    if not student_exists(student_id):
        raise ValidationError("Student ID was not found. Add the student before adding scores.")


def ensure_unique_subject(
    records: list[dict[str, Any]],
    candidate: dict[str, Any],
    ignored_academic_id: str | None = None,
) -> None:
    candidate_key = uniqueness_key(candidate)
    ignored = ignored_academic_id.casefold() if ignored_academic_id else None
    for record in records:
        if ignored and record["academic_id"].casefold() == ignored:
            continue
        if uniqueness_key(record) == candidate_key:
            raise ValidationError(
                "An academic record for this student, subject, term, and year already exists."
            )
