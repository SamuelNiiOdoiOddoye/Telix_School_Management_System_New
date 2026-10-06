"""Turns raw form values into a validated teacher record."""

from __future__ import annotations

from typing import Any, Mapping

from telix.core.validators import (
    require_fields,
    validate_amount,
    validate_date_of_birth,
    validate_email,
    validate_phone,
)
from telix.teachers.schema import TEACHER_FIELD_LABELS

MINIMUM_TEACHER_AGE = 18
MAXIMUM_TEACHER_AGE = 100


def prepare_teacher(values: Mapping[str, object]) -> dict[str, Any]:
    required_values = {
        field_name: values.get(field_name, "") for field_name in TEACHER_FIELD_LABELS
    }
    cleaned = require_fields(required_values, TEACHER_FIELD_LABELS)
    return {
        "teacher_id": cleaned["teacher_id"].upper(),
        "name": cleaned["name"],
        "date_of_birth": validate_date_of_birth(
            cleaned["date_of_birth"],
            MINIMUM_TEACHER_AGE,
            MAXIMUM_TEACHER_AGE,
            "Teacher date of birth",
        ),
        "class_name": cleaned["class_name"],
        "salary": validate_amount(cleaned["salary"], "Salary"),
        "gender": cleaned["gender"],
        "address": cleaned["address"],
        "phone": validate_phone(cleaned["phone"], "Teacher phone number"),
        "email": validate_email(cleaned["email"]),
        "medical_info": cleaned["medical_info"],
        "emergency_contact": validate_phone(cleaned["emergency_contact"], "Emergency contact"),
    }
