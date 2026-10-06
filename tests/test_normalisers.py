import unittest

from telix.academics.normaliser import normalise_academic_record
from telix.students.normaliser import normalise_student
from telix.teachers.normaliser import normalise_teacher


class NormaliserTests(unittest.TestCase):
    def test_legacy_student_keys_are_mapped(self):
        student = normalise_student(
            {
                "ID": "a1",
                "Name": "Ama",
                "DOB": "2015-01-01",
                "Class": "5",
                "Fees": 100,
                "Gender": "Female",
                "Address": "Accra",
                "Contact": "0241234567",
                "Email Address": "a@b.co",
                "MedicalInfo": "None",
                "Emergency Contact": "0207654321",
            }
        )
        self.assertEqual(student["student_id"], "a1")
        self.assertEqual(student["phone"], "0241234567")
        self.assertEqual(student["parent_phone"], "0207654321")
        self.assertEqual(student["parent_name"], "Not provided")

    def test_current_student_keys_win_over_legacy(self):
        self.assertEqual(normalise_student({"student_id": "new", "ID": "old"})["student_id"], "new")

    def test_legacy_teacher_keys_are_mapped(self):
        teacher = normalise_teacher({"TID": "t1", "Teacher Name": "Kwame", "Teacher Salary": 10})
        self.assertEqual(
            (teacher["teacher_id"], teacher["name"], teacher["salary"]), ("t1", "Kwame", 10)
        )

    def test_academic_defaults(self):
        record = normalise_academic_record({"ID": "x", "Student ID": "s"})
        self.assertEqual(
            (record["academic_id"], record["student_id"], record["score"]), ("x", "s", 0)
        )
