"""Assessment capture and configurable grading calculations."""

from __future__ import annotations

import builtins
from decimal import Decimal
from typing import Any, Callable, Mapping, Sequence

from telix.academics.assessment_repository import AssessmentRepository
from telix.academics.structure_service import AcademicStructureService
from telix.core.errors import ValidationError
from telix.core.identifiers import generate_id
from telix.core.numbers import parse_amount
from telix.core.text import clean_text

StudentExists = Callable[[str], bool]


class AssessmentService:
    def __init__(
        self,
        repository: AssessmentRepository | None = None,
        structure: AcademicStructureService | None = None,
        student_exists: StudentExists | None = None,
    ) -> None:
        self._repository = repository or AssessmentRepository()
        self._structure = structure
        self._student_exists = student_exists or (lambda _student_id: False)

    def list(self) -> builtins.list[dict[str, Any]]:
        return self._repository.list("assessment")

    def profiles(self) -> builtins.list[dict[str, Any]]:
        return self._repository.list("profile")

    def configure(
        self,
        academic_year_id: str,
        term_id: str,
        method: str,
        components: Sequence[Mapping[str, object]],
        grade_bands: Sequence[Mapping[str, object]],
    ) -> dict[str, Any]:
        if self._structure is None:
            raise ValidationError("Academic catalogs are unavailable; refresh and try again.")
        year = self._structure.get("academic_year", academic_year_id)
        if year is None:
            raise ValidationError("Select an existing academic year.")
        term = self._structure.get("term", term_id) if term_id.strip() else None
        if term_id.strip() and term is None:
            raise ValidationError("Select an existing term.")
        if term and term["academic_year_id"].casefold() != year["academic_year_id"].casefold():
            raise ValidationError("The selected term does not belong to the selected year.")
        normalized_method = method.strip().casefold()
        if normalized_method not in {"weighted", "unweighted"}:
            raise ValidationError("Grading method must be weighted or unweighted.")
        prepared_components = self._prepare_components(components)
        prepared_bands = self._prepare_bands(grade_bands)
        profile = {
            "profile_id": generate_id("GRD"),
            "academic_year_id": year["academic_year_id"],
            "term_id": term["term_id"] if term else "",
            "method": normalized_method,
            "components": prepared_components,
            "grade_bands": prepared_bands,
        }
        records = self.profiles()
        match_index = next(
            (
                index
                for index, existing in enumerate(records)
                if self._same(existing.get("academic_year_id"), profile["academic_year_id"])
                and self._same(existing.get("term_id", ""), profile["term_id"])
            ),
            None,
        )
        if match_index is None:
            records.append(profile)
        else:
            current_profile = records[match_index]
            previous_names = {
                str(item.get("name", "")).casefold()
                for item in current_profile.get("components", [])
                if isinstance(item, dict)
            }
            next_names = {str(item["name"]).casefold() for item in prepared_components}
            if previous_names != next_names and any(
                self._same(item.get("academic_year_id"), profile["academic_year_id"])
                and (not profile["term_id"] or self._same(item.get("term_id"), profile["term_id"]))
                for item in self.list()
            ):
                raise ValidationError(
                    "Cannot change configured component names while scores exist; "
                    "remove or update those scores first."
                )
            profile["profile_id"] = records[match_index]["profile_id"]
            records[match_index] = profile
        self._repository.save("profile", records)
        return profile

    def add(self, values: Mapping[str, object]) -> dict[str, Any]:
        record = self._prepare_assessment(values)
        records = self.list()
        if any(self._same_assessment_key(existing, record) for existing in records):
            raise ValidationError("That student already has a score for this component.")
        records.append(record)
        self._repository.save("assessment", records)
        return record

    def update(self, assessment_id: str, values: Mapping[str, object]) -> dict[str, Any]:
        records = self.list()
        index = next(
            (
                position
                for position, record in enumerate(records)
                if self._same(record.get("assessment_id"), assessment_id)
            ),
            None,
        )
        if index is None:
            raise ValidationError("Assessment not found. Select a record from the table first.")
        updated = self._prepare_assessment(values, assessment_id)
        if any(
            position != index and self._same_assessment_key(existing, updated)
            for position, existing in enumerate(records)
        ):
            raise ValidationError("That student already has a score for this component.")
        records[index] = updated
        self._repository.save("assessment", records)
        return updated

    def delete(self, assessment_id: str) -> dict[str, Any]:
        records = self.list()
        index = next(
            (
                position
                for position, record in enumerate(records)
                if self._same(record.get("assessment_id"), assessment_id)
            ),
            None,
        )
        if index is None:
            raise ValidationError("Assessment not found. Select a record from the table first.")
        deleted = records.pop(index)
        self._repository.save("assessment", records)
        return deleted

    def delete_for_student(self, student_id: str) -> int:
        target = student_id.strip().casefold()
        records = self.list()
        remaining = [
            record for record in records if not self._same(record.get("student_id"), target)
        ]
        deleted_count = len(records) - len(remaining)
        if deleted_count:
            self._repository.save("assessment", remaining)
        return deleted_count

    def grade(
        self, student_id: str, subject_id: str, academic_year_id: str, term_id: str
    ) -> dict[str, Any]:
        profile = self._profile_for(academic_year_id, term_id)
        if profile is None:
            raise ValidationError("Configure grading components and grade bands first.")
        scores = [
            record
            for record in self.list()
            if self._same(record.get("student_id"), student_id)
            and self._same(record.get("subject_id"), subject_id)
            and self._same(record.get("academic_year_id"), academic_year_id)
            and self._same(record.get("term_id"), term_id)
        ]
        by_component = {str(record["component"]).casefold(): record for record in scores}
        components = profile["components"]
        missing = [
            str(component["name"])
            for component in components
            if str(component["name"]).casefold() not in by_component
        ]
        if missing:
            raise ValidationError(f"Missing assessment scores for: {', '.join(missing)}.")
        if len(by_component) != len(components):
            raise ValidationError("Assessment scores do not match the configured components.")
        values = [
            parse_amount(by_component[str(component["name"]).casefold()]["score"])
            for component in components
        ]
        if any(value is None for value in values):
            raise ValidationError("Stored assessment scores are invalid.")
        method = profile["method"]
        if method == "weighted":
            total = sum(
                (
                    value * Decimal(str(component["weight"])) / Decimal("100")
                    for value, component in zip(values, components, strict=True)
                    if value is not None
                ),
                Decimal("0"),
            )
        else:
            total = sum((value for value in values if value is not None), Decimal("0")) / len(
                values
            )
        total = total.quantize(Decimal("0.01"))
        matching_bands = [
            band for band in profile["grade_bands"] if total >= Decimal(str(band["minimum"]))
        ]
        band = max(matching_bands, key=lambda item: Decimal(str(item["minimum"])))
        return {
            "student_id": student_id,
            "subject_id": subject_id,
            "academic_year_id": academic_year_id,
            "term_id": term_id,
            "score": total,
            "grade": band["grade"],
            "remark": band["remark"],
            "method": method,
        }

    def _prepare_assessment(
        self, values: Mapping[str, object], assessment_id: str | None = None
    ) -> dict[str, Any]:
        student_id = clean_text(values.get("student_id")).upper()
        subject_id = clean_text(values.get("subject_id"))
        academic_year_id = clean_text(values.get("academic_year_id"))
        term_id = clean_text(values.get("term_id"))
        component = clean_text(values.get("component"))
        if not all((student_id, subject_id, academic_year_id, term_id, component)):
            raise ValidationError(
                "Student, subject, academic year, term, and component are required."
            )
        if not self._student_exists(student_id):
            raise ValidationError("Select an existing student.")
        if self._structure is None:
            raise ValidationError("Academic catalogs are unavailable; refresh and try again.")
        subject = self._structure.get("subject", subject_id)
        year = self._structure.get("academic_year", academic_year_id)
        term = self._structure.get("term", term_id)
        if subject is None or year is None or term is None:
            raise ValidationError("Select existing subject, academic year, and term records.")
        if term["academic_year_id"].casefold() != year["academic_year_id"].casefold():
            raise ValidationError("The selected term does not belong to the selected year.")
        profile = self._profile_for(year["academic_year_id"], term["term_id"])
        if profile is None:
            raise ValidationError("Configure grading components and grade bands first.")
        configured = {str(item["name"]).casefold(): item["name"] for item in profile["components"]}
        if component.casefold() not in configured:
            raise ValidationError("Choose a component configured for this year and term.")
        score = parse_amount(values.get("score"))
        if score is None or score < 0 or score > 100:
            raise ValidationError("Assessment score must be between 0 and 100.")
        return {
            "assessment_id": assessment_id or generate_id("ASM"),
            "student_id": student_id,
            "subject_id": subject["subject_id"],
            "subject": subject["name"],
            "academic_year_id": year["academic_year_id"],
            "academic_year": year["name"],
            "term_id": term["term_id"],
            "term": term["name"],
            "component": configured[component.casefold()],
            "score": score.quantize(Decimal("0.01")),
        }

    def _profile_for(self, academic_year_id: str, term_id: str) -> dict[str, Any] | None:
        profiles = self.profiles()
        exact = next(
            (
                profile
                for profile in profiles
                if self._same(profile.get("academic_year_id"), academic_year_id)
                and self._same(profile.get("term_id", ""), term_id)
            ),
            None,
        )
        if exact is not None:
            return exact
        return next(
            (
                profile
                for profile in profiles
                if self._same(profile.get("academic_year_id"), academic_year_id)
                and not clean_text(profile.get("term_id"))
            ),
            None,
        )

    @staticmethod
    def _prepare_components(
        components: Sequence[Mapping[str, object]],
    ) -> builtins.list[dict[str, Any]]:
        if not components:
            raise ValidationError("Configure at least one assessment component.")
        prepared: builtins.list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in components:
            name = clean_text(item.get("name"))
            weight = parse_amount(item.get("weight"))
            if not name or weight is None or weight <= 0:
                raise ValidationError("Each component needs a name and positive weight.")
            if name.casefold() in seen:
                raise ValidationError("Assessment component names must be unique.")
            seen.add(name.casefold())
            prepared.append({"name": name, "weight": weight.quantize(Decimal("0.01"))})
        total = sum((item["weight"] for item in prepared), Decimal("0"))
        if total != Decimal("100.00"):
            raise ValidationError("Assessment component weights must total 100.")
        return prepared

    @staticmethod
    def _prepare_bands(
        bands: Sequence[Mapping[str, object]],
    ) -> builtins.list[dict[str, Any]]:
        if not bands:
            raise ValidationError("Configure at least one grade band.")
        prepared: builtins.list[dict[str, Any]] = []
        seen: set[Decimal] = set()
        for item in bands:
            minimum = parse_amount(item.get("minimum"))
            grade = clean_text(item.get("grade"))
            remark = clean_text(item.get("remark"))
            if minimum is None or minimum < 0 or minimum > 100 or not grade:
                raise ValidationError("Each grade band needs a grade and minimum from 0 to 100.")
            if minimum in seen:
                raise ValidationError("Grade-band minimum scores must be unique.")
            seen.add(minimum)
            prepared.append(
                {
                    "minimum": minimum.quantize(Decimal("0.01")),
                    "grade": grade,
                    "remark": remark,
                }
            )
        if Decimal("0") not in seen:
            raise ValidationError("Grade bands must include a minimum score of 0.")
        return sorted(prepared, key=lambda item: item["minimum"])

    @classmethod
    def _same_assessment_key(cls, first: Mapping[str, Any], second: Mapping[str, Any]) -> bool:
        return all(
            cls._same(first.get(field), second.get(field))
            for field in (
                "student_id",
                "subject_id",
                "academic_year_id",
                "term_id",
                "component",
            )
        )

    @staticmethod
    def _same(first: object, second: object) -> bool:
        return clean_text(first).casefold() == clean_text(second).casefold()
