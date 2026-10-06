from decimal import Decimal

from telix.core.errors import ValidationError
from tests.support import ServiceTestCase, valid_student


class AssessmentServiceTests(ServiceTestCase):
    def setUp(self):
        super().setUp()
        self.students.add(valid_student())
        self.subject = self.academic_structure.add("subject", {"name": "Mathematics"})
        self.year = self.academic_structure.add(
            "academic_year",
            {"name": "2026/2027", "start_date": "2026-09-01", "end_date": "2027-06-30"},
        )
        self.term = self.academic_structure.add(
            "term",
            {
                "academic_year_id": self.year["academic_year_id"],
                "name": "Term 1",
                "start_date": "2026-09-01",
                "end_date": "2026-12-20",
            },
        )
        self.common = {
            "student_id": "STU-001",
            "subject_id": self.subject["subject_id"],
            "academic_year_id": self.year["academic_year_id"],
            "term_id": self.term["term_id"],
        }
        self.components = [
            {"name": "Coursework", "weight": "40"},
            {"name": "Exam", "weight": "60"},
        ]
        self.bands = [
            {"minimum": "0", "grade": "F", "remark": "Needs improvement"},
            {"minimum": "50", "grade": "C", "remark": "Satisfactory"},
            {"minimum": "80", "grade": "A", "remark": "Excellent"},
        ]

    def configure(self, method="weighted", term_id=None):
        return self.assessments.configure(
            self.year["academic_year_id"],
            term_id or self.term["term_id"],
            method,
            self.components,
            self.bands,
        )

    def add_score(self, component, score):
        return self.assessments.add({**self.common, "component": component, "score": score})

    def test_weighted_grade_uses_component_weights_and_configured_band(self):
        self.configure()
        self.add_score("Coursework", "90")
        self.add_score("Exam", "70")

        grade = self.assessments.grade(
            self.common["student_id"],
            self.common["subject_id"],
            self.common["academic_year_id"],
            self.common["term_id"],
        )

        self.assertEqual(grade["score"], Decimal("78.00"))
        self.assertEqual(grade["grade"], "C")
        self.assertEqual(grade["method"], "weighted")

    def test_unweighted_grade_averages_components_and_year_profile_is_fallback(self):
        self.configure(method="unweighted", term_id="")
        self.add_score("Coursework", "90")
        self.add_score("Exam", "70")

        grade = self.assessments.grade(
            self.common["student_id"],
            self.common["subject_id"],
            self.common["academic_year_id"],
            self.common["term_id"],
        )

        self.assertEqual(grade["score"], Decimal("80.00"))
        self.assertEqual(grade["grade"], "A")

    def test_grade_requires_all_configured_components(self):
        self.configure()
        self.add_score("Exam", "70")
        with self.assertRaisesRegex(ValidationError, "Missing assessment scores"):
            self.assessments.grade(
                self.common["student_id"],
                self.common["subject_id"],
                self.common["academic_year_id"],
                self.common["term_id"],
            )

    def test_component_weights_must_total_one_hundred(self):
        with self.assertRaisesRegex(ValidationError, "total 100"):
            self.assessments.configure(
                self.year["academic_year_id"],
                self.term["term_id"],
                "weighted",
                [{"name": "Coursework", "weight": "30"}],
                self.bands,
            )

    def test_assessment_component_is_unique_for_student_subject_and_term(self):
        self.configure()
        self.add_score("Coursework", "90")
        with self.assertRaisesRegex(ValidationError, "already has a score"):
            self.add_score("coursework", "75")

    def test_component_names_cannot_be_changed_while_scores_use_the_profile(self):
        self.configure()
        self.add_score("Coursework", "90")
        with self.assertRaisesRegex(ValidationError, "Cannot change configured component names"):
            self.assessments.configure(
                self.year["academic_year_id"],
                self.term["term_id"],
                "weighted",
                [{"name": "Project", "weight": "40"}, {"name": "Exam", "weight": "60"}],
                self.bands,
            )

    def test_term_profile_must_belong_to_selected_year(self):
        other_year = self.academic_structure.add(
            "academic_year",
            {"name": "2027/2028", "start_date": "2027-09-01", "end_date": "2028-06-30"},
        )
        with self.assertRaisesRegex(ValidationError, "does not belong"):
            self.assessments.configure(
                other_year["academic_year_id"],
                self.term["term_id"],
                "weighted",
                self.components,
                self.bands,
            )
