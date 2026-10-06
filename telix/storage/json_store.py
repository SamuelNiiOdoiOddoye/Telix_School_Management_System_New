"""Reliable JSON persistence with automatic pre-write backups."""

from __future__ import annotations

import json
import os
import shutil
from decimal import Decimal
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from telix.core.errors import StorageError


class JsonStore:
    """Reads and writes one JSON file that contains a list of records."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    @property
    def backup_path(self) -> Path:
        return self.file_path.with_name(f"{self.file_path.stem}.backup.json")

    def load(self) -> list[dict[str, Any]]:
        if not self.file_path.exists():
            return []
        records = self._read_json()
        if not isinstance(records, list):
            raise StorageError(f"{self.file_path.name} must contain a JSON list of records.")
        return records

    def save(self, records: list[dict[str, Any]]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            self._create_backup()
            temporary_path = self._write_temporary_file(records)
            temporary_path.replace(self.file_path)
        except (OSError, TypeError) as error:
            self._discard(temporary_path)
            raise StorageError(f"Could not save {self.file_path.name}: {error}") from error

    def _read_json(self) -> Any:
        try:
            with self.file_path.open("r", encoding="utf-8") as record_file:
                return json.load(record_file)
        except json.JSONDecodeError as error:
            raise StorageError(
                f"{self.file_path.name} is not valid JSON. Restore its backup before continuing."
            ) from error
        except OSError as error:
            raise StorageError(f"Could not read {self.file_path.name}: {error}") from error

    def _create_backup(self) -> None:
        if self.file_path.exists():
            shutil.copy2(self.file_path, self.backup_path)

    def _write_temporary_file(self, records: list[dict[str, Any]]) -> Path:
        """Write ``records`` to a temp file beside the target and return its path."""
        temporary_file = NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self.file_path.parent,
            prefix=f".{self.file_path.stem}.",
            suffix=".tmp",
            delete=False,
        )
        temporary_path = Path(temporary_file.name)
        try:
            with temporary_file:
                json.dump(
                    records,
                    temporary_file,
                    indent=2,
                    ensure_ascii=False,
                    default=self._json_default,
                )
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
        except (OSError, TypeError):
            self._discard(temporary_path)
            raise
        return temporary_path

    @staticmethod
    def _json_default(value: object) -> str:
        if isinstance(value, Decimal):
            return format(value, "f")
        raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")

    @staticmethod
    def _discard(path: Path | None) -> None:
        if path and path.exists():
            path.unlink(missing_ok=True)
