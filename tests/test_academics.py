from telix.core.errors import ValidationError
from tests.support import ServiceTestCase, valid_score, valid_student


class AcademicServiceTests(ServiceTestCase):
    def setUp(self):
        super().setUp()
        self.students.add(valid_student())

    def add_score(self, **overrides):
        return self.academics.add(valid_score(**overrides), self.students.exists)

    def test_add_requires_existing_student(self):
        with self.assertRaisesRegex(ValidationError, "not found"):
            self.add_score(student_id="NOPE")

    def test_one_score_per_student_subject_term_year(self):
        self.add_score()
        with self.assertRaisesRegex(ValidationError, "already exists"):
            self.add_score(subject="mathematics")
        self.add_score(term="Term 2")  # different term is allowed

    def test_update_can_keep_its_own_key_but_not_collide_with_another(self):
        first = self.add_score()
        second = self.add_score(subject="English")
        self.academics.update(first["academic_id"], valid_score(score="90"), self.students.exists)
        self.assertEqual(self.academics.get(first["academic_id"])["score"], 90)
        with self.assertRaisesRegex(ValidationError, "already exists"):
            self.academics.update(second["academic_id"], valid_score(), self.students.exists)

    def test_update_and_delete_missing_record(self):
        with self.assertRaisesRegex(ValidationError, "not found"):
            self.academics.update("ACA-NONE", valid_score(), self.students.exists)
        with self.assertRaisesRegex(ValidationError, "not found"):
            self.academics.delete("ACA-NONE")

    def test_for_student_and_delete(self):
        record = self.add_score()
        self.assertEqual(len(self.academics.for_student("stu-001")), 1)
        self.academics.delete(record["academic_id"])
        self.assertEqual(self.academics.list(), [])

    def test_score_range(self):
        with self.assertRaisesRegex(ValidationError, "0 to 100"):
            self.add_score(score="101")
