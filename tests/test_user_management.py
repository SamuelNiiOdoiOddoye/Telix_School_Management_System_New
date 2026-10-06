"""Tests for authorized V1 user account administration."""

from __future__ import annotations

import secrets
import tempfile
import unittest
from pathlib import Path

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
from telix.authentication.user_management import UserManagementService
from telix.core.errors import AuthorizationError, ValidationError
from telix.storage.json_store import JsonStore
from telix.students.repository import StudentRepository
from telix.students.service import StudentService
from telix.ui.tabs.users import role_access_summary
from tests.support import valid_student


class UserManagementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name)
        self.students = StudentService(StudentRepository(JsonStore(root / "student_records.json")))
        self.students.add(valid_student(student_id="STU-001"))
        self.authentication = AuthenticationService(
            UserRepository(JsonStore(root / "users.json")),
            self.students.exists,
        )
        self.password = secrets.token_urlsafe(24)
        self.super_admin = self.authentication.create_super_admin(
            "Super Admin",
            "super-admin@example.invalid",
            "+12025550101",
            self.password,
        )
        self.super_admin_management = self._management(self.super_admin)

    def _management(self, user, *, acting_user_id: str | None = None):
        return UserManagementService(
            self.authentication,
            Authorization(user.role, user.student_id),
            user.user_id if acting_user_id is None else acting_user_id,
        )

    def _create_account(self, role: str, email: str):
        return self.super_admin_management.create(
            f"Test {role}",
            email,
            "+12025550102",
            secrets.token_urlsafe(24),
            role,
            student_id="STU-001" if role == STUDENT else "",
        )

    def test_admin_can_manage_only_assignable_roles(self) -> None:
        admin = self._create_account(ADMIN, "admin@example.invalid")
        teacher = self._create_account(TEACHER, "teacher@example.invalid")
        admin_management = self._management(admin)

        listed = admin_management.list()
        self.assertEqual([record["user_id"] for record in listed], [teacher.user_id])
        self.assertNotIn("password_hash", listed[0])
        self.assertNotIn("password", listed[0])
        self.assertEqual(
            set(admin_management.assignable_roles()), {TEACHER, FINANCE_OFFICER, STUDENT}
        )
        with self.assertRaises(AuthorizationError):
            admin_management.create(
                "Escalated Admin",
                "escalated@example.invalid",
                "+12025550103",
                secrets.token_urlsafe(24),
                SUPER_ADMIN,
            )
        with self.assertRaises(AuthorizationError):
            admin_management.update(
                teacher.user_id,
                name=teacher.name,
                email=teacher.email,
                phone=teacher.phone,
                role=SUPER_ADMIN,
            )
        with self.assertRaises(AuthorizationError):
            admin_management.update(
                self.super_admin.user_id,
                name="Super Admin",
                email="super-admin@example.invalid",
                phone="+12025550101",
                role=ADMIN,
            )
        with self.assertRaises(AuthorizationError):
            admin_management.set_active(self.super_admin.user_id, False)

    def test_only_admin_and_super_admin_can_access_user_management(self) -> None:
        for role in (TEACHER, FINANCE_OFFICER, STUDENT):
            with self.subTest(role=role):
                user = self._create_account(role, f"{role.casefold()}@example.invalid")
                management = self._management(user)
                with self.assertRaises(AuthorizationError):
                    management.list()

    def test_access_summary_is_derived_from_role_capabilities(self) -> None:
        teacher_summary = role_access_summary(TEACHER)
        admin_summary = role_access_summary(ADMIN)

        self.assertIn("Effective V1 access for TEACHER", teacher_summary)
        self.assertIn("Academics: read, write", teacher_summary)
        self.assertNotIn("users: manage", teacher_summary)
        self.assertIn("Users: manage", admin_summary)
        self.assertIn("All V1 capabilities", role_access_summary(SUPER_ADMIN))

    def test_student_link_is_required_and_removed_when_role_changes(self) -> None:
        with self.assertRaisesRegex(ValidationError, "must link to an existing"):
            self.super_admin_management.create(
                "Unlinked Student",
                "unlinked@example.invalid",
                "+12025550104",
                secrets.token_urlsafe(24),
                STUDENT,
            )
        student_password = secrets.token_urlsafe(24)
        student = self.super_admin_management.create(
            "Linked Student",
            "student@example.invalid",
            "+12025550105",
            student_password,
            STUDENT,
            student_id="STU-001",
        )

        updated = self.super_admin_management.update(
            student.user_id,
            name="Former Student",
            email="former-student@example.invalid",
            phone="+12025550105",
            role=TEACHER,
        )

        self.assertEqual(updated["student_id"], "")
        self.assertEqual(
            self.authentication.repository.find_by_id(student.user_id).get("student_id", ""),
            "",
        )
        self.assertEqual(
            self.authentication.authenticate(
                "former-student@example.invalid", student_password
            ).role,
            TEACHER,
        )

    def test_email_collision_is_rejected_without_changing_account(self) -> None:
        teacher = self._create_account(TEACHER, "teacher@example.invalid")
        another = self._create_account(TEACHER, "another@example.invalid")

        with self.assertRaisesRegex(ValidationError, "email already exists"):
            self.super_admin_management.update(
                another.user_id,
                name="Another",
                email="TEACHER@example.invalid",
                phone="+12025550106",
                role=TEACHER,
            )

        self.assertEqual(
            self.authentication.repository.find_by_id(another.user_id)["email"],
            "another@example.invalid",
        )
        self.assertEqual(teacher.email, "teacher@example.invalid")

    def test_deactivated_account_cannot_login_and_reactivated_account_can(self) -> None:
        password = secrets.token_urlsafe(24)
        teacher = self.super_admin_management.create(
            "Teacher",
            "teacher@example.invalid",
            "+12025550106",
            password,
            TEACHER,
        )

        self.super_admin_management.set_active(teacher.user_id, False)
        self.assertIsNone(self.authentication.authenticate("teacher@example.invalid", password))
        self.super_admin_management.set_active(teacher.user_id, True)
        self.assertEqual(
            self.authentication.authenticate("teacher@example.invalid", password).role,
            TEACHER,
        )

    def test_super_admin_can_create_another_and_protects_own_account(self) -> None:
        second = self.super_admin_management.create(
            "Second Super Admin",
            "second-super-admin@example.invalid",
            "+12025550107",
            secrets.token_urlsafe(24),
            SUPER_ADMIN,
        )
        second_management = self._management(second)

        with self.assertRaisesRegex(ValidationError, "currently signed-in"):
            second_management.set_active(second.user_id, False)
        with self.assertRaisesRegex(ValidationError, "own role"):
            second_management.update(
                second.user_id,
                name=second.name,
                email=second.email,
                phone=second.phone,
                role=ADMIN,
            )
        second_management.set_active(self.super_admin.user_id, False)
        final_admin_management = UserManagementService(
            self.authentication,
            Authorization(SUPER_ADMIN),
            "another-session",
        )
        with self.assertRaisesRegex(ValidationError, "last active Super Admin"):
            final_admin_management.set_active(second.user_id, False)
        with self.assertRaisesRegex(ValidationError, "last active Super Admin"):
            final_admin_management.update(
                second.user_id,
                name=second.name,
                email=second.email,
                phone=second.phone,
                role=ADMIN,
            )


if __name__ == "__main__":
    unittest.main()
