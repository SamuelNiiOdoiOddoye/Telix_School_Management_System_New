"""Form building helpers."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Mapping, Sequence

FieldSpec = tuple[str, str]  # (field name, label)
ButtonSpec = tuple[str, Callable[[], None]]  # (text, command)
FIELDS_PER_ROW = 3


def add_form_field(
    parent: ttk.LabelFrame,
    label: str,
    variable: tk.StringVar,
    row: int,
    column: int,
    choices: tuple[str, ...] | None = None,
) -> None:
    ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", padx=(0, 6), pady=5)
    if choices:
        widget: ttk.Entry | ttk.Combobox = ttk.Combobox(
            parent, textvariable=variable, values=choices, state="readonly", width=24
        )
    else:
        widget = ttk.Entry(parent, textvariable=variable, width=27)
    widget.grid(row=row, column=column + 1, sticky="ew", padx=(0, 14), pady=5)
    parent.columnconfigure(column + 1, weight=1)


def build_form_fields(
    parent: ttk.LabelFrame,
    fields: Sequence[FieldSpec],
    variables: Mapping[str, tk.StringVar],
    choices: Mapping[str, tuple[str, ...]] | None = None,
) -> int:
    """Lay out ``fields`` in a grid; returns the number of rows used."""
    choices = choices or {}
    for index, (field_name, label) in enumerate(fields):
        add_form_field(
            parent,
            label,
            variables[field_name],
            index // FIELDS_PER_ROW,
            (index % FIELDS_PER_ROW) * 2,
            choices=choices.get(field_name),
        )
    return -(-len(fields) // FIELDS_PER_ROW)


def add_button_row(
    parent: ttk.LabelFrame, buttons: Sequence[ButtonSpec], row: int, columnspan: int = 6
) -> ttk.Frame:
    frame = ttk.Frame(parent)
    frame.grid(row=row, column=0, columnspan=columnspan, sticky="w", pady=(12, 0))
    for index, (text, command) in enumerate(buttons):
        padding = (0, 8) if index < len(buttons) - 1 else 0
        ttk.Button(frame, text=text, command=command).grid(row=0, column=index, padx=padding)
    return frame


def add_search_entry(
    parent: ttk.Frame, label: str, variable: tk.StringVar, column: int = 0
) -> None:
    ttk.Label(parent, text=label).grid(row=0, column=column, sticky="w")
    ttk.Entry(parent, textvariable=variable, width=24).grid(row=0, column=column + 1, padx=(6, 8))
