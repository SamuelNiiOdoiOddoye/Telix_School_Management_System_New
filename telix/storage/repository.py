"""Generic repository: loads normalised records from a JSON store and saves them back."""

from __future__ import annotations

import builtins
from typing import Any, Callable

from telix.storage.json_store import JsonStore

Record = dict[str, Any]
Normaliser = Callable[[Record], Record]


class JsonRecordRepository:
    """Gives services a clean list of records regardless of legacy key names on disk."""

    def __init__(self, store: JsonStore, normaliser: Normaliser) -> None:
        self._store = store
        self._normaliser = normaliser

    def list(self) -> builtins.list[Record]:
        return [
            self._normaliser(record) for record in self._store.load() if isinstance(record, dict)
        ]

    def save(self, records: builtins.list[Record]) -> None:
        self._store.save(records)
