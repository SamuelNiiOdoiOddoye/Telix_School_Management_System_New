"""Builds the services the application needs and keeps them together."""

from __future__ import annotations

from dataclasses import dataclass

from telix.academics.service import AcademicRecordService
from telix.services.student_removal import StudentRemovalService
from telix.students.service import StudentService
from telix.teachers.service import TeacherService


@dataclass(frozen=True)
class Services:
    students: StudentService
    teachers: TeacherService
    academics: AcademicRecordService
    student_removal: StudentRemovalService


def build_services() -> Services:
    students = StudentService()
    teachers = TeacherService()
    academics = AcademicRecordService()
    return Services(
        students=students,
        teachers=teachers,
        academics=academics,
        student_removal=StudentRemovalService(students, academics),
    )
