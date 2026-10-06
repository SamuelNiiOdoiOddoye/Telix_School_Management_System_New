"""Tests for academic catalogs and effective-dated student enrollment."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from telix.academics.structure_repository import (
    AcademicStructureRepository,
    StructureKind,
)
from telix.academics.structure_service import AcademicStructureService
from telix.core.errors import StorageError, ValidationError
from telix.storage.json_store import JsonStore


class AcademicStructureTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.stores: dict[StructureKind, JsonStore] = {
            kind: JsonStore(self.directory / f"{kind}.json")
            for kind in ("class", "subject", "academic_year", "term", "enrollment")
        }
        repository = AcademicStructureRepository(self.stores)
        self.service = AcademicStructureService(
            repository, lambda student_id: student_id == "STU-001"
        )
        self.classroom = self.service.add("class", {"name": "Grade 1"})
        self.subject = self.service.add("subject", {"name": "Mathematics", "code": "math"})
        self.year = self.service.add(
            "academic_year",
            {"name": "2026/2027", "start_date": "2026-09-01", "end_date": "2027-06-30"},
        )

    def test_add_and_list_academic_catalog_records(self) -> None:
        term = self.service.add(
            "term",
            {
                "academic_year_id": self.year["academic_year_id"],
                "name": "Term 1",
                "start_date": "2026-09-01",
                "end_date": "2026-12-20",
            },
        )

        self.assertTrue(self.classroom["class_id"].startswith("CLS-"))
        self.assertTrue(self.subject["subject_id"].startswith("SUB-"))
        self.assertTrue(self.year["academic_year_id"].startswith("ACY-"))
        self.assertEqual(term["academic_year_id"], self.year["academic_year_id"])
        self.assertEqual(self.service.list("term"), [term])

    def test_catalog_name_and_subject_code_are_unique_case_insensitively(self) -> None:
        with self.assertRaisesRegex(ValidationError, "class with that name"):
            self.service.add("class", {"name": "grade 1"})
        with self.assertRaisesRegex(ValidationError, "subject with that code"):
            self.service.add("subject", {"name": "Numeracy", "code": "MATH"})

    def test_term_must_fit_academic_year_and_not_overlap(self) -> None:
        self.service.add(
            "term",
            {
                "academic_year_id": self.year["academic_year_id"],
                "name": "Term 1",
                "start_date": "2026-09-01",
                "end_date": "2026-12-20",
            },
        )
        with self.assertRaisesRegex(ValidationError, "within the selected academic year"):
            self.service.add(
                "term",
                {
                    "academic_year_id": self.year["academic_year_id"],
                    "name": "Term 2",
                    "start_date": "2027-06-20",
                    "end_date": "2027-07-15",
                },
            )
        with self.assertRaisesRegex(ValidationError, "cannot overlap"):
            self.service.add(
                "term",
                {
                    "academic_year_id": self.year["academic_year_id"],
                    "name": "Term 1b",
                    "start_date": "2026-12-20",
                    "end_date": "2027-02-01",
                },
            )

    def test_rejects_invalid_academic_year_dates(self) -> None:
        with self.assertRaisesRegex(ValidationError, "end date must be on or after"):
            self.service.add(
                "academic_year",
                {"name": "Invalid", "start_date": "2027-01-01", "end_date": "2026-12-31"},
            )
        with self.assertRaisesRegex(ValidationError, "YYYY-MM-DD"):
            self.service.add(
                "academic_year",
                {"name": "Invalid", "start_date": "1/1/2026", "end_date": "2027-06-30"},
            )

    def test_term_requires_an_existing_academic_year(self) -> None:
        with self.assertRaisesRegex(ValidationError, "existing academic year"):
            self.service.add(
                "term",
                {
                    "academic_year_id": "MISSING",
                    "name": "Term 1",
                    "start_date": "2026-09-01",
                    "end_date": "2026-12-20",
                },
            )

    def test_updating_academic_year_cannot_exclude_existing_terms(self) -> None:
        self.service.add(
            "term",
            {
                "academic_year_id": self.year["academic_year_id"],
                "name": "Term 1",
                "start_date": "2026-09-01",
                "end_date": "2026-12-20",
            },
        )
        with self.assertRaisesRegex(ValidationError, "Term dates must be within"):
            self.service.update(
                "academic_year",
                self.year["academic_year_id"],
                {
                    "name": "2026/2027",
                    "start_date": "2026-10-01",
                    "end_date": "2027-06-30",
                },
            )

    def test_enrollment_requires_existing_student_year_and_class(self) -> None:
        values = {
            "student_id": "STU-001",
            "academic_year_id": self.year["academic_year_id"],
            "class_id": self.classroom["class_id"],
            "start_date": "2026-09-01",
        }
        enrollment = self.service.add("enrollment", values)
        self.assertEqual(enrollment["status"], "active")
        self.assertEqual(enrollment["end_date"], "")

        with self.assertRaisesRegex(ValidationError, "existing student"):
            self.service.add("enrollment", {**values, "student_id": "STU-999"})
        with self.assertRaisesRegex(ValidationError, "existing class"):
            self.service.add("enrollment", {**values, "class_id": "MISSING"})

    def test_enrollment_dates_must_fit_the_academic_year(self) -> None:
        with self.assertRaisesRegex(ValidationError, "within the selected academic year"):
            self.service.add(
                "enrollment",
                {
                    "student_id": "STU-001",
                    "academic_year_id": self.year["academic_year_id"],
                    "class_id": self.classroom["class_id"],
                    "start_date": "2026-08-31",
                },
            )

    def test_non_overlapping_enrollments_preserve_class_history(self) -> None:
        first = self.service.add(
            "enrollment",
            {
                "student_id": "STU-001",
                "academic_year_id": self.year["academic_year_id"],
                "class_id": self.classroom["class_id"],
                "start_date": "2026-09-01",
                "end_date": "2027-01-15",
                "status": "transferred",
            },
        )
        next_class = self.service.add("class", {"name": "Grade 2"})
        second = self.service.add(
            "enrollment",
            {
                "student_id": "STU-001",
                "academic_year_id": self.year["academic_year_id"],
                "class_id": next_class["class_id"],
                "start_date": "2027-01-16",
            },
        )

        self.assertEqual(len(self.service.list("enrollment")), 2)
        self.assertEqual(first["class_id"], self.classroom["class_id"])
        self.assertEqual(second["class_id"], next_class["class_id"])

    def test_transfer_closes_current_enrollment_and_creates_successor(self) -> None:
        current = self.service.add(
            "enrollment",
            {
                "student_id": "STU-001",
                "academic_year_id": self.year["academic_year_id"],
                "class_id": self.classroom["class_id"],
                "start_date": "2026-09-01",
            },
        )
        next_class = self.service.add("class", {"name": "Grade 2"})

        closed, successor = self.service.transfer_or_promote(
            "STU-001",
            next_class["class_id"],
            self.year["academic_year_id"],
            "2027-01-15",
        )

        self.assertEqual(closed["enrollment_id"], current["enrollment_id"])
        self.assertEqual(closed["end_date"], "2027-01-14")
        self.assertEqual(closed["status"], "transferred")
        self.assertEqual(successor["class_id"], next_class["class_id"])
        self.assertEqual(
            self.service.enrollment_for_student_on("STU-001", "2027-01-15")["enrollment_id"],
            successor["enrollment_id"],
        )

    def test_promotion_into_next_year_completes_prior_enrollment(self) -> None:
        current = self.service.add(
            "enrollment",
            {
                "student_id": "STU-001",
                "academic_year_id": self.year["academic_year_id"],
                "class_id": self.classroom["class_id"],
                "start_date": "2026-09-01",
            },
        )
        next_year = self.service.add(
            "academic_year",
            {"name": "2027/2028", "start_date": "2027-09-01", "end_date": "2028-06-30"},
        )
        next_class = self.service.add("class", {"name": "Grade 2"})

        closed, successor = self.service.transfer_or_promote(
            "STU-001", next_class["class_id"], next_year["academic_year_id"], "2027-09-01"
        )

        self.assertEqual(closed["enrollment_id"], current["enrollment_id"])
        self.assertEqual(closed["end_date"], "2027-06-30")
        self.assertEqual(closed["status"], "completed")
        self.assertEqual(successor["start_date"], "2027-09-01")

    def test_withdrawal_ends_active_enrollment_on_given_day(self) -> None:
        self.service.add(
            "enrollment",
            {
                "student_id": "STU-001",
                "academic_year_id": self.year["academic_year_id"],
                "class_id": self.classroom["class_id"],
                "start_date": "2026-09-01",
            },
        )

        withdrawn = self.service.withdraw("STU-001", "2027-02-01")

        self.assertEqual(withdrawn["end_date"], "2027-02-01")
        self.assertEqual(withdrawn["status"], "withdrawn")

    def test_overlapping_enrollments_are_rejected(self) -> None:
        values = {
            "student_id": "STU-001",
            "academic_year_id": self.year["academic_year_id"],
            "class_id": self.classroom["class_id"],
            "start_date": "2026-09-01",
        }
        self.service.add("enrollment", values)
        with self.assertRaisesRegex(ValidationError, "cannot overlap"):
            self.service.add("enrollment", {**values, "start_date": "2027-01-01"})

    def test_enrollment_status_and_end_date_must_agree(self) -> None:
        values = {
            "student_id": "STU-001",
            "academic_year_id": self.year["academic_year_id"],
            "class_id": self.classroom["class_id"],
            "start_date": "2026-09-01",
            "status": "withdrawn",
        }
        with self.assertRaisesRegex(ValidationError, "requires one"):
            self.service.add("enrollment", values)

    def test_referenced_class_and_year_cannot_be_deleted(self) -> None:
        self.service.add(
            "enrollment",
            {
                "student_id": "STU-001",
                "academic_year_id": self.year["academic_year_id"],
                "class_id": self.classroom["class_id"],
                "start_date": "2026-09-01",
            },
        )
        with self.assertRaisesRegex(ValidationError, "while records refer"):
            self.service.delete("class", self.classroom["class_id"])
        with self.assertRaisesRegex(ValidationError, "while records refer"):
            self.service.delete("academic_year", self.year["academic_year_id"])

    def test_update_preserves_identifier_and_reports_missing_records(self) -> None:
        updated = self.service.update("class", self.classroom["class_id"], {"name": "Grade One"})
        self.assertEqual(updated["class_id"], self.classroom["class_id"])
        self.assertEqual(updated["name"], "Grade One")
        with self.assertRaisesRegex(ValidationError, "Class not found"):
            self.service.update("class", "MISSING", {"name": "Grade 3"})

    def test_non_object_json_records_are_reported_not_silently_dropped(self) -> None:
        self.stores["class"].file_path.write_text("[null]", encoding="utf-8")
        with self.assertRaisesRegex(StorageError, "only JSON object records"):
            self.service.list("class")

    def test_duplicate_catalog_ids_in_json_are_reported(self) -> None:
        self.stores["class"].file_path.write_text(
            '[{"class_id":"CLS-1","name":"Grade 1"},{"class_id":"cls-1","name":"Grade 2"}]',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(StorageError, "duplicate record IDs"):
            self.service.list("class")


if __name__ == "__main__":
    unittest.main()
