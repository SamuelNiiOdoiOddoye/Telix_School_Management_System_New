"""Application shell: window, tab registry and start-up."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from telix.core.errors import StorageError
from telix.services.container import Services, build_services
from telix.ui.feedback import Feedback
from telix.ui.operations import OperationRunner
from telix.ui.tabs.academics import AcademicsTab
from telix.ui.tabs.academic_setup import AcademicSetupTab
from telix.ui.tabs.base import BaseTab, TabContext
from telix.ui.tabs.dashboard import DashboardTab
from telix.ui.tabs.finance import FinanceTab
from telix.ui.tabs.reports import ReportsTab
from telix.ui.tabs.students import StudentsTab
from telix.ui.tabs.teachers import TeachersTab
from telix.ui.theme import configure_style
from telix.ui.window import apply_window_icon

# Tab order in the notebook. Add a new tab by adding its class here.
TAB_CLASSES: tuple[type[BaseTab], ...] = (
    DashboardTab,
    StudentsTab,
    TeachersTab,
    AcademicsTab,
    AcademicSetupTab,
    ReportsTab,
    FinanceTab,
)


class SchoolManagementSystem:
    def __init__(self, master: tk.Tk, services: Services | None = None) -> None:
        self.master = master
        self.master.title("Telix School Management System V1")
        self.master.geometry("1200x780")
        self.master.minsize(1080, 680)
        self._icon_image = apply_window_icon(master)
        configure_style(master)

        feedback = Feedback(master)
        self._feedback = feedback
        self._context = TabContext(
            services=services or build_services(),
            feedback=feedback,
            runner=OperationRunner(feedback),
            refresh_all=self.refresh_all,
            navigate=self.show_tab,
        )
        self.tabs: dict[str, BaseTab] = {}
        self._build_header_and_tabs()
        self.refresh_all()

    def _build_header_and_tabs(self) -> None:
        container = ttk.Frame(self.master, padding=16)
        container.pack(fill="both", expand=True)
        ttk.Label(container, text="Telix School Management System", style="Title.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            container,
            text="V1 · Student, teacher, academic, finance, and reporting workspace",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 12))
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)
        for tab_class in TAB_CLASSES:
            tab = tab_class(self.notebook, self._context)
            self.tabs[tab.key] = tab
            self.notebook.add(tab.frame, text=tab.title)

    def show_tab(self, key: str) -> None:
        self.notebook.select(self.tabs[key].frame)

    def refresh_all(self) -> None:
        try:
            for tab in self.tabs.values():
                tab.refresh()
        except StorageError as error:
            self._feedback.error(str(error))


def main() -> None:
    from telix.logging_config import configure_logging

    configure_logging()
    root = tk.Tk()
    SchoolManagementSystem(root)
    root.mainloop()
