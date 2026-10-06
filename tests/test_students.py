from decimal import Decimal

from telix.core.errors import ValidationError
from tests.support import ServiceTestCase, valid_student


class StudentServiceTests(ServiceTestCase):
    def test_add_uppercases_id_and_persists(self):
        self.students.add(valid_student())
        stored = self.students.get("STU-001")
        self.assertEqual(stored["name"], "Ama Mensah")
        self.assertEqual(stored["fees"], Decimal("500.00"))

    def test_duplicate_id_rejected_case_insensitively(self):
        self.students.add(valid_student())
        with self.assertRaisesRegex(ValidationError, "already exists"):
            self.students.add(valid_student(student_id="STU-001"))

    def test_empty_and_invalid_fields_rejected(self):
        with self.assertRaisesRegex(ValidationError, "Please complete"):
            self.students.add(valid_student(name=""))
        with self.assertRaisesRegex(ValidationError, "phone"):
            self.students.add(valid_student(phone="6256"))

    def test_update_changes_record_but_not_id(self):
        self.students.add(valid_student())
        self.students.update("STU-001", valid_student(name="Ama K. Mensah"))
        self.assertEqual(self.students.get("stu-001")["name"], "Ama K. Mensah")
        with self.assertRaisesRegex(ValidationError, "cannot be changed"):
            self.students.update("STU-001", valid_student(student_id="STU-999"))

    def test_update_missing_record(self):
        with self.assertRaisesRegex(ValidationError, "not found"):
            self.students.update("STU-001", valid_student())

    def test_delete_really_removes_the_record(self):
        self.students.add(valid_student())
        self.students.delete("STU-001")
        self.assertIsNone(self.students.get("STU-001"))
        self.assertEqual(self.student_store.load(), [])
        with self.assertRaisesRegex(ValidationError, "not found"):
            self.students.delete("STU-001")

    def test_classes_and_filter(self):
        self.students.add(valid_student())
        self.students.add(valid_student(student_id="STU-002", class_name="6"))
        self.assertEqual(self.students.classes(), ["5", "6"])
        self.assertEqual([s["student_id"] for s in self.students.by_class("6")], ["STU-002"])
        self.assertTrue(self.students.exists("stu-002"))
        self.assertFalse(self.students.exists("nope"))

    def test_student_status_defaults_validates_persists_and_filters(self):
        self.students.add(valid_student())
        inactive = self.students.add(valid_student(student_id="STU-002", status="inactive"))
        active_again = self.students.update(
            inactive["student_id"],
            valid_student(student_id=inactive["student_id"], status="Active"),
        )
        self.assertEqual(active_again["status"], "Active")
        withdrawn = self.students.update(
            inactive["student_id"],
            valid_student(student_id=inactive["student_id"], status="Withdrawn"),
        )

        self.assertEqual(self.students.get("STU-001")["status"], "Active")
        self.assertEqual(withdrawn["status"], "Withdrawn")
        self.assertEqual(
            [student["student_id"] for student in self.students.by_status("inactive")],
            [],
        )
        self.assertEqual(
            [student["student_id"] for student in self.students.by_status("withdrawn")],
            ["STU-002"],
        )
        with self.assertRaisesRegex(ValidationError, "status must be one of"):
            self.students.add(valid_student(student_id="STU-003", status="Graduated"))

    def test_withdrawn_student_must_be_reactivated_explicitly_before_other_status(self):
        self.students.add(valid_student(status="Withdrawn"))
        with self.assertRaisesRegex(ValidationError, "Cannot change student status"):
            self.students.update("STU-001", valid_student(status="Inactive"))
        reactivated = self.students.update("STU-001", valid_student(status="Active"))
        self.assertEqual(reactivated["status"], "Active")

    def test_legacy_file_is_read_and_migrated_on_next_save(self):
        self.student_store.save(
            [{"ID": "OLD1", "Name": "Legacy", "DOB": "2015-01-01", "Class": "5", "Fees": 10}]
        )
        self.assertEqual(self.students.get("old1")["name"], "Legacy")
        self.students.add(valid_student())
        self.assertIn("student_id", self.student_store.load()[0])
