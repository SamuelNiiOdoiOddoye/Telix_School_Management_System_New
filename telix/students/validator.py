"""Turns raw form values into a validated student record."""

from __future__ import annotations

from typing import Any, Mapping

from telix.core.errors import ValidationError
from telix.core.validators import (
    require_fields,
    validate_amount,
    validate_date_of_birth,
    validate_email,
    validate_phone,
)
from telix.students.schema import (
    DEFAULT_STUDENT_STATUS,
    STUDENT_FIELD_LABELS,
    STUDENT_STATUSES,
)

MINIMUM_STUDENT_AGE = 3
MAXIMUM_STUDENT_AGE = 25


def prepare_student(values: Mapping[str, object]) -> dict[str, Any]:
    required_values = {
        field_name: values.get(field_name, "") for field_name in STUDENT_FIELD_LABELS
    }
    if not str(required_values["status"]).strip():
        required_values["status"] = DEFAULT_STUDENT_STATUS
    cleaned = require_fields(required_values, STUDENT_FIELD_LABELS)
    status = cleaned["status"].title() if cleaned["status"] else DEFAULT_STUDENT_STATUS
    if status not in STUDENT_STATUSES:
        raise ValidationError(f"Student status must be one of: {', '.join(STUDENT_STATUSES)}.")
    return {
        "student_id": cleaned["student_id"].upper(),
        "name": cleaned["name"],
        "date_of_birth": validate_date_of_birth(
            cleaned["date_of_birth"],
            MINIMUM_STUDENT_AGE,
            MAXIMUM_STUDENT_AGE,
            "Student date of birth",
        ),
        "class_name": cleaned["class_name"],
        "fees": validate_amount(cleaned["fees"], "School fees"),
        "status": status,
        "gender": cleaned["gender"],
        "address": cleaned["address"],
        "phone": validate_phone(cleaned["phone"], "Student phone number"),
        "email": validate_email(cleaned["email"]),
        "medical_info": cleaned["medical_info"],
        "parent_name": cleaned["parent_name"],
        "parent_phone": validate_phone(cleaned["parent_phone"], "Parent or guardian phone number"),
    }
