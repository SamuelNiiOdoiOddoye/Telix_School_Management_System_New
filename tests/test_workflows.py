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

    def test_teachers_are_unaffected(self):
        self.teachers.add(valid_teacher())
        self.students.add(valid_student())
        self.removal.remove("STU-001")
        self.assertEqual(len(self.teachers.list()), 1)
