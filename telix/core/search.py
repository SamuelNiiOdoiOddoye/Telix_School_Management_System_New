"""Small, ID-first lookup helpers that work on lists of records."""

from __future__ import annotations

from typing import Any, Iterable


def _normalise_key(value: object) -> str:
    return str(value).strip().casefold()


def find_index_by_id(
    records: Iterable[dict[str, Any]], field_name: str, record_id: str
) -> int | None:
    """Return the position of the record whose ``field_name`` equals ``record_id``."""
    target = _normalise_key(record_id)
    for index, record in enumerate(records):
        if _normalise_key(record.get(field_name, "")) == target:
            return index
    return None


def find_by_id(
    records: Iterable[dict[str, Any]], field_name: str, record_id: str
) -> dict[str, Any] | None:
    """Return the record whose ``field_name`` equals ``record_id`` (case-insensitive)."""
    records = list(records)
    index = find_index_by_id(records, field_name, record_id)
    return None if index is None else records[index]


def filter_by_class(records: Iterable[dict[str, Any]], class_name: str) -> list[dict[str, Any]]:
    """Return records in ``class_name``; an empty ``class_name`` returns everything."""
    target = _normalise_key(class_name)
    if not target:
        return list(records)
    return [record for record in records if _normalise_key(record.get("class_name", "")) == target]
