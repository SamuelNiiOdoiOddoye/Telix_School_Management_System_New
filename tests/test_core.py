import unittest
from datetime import date
from decimal import Decimal

from telix.academics.defaults import default_academic_year
from telix.core.errors import ValidationError
from telix.core.formatting import format_currency
from telix.core.numbers import as_amount
from telix.core.search import filter_by_class, find_by_id, find_index_by_id
from telix.core.text import clean_text, first_value
from telix.core.validators import (
    calculate_age,
    require_fields,
    validate_amount,
    validate_date_of_birth,
    validate_email,
    validate_phone,
    validate_score,
)


class ValidatorTests(unittest.TestCase):
    def test_require_fields_reports_every_missing_label(self):
        with self.assertRaisesRegex(ValidationError, "Name, Class"):
            require_fields(
                {"a": "x", "name": " ", "class": ""}, {"a": "A", "name": "Name", "class": "Class"}
            )

    def test_age_boundaries(self):
        today = date(2026, 10, 5)
        self.assertEqual(calculate_age(date(2016, 10, 5), today), 10)
        self.assertEqual(calculate_age(date(2016, 10, 6), today), 9)

    def test_date_of_birth_format_and_range(self):
        today = date(2026, 10, 5)
        self.assertEqual(validate_date_of_birth("2015-01-01", 3, 25, "DOB", today), "2015-01-01")
        with self.assertRaisesRegex(ValidationError, "YYYY-MM-DD"):
            validate_date_of_birth("01/01/2015", 3, 25, "DOB", today)
        with self.assertRaisesRegex(ValidationError, "between 3 and 25"):
            validate_date_of_birth("1990-01-01", 3, 25, "DOB", today)

    def test_phone(self):
        self.assertEqual(validate_phone("024 123-4567", "Phone"), "0241234567")
        self.assertEqual(validate_phone("+233241234567", "Phone"), "+233241234567")
        for bad in ("6256", "none", "abc1234567890"):
            with self.assertRaises(ValidationError):
                validate_phone(bad, "Phone")

    def test_email_amount_score(self):
        self.assertEqual(validate_email("a@b.co"), "a@b.co")
        with self.assertRaises(ValidationError):
            validate_email("nope")
        self.assertEqual(validate_amount("12.345", "Fees"), Decimal("12.34"))
        for bad in ("abc", "-1", "NaN", "Infinity"):
            with self.assertRaises(ValidationError):
                validate_amount(bad, "Fees")
        self.assertEqual(validate_score("100"), 100)
        for bad in ("101", "-1", "8.5", "x"):
            with self.assertRaises(ValidationError):
                validate_score(bad)


class HelperTests(unittest.TestCase):
    def test_text_helpers(self):
        self.assertEqual(clean_text(None), "")
        self.assertEqual(clean_text("  hi "), "hi")
        self.assertEqual(first_value({"a": "", "b": 0, "c": "x"}, "a", "b", "c"), 0)
        self.assertEqual(first_value({}, "a", default="d"), "d")

    def test_amount_and_currency(self):
        self.assertEqual(as_amount("12.5"), Decimal("12.50"))
        self.assertEqual(as_amount(None), Decimal("0.00"))
        self.assertEqual(as_amount("oops"), Decimal("0.00"))
        self.assertEqual(format_currency(1234.5), "GHS 1,234.50")
        self.assertEqual(
            as_amount("0.1") + as_amount("0.2"),
            Decimal("0.30"),
        )

    def test_search_is_case_insensitive_and_returns_index(self):
        records = [{"id": "A1"}, {"id": "b2"}]
        self.assertEqual(find_index_by_id(records, "id", " B2 "), 1)
        self.assertIsNone(find_index_by_id(records, "id", "zz"))
        self.assertEqual(find_by_id(records, "id", "a1"), {"id": "A1"})

    def test_filter_by_class(self):
        records = [{"class_name": "5"}, {"class_name": "6"}]
        self.assertEqual(filter_by_class(records, "5"), [{"class_name": "5"}])
        self.assertEqual(len(filter_by_class(records, "")), 2)

    def test_default_academic_year(self):
        self.assertEqual(default_academic_year(date(2026, 10, 5)), "2026/2027")
