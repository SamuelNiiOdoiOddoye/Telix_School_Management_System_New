"""Application shell: window, tab registry and start-up."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from telix.authentication.service import AuthenticatedUser, AuthenticationService
from telix.authentication.session import UserSession
from telix.authentication.roles import ADMIN, FINANCE_OFFICER, STUDENT, SUPER_ADMIN, TEACHER
from telix.core.errors import AuthorizationError, StorageError
from telix.services.container import Services, build_services
from telix.ui.feedback import Feedback
from telix.ui.login import LoginScreen
from telix.ui.operations import OperationRunner
from telix.ui.tabs.academics import AcademicsTab
from telix.ui.tabs.assessments import AssessmentsTab
from telix.ui.tabs.academic_setup import AcademicSetupTab
from telix.ui.tabs.attendance import AttendanceTab
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
    AssessmentsTab,
    AcademicSetupTab,
    AttendanceTab,
    ReportsTab,
    FinanceTab,
)


class SchoolManagementSystem:
    def __init__(
        self,
        master: tk.Tk,
        services: Services | None,
        session: UserSession,
        on_logout: Callable[[], None],
    ) -> None:
        if not session.authenticated:
            raise ValueError("An authenticated session is required to open Telix.")
        user = session.user
        assert user is not None
        self.master = master
        self.session = session
        self._on_logout = on_logout
        self.master.title("Telix School Management System V1")
        self.master.geometry("1200x780")
        self.master.minsize(1080, 680)
        self._icon_image = apply_window_icon(master)
        configure_style(master)

        feedback = Feedback(master)
        self._feedback = feedback
        active_services = services or build_services(user)
        if (
            active_services.authorization.role != user.role
            or active_services.authorization.student_id.casefold() != user.student_id.casefold()
        ):
            raise ValueError("Application services must match the authenticated account.")
        self._context = TabContext(
            services=active_services,
            feedback=feedback,
            runner=OperationRunner(feedback),
            refresh_all=self.refresh_all,
            navigate=self.show_tab,
        )
        self.tabs: dict[str, BaseTab] = {}
        self._build_header_and_tabs()
        self.refresh_all()

    def _build_header_and_tabs(self) -> None:
        user = self.session.user
        assert user is not None
        self._container = ttk.Frame(self.master, padding=16)
        self._container.pack(fill="both", expand=True)
        header = ttk.Frame(self._container)
        header.pack(fill="x")
        heading = ttk.Frame(header)
        heading.pack(side="left", fill="x", expand=True)
        ttk.Label(heading, text="Telix School Management System", style="Title.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            heading,
            text=f"V1 · {user.role.replace('_', ' ').title()} workspace",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 12))
        ttk.Button(
            header,
            text=f"Log out ({user.name})",
            command=self.logout,
        ).pack(side="right", anchor="n")
        self.notebook = ttk.Notebook(self._container)
        self.notebook.pack(fill="both", expand=True)
        visible_roles: dict[str, set[str]] = {
            "dashboard": {SUPER_ADMIN, ADMIN, TEACHER, FINANCE_OFFICER, STUDENT},
            "students": {SUPER_ADMIN, ADMIN, TEACHER},
            "teachers": {SUPER_ADMIN, ADMIN},
            "academics": {SUPER_ADMIN, ADMIN, TEACHER},
            "assessments": {SUPER_ADMIN, ADMIN, TEACHER},
            "academic_setup": {SUPER_ADMIN, ADMIN},
            "attendance": {SUPER_ADMIN, ADMIN, TEACHER},
            "reports": {SUPER_ADMIN, ADMIN, TEACHER, FINANCE_OFFICER, STUDENT},
            "finance": {SUPER_ADMIN, ADMIN, FINANCE_OFFICER},
        }
        for tab_class in TAB_CLASSES:
            if user.role not in visible_roles.get(tab_class.key, set()):
                continue
            tab = tab_class(self.notebook, self._context)
            self.tabs[tab.key] = tab
            self.notebook.add(tab.frame, text=tab.title)

    def show_tab(self, key: str) -> None:
        self.notebook.select(self.tabs[key].frame)

    def refresh_all(self) -> None:
        try:
            for tab in self.tabs.values():
                tab.refresh()
        except (StorageError, AuthorizationError) as error:
            self._feedback.error(str(error))

    def logout(self) -> None:
        self.session.clear()
        self._container.destroy()
        self._on_logout()


class ApplicationController:
    """Own the transition between the public login screen and protected workspace."""

    def __init__(
        self,
        master: tk.Tk,
        authentication: AuthenticationService,
        services_factory: Callable[[], Services] | None = None,
    ) -> None:
        self.master = master
        self.authentication = authentication
        self.services_factory = services_factory
        self.active_app: SchoolManagementSystem | None = None
        self.login_screen: LoginScreen | None = None
        configure_style(master)
        master.geometry("720x480")
        master.minsize(520, 400)

    def start(self) -> None:
        self.show_login()

    def show_login(self) -> None:
        self.active_app = None
        self.master.title("Telix School Management System · Log in")
        self.master.geometry("720x480")
        self.master.minsize(520, 400)
        self.login_screen = LoginScreen(self.master, self.authentication, self.show_application)

    def show_application(self, user: AuthenticatedUser) -> None:
        self.login_screen = None
        session = UserSession()
        session.start(user)
        services = (
            self.services_factory() if self.services_factory is not None else build_services(user)
        )
        self.master.title("Telix School Management System V1")
        self.master.geometry("1200x780")
        self.master.minsize(1080, 680)
        self.active_app = SchoolManagementSystem(
            self.master,
            services,
            session,
            self.show_login,
        )


def main() -> None:
    from telix.logging_config import configure_logging
    from telix.services.container import build_services

    configure_logging()
    root = tk.Tk()
    from telix.authentication.service import AuthenticationService

    services = build_services()
    controller = ApplicationController(
        root,
        AuthenticationService(student_exists=services.students.exists),
    )
    controller.start()
    root.mainloop()
