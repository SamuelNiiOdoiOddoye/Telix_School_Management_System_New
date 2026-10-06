"""Tests for the secure first-run Super Admin bootstrap command."""

from __future__ import annotations

import contextlib
import io
import secrets
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from telix.authentication.service import AuthenticationService
from telix.bootstrap_admin import main


class BootstrapAdminTests(unittest.TestCase):
    def test_interactive_bootstrap_creates_once_without_displaying_password(self) -> None:
        password = secrets.token_urlsafe(24)
        with tempfile.TemporaryDirectory() as directory:
            users_file = Path(directory) / "users.json"
            with (
                patch("telix.authentication.repository.USERS_FILE", users_file),
                patch.dict(
                    "os.environ",
                    {
                        "TELIX_SUPERADMIN_EMAIL": "",
                        "TELIX_SUPERADMIN_NAME": "",
                        "TELIX_SUPERADMIN_PHONE": "",
                        "TELIX_SUPERADMIN_PASSWORD": "",
                    },
                ),
                patch(
                    "builtins.input",
                    side_effect=[
                        "Test Administrator",
                        "admin@example.invalid",
                        "+12025550123",
                    ],
                ),
                patch("getpass.getpass", side_effect=[password, password]),
            ):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(main(), 0)
                    self.assertEqual(main(), 0)

                auth = AuthenticationService()
                self.assertTrue(auth.has_super_admin())
                self.assertIsNotNone(auth.authenticate("admin@example.invalid", password))

        self.assertNotIn(password, output.getvalue())
        self.assertIn("already exists", output.getvalue())
        self.assertIn("admin@example.invalid", output.getvalue())

    def test_environment_bootstrap_never_prints_the_password(self) -> None:
        password = secrets.token_urlsafe(24)
        with tempfile.TemporaryDirectory() as directory:
            users_file = Path(directory) / "users.json"
            environment = {
                "TELIX_SUPERADMIN_EMAIL": "admin@example.invalid",
                "TELIX_SUPERADMIN_NAME": "Test Administrator",
                "TELIX_SUPERADMIN_PHONE": "+12025550123",
                "TELIX_SUPERADMIN_PASSWORD": password,
            }
            with (
                patch("telix.authentication.repository.USERS_FILE", users_file),
                patch.dict("os.environ", environment),
                patch("builtins.input", side_effect=AssertionError("unexpected prompt")),
                patch("getpass.getpass", side_effect=AssertionError("unexpected prompt")),
            ):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(main(), 0)
                auth = AuthenticationService()
                self.assertIsNotNone(auth.authenticate("admin@example.invalid", password))

        self.assertNotIn(password, output.getvalue())
        self.assertIn("admin@example.invalid", output.getvalue())


if __name__ == "__main__":
    unittest.main()
