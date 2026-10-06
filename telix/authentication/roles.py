"""Explicit local V1 role and capability rules."""

from __future__ import annotations

from dataclasses import dataclass

from telix.core.errors import AuthorizationError

SUPER_ADMIN = "SUPER_ADMIN"
ADMIN = "ADMIN"
TEACHER = "TEACHER"
FINANCE_OFFICER = "FINANCE_OFFICER"
STUDENT = "STUDENT"
V1_ROLES = frozenset({SUPER_ADMIN, ADMIN, TEACHER, FINANCE_OFFICER, STUDENT})

STUDENTS_READ = "students.read"
STUDENTS_READ_FINANCE = "students.read.finance"
STUDENTS_READ_TEACHING = "students.read.teaching"
STUDENTS_READ_OWN = "students.read.own"
STUDENTS_WRITE = "students.write"
STUDENTS_DELETE = "students.delete"
TEACHERS_READ = "teachers.read"
TEACHERS_WRITE = "teachers.write"
TEACHERS_DELETE = "teachers.delete"
TEACHERS_SALARY_SUMMARY = "teachers.salary_summary"
ACADEMICS_READ = "academics.read"
ACADEMICS_READ_OWN = "academics.read.own"
ACADEMICS_WRITE = "academics.write"
ACADEMICS_DELETE = "academics.delete"
ACADEMIC_SETUP_READ = "academic_setup.read"
ACADEMIC_SETUP_WRITE = "academic_setup.write"
ASSESSMENTS_READ = "assessments.read"
ASSESSMENTS_READ_OWN = "assessments.read.own"
ASSESSMENTS_WRITE = "assessments.write"
ASSESSMENTS_DELETE = "assessments.delete"
ATTENDANCE_READ = "attendance.read"
ATTENDANCE_READ_OWN = "attendance.read.own"
ATTENDANCE_WRITE = "attendance.write"
ATTENDANCE_DELETE = "attendance.delete"
FINANCE_READ = "finance.read"
FINANCE_WRITE = "finance.write"
REPORTS_OPERATIONAL = "reports.operational"
REPORTS_TEACHING = "reports.teaching"
REPORTS_FINANCE = "reports.finance"
REPORTS_OWN = "reports.own"
DASHBOARD_OPERATIONAL = "dashboard.operational"
DASHBOARD_TEACHING = "dashboard.teaching"
DASHBOARD_FINANCE = "dashboard.finance"
DASHBOARD_OWN = "dashboard.own"
USERS_MANAGE = "users.manage"

_ROLE_CAPABILITIES: dict[str, frozenset[str]] = {
    SUPER_ADMIN: frozenset({"*"}),
    ADMIN: frozenset(
        {
            STUDENTS_READ,
            STUDENTS_WRITE,
            STUDENTS_DELETE,
            TEACHERS_READ,
            TEACHERS_WRITE,
            TEACHERS_DELETE,
            ACADEMICS_READ,
            ACADEMICS_WRITE,
            ACADEMICS_DELETE,
            ACADEMIC_SETUP_READ,
            ACADEMIC_SETUP_WRITE,
            ASSESSMENTS_READ,
            ASSESSMENTS_WRITE,
            ASSESSMENTS_DELETE,
            ATTENDANCE_READ,
            ATTENDANCE_WRITE,
            ATTENDANCE_DELETE,
            FINANCE_READ,
            FINANCE_WRITE,
            USERS_MANAGE,
            REPORTS_OPERATIONAL,
            REPORTS_FINANCE,
            DASHBOARD_OPERATIONAL,
            DASHBOARD_FINANCE,
        }
    ),
    TEACHER: frozenset(
        {
            STUDENTS_READ_TEACHING,
            ACADEMICS_READ,
            ACADEMICS_WRITE,
            ACADEMIC_SETUP_READ,
            ASSESSMENTS_READ,
            ASSESSMENTS_WRITE,
            ATTENDANCE_READ,
            ATTENDANCE_WRITE,
            REPORTS_TEACHING,
            DASHBOARD_TEACHING,
        }
    ),
    FINANCE_OFFICER: frozenset(
        {
            STUDENTS_READ_FINANCE,
            TEACHERS_SALARY_SUMMARY,
            FINANCE_READ,
            FINANCE_WRITE,
            REPORTS_FINANCE,
            DASHBOARD_FINANCE,
        }
    ),
    STUDENT: frozenset(
        {
            STUDENTS_READ_OWN,
            ACADEMICS_READ_OWN,
            ASSESSMENTS_READ_OWN,
            ATTENDANCE_READ_OWN,
            ACADEMIC_SETUP_READ,
            REPORTS_OWN,
            DASHBOARD_OWN,
        }
    ),
}


@dataclass(frozen=True)
class Authorization:
    """Authorization snapshot created from the authenticated local user."""

    role: str
    student_id: str = ""

    def __post_init__(self) -> None:
        if self.role not in V1_ROLES:
            raise AuthorizationError("This account has an unsupported V1 role.")
        if self.role == STUDENT and not self.student_id.strip():
            raise AuthorizationError("A student account must be linked to a student record.")

    def allows(self, capability: str) -> bool:
        return "*" in _ROLE_CAPABILITIES[self.role] or capability in _ROLE_CAPABILITIES[self.role]

    def require(self, capability: str) -> None:
        if not self.allows(capability):
            raise AuthorizationError("Your account is not authorized to perform this operation.")

    def require_any(self, *capabilities: str) -> None:
        if not any(self.allows(capability) for capability in capabilities):
            raise AuthorizationError("Your account is not authorized to access these records.")

    def scoped_student_id(self, requested_id: str = "") -> str:
        requested = requested_id.strip()
        if self.role != STUDENT:
            return requested
        owner = self.student_id.strip()
        if requested and requested.casefold() != owner.casefold():
            raise AuthorizationError("Student accounts can only access their own records.")
        return owner

    def filter_student_records(self, records: list[dict[str, object]]) -> list[dict[str, object]]:
        if self.role != STUDENT:
            return records
        target = self.student_id.casefold()
        return [
            record for record in records if str(record.get("student_id", "")).casefold() == target
        ]


def capabilities_for(role: str) -> frozenset[str]:
    """Return the explicit V1 capability set for navigation and presentation."""
    if role not in V1_ROLES:
        raise AuthorizationError("This account has an unsupported V1 role.")
    return _ROLE_CAPABILITIES[role]


def assignable_roles(role: str) -> frozenset[str]:
    """Return the account roles an administrator may assign through V1."""
    if role == SUPER_ADMIN:
        return V1_ROLES
    if role == ADMIN:
        return frozenset({TEACHER, FINANCE_OFFICER, STUDENT})
    raise AuthorizationError("Your account cannot manage user roles.")
