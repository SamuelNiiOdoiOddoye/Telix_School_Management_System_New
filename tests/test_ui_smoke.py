"""Headless-safe desktop startup and tab-registration smoke test."""

import tkinter as tk

from telix.services.container import Services
from telix.ui.app import SchoolManagementSystem, TAB_CLASSES
from tests.support import ServiceTestCase


class DesktopStartupSmokeTests(ServiceTestCase):
    def test_application_window_and_registered_tabs_initialize(self) -> None:
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk desktop display is unavailable: {error}")
        try:
            root.withdraw()
            services = Services(
                self.students,
                self.teachers,
                self.academics,
                self.assessments,
                self.academic_structure,
                self.attendance,
                self.finance,
                self.removal,
            )
            application = SchoolManagementSystem(root, services)
            root.update()
            self.assertEqual(set(application.tabs), {tab.key for tab in TAB_CLASSES})
        finally:
            root.destroy()
