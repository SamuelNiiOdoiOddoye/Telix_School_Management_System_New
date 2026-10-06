"""Removing a student together with the student's linked academic records."""

from __future__ import annotations

from typing import Any

from telix.academics.service import AcademicRecordService
from telix.students.service import StudentService


class StudentRemovalService:
    def __init__(self, students: StudentService, academics: AcademicRecordService) -> None:
        self._students = students
        self._academics = academics

    def remove(self, student_id: str) -> dict[str, Any]:
        """Delete linked academic records first, then the student record."""
        self._academics.delete_for_student(student_id)
        return self._students.delete(student_id)
