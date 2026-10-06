"""Shared attendance status definitions."""

from typing import Final

ATTENDANCE_STATUSES: Final[tuple[str, ...]] = ("Present", "Absent", "Late", "Excused")
ATTENDED_STATUSES: Final[frozenset[str]] = frozenset({"Present", "Late"})
