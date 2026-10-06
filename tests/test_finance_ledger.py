"""Payment, expense, balance, and finance-summary service tests."""

from decimal import Decimal

from telix.core.errors import StorageError, ValidationError
from telix.core.numbers import as_amount
from telix.finance.repository import FinanceRepository
from telix.storage.json_store import JsonStore
from tests.support import ServiceTestCase, valid_student, valid_teacher


class FinanceLedgerTests(ServiceTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.students.add(valid_student(fees="100.00"))
        self.teachers.add(valid_teacher(salary="25.25"))

    def test_payments_support_partial_and_overpayment_credit(self) -> None:
        first = self.finance.add_payment(
            {
                "student_id": "STU-001",
                "payment_date": "2026-10-01",
                "amount": "40.10",
                "description": "First installment",
            }
        )
        second = self.finance.add_payment(
            {
                "student_id": "STU-001",
                "payment_date": "2026-10-02",
                "amount": "70.00",
            }
        )
        summary = self.finance.summary(self.students.list(), self.teachers.list())

        self.assertEqual(first["amount"], Decimal("40.10"))
        self.assertEqual(second["student_id"], "STU-001")
        self.assertEqual(summary["expected_fee_income"], Decimal("100.00"))
        self.assertEqual(summary["received_income"], Decimal("110.10"))
        self.assertEqual(summary["outstanding_balances"], Decimal("0.00"))
        self.assertEqual(summary["student_credit"], Decimal("10.10"))
        self.assertEqual(summary["salary_expense"], Decimal("25.25"))
        self.assertEqual(summary["profit_or_loss"], Decimal("84.85"))

    def test_invalid_payment_references_dates_and_amounts_are_rejected(self) -> None:
        for values, message in (
            (
                {"student_id": "missing", "payment_date": "2026-10-01", "amount": "2"},
                "existing student",
            ),
            ({"student_id": "STU-001", "payment_date": "10/01/2026", "amount": "2"}, "YYYY-MM-DD"),
            (
                {"student_id": "STU-001", "payment_date": "2026-10-01", "amount": "-1"},
                "cannot be negative",
            ),
            (
                {"student_id": "STU-001", "payment_date": "2026-10-01", "amount": "0"},
                "greater than zero",
            ),
        ):
            with self.subTest(values=values), self.assertRaisesRegex(ValidationError, message):
                self.finance.add_payment(values)

    def test_expenses_are_persisted_and_counted_in_summary(self) -> None:
        expense = self.finance.add_expense(
            {
                "expense_date": "2026-10-03",
                "category": "Utilities",
                "description": "Water bill",
                "amount": "5.50",
            }
        )
        saved = self.finance.list("expense")
        self.assertEqual(saved[0]["expense_id"], expense["expense_id"])
        self.assertEqual(as_amount(saved[0]["amount"]), Decimal("5.50"))
        self.assertEqual(
            self.finance.summary(self.students.list(), self.teachers.list())["other_expenses"],
            Decimal("5.50"),
        )

    def test_payment_filters_delete_and_student_deletion_guard(self) -> None:
        payment = self.finance.add_payment(
            {"student_id": "STU-001", "payment_date": "2026-10-01", "amount": "10"}
        )
        saved = self.finance.list("payment", student_id="stu-001")
        self.assertEqual(saved[0]["payment_id"], payment["payment_id"])
        self.assertEqual(as_amount(saved[0]["amount"]), Decimal("10.00"))
        self.assertEqual(
            self.finance.list("payment", start_date="2026-10-02", end_date="2026-10-03"), []
        )
        with self.assertRaisesRegex(ValidationError, "payment history"):
            self.removal.remove("STU-001")
        self.assertTrue(self.students.exists("STU-001"))
        self.finance.delete("payment", payment["payment_id"])
        self.removal.remove("STU-001")
        self.assertFalse(self.students.exists("STU-001"))

    def test_corrupt_financial_records_are_reported(self) -> None:
        repository = FinanceRepository(
            {
                "payment": JsonStore(self.directory / "bad-payments.json"),
                "expense": JsonStore(self.directory / "bad-expenses.json"),
            }
        )
        repository.save(
            "payment",
            [
                {
                    "payment_id": "PAY-1",
                    "student_id": "STU-001",
                    "payment_date": "2026-10-01",
                    "amount": "NaN",
                    "description": "",
                }
            ],
        )
        with self.assertRaisesRegex(StorageError, "invalid financial record"):
            repository.list("payment")
