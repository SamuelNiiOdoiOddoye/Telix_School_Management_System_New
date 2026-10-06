"""Authorized account administration for the local V1 application."""

from __future__ import annotations

from typing import Any

from telix.authentication.roles import (
    ADMIN,
    STUDENT,
    SUPER_ADMIN,
    USERS_MANAGE,
    Authorization,
    assignable_roles,
)
from telix.authentication.service import AuthenticationService, AuthenticatedUser
from telix.core.errors import AuthorizationError, ValidationError
from telix.core.validators import require_fields, validate_email, validate_phone

_PUBLIC_FIELDS = (
    "user_id",
    "name",
    "email",
    "phone",
    "role",
    "student_id",
    "active",
    "created_at",
    "updated_at",
)


class UserManagementService:
    def __init__(
        self,
        authentication: AuthenticationService,
        authorization: Authorization,
        current_user_id: str = "",
    ) -> None:
        self._authentication = authentication
        self._authorization = authorization
        self._current_user_id = current_user_id.strip().casefold()

    def list(self, query: str = "") -> list[dict[str, Any]]:
        self._authorization.require(USERS_MANAGE)
        normalized_query = query.strip().casefold()
        users = self._authentication.repository.list()
        matches = (
            user
            for user in users
            if user.get("role") in assignable_roles(self._authorization.role)
            and (
                not normalized_query
                or any(
                    normalized_query in str(user.get(field, "")).casefold()
                    for field in ("name", "email", "role", "user_id")
                )
            )
        )
        return [
            {field: user[field] for field in _PUBLIC_FIELDS if field in user}
            for user in sorted(matches, key=lambda item: str(item.get("email", "")).casefold())
        ]

    def create(
        self,
        name: str,
        email: str,
        phone: str,
        password: str,
        role: str,
        *,
        student_id: str = "",
    ) -> AuthenticatedUser:
        self._authorization.require(USERS_MANAGE)
        self._require_assignable_role(role)
        return self._authentication.create_account(
            name,
            email,
            phone,
            password,
            role,
            authorization=self._authorization,
            student_id=student_id,
        )

    def update(
        self,
        user_id: str,
        *,
        name: str,
        email: str,
        phone: str,
        role: str,
        student_id: str = "",
    ) -> dict[str, Any]:
        self._authorization.require(USERS_MANAGE)
        existing = self._require_target(user_id)
        self._require_assignable_role(role)
        role_changed = role != existing["role"]
        if role_changed and self._is_current_user(user_id):
            raise ValidationError("You cannot change your own role while signed in.")
        if role_changed and existing["role"] == SUPER_ADMIN and existing["active"]:
            self._require_another_active_super_admin()
        values = require_fields(
            {"name": name, "email": email},
            {"name": "Name", "email": "Email"},
        )
        normalized_email = validate_email(values["email"]).casefold()
        normalized_phone = validate_phone(phone, "Phone number") if phone.strip() else ""
        duplicate = self._authentication.repository.find_by_email(normalized_email)
        if duplicate is not None and duplicate["user_id"] != existing["user_id"]:
            raise ValidationError("An account with this email already exists.")
        normalized_student_id = ""
        if role == STUDENT:
            normalized_student_id = student_id.strip().upper()
            if not normalized_student_id or not self._authentication.student_exists(
                normalized_student_id
            ):
                raise ValidationError("A student account must link to an existing student record.")
        updates: dict[str, Any] = {
            "name": values["name"],
            "email": normalized_email,
            "phone": normalized_phone,
            "role": role,
            "student_id": normalized_student_id,
        }
        updated = self._authentication.repository.update_account(user_id, updates)
        if updated is None:
            raise ValidationError("User account was not found.")
        return {field: updated[field] for field in _PUBLIC_FIELDS if field in updated}

    def set_active(self, user_id: str, is_active: bool) -> dict[str, Any]:
        self._authorization.require(USERS_MANAGE)
        target = self._require_target(user_id)
        if not isinstance(is_active, bool):
            raise ValidationError("Account active status must be true or false.")
        if target["active"] == is_active:
            return {field: target[field] for field in _PUBLIC_FIELDS if field in target}
        if not is_active and self._is_current_user(user_id):
            raise ValidationError("You cannot deactivate your currently signed-in account.")
        if not is_active and target["role"] == SUPER_ADMIN:
            self._require_another_active_super_admin()
        updated = self._authentication.repository.update_account(user_id, {"active": is_active})
        if updated is None:
            raise ValidationError("User account was not found.")
        return {field: updated[field] for field in _PUBLIC_FIELDS if field in updated}

    def assignable_roles(self) -> tuple[str, ...]:
        self._authorization.require(USERS_MANAGE)
        return tuple(sorted(assignable_roles(self._authorization.role)))

    def _require_assignable_role(self, role: str) -> None:
        if role not in assignable_roles(self._authorization.role):
            raise AuthorizationError("Your account cannot assign this V1 role.")

    def _require_target(self, user_id: str) -> dict[str, Any]:
        target = self._authentication.repository.find_by_id(user_id)
        if target is None:
            raise ValidationError("User account was not found.")
        if self._authorization.role == ADMIN and target["role"] not in assignable_roles(ADMIN):
            raise AuthorizationError("Admins cannot manage Super Admin or Admin accounts.")
        return target

    def _require_another_active_super_admin(self) -> None:
        if self._authentication.repository.active_super_admin_count() <= 1:
            raise ValidationError("The last active Super Admin cannot be deactivated or demoted.")

    def _is_current_user(self, user_id: str) -> bool:
        return user_id.strip().casefold() == self._current_user_id
