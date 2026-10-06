from telix.core.errors import StorageError, ValidationError
from tests.support import ServiceTestCase, valid_teacher


class TeacherAssignmentTests(ServiceTestCase):
    def setUp(self):
        super().setUp()
        self.teacher = self.teachers.add(valid_teacher())
        self.subject = self.academic_structure.add("subject", {"name": "Mathematics"})
        self.year = self.academic_structure.add(
            "academic_year",
            {"name": "2026/2027", "start_date": "2026-09-01", "end_date": "2027-06-30"},
        )
        self.values = {
            "teacher_id": self.teacher["teacher_id"],
            "subject_id": self.subject["subject_id"],
            "academic_year_id": self.year["academic_year_id"],
        }

    def test_add_assignment_persists_names_and_rejects_duplicates(self):
        assignment = self.teacher_assignments.add(self.values)

        self.assertEqual(assignment["teacher_name"], self.teacher["name"])
        self.assertEqual(assignment["subject_name"], "Mathematics")
        self.assertEqual(assignment["academic_year"], "2026/2027")
        self.assertEqual(self.teacher_assignments.for_teacher("TCH-001"), [assignment])
        with self.assertRaisesRegex(ValidationError, "already assigned"):
            self.teacher_assignments.add(self.values)

    def test_assignment_requires_existing_teacher_subject_and_year(self):
        with self.assertRaisesRegex(ValidationError, "existing teacher"):
            self.teacher_assignments.add({**self.values, "teacher_id": "TCH-MISSING"})
        with self.assertRaisesRegex(ValidationError, "existing subject"):
            self.teacher_assignments.add({**self.values, "subject_id": "SUB-MISSING"})
        with self.assertRaisesRegex(ValidationError, "existing academic year"):
            self.teacher_assignments.add({**self.values, "academic_year_id": "ACY-MISSING"})

    def test_update_delete_and_referenced_record_deletion_rules(self):
        assignment = self.teacher_assignments.add(self.values)
        other_teacher = self.teachers.add(valid_teacher(teacher_id="TCH-002", name="Test Teacher"))

        with self.assertRaisesRegex(ValidationError, "assignments refer"):
            self.teachers.delete(self.teacher["teacher_id"])
        with self.assertRaisesRegex(ValidationError, "records refer"):
            self.academic_structure.delete("subject", self.subject["subject_id"])
        with self.assertRaisesRegex(ValidationError, "records refer"):
            self.academic_structure.delete("academic_year", self.year["academic_year_id"])

        updated = self.teacher_assignments.update(
            assignment["assignment_id"], {**self.values, "teacher_id": other_teacher["teacher_id"]}
        )
        self.assertEqual(updated["teacher_id"], other_teacher["teacher_id"])
        self.teacher_assignments.delete(assignment["assignment_id"])
        self.teachers.delete(self.teacher["teacher_id"])
        self.academic_structure.delete("subject", self.subject["subject_id"])
        self.academic_structure.delete("academic_year", self.year["academic_year_id"])
        self.assertEqual(self.teacher_assignments.list(), [])

    def test_update_and_delete_reject_missing_assignment(self):
        with self.assertRaisesRegex(ValidationError, "not found"):
            self.teacher_assignments.update("TAS-MISSING", self.values)
        with self.assertRaisesRegex(ValidationError, "not found"):
            self.teacher_assignments.delete("TAS-MISSING")

    def test_malformed_assignment_storage_is_reported(self):
        self.teacher_assignment_store.save([{"teacher_id": "TCH-001"}])
        with self.assertRaisesRegex(StorageError, "without an ID"):
            self.teacher_assignments.list()
