"""Validation and workflows for academic catalogs and effective-dated enrollment."""

from __future__ import annotations

import builtins
from datetime import date, timedelta
from typing import Any, Callable, Mapping

from telix.academics.structure_repository import AcademicStructureRepository, StructureKind
from telix.core.errors import StorageError, ValidationError
from telix.core.identifiers import generate_id
from telix.core.text import clean_text
from telix.teachers.assignment_repository import TeacherAssignmentRepository

ID_FIELDS: dict[StructureKind, str] = {
    "class": "class_id",
    "subject": "subject_id",
    "academic_year": "academic_year_id",
    "term": "term_id",
    "enrollment": "enrollment_id",
}
PREFIXES: dict[StructureKind, str] = {
    "class": "CLS",
    "subject": "SUB",
    "academic_year": "ACY",
    "term": "TRM",
    "enrollment": "ENR",
}
ENROLLMENT_STATUSES = {"active", "completed", "withdrawn", "transferred"}
StudentExists = Callable[[str], bool]


def _text(values: Mapping[str, object], field: str, label: str) -> str:
    value = clean_text(values.get(field, ""))
    if not value:
        raise ValidationError(f"{label} is required.")
    return value


def _optional_text(values: Mapping[str, object], field: str) -> str:
    return clean_text(values.get(field, ""))


def _date(values: Mapping[str, object], field: str, label: str, *, optional: bool = False) -> str:
    value = _optional_text(values, field)
    if not value and optional:
        return ""
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ValidationError(f"{label} must use the format YYYY-MM-DD.") from error
    if parsed.isoformat() != value:
        raise ValidationError(f"{label} must use the format YYYY-MM-DD.")
    return value


def _require_order(start: str, end: str, label: str) -> None:
    if date.fromisoformat(start) > date.fromisoformat(end):
        raise ValidationError(f"{label} end date must be on or after its start date.")


def _overlaps(first_start: str, first_end: str, second_start: str, second_end: str) -> bool:
    first_end_date = date.max if not first_end else date.fromisoformat(first_end)
    second_end_date = date.max if not second_end else date.fromisoformat(second_end)
    return (
        date.fromisoformat(first_start) <= second_end_date
        and date.fromisoformat(second_start) <= first_end_date
    )


def _stored_period(
    record: dict[str, Any], label: str, *, allow_open_end: bool = False
) -> tuple[str, str]:
    start = record.get("start_date")
    end = record.get("end_date", "") if allow_open_end else record.get("end_date")
    if not isinstance(start, str) or not isinstance(end, str) or (not end and not allow_open_end):
        raise ValidationError(f"Stored {label.lower()} data is incomplete; review its JSON file.")
    try:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end) if end else None
    except ValueError as error:
        raise ValidationError(
            f"Stored {label.lower()} dates are invalid; review its JSON file."
        ) from error
    if start_date.isoformat() != start or (end_date and end_date.isoformat() != end):
        raise ValidationError(f"Stored {label.lower()} dates are invalid; review its JSON file.")
    if end_date and start_date > end_date:
        raise ValidationError(
            f"Stored {label.lower()} date range is invalid; review its JSON file."
        )
    return start, end


