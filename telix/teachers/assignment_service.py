"""Validation and maintenance of teacher-to-subject assignments."""

from __future__ import annotations

import builtins
from typing import Any, Callable, Mapping

from telix.authentication.roles import (
    ACADEMIC_SETUP_WRITE,
    Authorization,
    SUPER_ADMIN,
)
from telix.core.errors import ValidationError
from telix.core.identifiers import generate_id
from telix.core.search import find_index_by_id
from telix.core.text import clean_text
from telix.academics.structure_repository import StructureKind
from telix.teachers.assignment_repository import TeacherAssignmentRepository

EntityLookup = Callable[[str], dict[str, Any] | None]
CatalogLookup = Callable[[StructureKind, str], dict[str, Any] | None]


class TeacherAssignmentService:
    def __init__(
        self,
        repository: TeacherAssignmentRepository | None = None,
        teacher_lookup: EntityLookup | None = None,
        catalog_lookup: CatalogLookup | None = None,
        authorization: Authorization | None = None,
    ) -> None:
        self._repository = repository or TeacherAssignmentRepository()
        self._teacher_lookup = teacher_lookup or (lambda _teacher_id: None)
        self._catalog_lookup = catalog_lookup or (lambda _kind, _entity_id: None)
        self._authorization = authorization or Authorization(SUPER_ADMIN)

    def list(self) -> builtins.list[dict[str, Any]]:
        self._authorization.require(ACADEMIC_SETUP_WRITE)
        return self._repository.list()

    def for_teacher(self, teacher_id: str) -> builtins.list[dict[str, Any]]:
        self._authorization.require(ACADEMIC_SETUP_WRITE)
        target = teacher_id.strip().casefold()
        return [
            item for item in self.list() if str(item.get("teacher_id", "")).casefold() == target
        ]

    def add(self, values: Mapping[str, object]) -> dict[str, Any]:
        self._authorization.require(ACADEMIC_SETUP_WRITE)
        record = self._prepare(values, generate_id("TAS"))
        records = self.list()
        self._ensure_unique(records, record)
        self._repository.save([*records, record])
        return record

    def update(self, assignment_id: str, values: Mapping[str, object]) -> dict[str, Any]:
        self._authorization.require(ACADEMIC_SETUP_WRITE)
        records = self.list()
        index = find_index_by_id(records, "assignment_id", assignment_id)
        if index is None:
            raise ValidationError("Teacher assignment not found.")
        record = self._prepare(values, str(records[index]["assignment_id"]))
        self._ensure_unique(records, record, assignment_id)
        records[index] = record
        self._repository.save(records)
        return record

    def delete(self, assignment_id: str) -> dict[str, Any]:
        self._authorization.require(ACADEMIC_SETUP_WRITE)
        records = self.list()
        index = find_index_by_id(records, "assignment_id", assignment_id)
        if index is None:
            raise ValidationError("Teacher assignment not found.")
        deleted = records.pop(index)
        self._repository.save(records)
        return deleted

    def _prepare(self, values: Mapping[str, object], assignment_id: str) -> dict[str, Any]:
        teacher_id = clean_text(values.get("teacher_id", ""))
        subject_id = clean_text(values.get("subject_id", ""))
        academic_year_id = clean_text(values.get("academic_year_id", ""))
        if not teacher_id:
            raise ValidationError("Teacher is required for this assignment.")
        if not subject_id:
            raise ValidationError("Subject is required for this assignment.")
        if not academic_year_id:
            raise ValidationError("Academic year is required for this assignment.")

        teacher = self._teacher_lookup(teacher_id)
        subject = self._catalog_lookup("subject", subject_id)
        year = self._catalog_lookup("academic_year", academic_year_id)
        if teacher is None:
            raise ValidationError("Select an existing teacher for this assignment.")
        if subject is None:
            raise ValidationError("Select an existing subject for this assignment.")
        if year is None:
            raise ValidationError("Select an existing academic year for this assignment.")

        return {
            "assignment_id": assignment_id,
            "teacher_id": teacher["teacher_id"],
            "teacher_name": teacher["name"],
            "subject_id": subject["subject_id"],
            "subject_name": subject["name"],
            "academic_year_id": year["academic_year_id"],
            "academic_year": year["name"],
        }

    def _ensure_unique(
        self,
        records: builtins.list[dict[str, Any]],
        record: dict[str, Any],
        ignored_id: str | None = None,
    ) -> None:
        for existing in records:
            if (
                ignored_id
                and str(existing.get("assignment_id", "")).casefold() == ignored_id.casefold()
            ):
                continue
            if all(
                str(existing.get(field, "")).casefold() == str(record[field]).casefold()
                for field in ("teacher_id", "subject_id", "academic_year_id")
            ):
                raise ValidationError(
                    "That teacher is already assigned to this subject for this academic year."
                )
