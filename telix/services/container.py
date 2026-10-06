"""Builds the services the application needs and keeps them together."""

from __future__ import annotations

from dataclasses import dataclass

from telix.attendance.repository import AttendanceRepository
from telix.attendance.service import AttendanceService
from telix.academics.assessment_repository import AssessmentRepository
from telix.academics.assessment_service import AssessmentService
from telix.academics.service import AcademicRecordService
from telix.academics.structure_service import AcademicStructureService
from telix.finance.ledger_service import FinanceLedgerService
from telix.finance.repository import FinanceRepository
from telix.services.student_removal import StudentRemovalService
from telix.students.service import StudentService
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


def build_services() -> Services:
    students = StudentService()
    teachers = TeacherService()
    academic_structure = AcademicStructureService(student_exists=students.exists)
    academics = AcademicRecordService(structure=academic_structure)
    assessments = AssessmentService(AssessmentRepository(), academic_structure, students.exists)
    attendance = AttendanceService(AttendanceRepository(), academic_structure, students.exists)
    finance = FinanceLedgerService(FinanceRepository(), students.exists)
    return Services(
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
    )
