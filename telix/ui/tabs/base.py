"""Shared plumbing for notebook tabs."""

from __future__ import annotations

from dataclasses import dataclass
from tkinter import ttk
from typing import Callable

from telix.services.container import Services
from telix.ui.feedback import Feedback
from telix.ui.operations import OperationRunner


@dataclass(frozen=True)
class TabContext:
    """Everything a tab needs from the application, passed in rather than reached for."""

    services: Services
    feedback: Feedback
    runner: OperationRunner
    refresh_all: Callable[[], None]
    navigate: Callable[[str], None]


class BaseTab:
    """A tab owns its frame, its widgets and the handlers for its own buttons."""

    key = ""
    title = ""
    padding = 12

    def __init__(self, notebook: ttk.Notebook, context: TabContext) -> None:
        self.context = context
        self.frame = ttk.Frame(notebook, padding=self.padding)

    def refresh(self) -> None:
        """Reload this tab's data from the services."""
        raise NotImplementedError
