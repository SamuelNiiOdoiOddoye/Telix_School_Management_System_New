"""Academic record operations linked to students by Student ID."""

from __future__ import annotations

import builtins
from typing import Any, Callable, Mapping

from telix.academics.repository import AcademicRepository
from telix.academics.rules import ensure_student_exists, ensure_unique_subject
from telix.academics.structure_service import AcademicStructureService
from telix.academics.validator import prepare_academic_record
from telix.core.errors import ValidationError
from telix.core.search import find_by_id, find_index_by_id

StudentExists = Callable[[str], bool]
NOT_FOUND_MESSAGE = "Academic record not found. Select a record from the table first."


class AcademicRecordService:
    def __init__(
        self,
        repository: AcademicRepository | None = None,
        structure: AcademicStructureService | None = None,
    ) -> None:
        self._repository = repository or AcademicRepository()
        self._structure = structure

    def list(self) -> builtins.list[dict[str, Any]]:
        return self._repository.list()

    def get(self, academic_id: str) -> dict[str, Any] | None:
        return find_by_id(self.list(), "academic_id", academic_id)

    def for_student(self, student_id: str) -> builtins.list[dict[str, Any]]:
        target = student_id.strip().casefold()
        return [record for record in self.list() if record["student_id"].casefold() == target]

    def add(self, values: Mapping[str, object], student_exists: StudentExists) -> dict[str, Any]:
        record = prepare_academic_record(values)
        ensure_student_exists(record["student_id"], student_exists)
        self._attach_catalog_references(record)
        records = self.list()
        ensure_unique_subject(records, record)
        records.append(record)
        self._repository.save(records)
        return record

    def update(
        self,
        existing_academic_id: str,
        values: Mapping[str, object],
        student_exists: StudentExists,
    ) -> dict[str, Any]:
        record = prepare_academic_record(values, existing_academic_id)
        ensure_student_exists(record["student_id"], student_exists)
        self._attach_catalog_references(record)
        records = self.list()
        index = find_index_by_id(records, "academic_id", existing_academic_id)
        if index is None:
            raise ValidationError(NOT_FOUND_MESSAGE)
        ensure_unique_subject(records, record, ignored_academic_id=existing_academic_id)
        records[index] = record
        self._repository.save(records)
        return record

    def delete(self, academic_id: str) -> dict[str, Any]:
        records = self.list()
        index = find_index_by_id(records, "academic_id", academic_id)
        if index is None:
            raise ValidationError(NOT_FOUND_MESSAGE)
        deleted = records.pop(index)
        self._repository.save(records)
        return deleted

    def delete_for_student(self, student_id: str) -> int:
        target = student_id.strip().casefold()
        records = self.list()
        remaining = [record for record in records if record["student_id"].casefold() != target]
        deleted_count = len(records) - len(remaining)
        if deleted_count:
            self._repository.save(remaining)
        return deleted_count

    def _attach_catalog_references(self, record: dict[str, Any]) -> None:
        references = (
            record["subject_id"],
            record["term_id"],
            record["academic_year_id"],
        )
        if not any(references):
            return
        if not all(references):
            raise ValidationError("Choose a managed subject, term, and academic year together.")
        if self._structure is None:
            raise ValidationError("Academic catalogs are unavailable; refresh and try again.")
        subject = self._structure.get("subject", record["subject_id"])
        term = self._structure.get("term", record["term_id"])
        year = self._structure.get("academic_year", record["academic_year_id"])
        if subject is None:
            raise ValidationError("Select an existing subject.")
        if term is None:
            raise ValidationError("Select an existing term.")
        if year is None:
            raise ValidationError("Select an existing academic year.")
        if term["academic_year_id"].casefold() != year["academic_year_id"].casefold():
            raise ValidationError(
                "The selected term does not belong to the selected academic year."
            )
        record["subject"] = subject["name"]
        record["term"] = term["name"]
        record["academic_year"] = year["name"]
