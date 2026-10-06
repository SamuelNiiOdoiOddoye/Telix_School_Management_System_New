"""V1 Super Admin account creation and login rules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from telix.authentication.passwords import hash_password, verify_password
from telix.authentication.repository import UserRepository
from telix.core.errors import ValidationError
from telix.core.validators import require_fields, validate_email, validate_phone

_PASSWORD_MIN_LENGTH = 12
_PASSWORD_MAX_LENGTH = 1024
_ACCOUNT_LABELS = {"name": "Name", "email": "Email", "phone": "Phone"}


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: str
    name: str
    email: str
    phone: str
    role: str


class AuthenticationService:
    def __init__(self, repository: UserRepository | None = None) -> None:
        self.repository = repository or UserRepository()

    def create_super_admin(
        self, name: str, email: str, phone: str, password: str
    ) -> AuthenticatedUser:
        values = require_fields(
            {"name": name, "email": email, "phone": phone},
            _ACCOUNT_LABELS,
        )
        normalized_email = validate_email(values["email"]).casefold()
        normalized_phone = validate_phone(values["phone"], "Phone number")
        self._validate_password(password)
        if self.repository.find_by_email(normalized_email):
            raise ValidationError("An account with this email already exists.")
        if self.repository.has_super_admin():
            raise ValidationError("A Super Admin account already exists.")

        now = datetime.now(timezone.utc).isoformat()
        record = {
            "user_id": f"USR-{uuid4().hex}",
            "name": values["name"],
            "email": normalized_email,
            "phone": normalized_phone,
            "password_hash": hash_password(password),
            "role": "SUPER_ADMIN",
            "active": True,
            "created_at": now,
            "updated_at": now,
        }
        self.repository.save(record)
        return self._public_user(record)

    def authenticate(self, email: str, password: str) -> AuthenticatedUser | None:
        if not email.strip() or not password:
            return None
        user = self.repository.find_by_email(email)
        if (
            user is None
            or user.get("active") is not True
            or user.get("role") != "SUPER_ADMIN"
            or not isinstance(user.get("password_hash"), str)
            or not verify_password(password, user["password_hash"])
        ):
            return None
        return self._public_user(user)

    def has_super_admin(self) -> bool:
        return self.repository.has_super_admin()

    @staticmethod
    def _validate_password(password: str) -> None:
        if (
            not isinstance(password, str)
            or not _PASSWORD_MIN_LENGTH <= len(password) <= _PASSWORD_MAX_LENGTH
        ):
            raise ValidationError(
                f"Password must contain between {_PASSWORD_MIN_LENGTH} and "
                f"{_PASSWORD_MAX_LENGTH} characters."
            )

    @staticmethod
    def _public_user(user: dict[str, object]) -> AuthenticatedUser:
        return AuthenticatedUser(
            user_id=str(user["user_id"]),
            name=str(user["name"]),
            email=str(user["email"]),
            phone=str(user["phone"]),
            role=str(user["role"]),
        )
