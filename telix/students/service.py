"""Student business rules: unique IDs, immutable IDs, and lookups."""

from __future__ import annotations

import builtins
from typing import Any, Mapping

from telix.core.errors import ValidationError
from telix.core.search import filter_by_class, find_by_id, find_index_by_id
from telix.students.repository import StudentRepository
from telix.students.validator import prepare_student


class StudentService:
    def __init__(self, repository: StudentRepository | None = None) -> None:
        self._repository = repository or StudentRepository()

    def list(self) -> builtins.list[dict[str, Any]]:
        return self._repository.list()

    def get(self, student_id: str) -> dict[str, Any] | None:
        return find_by_id(self.list(), "student_id", student_id)

    def exists(self, student_id: str) -> bool:
        return self.get(student_id) is not None

    def by_class(self, class_name: str) -> builtins.list[dict[str, Any]]:
        return filter_by_class(self.list(), class_name)

    def classes(self) -> builtins.list[str]:
        return sorted({record["class_name"] for record in self.list() if record["class_name"]})

    def add(self, values: Mapping[str, object]) -> dict[str, Any]:
        student = prepare_student(values)
        records = self.list()
        if find_by_id(records, "student_id", student["student_id"]):
            raise ValidationError("That Student ID already exists. Use a unique Student ID.")
        records.append(student)
        self._repository.save(records)
        return student

    def update(self, existing_student_id: str, values: Mapping[str, object]) -> dict[str, Any]:
        student = prepare_student(values)
        if student["student_id"].casefold() != existing_student_id.strip().casefold():
            raise ValidationError(
                "Student ID cannot be changed. Create a new student record instead."
            )
        records = self.list()
        index = find_index_by_id(records, "student_id", existing_student_id)
        if index is None:
            raise ValidationError("Student record not found. Search by Student ID first.")
        records[index] = student
        self._repository.save(records)
        return student

    def delete(self, student_id: str) -> dict[str, Any]:
        records = self.list()
        index = find_index_by_id(records, "student_id", student_id)
        if index is None:
            raise ValidationError("Student record not found. Search by Student ID first.")
        deleted = records.pop(index)
        self._repository.save(records)
        return deleted
