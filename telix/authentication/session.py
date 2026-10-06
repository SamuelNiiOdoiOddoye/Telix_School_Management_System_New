"""In-memory authenticated session for the local desktop application."""

from __future__ import annotations

from telix.authentication.service import AuthenticatedUser


class UserSession:
    def __init__(self) -> None:
        self._user: AuthenticatedUser | None = None

    @property
    def user(self) -> AuthenticatedUser | None:
        return self._user

    @property
    def authenticated(self) -> bool:
        return self._user is not None

    def start(self, user: AuthenticatedUser) -> None:
        if user.role != "SUPER_ADMIN":
            raise ValueError("Only a Super Admin can start the V1 desktop session.")
        self._user = user

    def clear(self) -> None:
        self._user = None
