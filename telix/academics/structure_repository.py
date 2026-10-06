"""JSON repositories for academic catalogs and student enrollments."""

from __future__ import annotations

import builtins
from typing import Any, Literal

from telix.config import (
    ACADEMIC_YEAR_FILE,
    CLASS_FILE,
    ENROLLMENT_FILE,
    SUBJECT_FILE,
    TERM_FILE,
)
from telix.core.errors import StorageError
from telix.storage.json_store import JsonStore

StructureKind = Literal["class", "subject", "academic_year", "term", "enrollment"]
ID_FIELDS: dict[StructureKind, str] = {
    "class": "class_id",
    "subject": "subject_id",
    "academic_year": "academic_year_id",
    "term": "term_id",
    "enrollment": "enrollment_id",
}


class AcademicStructureRepository:
    """Keeps each academic catalog in its own replaceable JSON collection."""

    def __init__(self, stores: dict[StructureKind, JsonStore] | None = None) -> None:
        self._stores = stores or {
            "class": JsonStore(CLASS_FILE),
            "subject": JsonStore(SUBJECT_FILE),
            "academic_year": JsonStore(ACADEMIC_YEAR_FILE),
            "term": JsonStore(TERM_FILE),
            "enrollment": JsonStore(ENROLLMENT_FILE),
        }

    def list(self, kind: StructureKind) -> builtins.list[dict[str, Any]]:
        records = self._stores[kind].load()
        if any(not isinstance(record, dict) for record in records):
            raise StorageError(
                f"{self._stores[kind].file_path.name} must contain only JSON object records."
            )
        seen_ids: set[str] = set()
        for record in records:
            record_id = record.get(ID_FIELDS[kind])
            if not isinstance(record_id, str) or not record_id.strip():
                raise StorageError(
                    f"{self._stores[kind].file_path.name} contains a record without an ID."
                )
            normalized_id = record_id.strip().casefold()
            if normalized_id in seen_ids:
                raise StorageError(
                    f"{self._stores[kind].file_path.name} contains duplicate record IDs."
                )
            seen_ids.add(normalized_id)
        return records

    def save(self, kind: StructureKind, records: builtins.list[dict[str, Any]]) -> None:
        self._stores[kind].save(records)
