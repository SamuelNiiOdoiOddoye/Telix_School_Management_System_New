"""Turns raw form values into a validated academic record."""

from __future__ import annotations

from typing import Any, Mapping

from telix.academics.schema import ACADEMIC_FIELD_LABELS
from telix.core.identifiers import generate_id
from telix.core.text import clean_text
from telix.core.validators import require_fields, validate_score


def prepare_academic_record(
    values: Mapping[str, object], academic_id: str | None = None
) -> dict[str, Any]:
    required_values = {
        field_name: values.get(field_name, "") for field_name in ACADEMIC_FIELD_LABELS
    }
    cleaned = require_fields(required_values, ACADEMIC_FIELD_LABELS)
    record = {
        "academic_id": academic_id or generate_id("ACA"),
        "student_id": cleaned["student_id"].upper(),
        "subject": cleaned["subject"],
        "score": validate_score(cleaned["score"]),
        "term": cleaned["term"],
        "academic_year": cleaned["academic_year"],
    }
    for field in ("subject_id", "term_id", "academic_year_id"):
        record[field] = clean_text(values.get(field, ""))
    return record
