"""Converts stored teacher records (current or legacy key names) to the current shape."""

from __future__ import annotations

from typing import Any

from telix.core.numbers import parse_amount
from telix.core.text import clean_text, first_value


def normalise_teacher(record: dict[str, Any]) -> dict[str, Any]:
    salary = first_value(record, "salary", "Teacher Salary", "Salary", default=0)
    parsed_salary = parse_amount(salary)
    return {
        "teacher_id": clean_text(first_value(record, "teacher_id", "Teacher ID", "TID")),
        "name": clean_text(first_value(record, "name", "Teacher Name")),
        "date_of_birth": clean_text(first_value(record, "date_of_birth", "Teacher DOB")),
        "class_name": clean_text(first_value(record, "class_name", "Teacher Class", "Class")),
        "salary": parsed_salary if parsed_salary is not None else salary,
        "gender": clean_text(first_value(record, "gender", "Teacher Gender", "Gender")),
        "address": clean_text(first_value(record, "address", "Teacher Address", "Address")),
        "phone": clean_text(first_value(record, "phone", "Teacher Contact", "Contact")),
        "email": clean_text(first_value(record, "email", "Teacher Email Address", "Email Address")),
        "medical_info": clean_text(
            first_value(
                record, "medical_info", "Teacher MedicalInfo", "MedicalInfo", default="Not provided"
            )
        ),
        "emergency_contact": clean_text(
            first_value(
                record,
                "emergency_contact",
                "Teacher Emergency Contact",
                "Teacher Emergency contact",
                "Emergency Contact",
            )
        ),
    }
