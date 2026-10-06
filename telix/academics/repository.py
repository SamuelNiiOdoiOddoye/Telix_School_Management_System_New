"""Academic record storage."""

from __future__ import annotations

from telix.academics.normaliser import normalise_academic_record
from telix.config import ACADEMIC_FILE
from telix.storage.json_store import JsonStore
from telix.storage.repository import JsonRecordRepository


class AcademicRepository(JsonRecordRepository):
    def __init__(self, store: JsonStore | None = None) -> None:
        super().__init__(store or JsonStore(ACADEMIC_FILE), normalise_academic_record)
