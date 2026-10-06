"""Write displayed tabular report data as a UTF-8 CSV file."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Sequence


def write_csv_report(
    target: Path, headers: Sequence[str], rows: Iterable[Sequence[object]]
) -> None:
    with target.open("w", newline="", encoding="utf-8-sig") as output:
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)
