"""Converts stored academic records (current or legacy key names) to the current shape."""

from __future__ import annotations

from typing import Any

from telix.core.text import clean_text


def normalise_academic_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "academic_id": clean_text(record.get("academic_id") or record.get("ID")),
        "student_id": clean_text(record.get("student_id") or record.get("Student ID")),
        "subject": clean_text(record.get("subject") or record.get("Subject")),
        "score": record.get("score", record.get("Score", 0)),
        "term": clean_text(record.get("term") or record.get("Term")),
        "academic_year": clean_text(record.get("academic_year") or record.get("Academic Year")),
        "subject_id": clean_text(record.get("subject_id")),
        "term_id": clean_text(record.get("term_id")),
        "academic_year_id": clean_text(record.get("academic_year_id")),
    }
