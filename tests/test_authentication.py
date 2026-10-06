"""Tests for secure local Super Admin authentication."""

from __future__ import annotations

import tempfile
import secrets
import io
import logging
import unittest
from pathlib import Path

from telix.authentication.passwords import hash_password, verify_password
from telix.authentication.repository import UserRepository
from telix.authentication.service import AuthenticationService
from telix.authentication.session import UserSession
from telix.core.errors import StorageError, ValidationError
from telix.storage.json_store import JsonStore


class PasswordHashTests(unittest.TestCase):
    def test_password_hash_is_salted_and_verifies_without_storing_plaintext(self) -> None:
        password = secrets.token_urlsafe(24)
        first_hash = hash_password(password)
        second_hash = hash_password(password)

        self.assertNotEqual(first_hash, password)
        self.assertNotEqual(first_hash, second_hash)
        self.assertTrue(verify_password(password, first_hash))
        self.assertFalse(verify_password(f"{password}-wrong", first_hash))
        self.assertFalse(verify_password(password, "not-a-valid-hash"))


class AuthenticationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.repository = UserRepository(JsonStore(Path(directory.name) / "users.json"))
        self.authentication = AuthenticationService(self.repository)
        self.password = secrets.token_urlsafe(24)

    def _create_admin(self):
        return self.authentication.create_super_admin(
            "Test Administrator",
            "Admin@Example.invalid",
            "+12025550123",
            self.password,
        )

    def test_create_account_normalizes_email_and_persists_only_password_hash(self) -> None:
        user = self._create_admin()
        stored = self.repository.list()[0]

        self.assertEqual(user.email, "admin@example.invalid")
        self.assertEqual(stored["email"], "admin@example.invalid")
        self.assertNotEqual(stored["password_hash"], self.password)
        self.assertNotIn("password", stored)
        self.assertEqual(user.role, "SUPER_ADMIN")
        self.assertNotIn("password_hash", user.__dict__)

    def test_duplicate_account_and_second_super_admin_are_rejected(self) -> None:
        self._create_admin()
        with self.assertRaisesRegex(ValidationError, "already exists"):
            self.authentication.create_super_admin(
                "Duplicate",
                "ADMIN@example.invalid",
                "+12025550124",
                secrets.token_urlsafe(24),
            )
        with self.assertRaisesRegex(ValidationError, "Super Admin account already exists"):
            self.authentication.create_super_admin(
                "Second",
                "second@example.invalid",
                "+12025550125",
                secrets.token_urlsafe(24),
            )
        self.assertEqual(len(self.repository.list()), 1)

    def test_required_fields_and_password_policy_are_enforced(self) -> None:
        with self.assertRaisesRegex(ValidationError, "complete"):
            self.authentication.create_super_admin(
                "", "admin@example.invalid", "+12025550123", self.password
            )
        with self.assertRaisesRegex(ValidationError, "between 12 and 1024"):
            self.authentication.create_super_admin(
                "Test Administrator",
                "admin@example.invalid",
                "+12025550123",
                "x" * 6,
            )
        self.assertEqual(self.repository.list(), [])

    def test_login_is_case_insensitive_and_rejects_unknown_or_invalid_credentials(self) -> None:
        self._create_admin()

        user = self.authentication.authenticate("ADMIN@EXAMPLE.INVALID", self.password)

        self.assertIsNotNone(user)
        self.assertEqual(user.email, "admin@example.invalid")
        self.assertIsNone(
            self.authentication.authenticate("missing@example.invalid", self.password)
        )
        self.assertIsNone(
            self.authentication.authenticate("admin@example.invalid", f"{self.password}-wrong")
        )
        self.assertIsNone(self.authentication.authenticate("", self.password))

    def test_disabled_accounts_cannot_log_in(self) -> None:
        user = self._create_admin()
        self.assertTrue(self.repository.set_active(user.user_id, False))
        self.assertIsNone(self.authentication.authenticate(user.email, self.password))

    def test_authentication_does_not_log_password_values(self) -> None:
        self._create_admin()
        stream = io.StringIO()
        logger = logging.getLogger("telix")
        handler = logging.StreamHandler(stream)
        logger.addHandler(handler)
        try:
            self.authentication.authenticate("admin@example.invalid", self.password)
            self.authentication.authenticate("admin@example.invalid", f"{self.password}-wrong")
        finally:
            logger.removeHandler(handler)
            handler.close()

        self.assertNotIn(self.password, stream.getvalue())

    def test_session_is_only_authenticated_after_login_and_clears_on_logout(self) -> None:
        user = self._create_admin()
        session = UserSession()

        self.assertFalse(session.authenticated)
        session.start(user)
        self.assertTrue(session.authenticated)
        self.assertEqual(session.user, user)
        session.clear()
        self.assertFalse(session.authenticated)
        self.assertIsNone(session.user)

    def test_session_rejects_roles_outside_the_v1_super_admin(self) -> None:
        from telix.authentication.service import AuthenticatedUser

        session = UserSession()
        with self.assertRaisesRegex(ValueError, "Only a Super Admin"):
            session.start(
                AuthenticatedUser(
                    user_id="USR-OTHER",
                    name="Other",
                    email="other@example.invalid",
                    phone="+12025550124",
                    role="TEACHER",
                )
            )
        self.assertFalse(session.authenticated)

    def test_corrupt_account_storage_fails_explicitly(self) -> None:
        self.repository._store.save([{"user_id": "incomplete"}])

        with self.assertRaisesRegex(StorageError, "invalid account record"):
            self.authentication.has_super_admin()


if __name__ == "__main__":
    unittest.main()
