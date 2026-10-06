"""Teacher storage."""

from __future__ import annotations

from telix.config import TEACHER_FILE
from telix.storage.json_store import JsonStore
from telix.storage.repository import JsonRecordRepository
from telix.teachers.normaliser import normalise_teacher


class TeacherRepository(JsonRecordRepository):
    def __init__(self, store: JsonStore | None = None) -> None:
        super().__init__(store or JsonStore(TEACHER_FILE), normalise_teacher)
