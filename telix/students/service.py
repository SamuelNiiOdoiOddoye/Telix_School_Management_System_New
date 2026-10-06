"""Student business rules: unique IDs, immutable IDs, and lookups."""

from __future__ import annotations

import builtins
from typing import Any, Mapping

from telix.authentication.roles import (
    FINANCE_OFFICER,
    STUDENT,
    SUPER_ADMIN,
    TEACHER,
    Authorization,
    STUDENTS_DELETE,
    STUDENTS_READ,
    STUDENTS_READ_FINANCE,
    STUDENTS_READ_OWN,
    STUDENTS_READ_TEACHING,
    STUDENTS_WRITE,
)
from telix.core.errors import ValidationError
from telix.core.search import filter_by_class, find_by_id, find_index_by_id
from telix.students.repository import StudentRepository
from telix.students.schema import STUDENT_STATUS_TRANSITIONS, STUDENT_STATUSES
from telix.students.validator import prepare_student


class StudentService:
    def __init__(
        self,
        repository: StudentRepository | None = None,
        authorization: Authorization | None = None,
    ) -> None:
        self._repository = repository or StudentRepository()
        self._authorization = authorization or Authorization(SUPER_ADMIN)

    @property
    def authorization(self) -> Authorization:
        return self._authorization

    def list(self) -> builtins.list[dict[str, Any]]:
        self._authorization.require_any(
            STUDENTS_READ,
            STUDENTS_READ_FINANCE,
            STUDENTS_READ_TEACHING,
            STUDENTS_READ_OWN,
        )
        records = self._authorization.filter_student_records(self._repository.list())
        if self._authorization.role == FINANCE_OFFICER:
            allowed_fields = {"student_id", "name", "status", "fees"}
        elif self._authorization.role == TEACHER:
            allowed_fields = {"student_id", "name", "status", "class_name"}
        elif self._authorization.role == STUDENT:
            allowed_fields = {
                "student_id",
                "name",
                "date_of_birth",
                "class_name",
                "status",
                "gender",
                "address",
                "phone",
                "email",
            }
        else:
            return records
        return [
            {field: value for field, value in record.items() if field in allowed_fields}
            for record in records
        ]

    def get(self, student_id: str) -> dict[str, Any] | None:
        return find_by_id(self.list(), "student_id", student_id)

    def exists(self, student_id: str) -> bool:
        return self.get(student_id) is not None

    def by_class(self, class_name: str) -> builtins.list[dict[str, Any]]:
        return filter_by_class(self.list(), class_name)

    def by_status(self, status: str) -> builtins.list[dict[str, Any]]:
        selected = status.strip().casefold()
        if selected and selected not in {value.casefold() for value in STUDENT_STATUSES}:
            raise ValidationError(f"Student status must be one of: {', '.join(STUDENT_STATUSES)}.")
        return [
            record
            for record in self.list()
            if not selected or record["status"].casefold() == selected
        ]

    def classes(self) -> builtins.list[str]:
        return sorted({record["class_name"] for record in self.list() if record["class_name"]})

    def add(self, values: Mapping[str, object]) -> dict[str, Any]:
        self._authorization.require(STUDENTS_WRITE)
        student = prepare_student(values)
        records = self.list()
        if find_by_id(records, "student_id", student["student_id"]):
            raise ValidationError("That Student ID already exists. Use a unique Student ID.")
        records.append(student)
        self._repository.save(records)
        return student

    def update(self, existing_student_id: str, values: Mapping[str, object]) -> dict[str, Any]:
        self._authorization.require(STUDENTS_WRITE)
        student = prepare_student(values)
        if student["student_id"].casefold() != existing_student_id.strip().casefold():
            raise ValidationError(
                "Student ID cannot be changed. Create a new student record instead."
            )
        records = self.list()
        index = find_index_by_id(records, "student_id", existing_student_id)
        if index is None:
            raise ValidationError("Student record not found. Search by Student ID first.")
        previous_status = records[index].get("status", "Active")
        if student["status"] not in STUDENT_STATUS_TRANSITIONS.get(
            str(previous_status), frozenset()
        ):
            raise ValidationError(
                f"Cannot change student status from {previous_status} to {student['status']}."
            )
        records[index] = student
        self._repository.save(records)
        return student

    def delete(self, student_id: str) -> dict[str, Any]:
        self._authorization.require(STUDENTS_DELETE)
        records = self.list()
        index = find_index_by_id(records, "student_id", student_id)
        if index is None:
            raise ValidationError("Student record not found. Search by Student ID first.")
        deleted = records.pop(index)
        self._repository.save(records)
        return deleted
