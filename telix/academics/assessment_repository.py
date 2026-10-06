"""JSON persistence for assessment scores and grading profiles."""

from __future__ import annotations

import builtins
from typing import Any, Literal

from telix.config import ASSESSMENT_FILE, GRADING_PROFILE_FILE
from telix.core.errors import StorageError
from telix.core.numbers import parse_amount
from telix.storage.json_store import JsonStore

AssessmentKind = Literal["assessment", "profile"]
ID_FIELDS: dict[AssessmentKind, str] = {
    "assessment": "assessment_id",
    "profile": "profile_id",
}


class AssessmentRepository:
    def __init__(self, stores: dict[AssessmentKind, JsonStore] | None = None) -> None:
        self._stores = stores or {
            "assessment": JsonStore(ASSESSMENT_FILE),
            "profile": JsonStore(GRADING_PROFILE_FILE),
        }

    def list(self, kind: AssessmentKind) -> builtins.list[dict[str, Any]]:
        store = self._stores[kind]
        records = store.load()
        if any(not isinstance(record, dict) for record in records):
            raise StorageError(f"{store.file_path.name} must contain only JSON object records.")
        seen_ids: set[str] = set()
        natural_keys: set[tuple[str, ...]] = set()
        for record in records:
            record_id = record.get(ID_FIELDS[kind])
            if not isinstance(record_id, str) or not record_id.strip():
                raise StorageError(f"{store.file_path.name} contains a record without an ID.")
            normalized_id = record_id.strip().casefold()
            if normalized_id in seen_ids:
                raise StorageError(f"{store.file_path.name} contains duplicate record IDs.")
            seen_ids.add(normalized_id)
            if kind == "assessment":
                required_fields = (
                    "student_id",
                    "subject_id",
                    "subject",
                    "academic_year_id",
                    "academic_year",
                    "term_id",
                    "term",
                    "component",
                )
                if any(
                    not isinstance(record.get(field), str) or not record[field].strip()
                    for field in required_fields
                ):
                    raise StorageError(f"{store.file_path.name} contains an incomplete record.")
                score = parse_amount(record.get("score"))
                if score is None or score < 0 or score > 100:
                    raise StorageError(f"{store.file_path.name} contains an invalid score.")
                natural_key = tuple(
                    record[field].strip().casefold()
                    for field in (
                        "student_id",
                        "subject_id",
                        "academic_year_id",
                        "term_id",
                        "component",
                    )
                )
                if natural_key in natural_keys:
                    raise StorageError(
                        f"{store.file_path.name} contains duplicate component scores."
                    )
                natural_keys.add(natural_key)
            else:
                if (
                    not isinstance(record.get("academic_year_id"), str)
                    or not record["academic_year_id"].strip()
                    or not isinstance(record.get("term_id", ""), str)
                    or record.get("method") not in {"weighted", "unweighted"}
                    or not isinstance(record.get("components"), list)
                    or not isinstance(record.get("grade_bands"), list)
                ):
                    raise StorageError(f"{store.file_path.name} contains an invalid profile.")
        return records

    def save(self, kind: AssessmentKind, records: builtins.list[dict[str, Any]]) -> None:
        self._stores[kind].save(records)
