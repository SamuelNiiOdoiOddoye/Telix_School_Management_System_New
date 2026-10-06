"""Headless-safe desktop startup and tab-registration smoke test."""

import tkinter as tk

from telix.services.container import Services
from telix.ui.app import SchoolManagementSystem, TAB_CLASSES
from tests.support import ServiceTestCase, valid_student, valid_teacher


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

    def test_reports_render_records_apply_filters_and_show_empty_state(self) -> None:
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
            reports = application.tabs["reports"]
            self.students.add(valid_student())
            self.students.add(valid_student(student_id="STU-002", status="Inactive"))
            self.teachers.add(valid_teacher())
            self.teachers.add(valid_teacher(teacher_id="TCH-002", name="Efua Owusu"))

            reports.refresh()
            root.update()
            self.assertEqual(len(reports.student_tree.get_children()), 2)
            self.assertEqual(len(reports.teacher_tree.get_children()), 2)

            reports.student_status_filter.set("Active")
            reports.teacher_filter.set("TCH-002")
            reports.refresh()
            root.update()
            student_rows = [
                reports.student_tree.item(item, "values")
                for item in reports.student_tree.get_children()
            ]
            teacher_rows = [
                reports.teacher_tree.item(item, "values")
                for item in reports.teacher_tree.get_children()
            ]
            self.assertEqual(len(student_rows), 1)
            self.assertEqual(student_rows[0][3], "Active")
            self.assertEqual(len(teacher_rows), 1)
            self.assertEqual(teacher_rows[0][0], "TCH-002")

            reports.student_id_filter.set("NO-MATCH")
            reports.refresh()
            root.update()
            empty_row = reports.student_tree.get_children()
            self.assertEqual(len(empty_row), 1)
            self.assertIn("empty", reports.student_tree.item(empty_row[0], "tags"))
            self.assertEqual(
                reports.student_tree.item(empty_row[0], "values")[0], "No records found."
            )
        finally:
            root.destroy()
