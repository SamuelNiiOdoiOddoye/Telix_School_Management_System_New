"""Securely create the initial local Telix Super Admin account."""

from __future__ import annotations

import getpass
import os
import sys

from telix.authentication.service import AuthenticationService
from telix.core.errors import StorageError, ValidationError


def _setting(name: str, prompt: str) -> str:
    configured = os.environ.get(name, "").strip()
    if configured:
        return configured
    return input(f"{prompt}: ").strip()


def main() -> int:
    authentication = AuthenticationService()
    try:
        if authentication.has_super_admin():
            print("A Super Admin account already exists; no changes were made.")
            return 0

        name = _setting("TELIX_SUPERADMIN_NAME", "Administrator name")
        email = _setting("TELIX_SUPERADMIN_EMAIL", "Administrator email")
        phone = _setting("TELIX_SUPERADMIN_PHONE", "Administrator phone")
        password = os.environ.get("TELIX_SUPERADMIN_PASSWORD", "")
        if not password:
            password = getpass.getpass("New password (input hidden): ")
            confirmation = getpass.getpass("Confirm password (input hidden): ")
            if password != confirmation:
                print("Passwords did not match.", file=sys.stderr)
                return 1

        user = authentication.create_super_admin(name, email, phone, password)
    except (StorageError, ValidationError) as error:
        print(f"Could not create the Super Admin: {error}", file=sys.stderr)
        return 1

    print(f"Super Admin account created for {user.email}. The password was not displayed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
