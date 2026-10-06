"""Removing a student together with the student's linked academic records."""

from __future__ import annotations

from typing import Any

from telix.academics.service import AcademicRecordService
from telix.academics.structure_service import AcademicStructureService
from telix.students.service import StudentService


class StudentRemovalService:
    def __init__(
        self,
        students: StudentService,
        academics: AcademicRecordService,
        academic_structure: AcademicStructureService | None = None,
    ) -> None:
        self._students = students
        self._academics = academics
        self._academic_structure = academic_structure

    def remove(self, student_id: str) -> dict[str, Any]:
        """Delete linked academic and enrollment records before the student."""
        self._academics.delete_for_student(student_id)
        if self._academic_structure:
            self._academic_structure.delete_for_student(student_id)
        return self._students.delete(student_id)
