"""Attendance service persistence, validation, filtering, and summary tests."""

from decimal import Decimal

from telix.core.errors import StorageError, ValidationError
from tests.support import ServiceTestCase, valid_student


class AttendanceServiceTests(ServiceTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.students.add(valid_student())
        self.year = self.academic_structure.add(
            "academic_year",
            {"name": "2026/2027", "start_date": "2026-09-01", "end_date": "2027-06-30"},
        )
        self.classroom = self.academic_structure.add("class", {"name": "Grade 1"})
        self.enrollment = self.academic_structure.add(
            "enrollment",
            {
                "student_id": "STU-001",
                "academic_year_id": self.year["academic_year_id"],
                "class_id": self.classroom["class_id"],
                "start_date": "2026-09-01",
            },
        )

    def _add(self, status: str = "Present", **values: str) -> dict:
        return self.attendance.add(
            {
                "student_id": "STU-001",
                "attendance_date": "2026-10-06",
                "status": status,
                **values,
            }
        )

    def test_create_record_links_student_enrollment_and_persists(self) -> None:
        attendance = self._add()
        self.assertEqual(attendance["class_id"], self.classroom["class_id"])
        self.assertEqual(attendance["enrollment_id"], self.enrollment["enrollment_id"])
        self.assertEqual(self.attendance.get(attendance["attendance_id"]), attendance)

    def test_invalid_date_status_and_unknown_student_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValidationError, "YYYY-MM-DD"):
            self._add(attendance_date="10/06/2026")
        with self.assertRaisesRegex(ValidationError, "status must be one of"):
            self._add("Holiday")
        with self.assertRaisesRegex(ValidationError, "existing student"):
            self.attendance.add(
                {
                    "student_id": "STU-999",
                    "attendance_date": "2026-10-06",
                    "status": "Present",
                }
            )

    def test_attendance_requires_enrollment_on_the_recorded_date(self) -> None:
        with self.assertRaisesRegex(ValidationError, "no class enrollment active"):
            self._add(attendance_date="2026-08-31")
        with self.assertRaisesRegex(ValidationError, "no class enrollment active"):
            self._add(attendance_date="2027-07-01")

    def test_duplicate_student_date_is_rejected(self) -> None:
        self._add()
        with self.assertRaisesRegex(ValidationError, "already been recorded"):
            self._add("Absent")

    def test_update_changes_status_and_prevents_duplicate(self) -> None:
        record = self._add()
        updated = self.attendance.update(
            record["attendance_id"],
            {
                "student_id": "STU-001",
                "attendance_date": "2026-10-06",
                "status": "Late",
            },
        )
        self.assertEqual(updated["attendance_id"], record["attendance_id"])
        self.assertEqual(self.attendance.get(record["attendance_id"])["status"], "Late")

        other = self.students.add(valid_student(student_id="STU-002"))
        self.academic_structure.add(
            "enrollment",
            {
                "student_id": other["student_id"],
                "academic_year_id": self.year["academic_year_id"],
                "class_id": self.classroom["class_id"],
                "start_date": "2026-09-01",
            },
        )
        self.attendance.add(
            {
                "student_id": "STU-002",
                "attendance_date": "2026-10-06",
                "status": "Present",
            }
        )
        with self.assertRaisesRegex(ValidationError, "already been recorded"):
            self.attendance.update(
                record["attendance_id"],
                {
                    "student_id": "STU-002",
                    "attendance_date": "2026-10-06",
                    "status": "Absent",
                },
            )

    def test_delete_and_missing_record(self) -> None:
        record = self._add()
        self.attendance.delete(record["attendance_id"])
        self.assertEqual(self.attendance.list(), [])
        with self.assertRaisesRegex(ValidationError, "not found"):
            self.attendance.delete(record["attendance_id"])

    def test_filters_by_date_student_and_class(self) -> None:
        record = self._add()
        self.assertEqual(len(self.attendance.list(attendance_date="2026-10-06")), 1)
        self.assertEqual(len(self.attendance.list(student_id="stu-001")), 1)
        self.assertEqual(len(self.attendance.list(class_id=self.classroom["class_id"])), 1)
        self.assertEqual(self.attendance.list(class_id="MISSING"), [])
        self.assertEqual(self.attendance.list(attendance_date="2026-10-07"), [])
        with self.assertRaisesRegex(ValidationError, "filter date must use"):
            self.attendance.list(attendance_date="10/06/2026")
        self.assertEqual(record["status"], "Present")

    def test_filters_by_date_range_and_status(self) -> None:
        self._add("Present", attendance_date="2026-10-06")
        self._add("Absent", attendance_date="2026-10-07")
        self._add("Late", attendance_date="2026-10-08")

        self.assertEqual(
            [
                record["status"]
                for record in self.attendance.list(
                    start_date="2026-10-07",
                    end_date="2026-10-08",
                    status="late",
                )
            ],
            ["Late"],
        )
        with self.assertRaisesRegex(ValidationError, "on or before"):
            self.attendance.list(start_date="2026-10-08", end_date="2026-10-07")

    def test_summary_excludes_excused_records_from_percentage(self) -> None:
        self._add("Present", attendance_date="2026-10-06")
        self._add("Late", attendance_date="2026-10-07")
        self._add("Absent", attendance_date="2026-10-08")
        self._add("Excused", attendance_date="2026-10-09")

        summary = self.attendance.summary()

        self.assertEqual(summary["total"], 4)
        self.assertEqual(summary["present"], 1)
        self.assertEqual(summary["late"], 1)
        self.assertEqual(summary["absent"], 1)
        self.assertEqual(summary["excused"], 1)
        self.assertEqual(summary["attendance_percentage"], Decimal("66.67"))

    def test_empty_and_only_excused_summaries_are_zero(self) -> None:
        self.assertEqual(self.attendance.summary([])["attendance_percentage"], Decimal("0.00"))
        self._add("Excused")
        self.assertEqual(self.attendance.summary()["attendance_percentage"], Decimal("0.00"))

    def test_student_removal_cleans_attendance(self) -> None:
        self._add()
        self.attendance.delete_for_student("STU-001")
        self.assertEqual(self.attendance.list(), [])

    def test_corrupt_attendance_records_are_reported(self) -> None:
        self.attendance_store.save(
            [
                {
                    "attendance_id": "ATT-1",
                    "student_id": "STU-001",
                    "class_id": self.classroom["class_id"],
                    "academic_year_id": self.year["academic_year_id"],
                    "enrollment_id": self.enrollment["enrollment_id"],
                    "attendance_date": "2026-10-06",
                    "status": "Holiday",
                }
            ]
        )
        with self.assertRaisesRegex(StorageError, "invalid attendance record"):
            self.attendance.list()
