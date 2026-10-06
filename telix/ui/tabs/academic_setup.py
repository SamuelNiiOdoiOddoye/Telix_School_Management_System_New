"""Manage academic catalogs and effective-dated student class enrollment."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Any

from telix.academics.structure_repository import StructureKind
from telix.core.errors import StorageError
from telix.ui.tabs.base import BaseTab, TabContext
from telix.ui.widgets.forms import add_button_row, add_form_field
from telix.ui.widgets.tables import create_tree, render_records

Field = tuple[str, str]


@dataclass
class Editor:
    kind: StructureKind
    fields: tuple[Field, ...]
    id_field: str
    tree: ttk.Treeview
    variables: dict[str, tk.StringVar]
    selectors: dict[str, ttk.Combobox]
    selected_id: str | None = None


EDITOR_DEFINITIONS: dict[
    StructureKind, tuple[str, tuple[Field, ...], tuple[str, ...], tuple[int, ...]]
] = {
    "class": (
        "Classes",
        (("name", "Class name"),),
        ("class_id", "name"),
        (160, 260),
    ),
    "subject": (
        "Subjects",
        (("name", "Subject name"), ("code", "Subject code (optional)")),
        ("subject_id", "name", "code"),
        (160, 240, 160),
    ),
    "academic_year": (
        "Academic years",
        (
            ("name", "Name"),
            ("start_date", "Start date (YYYY-MM-DD)"),
            ("end_date", "End date (YYYY-MM-DD)"),
        ),
        ("academic_year_id", "name", "start_date", "end_date"),
        (160, 180, 160, 160),
    ),
    "term": (
        "Terms",
        (
            ("academic_year_id", "Academic year"),
            ("name", "Term name"),
            ("start_date", "Start date (YYYY-MM-DD)"),
            ("end_date", "End date (YYYY-MM-DD)"),
        ),
        ("term_id", "academic_year_id", "name", "start_date", "end_date"),
        (150, 160, 150, 150, 150),
    ),
    "enrollment": (
        "Enrollments",
        (
            ("student_id", "Student ID"),
            ("academic_year_id", "Academic year"),
            ("class_id", "Class"),
            ("start_date", "Start / transition date (YYYY-MM-DD)"),
            ("end_date", "End date (optional)"),
            ("status", "Status"),
        ),
        (
            "enrollment_id",
            "student_id",
            "academic_year_id",
            "class_id",
            "start_date",
            "end_date",
            "status",
        ),
        (160, 140, 160, 140, 140, 140, 120),
    ),
}


class AcademicSetupTab(BaseTab):
    key = "academic_setup"
    title = "Academic Setup"

    def __init__(self, notebook: ttk.Notebook, context: TabContext) -> None:
        super().__init__(notebook, context)
        self.editors: dict[StructureKind, Editor] = {}
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True)
        for kind, (title, fields, columns, widths) in EDITOR_DEFINITIONS.items():
            self._build_editor(kind, title, fields, columns, widths)

    def _build_editor(
        self,
        kind: StructureKind,
        title: str,
        fields: tuple[Field, ...],
        columns: tuple[str, ...],
        widths: tuple[int, ...],
    ) -> None:
        page = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(page, text=title)
        variables = {name: tk.StringVar() for name, _ in fields}
        selectors: dict[str, ttk.Combobox] = {}
        form = ttk.LabelFrame(page, text=f"{self._noun(kind)} details", padding=12)
        form.pack(fill="x")
        for index, (name, label) in enumerate(fields):
            row, column = divmod(index, 3)
            if name in {"academic_year_id", "class_id", "student_id"}:
                add_form_field(form, label, variables[name], row, column * 2, ("",))
                widget = form.grid_slaves(row=row, column=column * 2 + 1)[0]
                if isinstance(widget, ttk.Combobox):
                    selectors[name] = widget
            elif name == "status":
                add_form_field(
                    form,
                    label,
                    variables[name],
                    row,
                    column * 2,
                    ("active", "completed", "withdrawn", "transferred"),
                )
            else:
                add_form_field(form, label, variables[name], row, column * 2)
        button_row = -(-len(fields) // 3)

        def add_selected(selected_kind: StructureKind = kind) -> None:
            self.add(selected_kind)

        def update_selected(selected_kind: StructureKind = kind) -> None:
            self.update(selected_kind)

        def delete_selected(selected_kind: StructureKind = kind) -> None:
            self.delete(selected_kind)

        def clear_selected(selected_kind: StructureKind = kind) -> None:
            self.clear(selected_kind)

        add_button_row(
            form,
            (
                ("Add", add_selected),
                ("Update Selected", update_selected),
                ("Delete Selected", delete_selected),
                ("Clear", clear_selected),
            ),
            row=button_row,
        )
        if kind == "enrollment":
            transition_buttons = ttk.Frame(form)
            transition_buttons.grid(
                row=button_row + 1, column=0, columnspan=6, sticky="w", pady=(8, 0)
            )
            ttk.Button(
                transition_buttons,
                text="Transfer / Promote",
                command=self.transfer_or_promote,
            ).grid(row=0, column=0, padx=(0, 8))
            ttk.Button(
                transition_buttons,
                text="Withdraw on selected date",
                command=self.withdraw,
            ).grid(row=0, column=1)
        tree_frame = ttk.Frame(page)
        tree_frame.pack(fill="both", expand=True, pady=(12, 0))
        tree = create_tree(tree_frame, columns, widths)

        def select_row(_event: tk.Event[Any], selected_kind: StructureKind = kind) -> None:
            self._on_select(selected_kind)

        tree.bind("<<TreeviewSelect>>", select_row)
        self.editors[kind] = Editor(
            kind=kind,
            fields=fields,
            id_field=columns[0],
            tree=tree,
            variables=variables,
            selectors=selectors,
        )

    def add(self, kind: StructureKind) -> None:
        editor = self.editors[kind]
        self.context.runner.run(
            lambda: self.context.services.academic_structure.add(kind, self._form_values(editor)),
            f"{self._noun(kind)} added successfully.",
            self._after_change,
        )

    def update(self, kind: StructureKind) -> None:
        editor = self.editors[kind]
        if not editor.selected_id:
            self.context.feedback.error(f"Select a {self._noun(kind).lower()} before updating it.")
            return
        selected_id = editor.selected_id
        self.context.runner.run(
            lambda: self.context.services.academic_structure.update(
                kind, selected_id, self._form_values(editor)
            ),
            f"{self._noun(kind)} updated successfully.",
            self._after_change,
        )

    def delete(self, kind: StructureKind) -> None:
        editor = self.editors[kind]
        if not editor.selected_id:
            self.context.feedback.error(f"Select a {self._noun(kind).lower()} before deleting it.")
            return
        if not self.context.feedback.confirm(
            f"Delete {self._noun(kind)}",
            f"Delete the selected {self._noun(kind).lower()}?",
        ):
            return
        selected_id = editor.selected_id
        self.context.runner.run(
            lambda: self.context.services.academic_structure.delete(kind, selected_id),
            f"{self._noun(kind)} deleted successfully.",
            self._after_change,
        )

    def clear(self, kind: StructureKind) -> None:
        editor = self.editors[kind]
        editor.selected_id = None
        for variable in editor.variables.values():
            variable.set("")

    def transfer_or_promote(self) -> None:
        editor = self.editors["enrollment"]
        values = self._form_values(editor)
        services = self.context.services.academic_structure
        self.context.runner.run(
            lambda: services.transfer_or_promote(
                values["student_id"],
                values["class_id"],
                values["academic_year_id"],
                values["start_date"],
            ),
            "Student enrollment transferred or promoted successfully.",
            self._after_change,
        )

    def withdraw(self) -> None:
        editor = self.editors["enrollment"]
        values = self._form_values(editor)
        services = self.context.services.academic_structure
        self.context.runner.run(
            lambda: services.withdraw(values["student_id"], values["start_date"]),
            "Student withdrawal recorded successfully.",
            self._after_change,
        )

    def _form_values(self, editor: Editor) -> dict[str, str]:
        values = {name: variable.get().strip() for name, variable in editor.variables.items()}
        for field, selector in editor.selectors.items():
            value = selector.get()
            values[field] = self._reference_id(value)
        return values

    @staticmethod
    def _reference_id(value: str) -> str:
        if " [" in value and value.endswith("]"):
            return value.rsplit(" [", 1)[1][:-1]
        return value

    def _on_select(self, kind: StructureKind) -> None:
        editor = self.editors[kind]
        selection = editor.tree.selection()
        if not selection:
            return
        try:
            records = self.context.services.academic_structure.list(kind)
            selected_id = selection[0]
            selected = next(
                (item for item in records if item.get(editor.id_field) == selected_id), None
            )
            if selected is None:
                return
            editor.selected_id = selected_id
            for field, variable in editor.variables.items():
                value = str(selected.get(field, ""))
                if field in editor.selectors:
                    value = self._reference_label(field, value)
                variable.set(value)
        except StorageError as error:
            self.context.feedback.error(str(error))

    def _reference_label(self, field: str, entity_id: str) -> str:
        if field == "class_id":
            records = self.context.services.academic_structure.list("class")
            id_field = "class_id"
        elif field == "student_id":
            records = self.context.services.students.list()
            id_field = "student_id"
        else:
            records = self.context.services.academic_structure.list("academic_year")
            id_field = "academic_year_id"
        record = next((item for item in records if item.get(id_field) == entity_id), None)
        if record is None:
            return entity_id
        return f"{record.get('name', entity_id)} [{entity_id}]"

    def _refresh_selectors(self) -> None:
        options: dict[str, list[str]] = {}
        selector_sources: tuple[tuple[StructureKind, str, str], ...] = (
            ("class", "class_id", "class_id"),
            ("academic_year", "academic_year_id", "academic_year_id"),
        )
        for kind, field, id_field in selector_sources:
            records = self.context.services.academic_structure.list(kind)
            options[field] = [
                f"{record['name']} [{record[id_field]}]"
                for record in records
                if record.get("name") and record.get(id_field)
            ]
        options["student_id"] = [
            f"{record.get('name', entity_id)} [{entity_id}]"
            for record in self.context.services.students.list()
            if (entity_id := record.get("student_id"))
        ]
        for editor in self.editors.values():
            for field, selector in editor.selectors.items():
                selector["values"] = options[field]

    def _after_change(self) -> None:
        for kind in self.editors:
            self.clear(kind)
        self.context.refresh_all()

    def refresh(self) -> None:
        self._refresh_selectors()
        for kind, editor in self.editors.items():
            records = self.context.services.academic_structure.list(kind)
            render_records(editor.tree, records, self._columns(kind))
            if not editor.selected_id:
                self.clear(kind)

    @staticmethod
    def _columns(kind: StructureKind) -> tuple[str, ...]:
        return EDITOR_DEFINITIONS[kind][2]

    @staticmethod
    def _noun(kind: StructureKind) -> str:
        return {
            "class": "Class",
            "subject": "Subject",
            "academic_year": "Academic year",
            "term": "Term",
            "enrollment": "Enrollment",
        }[kind]
