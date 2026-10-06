from decimal import Decimal

from telix.core.errors import ValidationError
from tests.support import ServiceTestCase, valid_teacher


class TeacherServiceTests(ServiceTestCase):
    def test_add_get_update_delete(self):
        self.teachers.add(valid_teacher())
        self.assertEqual(self.teachers.get("TCH-001")["salary"], Decimal("3000.00"))
        self.teachers.update("TCH-001", valid_teacher(salary="3500"))
        self.assertEqual(self.teachers.get("tch-001")["salary"], Decimal("3500.00"))
        self.teachers.delete("TCH-001")
        self.assertEqual(self.teachers.list(), [])

    def test_duplicate_and_immutable_id(self):
        self.teachers.add(valid_teacher())
        with self.assertRaisesRegex(ValidationError, "already exists"):
            self.teachers.add(valid_teacher())
        with self.assertRaisesRegex(ValidationError, "cannot be changed"):
            self.teachers.update("TCH-001", valid_teacher(teacher_id="TCH-002"))

    def test_teacher_must_be_adult(self):
        with self.assertRaisesRegex(ValidationError, "between 18 and 100"):
            self.teachers.add(valid_teacher(date_of_birth="2015-01-01"))
