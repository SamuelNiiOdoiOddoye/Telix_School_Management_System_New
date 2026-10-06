"""Turns raw form values into a validated student record."""

from __future__ import annotations

from typing import Any, Mapping

from telix.core.validators import (
    require_fields,
    validate_amount,
    validate_date_of_birth,
    validate_email,
    validate_phone,
)
from telix.students.schema import STUDENT_FIELD_LABELS

MINIMUM_STUDENT_AGE = 3
MAXIMUM_STUDENT_AGE = 25


def prepare_student(values: Mapping[str, object]) -> dict[str, Any]:
    required_values = {
        field_name: values.get(field_name, "") for field_name in STUDENT_FIELD_LABELS
    }
    cleaned = require_fields(required_values, STUDENT_FIELD_LABELS)
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
        "gender": cleaned["gender"],
        "address": cleaned["address"],
        "phone": validate_phone(cleaned["phone"], "Student phone number"),
        "email": validate_email(cleaned["email"]),
        "medical_info": cleaned["medical_info"],
        "parent_name": cleaned["parent_name"],
        "parent_phone": validate_phone(cleaned["parent_phone"], "Parent or guardian phone number"),
    }
