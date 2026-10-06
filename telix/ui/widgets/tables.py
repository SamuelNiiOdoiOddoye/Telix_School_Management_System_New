"""Table (Treeview) helpers."""

from __future__ import annotations

from tkinter import ttk
from typing import Any, Iterable, Sequence


def create_tree(parent: ttk.Frame, columns: Sequence[str], widths: Sequence[int]) -> ttk.Treeview:
    """Create a scrollable table whose headings are derived from the column names."""
    tree = ttk.Treeview(parent, columns=tuple(columns), show="headings")
    for column, width in zip(columns, widths, strict=True):
        tree.heading(column, text=column.replace("_", " ").title())
        tree.column(column, width=width, minwidth=80, anchor="w")
    vertical_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    horizontal_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
    tree.configure(
        yscrollcommand=vertical_scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set,
    )
    tree.grid(row=0, column=0, sticky="nsew")
    vertical_scrollbar.grid(row=0, column=1, sticky="ns")
    horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)
    return tree


def replace_rows(tree: ttk.Treeview, rows: Iterable[tuple[str, Sequence[Any]]]) -> None:
    """Replace the table contents with ``(row id, values)`` pairs."""
    tree.delete(*tree.get_children())
    for row_id, values in rows:
        tree.insert("", "end", iid=row_id, values=tuple(values))


def render_records(
    tree: ttk.Treeview, records: Iterable[dict[str, Any]], fields: Sequence[str]
) -> None:
    """Show ``fields`` of each record; the first field is the row id and rows without one are skipped."""
    rows = (
        (str(record[fields[0]]), [record.get(field, "") for field in fields])
        for record in records
        if record.get(fields[0])
    )
    replace_rows(tree, rows)
