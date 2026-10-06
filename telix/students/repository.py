"""Student storage."""

from __future__ import annotations

from telix.config import STUDENT_FILE
from telix.storage.json_store import JsonStore
from telix.storage.repository import JsonRecordRepository
from telix.students.normaliser import normalise_student


class StudentRepository(JsonRecordRepository):
    def __init__(self, store: JsonStore | None = None) -> None:
        super().__init__(store or JsonStore(STUDENT_FILE), normalise_student)
