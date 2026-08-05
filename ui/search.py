"""Small, ID-first search helpers."""

from __future__ import annotations

from typing import Any, Iterable


def find_by_id(
    records: Iterable[dict[str, Any]], field_name: str, record_id: str
) -> dict[str, Any] | None:
    target = record_id.strip().casefold()
    return next(
        (
            record
            for record in records
            if str(record.get(field_name, "")).strip().casefold() == target
        ),
        None,
    )


def filter_by_class(records: Iterable[dict[str, Any]], class_name: str) -> list[dict[str, Any]]:
    target = class_name.strip().casefold()
    if not target:
        return list(records)
    return [
        record
        for record in records
        if str(record.get("class_name", "")).strip().casefold() == target
    ]
