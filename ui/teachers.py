"""Teacher record operations for the Telix School Management System."""

from __future__ import annotations

from typing import Any

from config import TEACHER_FILE
from database import JsonStore
from search import find_by_id
from utils import (
    ValidationError,
    clean_text,
    require_fields,
    validate_amount,
    validate_date_of_birth,
    validate_email,
    validate_phone,
)


TEACHER_FIELD_LABELS = {
    "teacher_id": "Teacher ID",
    "name": "Teacher name",
    "date_of_birth": "Date of birth",
    "class_name": "Class or subject",
    "salary": "Salary",
    "gender": "Gender",
    "address": "Address",
    "phone": "Teacher phone number",
    "email": "Email address",
    "medical_info": "Medical information",
    "emergency_contact": "Emergency contact",
}


def _first_value(record: dict[str, Any], *keys: str, default: Any = "") -> Any:
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return value
    return default


class TeacherService:
    def __init__(self, store: JsonStore | None = None) -> None:
        self.store = store or JsonStore(TEACHER_FILE)

    def list(self) -> list[dict[str, Any]]:
        return [self._normalise(record) for record in self.store.load() if isinstance(record, dict)]

    def get(self, teacher_id: str) -> dict[str, Any] | None:
        return find_by_id(self.list(), "teacher_id", teacher_id)

    def add(self, values: dict[str, object]) -> dict[str, Any]:
        teacher = self._prepare(values)
        records = self.list()
        if find_by_id(records, "teacher_id", teacher["teacher_id"]):
            raise ValidationError("That Teacher ID already exists. Use a unique Teacher ID.")
        records.append(teacher)
        self.store.save(records)
        return teacher

    def update(self, existing_teacher_id: str, values: dict[str, object]) -> dict[str, Any]:
        teacher = self._prepare(values)
        if teacher["teacher_id"].casefold() != existing_teacher_id.strip().casefold():
            raise ValidationError("Teacher ID cannot be changed. Create a new teacher record instead.")

        records = self.list()
        for index, record in enumerate(records):
            if record["teacher_id"].casefold() == existing_teacher_id.strip().casefold():
                records[index] = teacher
                self.store.save(records)
                return teacher
        raise ValidationError("Teacher record not found. Search by Teacher ID first.")

    def delete(self, teacher_id: str) -> dict[str, Any]:
        records = self.list()
        for index, record in enumerate(records):
            if record["teacher_id"].casefold() == teacher_id.strip().casefold():
                deleted = records.pop(index)
                self.store.save(records)
                return deleted
        raise ValidationError("Teacher record not found. Search by Teacher ID first.")

    def _prepare(self, values: dict[str, object]) -> dict[str, Any]:
        required_values = {
            field_name: values.get(field_name, "") for field_name in TEACHER_FIELD_LABELS
        }
        cleaned = require_fields(required_values, TEACHER_FIELD_LABELS)
        return {
            "teacher_id": cleaned["teacher_id"].upper(),
            "name": cleaned["name"],
            "date_of_birth": validate_date_of_birth(
                cleaned["date_of_birth"], 18, 100, "Teacher date of birth"
            ),
            "class_name": cleaned["class_name"],
            "salary": validate_amount(cleaned["salary"], "Salary"),
            "gender": cleaned["gender"],
            "address": cleaned["address"],
            "phone": validate_phone(cleaned["phone"], "Teacher phone number"),
            "email": validate_email(cleaned["email"]),
            "medical_info": cleaned["medical_info"],
            "emergency_contact": validate_phone(
                cleaned["emergency_contact"], "Emergency contact"
            ),
        }

    @staticmethod
    def _normalise(record: dict[str, Any]) -> dict[str, Any]:
        return {
            "teacher_id": clean_text(_first_value(record, "teacher_id", "Teacher ID", "TID")),
            "name": clean_text(_first_value(record, "name", "Teacher Name")),
            "date_of_birth": clean_text(
                _first_value(record, "date_of_birth", "Teacher DOB")
            ),
            "class_name": clean_text(
                _first_value(record, "class_name", "Teacher Class", "Class")
            ),
            "salary": _first_value(record, "salary", "Teacher Salary", "Salary", default=0),
            "gender": clean_text(_first_value(record, "gender", "Teacher Gender", "Gender")),
            "address": clean_text(_first_value(record, "address", "Teacher Address", "Address")),
            "phone": clean_text(_first_value(record, "phone", "Teacher Contact", "Contact")),
            "email": clean_text(
                _first_value(record, "email", "Teacher Email Address", "Email Address")
            ),
            "medical_info": clean_text(
                _first_value(
                    record, "medical_info", "Teacher MedicalInfo", "MedicalInfo", default="Not provided"
                )
            ),
            "emergency_contact": clean_text(
                _first_value(
                    record,
                    "emergency_contact",
                    "Teacher Emergency Contact",
                    "Teacher Emergency contact",
                    "Emergency Contact",
                )
            ),
        }
