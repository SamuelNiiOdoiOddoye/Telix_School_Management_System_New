"""Student record operations for the Telix School Management System."""

from __future__ import annotations

from typing import Any

from config import STUDENT_FILE
from database import JsonStore
from search import filter_by_class, find_by_id
from utils import (
    ValidationError,
    clean_text,
    require_fields,
    validate_amount,
    validate_date_of_birth,
    validate_email,
    validate_phone,
)


STUDENT_FIELD_LABELS = {
    "student_id": "Student ID",
    "name": "Student name",
    "date_of_birth": "Date of birth",
    "class_name": "Class",
    "fees": "School fees",
    "gender": "Gender",
    "address": "Address",
    "phone": "Student phone number",
    "email": "Email address",
    "medical_info": "Medical information",
    "parent_name": "Parent or guardian name",
    "parent_phone": "Parent or guardian phone number",
}


def _first_value(record: dict[str, Any], *keys: str, default: Any = "") -> Any:
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return value
    return default


class StudentService:
    def __init__(self, store: JsonStore | None = None) -> None:
        self.store = store or JsonStore(STUDENT_FILE)

    def list(self) -> list[dict[str, Any]]:
        return [self._normalise(record) for record in self.store.load() if isinstance(record, dict)]

    def get(self, student_id: str) -> dict[str, Any] | None:
        return find_by_id(self.list(), "student_id", student_id)

    def add(self, values: dict[str, object]) -> dict[str, Any]:
        student = self._prepare(values)
        records = self.list()
        if find_by_id(records, "student_id", student["student_id"]):
            raise ValidationError("That Student ID already exists. Use a unique Student ID.")
        records.append(student)
        self.store.save(records)
        return student

    def update(self, existing_student_id: str, values: dict[str, object]) -> dict[str, Any]:
        student = self._prepare(values)
        if student["student_id"].casefold() != existing_student_id.strip().casefold():
            raise ValidationError("Student ID cannot be changed. Create a new student record instead.")

        records = self.list()
        for index, record in enumerate(records):
            if record["student_id"].casefold() == existing_student_id.strip().casefold():
                records[index] = student
                self.store.save(records)
                return student
        raise ValidationError("Student record not found. Search by Student ID first.")

    def delete(self, student_id: str) -> dict[str, Any]:
        records = self.list()
        for index, record in enumerate(records):
            if record["student_id"].casefold() == student_id.strip().casefold():
                deleted = records.pop(index)
                self.store.save(records)
                return deleted
        raise ValidationError("Student record not found. Search by Student ID first.")

    def by_class(self, class_name: str) -> list[dict[str, Any]]:
        return filter_by_class(self.list(), class_name)

    def classes(self) -> list[str]:
        return sorted({record["class_name"] for record in self.list() if record["class_name"]})

    def _prepare(self, values: dict[str, object]) -> dict[str, Any]:
        required_values = {
            field_name: values.get(field_name, "") for field_name in STUDENT_FIELD_LABELS
        }
        cleaned = require_fields(required_values, STUDENT_FIELD_LABELS)
        return {
            "student_id": cleaned["student_id"].upper(),
            "name": cleaned["name"],
            "date_of_birth": validate_date_of_birth(
                cleaned["date_of_birth"], 3, 25, "Student date of birth"
            ),
            "class_name": cleaned["class_name"],
            "fees": validate_amount(cleaned["fees"], "School fees"),
            "gender": cleaned["gender"],
            "address": cleaned["address"],
            "phone": validate_phone(cleaned["phone"], "Student phone number"),
            "email": validate_email(cleaned["email"]),
            "medical_info": cleaned["medical_info"],
            "parent_name": cleaned["parent_name"],
            "parent_phone": validate_phone(
                cleaned["parent_phone"], "Parent or guardian phone number"
            ),
        }

    @staticmethod
    def _normalise(record: dict[str, Any]) -> dict[str, Any]:
        return {
            "student_id": clean_text(_first_value(record, "student_id", "ID")),
            "name": clean_text(_first_value(record, "name", "Name")),
            "date_of_birth": clean_text(_first_value(record, "date_of_birth", "DOB")),
            "class_name": clean_text(_first_value(record, "class_name", "Class")),
            "fees": _first_value(record, "fees", "Fees", default=0),
            "gender": clean_text(_first_value(record, "gender", "Gender")),
            "address": clean_text(_first_value(record, "address", "Address")),
            "phone": clean_text(_first_value(record, "phone", "Contact")),
            "email": clean_text(_first_value(record, "email", "Email Address")),
            "medical_info": clean_text(
                _first_value(record, "medical_info", "MedicalInfo", default="Not provided")
            ),
            "parent_name": clean_text(
                _first_value(record, "parent_name", "Parent Name", default="Not provided")
            ),
            "parent_phone": clean_text(
                _first_value(record, "parent_phone", "Parent Phone", "Emergency Contact")
            ),
        }
