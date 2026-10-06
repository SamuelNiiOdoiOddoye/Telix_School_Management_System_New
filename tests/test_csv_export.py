"""CSV report export tests."""

import csv
import tempfile
import unittest
from pathlib import Path

from telix.reports.csv_export import write_csv_report


class CsvExportTests(unittest.TestCase):
    def test_writes_headings_and_rows_as_utf8_csv(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "report.csv"
            write_csv_report(target, ("Name", "Amount"), (("Ama Mensah", "GHS 12.50"),))

            with target.open("r", newline="", encoding="utf-8-sig") as source:
                rows = list(csv.reader(source))

        self.assertEqual(rows, [["Name", "Amount"], ["Ama Mensah", "GHS 12.50"]])
