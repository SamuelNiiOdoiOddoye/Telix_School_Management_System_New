"""Teacher business rules: unique IDs, immutable IDs, and lookups."""

from __future__ import annotations

import builtins
from typing import Any, Mapping

from telix.core.errors import ValidationError
from telix.core.search import find_by_id, find_index_by_id
from telix.teachers.assignment_repository import TeacherAssignmentRepository
from telix.teachers.repository import TeacherRepository
from telix.teachers.validator import prepare_teacher


class TeacherService:
    def __init__(
        self,
        repository: TeacherRepository | None = None,
        assignment_repository: TeacherAssignmentRepository | None = None,
    ) -> None:
        self._repository = repository or TeacherRepository()
        self._assignment_repository = assignment_repository

    def list(self) -> builtins.list[dict[str, Any]]:
        return self._repository.list()

    def get(self, teacher_id: str) -> dict[str, Any] | None:
        return find_by_id(self.list(), "teacher_id", teacher_id)

    def add(self, values: Mapping[str, object]) -> dict[str, Any]:
        teacher = prepare_teacher(values)
        records = self.list()
        if find_by_id(records, "teacher_id", teacher["teacher_id"]):
            raise ValidationError("That Teacher ID already exists. Use a unique Teacher ID.")
        records.append(teacher)
        self._repository.save(records)
        return teacher

    def update(self, existing_teacher_id: str, values: Mapping[str, object]) -> dict[str, Any]:
        teacher = prepare_teacher(values)
        if teacher["teacher_id"].casefold() != existing_teacher_id.strip().casefold():
            raise ValidationError(
                "Teacher ID cannot be changed. Create a new teacher record instead."
            )
        records = self.list()
        index = find_index_by_id(records, "teacher_id", existing_teacher_id)
        if index is None:
            raise ValidationError("Teacher record not found. Search by Teacher ID first.")
        records[index] = teacher
        self._repository.save(records)
        return teacher

    def delete(self, teacher_id: str) -> dict[str, Any]:
        if self._assignment_repository and self._assignment_repository.references(
            "teacher_id", teacher_id
        ):
            raise ValidationError(
                "Cannot delete this teacher while subject assignments refer to them."
            )
        records = self.list()
        index = find_index_by_id(records, "teacher_id", teacher_id)
        if index is None:
            raise ValidationError("Teacher record not found. Search by Teacher ID first.")
        deleted = records.pop(index)
        self._repository.save(records)
        return deleted
