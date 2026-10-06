"""V1 Super Admin account creation and login rules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from collections.abc import Callable
from uuid import uuid4

from telix.authentication.passwords import hash_password, verify_password
from telix.authentication.repository import UserRepository
from telix.authentication.roles import (
    SUPER_ADMIN,
    STUDENT,
    USERS_MANAGE,
    Authorization,
    V1_ROLES,
    assignable_roles,
)
from telix.core.errors import AuthorizationError, ValidationError
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
    student_id: str = ""


class AuthenticationService:
    def __init__(
        self,
        repository: UserRepository | None = None,
        student_exists: Callable[[str], bool] | None = None,
    ) -> None:
        self.repository = repository or UserRepository()
        self._student_exists = student_exists

    def create_super_admin(
        self, name: str, email: str, phone: str, password: str
    ) -> AuthenticatedUser:
        if self.repository.has_super_admin():
            raise ValidationError("A Super Admin account already exists.")
        return self._create_account_record(name, email, phone, password, SUPER_ADMIN)

    def create_account(
        self,
        name: str,
        email: str,
        phone: str,
        password: str,
        role: str,
        *,
        authorization: Authorization | None = None,
        student_id: str = "",
        _allow_additional_super_admin: bool = False,
    ) -> AuthenticatedUser:
        if authorization is None:
            raise AuthorizationError("Use authorized user management to create accounts.")
        authorization.require(USERS_MANAGE)
        if role not in assignable_roles(authorization.role):
            raise AuthorizationError("Your account cannot assign this V1 role.")
        return self._create_account_record(
            name,
            email,
            phone,
            password,
            role,
            student_id=student_id,
            allow_additional_super_admin=(
                _allow_additional_super_admin or authorization.role == SUPER_ADMIN
            ),
        )

    def _create_account_record(
        self,
        name: str,
        email: str,
        phone: str,
        password: str,
        role: str,
        *,
        student_id: str = "",
        allow_additional_super_admin: bool = False,
    ) -> AuthenticatedUser:
        values = require_fields(
            {"name": name, "email": email, "phone": phone},
            _ACCOUNT_LABELS,
        )
        if role not in V1_ROLES:
            raise ValidationError("Select a supported V1 role.")
        if role == STUDENT and not self.student_exists(student_id.strip().upper()):
            raise ValidationError("A student account must link to an existing student record.")
        if (
            role == SUPER_ADMIN
            and self.repository.has_super_admin()
            and not allow_additional_super_admin
        ):
            raise ValidationError("A Super Admin account already exists.")
        normalized_email = validate_email(values["email"]).casefold()
        normalized_phone = validate_phone(values["phone"], "Phone number")
        self._validate_password(password)
        if self.repository.find_by_email(normalized_email):
            raise ValidationError("An account with this email already exists.")
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "user_id": f"USR-{uuid4().hex}",
            "name": values["name"],
            "email": normalized_email,
            "phone": normalized_phone,
            "password_hash": hash_password(password),
            "role": role,
            **({"student_id": student_id.strip().upper()} if role == STUDENT else {}),
            "active": True,
            "created_at": now,
            "updated_at": now,
        }
        self.repository.save(record)
        return self._public_user(record)

    def create_development_demo_account(
        self,
        name: str,
        email: str,
        phone: str,
        password: str,
        role: str,
        *,
        student_id: str = "",
    ) -> AuthenticatedUser:
        if os.environ.get("TELIX_DEVELOPMENT_DEMO_BOOTSTRAP") != "1":
            raise ValidationError(
                "Demo accounts can only be created by the explicit dev bootstrap."
            )
        return self._create_account_record(
            name,
            email,
            phone,
            password,
            role,
            student_id=student_id,
            allow_additional_super_admin=True,
        )

    def authenticate(self, email: str, password: str) -> AuthenticatedUser | None:
        if not email.strip() or not password:
            return None
        user = self.repository.find_by_email(email)
        if (
            user is None
            or user.get("active") is not True
            or user.get("role") not in V1_ROLES
            or not isinstance(user.get("password_hash"), str)
            or not verify_password(password, user["password_hash"])
        ):
            return None
        if user.get("role") == STUDENT and (
            self._student_exists is None
            or not self._student_exists(str(user.get("student_id", "")))
        ):
            return None
        return self._public_user(user)

    def has_super_admin(self) -> bool:
        return self.repository.has_super_admin()

    def student_exists(self, student_id: str) -> bool:
        normalized_id = student_id.strip().upper()
        return bool(
            normalized_id
            and self._student_exists is not None
            and self._student_exists(normalized_id)
        )

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
            student_id=str(user.get("student_id", "")),
        )
