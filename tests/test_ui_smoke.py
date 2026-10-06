"""Headless-safe desktop startup and tab-registration smoke test."""

import tkinter as tk
from tkinter import ttk
import secrets
import os
from collections.abc import Iterator
from unittest.mock import patch

from telix.authentication.service import AuthenticatedUser, AuthenticationService
from telix.authentication.roles import ADMIN, STUDENT, SUPER_ADMIN, TEACHER, Authorization
from telix.authentication.repository import UserRepository
from telix.authentication.session import UserSession
from telix.authentication.user_management import UserManagementService
from telix.storage.json_store import JsonStore
from telix.services.container import Services
from telix.ui.login import LoginScreen
from telix.ui.app import ApplicationController, SchoolManagementSystem, TAB_CLASSES
from tests.support import ServiceTestCase, valid_student, valid_teacher


class DesktopStartupSmokeTests(ServiceTestCase):
    @staticmethod
    def _session() -> UserSession:
        session = UserSession()
        session.start(
            AuthenticatedUser(
                user_id="USR-TEST",
                name="Test Administrator",
                email="admin@example.invalid",
                phone="+12025550123",
                role="SUPER_ADMIN",
            )
        )
        return session

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
                self.teacher_assignments,
                user_management=self._user_management_for_role(SUPER_ADMIN),
            )
            application = SchoolManagementSystem(root, services, self._session(), lambda: None)
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
                self.teacher_assignments,
                user_management=self._user_management_for_role(SUPER_ADMIN),
            )
            application = SchoolManagementSystem(root, services, self._session(), lambda: None)
            reports = application.tabs["reports"]
            root.geometry("1080x680")
            root.update_idletasks()
            self.assertLessEqual(reports.toolbar.winfo_reqwidth(), 1048)
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

    def test_teacher_assignment_ui_creates_and_removes_assignment(self) -> None:
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
                self.teacher_assignments,
                user_management=self._user_management_for_role(SUPER_ADMIN),
            )
            application = SchoolManagementSystem(root, services, self._session(), lambda: None)
            setup = application.tabs["academic_setup"]
            teacher = self.teachers.add(valid_teacher())
            subject = self.academic_structure.add("subject", {"name": "Mathematics"})
            year = self.academic_structure.add(
                "academic_year",
                {
                    "name": "2026/2027",
                    "start_date": "2026-09-01",
                    "end_date": "2027-06-30",
                },
            )
            setup.refresh()
            setup.assignment_editor.variables["teacher_id"].set(
                f"{teacher['name']} [{teacher['teacher_id']}]"
            )
            setup.assignment_editor.variables["subject_id"].set(
                f"{subject['name']} [{subject['subject_id']}]"
            )
            setup.assignment_editor.variables["academic_year_id"].set(
                f"{year['name']} [{year['academic_year_id']}]"
            )
            application._context.feedback.success = lambda _message: None
            application._context.feedback.confirm = lambda _title, _message: True

            setup.add_assignment()
            self.assertEqual(len(self.teacher_assignments.list()), 1)
            self.assertEqual(len(setup.assignment_editor.tree.get_children()), 1)

            assignment_id = self.teacher_assignments.list()[0]["assignment_id"]
            setup.assignment_editor.selected_id = assignment_id
            setup.delete_assignment()
            self.assertEqual(self.teacher_assignments.list(), [])
        finally:
            root.destroy()

    def _services_for_role(self, role: str, student_id: str = "") -> Services:
        authorization = Authorization(role, student_id)
        services = (
            self.students,
            self.teachers,
            self.academics,
            self.assessments,
            self.academic_structure,
            self.attendance,
            self.finance,
            self.teacher_assignments,
        )
        for service in services:
            service._authorization = authorization
        return Services(
            self.students,
            self.teachers,
            self.academics,
            self.assessments,
            self.academic_structure,
            self.attendance,
            self.finance,
            self.removal,
            self.teacher_assignments,
            authorization=authorization,
            user_management=self._user_management_for_role(role, student_id),
        )

    def _user_management_for_role(self, role: str, student_id: str = "") -> UserManagementService:
        authorization = Authorization(role, student_id)
        authentication = AuthenticationService(
            UserRepository(JsonStore(self.directory / f"users-{role}.json")),
            self.students.exists,
        )
        return UserManagementService(authentication, authorization, "USR-TEST")

    def test_teacher_workspace_limits_tabs_and_student_personal_fields(self) -> None:
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk desktop display is unavailable: {error}")
        try:
            root.withdraw()
            self.students.add(valid_student())
            session = UserSession()
            session.start(
                AuthenticatedUser(
                    user_id="USR-TEACHER",
                    name="Demo Teacher",
                    email="teacher@example.invalid",
                    phone="+12025550123",
                    role=TEACHER,
                )
            )
            application = SchoolManagementSystem(
                root,
                self._services_for_role(TEACHER),
                session,
                lambda: None,
            )
            root.update()

            self.assertNotIn("finance", application.tabs)
            self.assertNotIn("teachers", application.tabs)
            self.assertNotIn("academic_setup", application.tabs)
            self.assertNotIn("users", application.tabs)
            self.assertEqual(
                tuple(application.tabs["students"].tree["columns"]),
                ("student_id", "name", "class_name", "status"),
            )
            application.logout()
        finally:
            root.destroy()

    def test_admin_workspace_exposes_restricted_user_management(self) -> None:
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk desktop display is unavailable: {error}")
        try:
            root.withdraw()
            session = UserSession()
            session.start(
                AuthenticatedUser(
                    user_id="USR-ADMIN",
                    name="Test Admin",
                    email="admin@example.invalid",
                    phone="+12025550123",
                    role=ADMIN,
                )
            )
            application = SchoolManagementSystem(
                root,
                self._services_for_role(ADMIN),
                session,
                lambda: None,
            )

            self.assertIn("users", application.tabs)
            self.assertNotIn(SUPER_ADMIN, application.tabs["users"].role_box["values"])
            self.assertEqual(
                set(application.tabs["users"].role_box["values"]) - {""},
                {"TEACHER", "FINANCE_OFFICER", STUDENT},
            )
            application.logout()
        finally:
            root.destroy()

    def test_student_workspace_shows_only_linked_student_report(self) -> None:
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk desktop display is unavailable: {error}")
        try:
            root.withdraw()
            self.students.add(valid_student(student_id="STU-001", name="Linked Student"))
            self.students.add(valid_student(student_id="STU-002", name="Other Student"))
            session = UserSession()
            session.start(
                AuthenticatedUser(
                    user_id="USR-STUDENT",
                    name="Linked Student",
                    email="student@example.invalid",
                    phone="+12025550123",
                    role=STUDENT,
                    student_id="STU-001",
                )
            )
            application = SchoolManagementSystem(
                root,
                self._services_for_role(STUDENT, "STU-001"),
                session,
                lambda: None,
            )
            root.update()
            reports = application.tabs["reports"]
            visible_rows = reports.student_tree.get_children()

            self.assertEqual(set(application.tabs), {"dashboard", "reports"})
            self.assertEqual(len(visible_rows), 1)
            self.assertEqual(
                reports.student_tree.item(visible_rows[0], "values")[0],
                "STU-001",
            )
            self.assertNotIn("finance_tree", reports.__dict__)
            self.assertNotIn("users", application.tabs)
            application.logout()
        finally:
            root.destroy()

    def test_main_application_requires_authentication_and_logout_clears_session(self) -> None:
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
                self.teacher_assignments,
                user_management=self._user_management_for_role(SUPER_ADMIN),
            )
            with self.assertRaisesRegex(ValueError, "authenticated session is required"):
                SchoolManagementSystem(root, services, UserSession(), lambda: None)

            session = self._session()
            logged_out: list[bool] = []
            application = SchoolManagementSystem(
                root, services, session, lambda: logged_out.append(True)
            )
            application.logout()
            self.assertFalse(session.authenticated)
            self.assertEqual(logged_out, [True])
        finally:
            root.destroy()

    def test_login_screen_rejects_bad_credentials_and_calls_success_handler(self) -> None:
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk desktop display is unavailable: {error}")
        try:
            root.withdraw()
            auth = AuthenticationService(UserRepository(JsonStore(self.directory / "users.json")))
            password = secrets.token_urlsafe(24)
            auth.create_super_admin(
                "Test Administrator",
                "admin@example.invalid",
                "+12025550123",
                password,
            )
            received: list[AuthenticatedUser] = []
            screen = LoginScreen(root, auth, received.append)
            screen.email.set("admin@example.invalid")
            screen.password.set(f"{password}-wrong")
            screen._submit()
            self.assertEqual(screen.message.get(), "Invalid email or password.")
            self.assertEqual(received, [])

            screen.email.set("unknown@example.invalid")
            screen.password.set(secrets.token_urlsafe(24))
            screen._submit()
            self.assertEqual(screen.message.get(), "Invalid email or password.")

            screen.email.set("admin@example.invalid")
            screen.password.set(password)
            screen._submit()
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0].email, "admin@example.invalid")
            self.assertEqual(screen.password.get(), "")
        finally:
            root.destroy()

    def test_login_screen_opens_opt_in_demo_registration(self) -> None:
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk desktop display is unavailable: {error}")
        try:
            root.withdraw()
            auth = AuthenticationService(UserRepository(JsonStore(self.directory / "users.json")))
            with patch.dict(os.environ, {"TELIX_ENABLE_DEMO_REGISTRATION": "1"}):
                received: list[AuthenticatedUser] = []
                screen = LoginScreen(root, auth, received.append)
                registration_button = screen.demo_registration_button
                self.assertIsNotNone(registration_button)
                assert registration_button is not None
                registration_button.invoke()
                root.update()
                registration_window = screen.registration_window
                self.assertIsNotNone(registration_window)
                assert registration_window is not None
                self.assertTrue(registration_window.winfo_exists())
                widgets = list(self._descendants(registration_window))
                entries = [widget for widget in widgets if isinstance(widget, ttk.Entry)]
                self.assertEqual(len(entries), 4)
                for entry, value in zip(
                    entries,
                    (
                        "Local Demo Teacher",
                        "local-teacher@example.invalid",
                        "local-demo-password",
                        "local-demo-password",
                    ),
                ):
                    entry.insert(0, value)
                create_button = next(
                    widget
                    for widget in widgets
                    if isinstance(widget, ttk.Button) and widget.cget("text") == "Create Account"
                )
                create_button.invoke()
                root.update()
                self.assertIsNone(screen.registration_window)
                self.assertEqual(screen.email.get(), "local-teacher@example.invalid")
                self.assertIn("account created", screen.message.get().casefold())
                self.assertEqual(
                    auth.authenticate("local-teacher@example.invalid", "local-demo-password").role,
                    TEACHER,
                )
                screen.password.set("local-demo-password")
                screen._submit()
                self.assertEqual(len(received), 1)
                self.assertEqual(received[0].role, TEACHER)
        finally:
            root.destroy()

    @staticmethod
    def _descendants(widget: tk.Misc) -> Iterator[tk.Misc]:
        for child in widget.winfo_children():
            yield child
            yield from DesktopStartupSmokeTests._descendants(child)

    def test_application_controller_wires_login_workspace_and_logout(self) -> None:
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk desktop display is unavailable: {error}")
        try:
            root.withdraw()
            authentication = AuthenticationService(
                UserRepository(JsonStore(self.directory / "users.json"))
            )
            password = secrets.token_urlsafe(24)
            authentication.create_super_admin(
                "Test Administrator",
                "admin@example.invalid",
                "+12025550123",
                password,
            )
            services = Services(
                self.students,
                self.teachers,
                self.academics,
                self.assessments,
                self.academic_structure,
                self.attendance,
                self.finance,
                self.removal,
                self.teacher_assignments,
                user_management=self._user_management_for_role(SUPER_ADMIN),
            )
            controller = ApplicationController(root, authentication, lambda: services)
            controller.start()
            root.update()
            self.assertIsNotNone(controller.login_screen)
            self.assertIsNone(controller.active_app)

            login = controller.login_screen
            assert login is not None
            login.email.set("admin@example.invalid")
            login.password.set(f"{password}-wrong")
            login._submit()
            self.assertIsNone(controller.active_app)

            login.password.set(password)
            login._submit()
            root.update()
            self.assertIsNone(controller.login_screen)
            self.assertIsNotNone(controller.active_app)
            session = controller.active_app.session
            self.assertTrue(session.authenticated)

            controller.active_app.logout()
            root.update()
            self.assertFalse(session.authenticated)
            self.assertIsNone(controller.active_app)
            self.assertIsNotNone(controller.login_screen)
        finally:
            root.destroy()
