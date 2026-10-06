"""Storage for teacher-to-subject assignments."""

from __future__ import annotations

from telix.config import TEACHER_ASSIGNMENT_FILE
from telix.core.errors import StorageError
from telix.core.text import clean_text
from telix.storage.json_store import JsonStore
from telix.storage.repository import JsonRecordRepository


def normalise_assignment(record: dict[str, object]) -> dict[str, object]:
    return {
        "assignment_id": clean_text(record.get("assignment_id", "")),
        "teacher_id": clean_text(record.get("teacher_id", "")),
        "teacher_name": clean_text(record.get("teacher_name", "")),
        "subject_id": clean_text(record.get("subject_id", "")),
        "subject_name": clean_text(record.get("subject_name", "")),
        "academic_year_id": clean_text(record.get("academic_year_id", "")),
        "academic_year": clean_text(record.get("academic_year", "")),
    }


class TeacherAssignmentRepository(JsonRecordRepository):
    def __init__(self, store: JsonStore | None = None) -> None:
        super().__init__(store or JsonStore(TEACHER_ASSIGNMENT_FILE), normalise_assignment)

    def list(self) -> list[dict[str, object]]:
        raw_records = self._store.load()
        if any(not isinstance(record, dict) for record in raw_records):
            raise StorageError(
                f"{self._store.file_path.name} must contain only JSON object records."
            )
        records = [normalise_assignment(record) for record in raw_records]
        seen_ids: set[str] = set()
        for record in records:
            assignment_id = record.get("assignment_id")
            if not isinstance(assignment_id, str) or not assignment_id:
                raise StorageError(
                    f"{self._store.file_path.name} contains an assignment without an ID."
                )
            normalized_id = assignment_id.casefold()
            if normalized_id in seen_ids:
                raise StorageError(
                    f"{self._store.file_path.name} contains duplicate assignment IDs."
                )
            seen_ids.add(normalized_id)
            if not all(
                isinstance(record.get(field), str) and record[field]
                for field in (
                    "teacher_id",
                    "teacher_name",
                    "subject_id",
                    "subject_name",
                    "academic_year_id",
                    "academic_year",
                )
            ):
                raise StorageError(
                    f"{self._store.file_path.name} contains an incomplete assignment."
                )
        return records

    def references(self, field: str, entity_id: str) -> bool:
        target = entity_id.strip().casefold()
        return any(str(record.get(field, "")).casefold() == target for record in self.list())
