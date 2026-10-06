import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from telix.core.errors import StorageError
from telix.storage.json_store import JsonStore


class JsonStoreTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "records.json"
        self.store = JsonStore(self.path)

    def test_missing_file_loads_empty_list(self):
        self.assertEqual(self.store.load(), [])

    def test_round_trip_and_backup_of_previous_version(self):
        self.store.save([{"a": 1}])
        self.assertFalse(self.store.backup_path.exists())
        self.store.save([{"a": 2}])
        self.assertEqual(self.store.load(), [{"a": 2}])
        self.assertEqual(json.loads(self.store.backup_path.read_text("utf-8")), [{"a": 1}])

    def test_decimal_round_trip_uses_exact_json_string(self):
        self.store.save([{"amount": Decimal("0.30")}])
        self.assertEqual(self.store.load(), [{"amount": "0.30"}])
        self.assertIn('"0.30"', self.path.read_text("utf-8"))

    def test_no_temp_files_left_behind(self):
        self.store.save([{"a": 1}])
        self.assertEqual([p.name for p in self.path.parent.glob(".*.tmp")], [])

    def test_unserialisable_data_raises_and_cleans_up(self):
        self.store.save([{"a": 1}])
        with self.assertRaises(StorageError):
            self.store.save([{"a": object()}])
        self.assertEqual(self.store.load(), [{"a": 1}])
        self.assertEqual([p.name for p in self.path.parent.glob(".*.tmp")], [])

    def test_invalid_json_and_wrong_shape(self):
        self.path.write_text("{not json", encoding="utf-8")
        with self.assertRaisesRegex(StorageError, "not valid JSON"):
            self.store.load()
        self.path.write_text('{"a": 1}', encoding="utf-8")
        with self.assertRaisesRegex(StorageError, "JSON list"):
            self.store.load()
