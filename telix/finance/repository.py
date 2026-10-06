"""JSON persistence for student payments and school expenses."""

from __future__ import annotations

import builtins
from datetime import date
from typing import Any, Literal

from telix.config import EXPENSE_FILE, PAYMENT_FILE
from telix.core.errors import StorageError
from telix.core.numbers import parse_amount
from telix.storage.json_store import JsonStore

LedgerKind = Literal["payment", "expense"]
ID_FIELDS: dict[LedgerKind, str] = {"payment": "payment_id", "expense": "expense_id"}


class FinanceRepository:
    def __init__(self, stores: dict[LedgerKind, JsonStore] | None = None) -> None:
        self._stores = stores or {
            "payment": JsonStore(PAYMENT_FILE),
            "expense": JsonStore(EXPENSE_FILE),
        }

    def list(self, kind: LedgerKind) -> builtins.list[dict[str, Any]]:
        store = self._stores[kind]
        records = store.load()
        if any(not isinstance(record, dict) for record in records):
            raise StorageError(f"{store.file_path.name} must contain only JSON object records.")
        seen_ids: set[str] = set()
        for record in records:
            record_id = record.get(ID_FIELDS[kind])
            if not isinstance(record_id, str) or not record_id.strip():
                raise StorageError(f"{store.file_path.name} contains a record without an ID.")
            normalized_id = record_id.strip().casefold()
            if normalized_id in seen_ids:
                raise StorageError(f"{store.file_path.name} contains duplicate record IDs.")
            seen_ids.add(normalized_id)
            if kind == "payment":
                date_field = "payment_date"
                required_fields: tuple[str, ...] = ("student_id", "payment_date", "amount")
            else:
                date_field = "expense_date"
                required_fields = ("expense_date", "category", "description", "amount")
            if any(
                not isinstance(record.get(field), str) or not record[field].strip()
                for field in required_fields
            ):
                raise StorageError(f"{store.file_path.name} contains an incomplete record.")
            try:
                stored_date = record[date_field]
                parsed_date = date.fromisoformat(stored_date)
            except (TypeError, ValueError) as error:
                raise StorageError(
                    f"{store.file_path.name} contains an invalid record date."
                ) from error
            amount = parse_amount(record["amount"])
            if parsed_date.isoformat() != stored_date or amount is None or amount <= 0:
                raise StorageError(f"{store.file_path.name} contains an invalid financial record.")
        return records

    def save(self, kind: LedgerKind, records: builtins.list[dict[str, Any]]) -> None:
        self._stores[kind].save(records)
