"""Builds the services the application needs and keeps them together."""

from __future__ import annotations

from dataclasses import dataclass, field

from telix.attendance.repository import AttendanceRepository
from telix.attendance.service import AttendanceService
from telix.authentication.roles import Authorization, SUPER_ADMIN
from telix.authentication.repository import UserRepository
from telix.authentication.service import AuthenticatedUser
from telix.authentication.service import AuthenticationService
from telix.authentication.user_management import UserManagementService
from telix.academics.assessment_repository import AssessmentRepository
from telix.academics.assessment_service import AssessmentService
from telix.academics.service import AcademicRecordService
from telix.academics.structure_service import AcademicStructureService
from telix.finance.ledger_service import FinanceLedgerService
from telix.finance.repository import FinanceRepository
from telix.services.student_removal import StudentRemovalService
from telix.students.service import StudentService
from telix.teachers.assignment_repository import TeacherAssignmentRepository
from telix.teachers.assignment_service import TeacherAssignmentService
from telix.teachers.service import TeacherService


@dataclass(frozen=True)
class Services:
    students: StudentService
    teachers: TeacherService
    academics: AcademicRecordService
    assessments: AssessmentService
    academic_structure: AcademicStructureService
    attendance: AttendanceService
    finance: FinanceLedgerService
    student_removal: StudentRemovalService
    teacher_assignments: TeacherAssignmentService
    authorization: Authorization = field(default_factory=lambda: Authorization(SUPER_ADMIN))
    user_management: UserManagementService | None = None

    def __post_init__(self) -> None:
        service_authorizations = (
            self.students._authorization,
            self.teachers._authorization,
            self.academics._authorization,
            self.assessments._authorization,
            self.academic_structure._authorization,
            self.attendance._authorization,
            self.finance._authorization,
            self.teacher_assignments._authorization,
        )
        if any(policy != self.authorization for policy in service_authorizations):
            raise ValueError("All application services must share one authorization policy.")
        if (
            self.user_management is not None
            and self.user_management._authorization != self.authorization
        ):
            raise ValueError("User management must share the application authorization policy.")


def build_services(user: AuthenticatedUser | None = None) -> Services:
    authorization = (
        Authorization(user.role, user.student_id)
        if user is not None
        else Authorization(SUPER_ADMIN)
    )
    students = StudentService(authorization=authorization)
    assignment_repository = TeacherAssignmentRepository()
    teachers = TeacherService(
        assignment_repository=assignment_repository,
        authorization=authorization,
    )
    academic_structure = AcademicStructureService(
        student_exists=students.exists,
        assignment_repository=assignment_repository,
        authorization=authorization,
    )
    teacher_assignments = TeacherAssignmentService(
        assignment_repository,
        teachers.get,
        academic_structure.get,
        authorization=authorization,
    )
    academics = AcademicRecordService(structure=academic_structure, authorization=authorization)
    assessments = AssessmentService(
        AssessmentRepository(), academic_structure, students.exists, authorization
    )
    attendance = AttendanceService(
        AttendanceRepository(), academic_structure, students.exists, authorization
    )
    finance = FinanceLedgerService(FinanceRepository(), students.exists, authorization)
    authentication = AuthenticationService(UserRepository(), students.exists)
    user_management = UserManagementService(
        authentication,
        authorization,
        user.user_id if user is not None else "",
    )
    return Services(
        authorization=authorization,
        user_management=user_management,
        students=students,
        teachers=teachers,
        academics=academics,
        assessments=assessments,
        academic_structure=academic_structure,
        attendance=attendance,
        finance=finance,
        student_removal=StudentRemovalService(
            students, academics, academic_structure, attendance, finance, assessments
        ),
        teacher_assignments=teacher_assignments,
    )
