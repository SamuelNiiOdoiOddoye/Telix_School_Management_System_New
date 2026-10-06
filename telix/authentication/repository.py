"""Persistence for local Telix user accounts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from telix.authentication.roles import STUDENT, V1_ROLES
from telix.config import USERS_FILE
from telix.core.errors import StorageError, ValidationError
from telix.storage.json_store import JsonStore


class UserRepository:
    def __init__(self, store: JsonStore | None = None) -> None:
        self._store = store or JsonStore(USERS_FILE)

    def list(self) -> list[dict[str, Any]]:
        users = self._store.load()
        for user in users:
            if not isinstance(user, dict) or any(
                not isinstance(user.get(field), expected)
                for field, expected in (
                    ("user_id", str),
                    ("name", str),
                    ("email", str),
                    ("phone", str),
                    ("password_hash", str),
                    ("role", str),
                    ("active", bool),
                )
            ):
                raise StorageError("users.json contains an invalid account record.")
            if user["role"] not in V1_ROLES or (
                user["role"] == STUDENT
                and (not isinstance(user.get("student_id"), str) or not user["student_id"].strip())
            ):
                raise StorageError("users.json contains an invalid role or student link.")
        return users

    def find_by_email(self, email: str) -> dict[str, Any] | None:
        normalized = email.strip().casefold()
        return next(
            (
                user
                for user in self.list()
                if str(user.get("email", "")).strip().casefold() == normalized
            ),
            None,
        )

    def save(self, user: dict[str, Any]) -> None:
        users = self.list()
        email = str(user["email"]).casefold()
        if any(
            str(existing.get("email", "")).casefold() == email
            and existing.get("user_id") != user.get("user_id")
            for existing in users
        ):
            raise ValidationError("An account with this email already exists.")
        replaced = False
        for index, existing in enumerate(users):
            if existing.get("user_id") == user.get("user_id"):
                users[index] = user
                replaced = True
                break
        if not replaced:
            users.append(user)
        self._store.save(users)

    def has_super_admin(self) -> bool:
        return any(user.get("role") == "SUPER_ADMIN" for user in self.list())

    def active_super_admin_count(self) -> int:
        return sum(
            user.get("role") == "SUPER_ADMIN" and user.get("active") is True for user in self.list()
        )

    def find_by_id(self, user_id: str) -> dict[str, Any] | None:
        target = user_id.strip().casefold()
        return next(
            (
                user
                for user in self.list()
                if str(user.get("user_id", "")).strip().casefold() == target
            ),
            None,
        )

    def set_active(self, user_id: str, is_active: bool) -> bool:
        users = self.list()
        for user in users:
            if user.get("user_id") == user_id:
                user["active"] = is_active
                user["updated_at"] = datetime.now(timezone.utc).isoformat()
                self._store.save(users)
                return True
        return False

    def update_account(self, user_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        users = self.list()
        target = user_id.strip().casefold()
        index = next(
            (
                position
                for position, user in enumerate(users)
                if str(user.get("user_id", "")).strip().casefold() == target
            ),
            None,
        )
        if index is None:
            return None
        updated = {**users[index], **updates}
        if any(
            str(existing.get("email", "")).casefold() == str(updated["email"]).casefold()
            and existing.get("user_id") != updated.get("user_id")
            for existing in users
        ):
            raise ValidationError("An account with this email already exists.")
        updated["updated_at"] = datetime.now(timezone.utc).isoformat()
        users[index] = updated
        self._store.save(users)
        return updated
