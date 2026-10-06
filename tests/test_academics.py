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

    def test_new_records_can_link_managed_subject_term_and_year(self):
        subject = self.academic_structure.add("subject", {"name": "Science"})
        year = self.academic_structure.add(
            "academic_year",
            {"name": "2026/2027", "start_date": "2026-09-01", "end_date": "2027-06-30"},
        )
        term = self.academic_structure.add(
            "term",
            {
                "academic_year_id": year["academic_year_id"],
                "name": "Term One",
                "start_date": "2026-09-01",
                "end_date": "2026-12-20",
            },
        )

        record = self.academics.add(
            {
                **valid_score(subject="non-canonical", term="old label", academic_year="old year"),
                "subject_id": subject["subject_id"],
                "term_id": term["term_id"],
                "academic_year_id": year["academic_year_id"],
            },
            self.students.exists,
        )

        self.assertEqual(record["subject"], "Science")
        self.assertEqual(record["term"], "Term One")
        self.assertEqual(record["academic_year"], "2026/2027")
        self.assertEqual(record["subject_id"], subject["subject_id"])
        self.assertEqual(record["term_id"], term["term_id"])
        self.assertEqual(record["academic_year_id"], year["academic_year_id"])
        self.assertEqual(self.academics.get(record["academic_id"]), record)

    def test_managed_references_must_be_complete_and_term_must_match_year(self):
        subject = self.academic_structure.add("subject", {"name": "Science"})
        first_year = self.academic_structure.add(
            "academic_year",
            {"name": "2026/2027", "start_date": "2026-09-01", "end_date": "2027-06-30"},
        )
        other_year = self.academic_structure.add(
            "academic_year",
            {"name": "2027/2028", "start_date": "2027-09-01", "end_date": "2028-06-30"},
        )
        term = self.academic_structure.add(
            "term",
            {
                "academic_year_id": first_year["academic_year_id"],
                "name": "Term One",
                "start_date": "2026-09-01",
                "end_date": "2026-12-20",
            },
        )
        common = {
            **valid_score(),
            "subject_id": subject["subject_id"],
            "term_id": term["term_id"],
            "academic_year_id": other_year["academic_year_id"],
        }
        with self.assertRaisesRegex(ValidationError, "does not belong"):
            self.academics.add(common, self.students.exists)
        with self.assertRaisesRegex(ValidationError, "Choose a managed"):
            self.academics.add(
                {**common, "academic_year_id": ""},
                self.students.exists,
            )

    def test_period_summaries_keep_historical_catalog_labels_after_renames(self):
        subject = self.academic_structure.add("subject", {"name": "Mathematics"})
        year = self.academic_structure.add(
            "academic_year",
            {"name": "2026/2027", "start_date": "2026-09-01", "end_date": "2027-06-30"},
        )
        term = self.academic_structure.add(
            "term",
            {
                "academic_year_id": year["academic_year_id"],
                "name": "Term 1",
                "start_date": "2026-09-01",
                "end_date": "2026-12-20",
            },
        )
        values = {
            **valid_score(score="80"),
            "subject_id": subject["subject_id"],
            "term_id": term["term_id"],
            "academic_year_id": year["academic_year_id"],
        }
        record = self.academics.add(values, self.students.exists)
        self.academics.add(
            valid_score(subject="English", score="70"),
            self.students.exists,
        )
        self.academic_structure.update(
            "subject", subject["subject_id"], {"name": "Mathematical Studies", "code": ""}
        )
        self.academic_structure.update(
            "academic_year",
            year["academic_year_id"],
            {"name": "Renamed year", "start_date": "2026-09-01", "end_date": "2027-06-30"},
        )
        self.academic_structure.update(
            "term",
            term["term_id"],
            {
                "academic_year_id": year["academic_year_id"],
                "name": "Renamed term",
                "start_date": "2026-09-01",
                "end_date": "2026-12-20",
            },
        )

        summary = self.academics.period_summaries("STU-001")
        self.assertEqual(
            (
                summary[0]["academic_year"],
                summary[0]["term"],
                summary[0]["subject_count"],
                summary[0]["average_score"],
            ),
            ("2026/2027", "Term 1", 2, 75),
        )
        updated = self.academics.update(record["academic_id"], values, self.students.exists)
        self.assertEqual(
            (updated["subject"], updated["academic_year"], updated["term"]),
            ("Mathematics", "2026/2027", "Term 1"),
        )
