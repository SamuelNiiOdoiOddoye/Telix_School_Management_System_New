"""Assessment capture, grading configuration, and calculated subject grades."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from telix.academics.structure_repository import StructureKind
from telix.core.errors import StorageError, ValidationError
from telix.ui.tabs.base import BaseTab, TabContext
from telix.ui.widgets.tables import create_tree, replace_rows


class AssessmentsTab(BaseTab):
    key = "assessments"
    title = "Assessments"

    def __init__(self, notebook: ttk.Notebook, context: TabContext) -> None:
        super().__init__(notebook, context)
        self.profile_vars = {
            name: tk.StringVar()
            for name in ("academic_year", "term", "method", "components", "grade_bands")
        }
        self.score_vars = {
            name: tk.StringVar()
            for name in ("student_id", "subject", "academic_year", "term", "component", "score")
        }
        self.profile_selectors: dict[str, ttk.Combobox] = {}
        self.score_selectors: dict[str, ttk.Combobox] = {}
        self.selected_id: str | None = None
        self._build_profile_form()
        self._build_score_form()
        self._build_table()

    def _build_profile_form(self) -> None:
        frame = ttk.LabelFrame(
            self.frame, text="Grading profile (term may be blank for year default)", padding=10
        )
        frame.pack(fill="x", pady=(0, 10))
        self._add_selector(
            frame, self.profile_vars, self.profile_selectors, "academic_year", "Year", 0, 0
        )
        self._add_selector(frame, self.profile_vars, self.profile_selectors, "term", "Term", 0, 2)
        self.profile_selectors["method"] = ttk.Combobox(
            frame,
            textvariable=self.profile_vars["method"],
            values=("weighted", "unweighted"),
            state="readonly",
            width=18,
        )
        ttk.Label(frame, text="Method").grid(row=1, column=0, sticky="w")
        self.profile_selectors["method"].grid(row=1, column=1, sticky="ew", padx=(0, 10))
        ttk.Label(frame, text="Components (name=weight, comma-separated)").grid(
            row=2, column=0, sticky="w"
        )
        ttk.Entry(frame, textvariable=self.profile_vars["components"], width=50).grid(
            row=2, column=1, columnspan=3, sticky="ew", padx=(0, 10)
        )
        ttk.Label(frame, text="Bands (minimum=grade:remark; ...)").grid(row=3, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.profile_vars["grade_bands"], width=50).grid(
            row=3, column=1, columnspan=3, sticky="ew", padx=(0, 10)
        )
        ttk.Button(frame, text="Save Grading Profile", command=self.save_profile).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

    def _build_score_form(self) -> None:
        frame = ttk.LabelFrame(self.frame, text="Assessment score", padding=10)
        frame.pack(fill="x", pady=(0, 10))
        fields = (
            ("student_id", "Student ID"),
            ("subject", "Subject"),
            ("academic_year", "Academic year"),
            ("term", "Term"),
            ("component", "Component"),
            ("score", "Score (0-100)"),
        )
        for index, (name, label) in enumerate(fields):
            row, column = divmod(index, 3)
            ttk.Label(frame, text=label).grid(row=row, column=column * 2, sticky="w")
            if name in {"score"}:
                widget: ttk.Entry | ttk.Combobox = ttk.Entry(
                    frame, textvariable=self.score_vars[name], width=22
                )
            else:
                widget = ttk.Combobox(
                    frame,
                    textvariable=self.score_vars[name],
                    state="readonly",
                    width=22,
                )
                self.score_selectors[name] = widget
            widget.grid(row=row, column=column * 2 + 1, sticky="ew", padx=(4, 12))
        buttons = ttk.Frame(frame)
        buttons.grid(row=2, column=0, columnspan=6, sticky="w", pady=(8, 0))
        for index, (label, command) in enumerate(
            (
                ("Add Score", self.add),
                ("Update Selected", self.update),
                ("Delete Selected", self.delete),
                ("Calculate Grade", self.calculate_grade),
                ("Clear", self.clear_form),
            )
        ):
            ttk.Button(buttons, text=label, command=command).grid(row=0, column=index, padx=(0, 8))
        for column in (1, 3, 5):
            frame.columnconfigure(column, weight=1)

    def _build_table(self) -> None:
        columns = (
            "assessment_id",
            "student_id",
            "subject",
            "component",
            "score",
            "term",
            "academic_year",
        )
        widths = (130, 120, 170, 130, 80, 110, 130)
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill="both", expand=True)
        self.tree = create_tree(table_frame, columns, widths)
        self.tree.bind("<<TreeviewSelect>>", self._on_row_selected)

    @staticmethod
    def _add_selector(
        parent: ttk.LabelFrame,
        variables: dict[str, tk.StringVar],
        selectors: dict[str, ttk.Combobox],
        name: str,
        label: str,
        row: int,
        column: int,
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w")
        selector = ttk.Combobox(parent, textvariable=variables[name], state="readonly", width=22)
        selector.grid(row=row, column=column + 1, sticky="ew", padx=(0, 10))
        selectors[name] = selector

    def save_profile(self) -> None:
        try:
            year_id = self._selected_id(self.profile_vars["academic_year"].get())
            term_label = self.profile_vars["term"].get()
            term_id = self._selected_id(term_label) if term_label else ""
            components = self._parse_components(self.profile_vars["components"].get())
            bands = self._parse_bands(self.profile_vars["grade_bands"].get())
        except (ValueError, ValidationError) as error:
            self.context.feedback.error(str(error))
            return
        services = self.context.services
        self.context.runner.run(
            lambda: services.assessments.configure(
                year_id,
                term_id,
                self.profile_vars["method"].get(),
                components,
                bands,
            ),
            "Grading profile saved.",
            self.context.refresh_all,
        )

    def add(self) -> None:
        self._save_assessment("add")

    def update(self) -> None:
        if not self.selected_id:
            self.context.feedback.error("Select an assessment from the table before updating.")
            return
        self._save_assessment("update")

    def delete(self) -> None:
        if not self.selected_id:
            self.context.feedback.error("Select an assessment from the table before deleting.")
            return
        if not self.context.feedback.confirm("Delete Assessment", "Delete the selected score?"):
            return
        assessment_id = self.selected_id
        self.context.runner.run(
            lambda: self.context.services.assessments.delete(assessment_id),
            "Assessment deleted.",
            self._after_change,
        )

    def _save_assessment(self, action: str) -> None:
        try:
            values = self._score_values()
        except ValueError as error:
            self.context.feedback.error(str(error))
            return
        service = self.context.services.assessments
        if action == "add":

            def operation() -> Any:
                return service.add(values)

            message = "Assessment score added."
        else:
            assessment_id = self.selected_id

            def operation() -> Any:
                return service.update(assessment_id or "", values)

            message = "Assessment score updated."
        self.context.runner.run(operation, message, self._after_change)

    def calculate_grade(self) -> None:
        try:
            values = self._score_values()
            result = self.context.services.assessments.grade(
                values["student_id"],
                values["subject_id"],
                values["academic_year_id"],
                values["term_id"],
            )
        except (StorageError, ValidationError, ValueError) as error:
            self.context.feedback.error(str(error))
            return
        self.context.feedback.success(
            f"Calculated score: {result['score']} · Grade: {result['grade']} · "
            f"{result['remark']} ({result['method']})."
        )

    def _score_values(self) -> dict[str, str]:
        result = {name: variable.get().strip() for name, variable in self.score_vars.items()}
        for name in ("subject", "academic_year", "term"):
            result[f"{name}_id"] = self._selected_id(result[name])
        return result

    def _on_row_selected(self, _: tk.Event[Any]) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        record = next(
            (
                item
                for item in self.context.services.assessments.list()
                if item["assessment_id"] == selection[0]
            ),
            None,
        )
        if record is None:
            return
        self.selected_id = record["assessment_id"]
        self.score_vars["student_id"].set(record["student_id"])
        self.score_vars["subject"].set(
            self._label("subject", record["subject_id"], record["subject"])
        )
        self.score_vars["academic_year"].set(
            self._label("academic_year", record["academic_year_id"], record["academic_year"])
        )
        self.score_vars["term"].set(self._label("term", record["term_id"], record["term"]))
        self.score_vars["component"].set(record["component"])
        self.score_vars["score"].set(str(record["score"]))

    def clear_form(self) -> None:
        self.selected_id = None
        for variable in self.score_vars.values():
            variable.set("")

    def _after_change(self) -> None:
        self.clear_form()
        self.context.refresh_all()

    def _label(self, kind: StructureKind, entity_id: str, fallback: str) -> str:
        entity = self.context.services.academic_structure.get(kind, entity_id)
        return f"{entity['name']} [{entity_id}]" if entity else fallback

    @staticmethod
    def _selected_id(value: str) -> str:
        if " [" in value and value.endswith("]"):
            return value.rsplit(" [", 1)[1][:-1]
        if not value:
            raise ValueError("Select the required academic catalog record.")
        return value

    @staticmethod
    def _parse_components(value: str) -> list[dict[str, str]]:
        result = []
        for item in value.split(","):
            if not item.strip():
                continue
            name, separator, weight = item.partition("=")
            if not separator:
                raise ValueError("Components must use name=weight, for example Coursework=40.")
            result.append({"name": name.strip(), "weight": weight.strip()})
        return result

    @staticmethod
    def _parse_bands(value: str) -> list[dict[str, str]]:
        result = []
        for item in value.split(";"):
            if not item.strip():
                continue
            minimum, separator, description = item.partition("=")
            grade, separator_grade, remark = description.partition(":")
            if not separator or not separator_grade:
                raise ValueError(
                    "Grade bands must use minimum=grade:remark, separated by semicolons."
                )
            result.append(
                {"minimum": minimum.strip(), "grade": grade.strip(), "remark": remark.strip()}
            )
        return result

    def refresh(self) -> None:
        try:
            services = self.context.services
            structure = services.academic_structure
            subjects = structure.list("subject")
            years = structure.list("academic_year")
            terms = structure.list("term")
            students = services.students.list()
            subject_options = [f"{item['name']} [{item['subject_id']}]" for item in subjects]
            year_options = [f"{item['name']} [{item['academic_year_id']}]" for item in years]
            term_options = [f"{item['name']} [{item['term_id']}]" for item in terms]
            student_options = [item["student_id"] for item in students]
            self.profile_selectors["academic_year"]["values"] = year_options
            self.profile_selectors["term"]["values"] = ["", *term_options]
            self.score_selectors["subject"]["values"] = subject_options
            self.score_selectors["academic_year"]["values"] = year_options
            self.score_selectors["term"]["values"] = term_options
            self.score_selectors["student_id"]["values"] = student_options
            for name in ("academic_year", "term"):
                self.score_selectors[name].bind(
                    "<<ComboboxSelected>>",
                    lambda _event: self._refresh_component_choices(),
                )
            self._refresh_component_choices()
            records = services.assessments.list()
            replace_rows(
                self.tree,
                (
                    (
                        record["assessment_id"],
                        (
                            record["assessment_id"],
                            record["student_id"],
                            record["subject"],
                            record["component"],
                            record["score"],
                            record["term"],
                            record["academic_year"],
                        ),
                    )
                    for record in records
                ),
            )
        except StorageError as error:
            self.context.feedback.error(str(error))

    def _refresh_component_choices(self) -> None:
        year_label = self.score_vars["academic_year"].get()
        term_label = self.score_vars["term"].get()
        if not year_label or not term_label:
            self.score_selectors["component"]["values"] = ()
            return
        year_id = self._selected_id(year_label)
        term_id = self._selected_id(term_label)
        profiles = self.context.services.assessments.profiles()
        profile = next(
            (
                item
                for item in profiles
                if item["academic_year_id"].casefold() == year_id.casefold()
                and item.get("term_id", "").casefold() == term_id.casefold()
            ),
            None,
        )
        if profile is None:
            profile = next(
                (
                    item
                    for item in profiles
                    if item["academic_year_id"].casefold() == year_id.casefold()
                    and not item.get("term_id")
                ),
                None,
            )
        self.score_selectors["component"]["values"] = (
            [item["name"] for item in profile["components"]] if profile else []
        )
