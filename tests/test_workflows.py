from decimal import Decimal

from telix.finance.summary import calculate_financial_summary
from tests.support import ServiceTestCase, valid_score, valid_student, valid_teacher


class FinanceSummaryTests(ServiceTestCase):
    def test_profit_or_loss(self):
        summary = calculate_financial_summary(
            [{"fees": 1000}, {"fees": "250.5"}, {"fees": "bad"}],
            [{"salary": 600}, {"salary": None}],
        )
        self.assertEqual(summary["fee_income"], Decimal("1250.50"))
        self.assertEqual(summary["salary_expense"], Decimal("600.00"))
        self.assertEqual(summary["profit_or_loss"], Decimal("650.50"))

    def test_empty(self):
        self.assertEqual(
            calculate_financial_summary([], [])["profit_or_loss"],
            Decimal("0.00"),
        )


class StudentRemovalTests(ServiceTestCase):
    def test_removing_a_student_removes_only_their_scores(self):
        self.students.add(valid_student())
        self.students.add(valid_student(student_id="STU-002"))
        self.academics.add(valid_score(), self.students.exists)
        self.academics.add(valid_score(student_id="STU-002"), self.students.exists)

        self.removal.remove("stu-001")

        self.assertIsNone(self.students.get("STU-001"))
        self.assertEqual([r["student_id"] for r in self.academics.list()], ["STU-002"])
        self.assertEqual([s["student_id"] for s in self.students.list()], ["STU-002"])

    def test_removing_a_student_also_removes_enrollments(self):
        self.students.add(valid_student())
        year = self.academic_structure.add(
            "academic_year",
            {"name": "2026/2027", "start_date": "2026-09-01", "end_date": "2027-06-30"},
        )
        classroom = self.academic_structure.add("class", {"name": "Grade 1"})
        self.academic_structure.add(
            "enrollment",
            {
                "student_id": "STU-001",
                "academic_year_id": year["academic_year_id"],
                "class_id": classroom["class_id"],
                "start_date": "2026-09-01",
            },
        )

        self.removal.remove("STU-001")

        self.assertEqual(self.academic_structure.list("enrollment"), [])

    def test_teachers_are_unaffected(self):
        self.teachers.add(valid_teacher())
        self.students.add(valid_student())
        self.removal.remove("STU-001")
        self.assertEqual(len(self.teachers.list()), 1)
