"""JSON persistence for attendance records."""

from __future__ import annotations

import builtins
from datetime import date
from typing import Any

from telix.config import ATTENDANCE_FILE
from telix.attendance.rules import ATTENDANCE_STATUSES
from telix.core.errors import StorageError
from telix.storage.json_store import JsonStore


class AttendanceRepository:
    """Reads and writes attendance records while rejecting invalid collection shapes."""

    def __init__(self, store: JsonStore | None = None) -> None:
        self._store = store or JsonStore(ATTENDANCE_FILE)

    def list(self) -> builtins.list[dict[str, Any]]:
        records = self._store.load()
        if any(not isinstance(record, dict) for record in records):
            raise StorageError(
                f"{self._store.file_path.name} must contain only JSON object records."
            )
        seen_ids: set[str] = set()
        seen_student_dates: set[tuple[str, str]] = set()
        for record in records:
            record_id = record.get("attendance_id")
            if not isinstance(record_id, str) or not record_id.strip():
                raise StorageError(
                    f"{self._store.file_path.name} contains a record without an attendance ID."
                )
            normalized_id = record_id.strip().casefold()
            if normalized_id in seen_ids:
                raise StorageError(
                    f"{self._store.file_path.name} contains duplicate attendance IDs."
                )
            seen_ids.add(normalized_id)
            required_fields = (
                "student_id",
                "class_id",
                "academic_year_id",
                "enrollment_id",
                "attendance_date",
                "status",
            )
            if any(
                not isinstance(record.get(field), str) or not record[field].strip()
                for field in required_fields
            ):
                raise StorageError(
                    f"{self._store.file_path.name} contains an incomplete attendance record."
                )
            try:
                parsed_date = date.fromisoformat(record["attendance_date"])
            except ValueError as error:
                raise StorageError(
                    f"{self._store.file_path.name} contains an invalid attendance date."
                ) from error
            if (
                parsed_date.isoformat() != record["attendance_date"]
                or record["status"] not in ATTENDANCE_STATUSES
            ):
                raise StorageError(
                    f"{self._store.file_path.name} contains an invalid attendance record."
                )
            unique_key = (record["student_id"].casefold(), record["attendance_date"])
            if unique_key in seen_student_dates:
                raise StorageError(
                    f"{self._store.file_path.name} contains duplicate student/date attendance."
                )
            seen_student_dates.add(unique_key)
        return records

    def save(self, records: builtins.list[dict[str, Any]]) -> None:
        self._store.save(records)
