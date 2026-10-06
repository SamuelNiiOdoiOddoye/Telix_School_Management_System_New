"""Attendance validation, enrollment linkage, filtering, and summaries."""

from __future__ import annotations

import builtins
from datetime import date
from decimal import Decimal
from typing import Any, Callable, Mapping

from telix.academics.structure_service import AcademicStructureService
from telix.attendance.repository import AttendanceRepository
from telix.attendance.rules import ATTENDANCE_STATUSES, ATTENDED_STATUSES
from telix.core.errors import ValidationError
from telix.core.identifiers import generate_id
from telix.core.search import find_index_by_id

CENT = Decimal("0.01")


class AttendanceService:
    def __init__(
        self,
        repository: AttendanceRepository,
        structure: AcademicStructureService,
        student_exists: Callable[[str], bool],
    ) -> None:
        self._repository = repository
        self._structure = structure
        self._student_exists = student_exists

    def list(
        self,
        *,
        attendance_date: str = "",
        student_id: str = "",
        class_id: str = "",
    ) -> builtins.list[dict[str, Any]]:
        attendance_date = attendance_date.strip()
        if attendance_date:
            try:
                parsed_date = date.fromisoformat(attendance_date)
            except ValueError as error:
                raise ValidationError(
                    "Attendance filter date must use the format YYYY-MM-DD."
                ) from error
            if parsed_date.isoformat() != attendance_date:
                raise ValidationError("Attendance filter date must use the format YYYY-MM-DD.")
        records = self._repository.list()
        target_student = student_id.strip().casefold()
        target_class = class_id.strip().casefold()
        return [
            record
            for record in records
            if (not attendance_date or record.get("attendance_date") == attendance_date)
            and (
                not target_student or str(record.get("student_id", "")).casefold() == target_student
            )
            and (not target_class or str(record.get("class_id", "")).casefold() == target_class)
        ]

    def get(self, attendance_id: str) -> dict[str, Any] | None:
        target = attendance_id.strip().casefold()
        return next(
            (
                record
                for record in self._repository.list()
                if str(record.get("attendance_id", "")).casefold() == target
            ),
            None,
        )

    def add(self, values: Mapping[str, object]) -> dict[str, Any]:
        record = self._prepare(values)
        records = self._repository.list()
        self._ensure_unique(records, record)
        self._repository.save([*records, record])
        return record

    def update(self, attendance_id: str, values: Mapping[str, object]) -> dict[str, Any]:
        records = self._repository.list()
        index = find_index_by_id(records, "attendance_id", attendance_id)
        if index is None:
            raise ValidationError("Attendance record not found. Select a record first.")
        record = self._prepare(values, attendance_id)
        self._ensure_unique(records, record, ignored_id=attendance_id)
        updated = [*records[:index], record, *records[index + 1 :]]
        self._repository.save(updated)
        return record

    def delete(self, attendance_id: str) -> dict[str, Any]:
        records = self._repository.list()
        index = find_index_by_id(records, "attendance_id", attendance_id)
        if index is None:
            raise ValidationError("Attendance record not found. Select a record first.")
        deleted = records[index]
        self._repository.save([*records[:index], *records[index + 1 :]])
        return deleted

    def delete_for_student(self, student_id: str) -> int:
        target = student_id.strip().casefold()
        records = self._repository.list()
        remaining = [
            record
            for record in records
            if str(record.get("student_id", "")).strip().casefold() != target
        ]
        deleted_count = len(records) - len(remaining)
        if deleted_count:
            self._repository.save(remaining)
        return deleted_count

    def summary(self, records: builtins.list[dict[str, Any]] | None = None) -> dict[str, Any]:
        selected = self._repository.list() if records is None else records
        counts = {
            status: sum(record.get("status") == status for record in selected)
            for status in ATTENDANCE_STATUSES
        }
        denominator = len(selected) - counts["Excused"]
        attended = sum(counts[status] for status in ATTENDED_STATUSES)
        percentage = (
            (Decimal(attended) * Decimal("100") / Decimal(denominator)).quantize(CENT)
            if denominator
            else Decimal("0.00")
        )
        return {
            "total": len(selected),
            "present": counts["Present"],
            "absent": counts["Absent"],
            "late": counts["Late"],
            "excused": counts["Excused"],
            "attendance_percentage": percentage,
        }

    def _prepare(
        self, values: Mapping[str, object], attendance_id: str | None = None
    ) -> dict[str, Any]:
        student_id = str(values.get("student_id", "")).strip().upper()
        if not student_id:
            raise ValidationError("Student ID is required.")
        if not self._student_exists(student_id):
            raise ValidationError("Select an existing student for attendance.")
        attendance_date = str(values.get("attendance_date", "")).strip()
        try:
            parsed_date = date.fromisoformat(attendance_date)
        except ValueError as error:
            raise ValidationError("Attendance date must use the format YYYY-MM-DD.") from error
        if parsed_date.isoformat() != attendance_date:
            raise ValidationError("Attendance date must use the format YYYY-MM-DD.")
        status = str(values.get("status", "")).strip().title()
        if status not in ATTENDANCE_STATUSES:
            raise ValidationError(
                f"Attendance status must be one of: {', '.join(ATTENDANCE_STATUSES)}."
            )
        enrollment = self._structure.enrollment_for_student_on(student_id, attendance_date)
        if enrollment is None:
            raise ValidationError("Student has no class enrollment active on that date.")
        return {
            "attendance_id": attendance_id or generate_id("ATT"),
            "student_id": student_id,
            "class_id": enrollment["class_id"],
            "academic_year_id": enrollment["academic_year_id"],
            "enrollment_id": enrollment["enrollment_id"],
            "attendance_date": attendance_date,
            "status": status,
        }

    @staticmethod
    def _ensure_unique(
        records: builtins.list[dict[str, Any]],
        record: dict[str, Any],
        ignored_id: str | None = None,
    ) -> None:
        for existing in records:
            if (
                ignored_id
                and str(existing.get("attendance_id", "")).casefold() == ignored_id.casefold()
            ):
                continue
            if (
                str(existing.get("student_id", "")).casefold() == record["student_id"].casefold()
                and existing.get("attendance_date") == record["attendance_date"]
            ):
                raise ValidationError(
                    "Attendance has already been recorded for this student and date."
                )
