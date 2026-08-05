"""Academic record operations linked to students by Student ID."""

from __future__ import annotations

from typing import Any, Callable

from config import ACADEMIC_FILE
from database import JsonStore
from search import find_by_id
from utils import ValidationError, clean_text, generate_id, require_fields, validate_score


ACADEMIC_FIELD_LABELS = {
    "student_id": "Student ID",
    "subject": "Subject",
    "score": "Score",
    "term": "Term",
    "academic_year": "Academic year",
}


class AcademicRecordService:
    def __init__(self, store: JsonStore | None = None) -> None:
        self.store = store or JsonStore(ACADEMIC_FILE)

    def list(self) -> list[dict[str, Any]]:
        return [self._normalise(record) for record in self.store.load() if isinstance(record, dict)]

    def get(self, academic_id: str) -> dict[str, Any] | None:
        return find_by_id(self.list(), "academic_id", academic_id)

    def for_student(self, student_id: str) -> list[dict[str, Any]]:
        target = student_id.strip().casefold()
        return [
            record for record in self.list() if record["student_id"].casefold() == target
        ]

    def add(
        self, values: dict[str, object], student_exists: Callable[[str], bool]
    ) -> dict[str, Any]:
        record = self._prepare(values)
        self._validate_student(record["student_id"], student_exists)
        records = self.list()
        self._ensure_unique_subject(records, record)
        records.append(record)
        self.store.save(records)
        return record

    def update(
        self,
        existing_academic_id: str,
        values: dict[str, object],
        student_exists: Callable[[str], bool],
    ) -> dict[str, Any]:
        record = self._prepare(values, existing_academic_id)
        self._validate_student(record["student_id"], student_exists)
        records = self.list()
        for index, current_record in enumerate(records):
            if current_record["academic_id"].casefold() == existing_academic_id.strip().casefold():
                self._ensure_unique_subject(records, record, ignored_academic_id=existing_academic_id)
                records[index] = record
                self.store.save(records)
                return record
        raise ValidationError("Academic record not found. Select a record from the table first.")

    def delete(self, academic_id: str) -> dict[str, Any]:
        records = self.list()
        for index, record in enumerate(records):
            if record["academic_id"].casefold() == academic_id.strip().casefold():
                deleted = records.pop(index)
                self.store.save(records)
                return deleted
        raise ValidationError("Academic record not found. Select a record from the table first.")

    def delete_for_student(self, student_id: str) -> int:
        target = student_id.strip().casefold()
        records = self.list()
        remaining_records = [
            record for record in records if record["student_id"].casefold() != target
        ]
        deleted_count = len(records) - len(remaining_records)
        if deleted_count:
            self.store.save(remaining_records)
        return deleted_count

    def _prepare(
        self, values: dict[str, object], academic_id: str | None = None
    ) -> dict[str, Any]:
        required_values = {
            field_name: values.get(field_name, "") for field_name in ACADEMIC_FIELD_LABELS
        }
        cleaned = require_fields(required_values, ACADEMIC_FIELD_LABELS)
        return {
            "academic_id": academic_id or generate_id("ACA"),
            "student_id": cleaned["student_id"].upper(),
            "subject": cleaned["subject"],
            "score": validate_score(cleaned["score"]),
            "term": cleaned["term"],
            "academic_year": cleaned["academic_year"],
        }

    @staticmethod
    def _validate_student(student_id: str, student_exists: Callable[[str], bool]) -> None:
        if not student_exists(student_id):
            raise ValidationError("Student ID was not found. Add the student before adding scores.")

    @staticmethod
    def _ensure_unique_subject(
        records: list[dict[str, Any]],
        candidate: dict[str, Any],
        ignored_academic_id: str | None = None,
    ) -> None:
        candidate_key = (
            candidate["student_id"].casefold(),
            candidate["subject"].casefold(),
            candidate["term"].casefold(),
            candidate["academic_year"].casefold(),
        )
        for record in records:
            if ignored_academic_id and record["academic_id"].casefold() == ignored_academic_id.casefold():
                continue
            record_key = (
                record["student_id"].casefold(),
                record["subject"].casefold(),
                record["term"].casefold(),
                record["academic_year"].casefold(),
            )
            if record_key == candidate_key:
                raise ValidationError(
                    "An academic record for this student, subject, term, and year already exists."
                )

    @staticmethod
    def _normalise(record: dict[str, Any]) -> dict[str, Any]:
        return {
            "academic_id": clean_text(record.get("academic_id") or record.get("ID")),
            "student_id": clean_text(record.get("student_id") or record.get("Student ID")),
            "subject": clean_text(record.get("subject") or record.get("Subject")),
            "score": record.get("score", record.get("Score", 0)),
            "term": clean_text(record.get("term") or record.get("Term")),
            "academic_year": clean_text(
                record.get("academic_year") or record.get("Academic Year")
            ),
        }
