"""Reliable JSON persistence with automatic pre-write backups."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


class StorageError(RuntimeError):
    """Raised when a JSON record file cannot be read or saved safely."""


class JsonStore:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    @property
    def backup_path(self) -> Path:
        return self.file_path.with_name(f"{self.file_path.stem}.backup.json")

    def load(self) -> list[dict[str, Any]]:
        if not self.file_path.exists():
            return []

        try:
            with self.file_path.open("r", encoding="utf-8") as record_file:
                records = json.load(record_file)
        except json.JSONDecodeError as error:
            raise StorageError(
                f"{self.file_path.name} is not valid JSON. Restore its backup before continuing."
            ) from error
        except OSError as error:
            raise StorageError(f"Could not read {self.file_path.name}: {error}") from error

        if not isinstance(records, list):
            raise StorageError(f"{self.file_path.name} must contain a JSON list of records.")
        return records

    def save(self, records: list[dict[str, Any]]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None

        try:
            if self.file_path.exists():
                shutil.copy2(self.file_path, self.backup_path)

            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.file_path.parent,
                prefix=f".{self.file_path.stem}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                json.dump(records, temporary_file, indent=2, ensure_ascii=False)
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
                temporary_path = Path(temporary_file.name)

            temporary_path.replace(self.file_path)
        except (OSError, TypeError) as error:
            if temporary_path and temporary_path.exists():
                temporary_path.unlink(missing_ok=True)
            raise StorageError(f"Could not save {self.file_path.name}: {error}") from error