class AcademicStructureService:
    """Owns stable IDs, validation, uniqueness, and relationship rules for V1 catalogs."""

    def __init__(
        self,
        repository: AcademicStructureRepository | None = None,
        student_exists: StudentExists | None = None,
        assignment_repository: TeacherAssignmentRepository | None = None,
    ) -> None:
        self._repository = repository or AcademicStructureRepository()
        self._student_exists = student_exists or (lambda _student_id: False)
        self._assignment_repository = assignment_repository

    def list(self, kind: StructureKind) -> builtins.list[dict[str, Any]]:
        return self._repository.list(kind)

    def get(self, kind: StructureKind, entity_id: str) -> dict[str, Any] | None:
        records = self.list(kind)
        index = self._find_index(kind, records, entity_id)
        return records[index] if index is not None else None

    def add(self, kind: StructureKind, values: Mapping[str, object]) -> dict[str, Any]:
        record = self._prepare(kind, values)
        records = self.list(kind)
        self._ensure_unique_id(kind, records, record[ID_FIELDS[kind]])
        self._ensure_unique(kind, record, records)
        self._repository.save(kind, [*records, record])
        return record

    def update(
        self, kind: StructureKind, entity_id: str, values: Mapping[str, object]
    ) -> dict[str, Any]:
        records = self.list(kind)
        index = self._find_index(kind, records, entity_id)
        if index is None:
            raise ValidationError(f"{self._label(kind)} not found.")
        record = self._prepare(kind, values, entity_id)
        self._ensure_unique(kind, record, records, ignored_id=entity_id)
        if kind == "academic_year":
            self._ensure_children_within_year(record)
        self._repository.save(kind, [*records[:index], record, *records[index + 1 :]])
        return record

    def delete(self, kind: StructureKind, entity_id: str) -> dict[str, Any]:
        records = self.list(kind)
        index = self._find_index(kind, records, entity_id)
        if index is None:
            raise ValidationError(f"{self._label(kind)} not found.")
        record = records[index]
        self._ensure_not_referenced(kind, record)
        self._repository.save(kind, [*records[:index], *records[index + 1 :]])
        return record

    def delete_for_student(self, student_id: str) -> int:
        target = student_id.strip().casefold()
        records = self.list("enrollment")
        remaining = [
            record for record in records if not self._same(record.get("student_id"), target)
        ]
        deleted_count = len(records) - len(remaining)
        if deleted_count:
            self._repository.save("enrollment", remaining)
        return deleted_count

    def transfer_or_promote(
        self,
        student_id: str,
        class_id: str,
        academic_year_id: str,
        effective_date: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Close the current enrollment and create its successor in one JSON save."""
        start = _date({"date": effective_date}, "date", "Transition date")
        previous_date = (date.fromisoformat(start) - timedelta(days=1)).isoformat()
        current = self.enrollment_for_student_on(student_id, previous_date)
        closure_date = previous_date
        if current is None:
            prior_year_enrollments: list[tuple[str, dict[str, Any]]] = []
            for enrollment in self.list("enrollment"):
                if (
                    not self._same(enrollment.get("student_id"), student_id)
                    or enrollment.get("status") != "active"
                ):
                    continue
                year = self._get("academic_year", str(enrollment.get("academic_year_id", "")))
                if year is None:
                    continue
                _, year_end = _stored_period(year, "Academic year")
                enrollment_start, _ = _stored_period(enrollment, "Enrollment", allow_open_end=True)
                if (
                    date.fromisoformat(enrollment_start)
                    <= date.fromisoformat(year_end)
                    < date.fromisoformat(start)
                ):
                    prior_year_enrollments.append((year_end, enrollment))
            if prior_year_enrollments:
                closure_date, current = max(prior_year_enrollments, key=lambda item: item[0])
        if current is None or current.get("status") != "active":
            raise ValidationError("No active enrollment exists immediately before this date.")
        records = self.list("enrollment")
        current_index = self._find_index("enrollment", records, str(current["enrollment_id"]))
        if current_index is None:
            raise StorageError("The current enrollment disappeared during the transition.")
        closed = dict(current)
        closed["end_date"] = closure_date
        closed["status"] = (
            "transferred"
            if self._same(current.get("academic_year_id"), academic_year_id)
            else "completed"
        )
        successor = self._prepare_enrollment(
            {
                "student_id": student_id,
                "class_id": class_id,
                "academic_year_id": academic_year_id,
                "start_date": start,
                "status": "active",
            },
            generate_id(PREFIXES["enrollment"]),
        )
        updated = [*records[:current_index], closed, *records[current_index + 1 :]]
        self._ensure_unique("enrollment", successor, updated)
        updated.append(successor)
        self._repository.save("enrollment", updated)
        return closed, successor

    def withdraw(self, student_id: str, effective_date: str) -> dict[str, Any]:
        """End an active enrollment on the student's final enrolled date."""
        end = _date({"date": effective_date}, "date", "Withdrawal date")
        current = self.enrollment_for_student_on(student_id, end)
        if current is None or current.get("status") != "active":
            raise ValidationError("No active enrollment exists on this withdrawal date.")
        start, _ = _stored_period(current, "Enrollment", allow_open_end=True)
        _require_order(start, end, "Enrollment")
        records = self.list("enrollment")
        index = self._find_index("enrollment", records, str(current["enrollment_id"]))
        if index is None:
            raise StorageError("The current enrollment disappeared during the withdrawal.")
        withdrawn = dict(current)
        withdrawn["end_date"] = end
        withdrawn["status"] = "withdrawn"
        records[index] = withdrawn
        self._repository.save("enrollment", records)
        return withdrawn

    def enrollment_for_student_on(
        self, student_id: str, enrollment_date: str
    ) -> dict[str, Any] | None:
        target = student_id.strip().casefold()
        date_value = _date({"date": enrollment_date}, "date", "Attendance date")
        day = date.fromisoformat(date_value)
        matches: list[dict[str, Any]] = []
        for enrollment in self.list("enrollment"):
            if not self._same(enrollment.get("student_id"), target):
                continue
            start, end = _stored_period(enrollment, "Enrollment", allow_open_end=True)
            academic_year = self._get("academic_year", str(enrollment["academic_year_id"]))
            if academic_year is None:
                raise StorageError("An enrollment references a missing academic year.")
            _, year_end = _stored_period(academic_year, "Academic year")
            effective_end = min(
                date.fromisoformat(end) if end else date.fromisoformat(year_end),
                date.fromisoformat(year_end),
            )
            if date.fromisoformat(start) <= day <= effective_end:
                matches.append(enrollment)
        if len(matches) > 1:
            raise ValidationError(
                "More than one enrollment covers this date; correct enrollment history before recording attendance."
            )
        return matches[0] if matches else None

    def _prepare(
        self,
        kind: StructureKind,
        values: Mapping[str, object],
        entity_id: str | None = None,
    ) -> dict[str, Any]:
        record_id = entity_id or generate_id(PREFIXES[kind])
        if kind == "class":
            record: dict[str, Any] = {
                "class_id": record_id,
                "name": _text(values, "name", "Class name"),
            }
        elif kind == "subject":
            record = {
                "subject_id": record_id,
                "name": _text(values, "name", "Subject name"),
                "code": _optional_text(values, "code").upper(),
            }
        elif kind == "academic_year":
            start = _date(values, "start_date", "Academic-year start date")
            end = _date(values, "end_date", "Academic-year end date")
            _require_order(start, end, "Academic year")
            record = {
                "academic_year_id": record_id,
                "name": _text(values, "name", "Academic-year name"),
                "start_date": start,
                "end_date": end,
            }
        elif kind == "term":
            academic_year_id = _text(values, "academic_year_id", "Academic year")
            year = self._get("academic_year", academic_year_id)
            if year is None:
                raise ValidationError("Select an existing academic year for this term.")
            year_start, year_end = _stored_period(year, "Academic year")
            start = _date(values, "start_date", "Term start date")
            end = _date(values, "end_date", "Term end date")
            _require_order(start, end, "Term")
            self._ensure_within_period(start, end, year_start, year_end, "Term")
            record = {
                "term_id": record_id,
                "academic_year_id": year["academic_year_id"],
                "name": _text(values, "name", "Term name"),
                "start_date": start,
                "end_date": end,
            }
        else:
            record = self._prepare_enrollment(values, record_id)
        return record

    def _prepare_enrollment(self, values: Mapping[str, object], record_id: str) -> dict[str, Any]:
        student_id = _text(values, "student_id", "Student ID").upper()
        if not self._student_exists(student_id):
            raise ValidationError("Select an existing student for this enrollment.")
        academic_year_id = _text(values, "academic_year_id", "Academic year")
        year = self._get("academic_year", academic_year_id)
        if year is None:
            raise ValidationError("Select an existing academic year for this enrollment.")
        year_start, year_end = _stored_period(year, "Academic year")
        class_id = _text(values, "class_id", "Class")
        classroom = self._get("class", class_id)
        if classroom is None:
            raise ValidationError("Select an existing class for this enrollment.")
        start = _date(values, "start_date", "Enrollment start date")
        end = _date(values, "end_date", "Enrollment end date", optional=True)
        if end:
            _require_order(start, end, "Enrollment")
        self._ensure_within_period(start, end or year_end, year_start, year_end, "Enrollment")
        status = _optional_text(values, "status").casefold() or "active"
        if status not in ENROLLMENT_STATUSES:
            choices = ", ".join(sorted(ENROLLMENT_STATUSES))
            raise ValidationError(f"Enrollment status must be one of: {choices}.")
        if (status == "active") != (not end):
            raise ValidationError(
                "Active enrollment has no end date; ended enrollment requires one."
            )
        return {
            "enrollment_id": record_id,
            "student_id": student_id,
            "academic_year_id": year["academic_year_id"],
            "class_id": classroom["class_id"],
            "start_date": start,
            "end_date": end,
            "status": status,
        }

    def _ensure_unique(
        self,
        kind: StructureKind,
        record: dict[str, Any],
        records: builtins.list[dict[str, Any]],
        ignored_id: str | None = None,
    ) -> None:
        record_id_field = ID_FIELDS[kind]
        for existing in records:
            existing_id = str(existing.get(record_id_field, ""))
            if ignored_id and existing_id.casefold() == ignored_id.casefold():
                continue
            if kind == "class" and self._same(existing.get("name"), record["name"]):
                raise ValidationError("A class with that name already exists.")
            if kind == "subject":
                if self._same(existing.get("name"), record["name"]):
                    raise ValidationError("A subject with that name already exists.")
                if record["code"] and self._same(existing.get("code"), record["code"]):
                    raise ValidationError("A subject with that code already exists.")
            if kind == "academic_year" and self._same(existing.get("name"), record["name"]):
                raise ValidationError("An academic year with that name already exists.")
            if kind == "term":
                if self._same(
                    existing.get("academic_year_id"), record["academic_year_id"]
                ) and self._same(existing.get("name"), record["name"]):
                    raise ValidationError(
                        "A term with that name already exists in this academic year."
                    )
                if self._same(existing.get("academic_year_id"), record["academic_year_id"]):
                    existing_start, existing_end = _stored_period(existing, "Term")
                    if _overlaps(
                        record["start_date"],
                        record["end_date"],
                        existing_start,
                        existing_end,
                    ):
                        raise ValidationError("Term dates cannot overlap within an academic year.")
            if (
                kind == "enrollment"
                and self._same(existing.get("student_id"), record["student_id"])
                and self._same(existing.get("academic_year_id"), record["academic_year_id"])
            ):
                existing_start, existing_end = _stored_period(
                    existing, "Enrollment", allow_open_end=True
                )
                if _overlaps(
                    record["start_date"],
                    record["end_date"],
                    existing_start,
                    existing_end,
                ):
                    raise ValidationError(
                        "A student's enrollments in the same academic year cannot overlap."
                    )
        self._ensure_unique_id(kind, records, record[record_id_field], ignored_id)

    def _ensure_not_referenced(self, kind: StructureKind, record: dict[str, Any]) -> None:
        if kind == "class":
            referenced = any(
                self._same(item.get("class_id"), record["class_id"])
                for item in self.list("enrollment")
            )
        elif kind == "academic_year":
            child_kinds: tuple[StructureKind, ...] = ("term", "enrollment")
            referenced = any(
                self._same(item.get("academic_year_id"), record["academic_year_id"])
                for child_kind in child_kinds
                for item in self.list(child_kind)
            )
            referenced = referenced or (
                self._assignment_repository is not None
                and self._assignment_repository.references(
                    "academic_year_id", str(record["academic_year_id"])
                )
            )
        elif kind == "subject":
            referenced = self._assignment_repository is not None and (
                self._assignment_repository.references("subject_id", str(record["subject_id"]))
            )
        else:
            referenced = False
        if referenced:
            raise ValidationError(
                f"Cannot delete this {self._label(kind).lower()} while records refer to it."
            )

    def _ensure_children_within_year(self, year: dict[str, Any]) -> None:
        for kind in ("term", "enrollment"):
            for child in self.list(kind):
                if not self._same(child.get("academic_year_id"), year["academic_year_id"]):
                    continue
                child_start, child_end = _stored_period(
                    child, self._label(kind), allow_open_end=kind == "enrollment"
                )
                self._ensure_within_period(
                    child_start,
                    child_end or year["end_date"],
                    year["start_date"],
                    year["end_date"],
                    self._label(kind),
                )

    def _ensure_within_period(
        self, start: str, end: str, period_start: str, period_end: str, label: str
    ) -> None:
        if date.fromisoformat(start) < date.fromisoformat(period_start) or date.fromisoformat(
            end
        ) > date.fromisoformat(period_end):
            raise ValidationError(f"{label} dates must be within the selected academic year.")

    def _get(self, kind: StructureKind, entity_id: str) -> dict[str, Any] | None:
        records = self.list(kind)
        index = self._find_index(kind, records, entity_id)
        if index is None:
            return None
        return records[index]

    @staticmethod
    def _same(first: object, second: object) -> bool:
        return str(first or "").strip().casefold() == str(second or "").strip().casefold()

    def _find_index(
        self, kind: StructureKind, records: builtins.list[dict[str, Any]], entity_id: str
    ) -> int | None:
        target = entity_id.strip().casefold()
        for index, record in enumerate(records):
            if str(record.get(ID_FIELDS[kind], "")).strip().casefold() == target:
                return index
        return None

    def _ensure_unique_id(
        self,
        kind: StructureKind,
        records: builtins.list[dict[str, Any]],
        entity_id: str,
        ignored_id: str | None = None,
    ) -> None:
        for record in records:
            current_id = str(record.get(ID_FIELDS[kind], ""))
            if current_id.casefold() == entity_id.casefold() and (
                ignored_id is None or current_id.casefold() != ignored_id.casefold()
            ):
                raise ValidationError(f"That {self._label(kind)} ID already exists.")

    @staticmethod
    def _label(kind: StructureKind) -> str:
        return {
            "class": "Class",
            "subject": "Subject",
            "academic_year": "Academic year",
            "term": "Term",
            "enrollment": "Enrollment",
        }[kind]
