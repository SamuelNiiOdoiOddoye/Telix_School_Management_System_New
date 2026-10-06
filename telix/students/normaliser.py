"""Converts stored student records (current or legacy key names) to the current shape."""

from __future__ import annotations

from typing import Any

from telix.core.numbers import parse_amount
from telix.core.text import clean_text, first_value


def normalise_student(record: dict[str, Any]) -> dict[str, Any]:
    fees = first_value(record, "fees", "Fees", default=0)
    parsed_fees = parse_amount(fees)
    return {
        "student_id": clean_text(first_value(record, "student_id", "ID")),
        "name": clean_text(first_value(record, "name", "Name")),
        "date_of_birth": clean_text(first_value(record, "date_of_birth", "DOB")),
        "class_name": clean_text(first_value(record, "class_name", "Class")),
        "fees": parsed_fees if parsed_fees is not None else fees,
        "status": clean_text(first_value(record, "status", "Status", default="Active")) or "Active",
        "gender": clean_text(first_value(record, "gender", "Gender")),
        "address": clean_text(first_value(record, "address", "Address")),
        "phone": clean_text(first_value(record, "phone", "Contact")),
        "email": clean_text(first_value(record, "email", "Email Address")),
        "medical_info": clean_text(
            first_value(record, "medical_info", "MedicalInfo", default="Not provided")
        ),
        "parent_name": clean_text(
            first_value(record, "parent_name", "Parent Name", default="Not provided")
        ),
        "parent_phone": clean_text(
            first_value(record, "parent_phone", "Parent Phone", "Emergency Contact")
        ),
    }
