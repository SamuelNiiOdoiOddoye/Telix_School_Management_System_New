"""Tests for local V1 account roles, service authorization, and demo setup."""

from __future__ import annotations

import os
import secrets
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from telix.authentication.repository import UserRepository
from telix.authentication.roles import (
    ADMIN,
    FINANCE_OFFICER,
    STUDENT,
    SUPER_ADMIN,
    TEACHER,
    Authorization,
)
from telix.authentication.service import AuthenticationService
from telix.authentication.session import UserSession
from telix.bootstrap_demo_accounts import DEMO_ACCOUNTS, DEMO_STUDENT_ID, run_demo_bootstrap
from telix.core.errors import AuthorizationError, ValidationError
from telix.storage.json_store import JsonStore
from telix.students.repository import StudentRepository
from telix.students.service import StudentService
from tests.support import ServiceTestCase, valid_student


class RoleAuthenticationTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.repository = UserRepository(JsonStore(Path(directory.name) / "users.json"))
        students = StudentService(
            StudentRepository(JsonStore(Path(directory.name) / "student_records.json"))
        )
        students.add(valid_student(student_id=DEMO_STUDENT_ID))
        self.authentication = AuthenticationService(self.repository, students.exists)

    def test_supported_roles_authenticate_and_student_link_is_carried(self) -> None:
        password = secrets.token_urlsafe(24)
        for index, role in enumerate((SUPER_ADMIN, ADMIN, TEACHER, FINANCE_OFFICER, STUDENT)):
            user = self.authentication.create_account(
                f"Demo {role}",
                f"{role.casefold()}@example.invalid",
                f"+1202555013{index}",
                password,
                role,
                student_id="DEMO-STU-001" if role == STUDENT else "",
            )
            authenticated = self.authentication.authenticate(user.email, password)
            self.assertIsNotNone(authenticated)
            self.assertEqual(authenticated.role, role)
            self.assertEqual(
                authenticated.student_id,
                "DEMO-STU-001" if role == STUDENT else "",
            )
            session = UserSession()
            session.start(authenticated)
            self.assertTrue(session.authenticated)

    def test_student_accounts_require_student_link_and_super_admin_is_unique(self) -> None:
        with self.assertRaisesRegex(ValidationError, "must link to an existing"):
            self.authentication.create_account(
                "Student",
                "student@example.invalid",
                "+12025550130",
                secrets.token_urlsafe(24),
                STUDENT,
            )
        self.authentication.create_super_admin(
            "Admin", "admin@example.invalid", "+12025550131", secrets.token_urlsafe(24)
        )
        with self.assertRaisesRegex(ValidationError, "Super Admin account already exists"):
            self.authentication.create_account(
                "Second",
                "second@example.invalid",
                "+12025550132",
                secrets.token_urlsafe(24),
                SUPER_ADMIN,
            )

    def test_student_account_cannot_authenticate_after_linked_record_disappears(self) -> None:
        password = secrets.token_urlsafe(24)
        user = self.authentication.create_account(
            "Student",
            "student@example.invalid",
            "+12025550135",
            password,
            STUDENT,
            student_id=DEMO_STUDENT_ID,
        )
        authentication_without_student = AuthenticationService(
            self.repository, lambda _student_id: False
        )

        self.assertIsNone(authentication_without_student.authenticate(user.email, password))

    def test_demo_bootstrap_is_repeatable_and_never_resets_passwords(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            authentication = AuthenticationService(
                UserRepository(JsonStore(Path(directory) / "users.json")),
                StudentService(
                    StudentRepository(JsonStore(Path(directory) / "student_records.json"))
                ).exists,
            )
            students = StudentService(
                StudentRepository(JsonStore(Path(directory) / "student_records.json"))
            )
            passwords = [secrets.token_urlsafe(24) for _ in DEMO_ACCOUNTS]
            prompts = [value for password in passwords for value in (password, password)]
            with patch.dict(os.environ, {"TELIX_DEVELOPMENT_DEMO_BOOTSTRAP": "1"}):
                created = run_demo_bootstrap(
                    authentication,
                    students,
                    password_prompt=unittest.mock.Mock(side_effect=prompts),
                    message=lambda _message: None,
                )
                second_run = run_demo_bootstrap(
                    authentication,
                    students,
                    password_prompt=unittest.mock.Mock(
                        side_effect=AssertionError("existing passwords must not be prompted")
                    ),
                    message=lambda _message: None,
                )
                self.assertEqual(len(created), 5)
                self.assertEqual(second_run, [])
                self.assertTrue(students.get(DEMO_STUDENT_ID))
                student_account = authentication.repository.find_by_email(
                    "demo-student@telix.example.invalid"
                )
                self.assertEqual(student_account["student_id"], DEMO_STUDENT_ID)

    def test_demo_bootstrap_refuses_to_link_an_unrelated_existing_student(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            students = StudentService(
                StudentRepository(JsonStore(Path(directory) / "student_records.json"))
            )
            students.add(valid_student(student_id=DEMO_STUDENT_ID, name="Existing Student"))
            authentication = AuthenticationService(
                UserRepository(JsonStore(Path(directory) / "users.json")),
                students.exists,
            )
            with patch.dict(os.environ, {"TELIX_DEVELOPMENT_DEMO_BOOTSTRAP": "1"}):
                with self.assertRaisesRegex(ValidationError, "not the expected synthetic demo"):
                    run_demo_bootstrap(
                        authentication,
                        students,
                        password_prompt=lambda _prompt: self.fail("must not prompt"),
                        message=lambda _message: None,
                    )
            self.assertEqual(authentication.repository.list(), [])


class ServiceAuthorizationTests(ServiceTestCase):
    def test_student_reads_are_limited_to_linked_student_and_safe_fields(self) -> None:
        self.students.add(valid_student(student_id="STU-OWN", medical_info="private"))
        self.students.add(valid_student(student_id="STU-OTHER", name="Other"))
        scoped_students = StudentService(
            self.students._repository,
            Authorization(STUDENT, "STU-OWN"),
        )

        rows = scoped_students.list()

        self.assertEqual([row["student_id"] for row in rows], ["STU-OWN"])
        self.assertNotIn("medical_info", rows[0])
        self.assertNotIn("parent_phone", rows[0])
        self.assertIsNone(scoped_students.get("STU-OTHER"))
        with self.assertRaises(AuthorizationError):
            scoped_students.update("STU-OWN", valid_student(student_id="STU-OWN"))

    def test_student_cannot_request_another_students_academic_history(self) -> None:
        self.students.add(valid_student(student_id="STU-OWN"))
        self.students.add(valid_student(student_id="STU-OTHER", name="Other"))
        self.academics.add(
            {
                "student_id": "STU-OWN",
                "subject": "Math",
                "score": "90",
                "term": "Term 1",
                "academic_year": "2026/2027",
            },
            self.students.exists,
        )
        self.academics.add(
            {
                "student_id": "STU-OTHER",
                "subject": "Math",
                "score": "10",
                "term": "Term 1",
                "academic_year": "2026/2027",
            },
            self.students.exists,
        )
        scoped = type(self.academics)(
            self.academics._repository,
            self.academic_structure,
            Authorization(STUDENT, "STU-OWN"),
        )

        self.assertEqual(len(scoped.list()), 1)
        self.assertEqual(len(scoped.period_summaries()), 1)
        with self.assertRaises(AuthorizationError):
            scoped.for_student("STU-OTHER")

    def test_role_service_boundaries_reject_unauthorized_access(self) -> None:
        teacher_finance = type(self.finance)(
            self.finance._repository,
            self.students.exists,
            Authorization(TEACHER),
        )
        finance_students = StudentService(
            self.students._repository,
            Authorization(FINANCE_OFFICER),
        )

        with self.assertRaises(AuthorizationError):
            teacher_finance.list("payment")
        with self.assertRaises(AuthorizationError):
            finance_students.add(valid_student())
        self.assertTrue(Authorization(ADMIN).allows("finance.read"))

    def test_teacher_and_finance_student_views_expose_only_permitted_fields(self) -> None:
        self.students.add(valid_student(student_id="STU-001", medical_info="Private"))
        teacher_view = StudentService(
            self.students._repository,
            Authorization(TEACHER),
        ).list()
        finance_view = StudentService(
            self.students._repository,
            Authorization(FINANCE_OFFICER),
        ).list()

        self.assertEqual(set(teacher_view[0]), {"student_id", "name", "status", "class_name"})
        self.assertEqual(
            set(finance_view[0]),
            {"student_id", "name", "status", "fees"},
        )

    def test_student_assessment_and_attendance_reads_cannot_be_widened(self) -> None:
        self.students.add(valid_student(student_id="STU-OWN"))
        self.students.add(valid_student(student_id="STU-OTHER", name="Other"))
        assessment_records = [
            {
                "assessment_id": f"ASM-{student_id}",
                "student_id": student_id,
                "subject_id": "SUB-MATH",
                "subject": "Mathematics",
                "academic_year_id": "YEAR-2026",
                "academic_year": "2026/2027",
                "term_id": "TERM-1",
                "term": "Term 1",
                "component": "Exam",
                "score": "80",
            }
            for student_id in ("STU-OWN", "STU-OTHER")
        ]
        self.assessments._repository.save("assessment", assessment_records)
        scoped_assessments = type(self.assessments)(
            self.assessments._repository,
            self.academic_structure,
            self.students.exists,
            Authorization(STUDENT, "STU-OWN"),
        )
        attendance_records = [
            {
                "attendance_id": f"ATT-{student_id}",
                "student_id": student_id,
                "class_id": "CLASS-1",
                "academic_year_id": "YEAR-2026",
                "enrollment_id": f"ENR-{student_id}",
                "attendance_date": "2026-10-06",
                "status": "Present",
            }
            for student_id in ("STU-OWN", "STU-OTHER")
        ]
        self.attendance._repository.save(attendance_records)
        scoped_attendance = type(self.attendance)(
            self.attendance._repository,
            self.academic_structure,
            self.students.exists,
            Authorization(STUDENT, "STU-OWN"),
        )

        self.assertEqual(
            [record["student_id"] for record in scoped_assessments.list()],
            ["STU-OWN"],
        )
        self.assertEqual(
            [record["student_id"] for record in scoped_attendance.list()],
            ["STU-OWN"],
        )
        with self.assertRaises(AuthorizationError):
            scoped_assessments.grade("STU-OTHER", "SUB-MATH", "YEAR-2026", "TERM-1")
        with self.assertRaises(AuthorizationError):
            scoped_attendance.list(student_id="STU-OTHER")


if __name__ == "__main__":
    unittest.main()
