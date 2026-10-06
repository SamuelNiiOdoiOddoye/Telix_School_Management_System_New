"""Builds the services the application needs and keeps them together."""

from __future__ import annotations

from dataclasses import dataclass

from telix.academics.service import AcademicRecordService
from telix.academics.structure_service import AcademicStructureService
from telix.services.student_removal import StudentRemovalService
from telix.students.service import StudentService
from telix.teachers.service import TeacherService


@dataclass(frozen=True)
class Services:
    students: StudentService
    teachers: TeacherService
    academics: AcademicRecordService
    academic_structure: AcademicStructureService
    student_removal: StudentRemovalService


def build_services() -> Services:
    students = StudentService()
    teachers = TeacherService()
    academics = AcademicRecordService()
    academic_structure = AcademicStructureService(student_exists=students.exists)
    return Services(
        students=students,
        teachers=teachers,
        academics=academics,
        academic_structure=academic_structure,
        student_removal=StudentRemovalService(students, academics, academic_structure),
    )
