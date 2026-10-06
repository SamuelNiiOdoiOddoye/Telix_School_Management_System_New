"""Shared helpers for tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from telix.attendance.repository import AttendanceRepository
from telix.attendance.service import AttendanceService
from telix.academics.assessment_repository import AssessmentRepository, AssessmentKind
from telix.academics.assessment_service import AssessmentService
from telix.finance.ledger_service import FinanceLedgerService
from telix.finance.repository import FinanceRepository, LedgerKind
from telix.academics.repository import AcademicRepository
from telix.academics.service import AcademicRecordService
from telix.academics.structure_repository import AcademicStructureRepository, StructureKind
from telix.academics.structure_service import AcademicStructureService
from telix.services.student_removal import StudentRemovalService
from telix.storage.json_store import JsonStore
from telix.students.repository import StudentRepository
from telix.students.service import StudentService
from telix.teachers.repository import TeacherRepository
from telix.teachers.service import TeacherService


def valid_student(**overrides: str) -> dict[str, str]:
    values = {
        "student_id": "stu-001",
        "name": "Ama Mensah",
        "date_of_birth": "2015-03-10",
        "class_name": "5",
        "fees": "500",
        "status": "Active",
        "gender": "Female",
        "address": "Accra",
        "phone": "0241234567",
        "email": "ama@example.com",
        "medical_info": "None",
        "parent_name": "Kofi Mensah",
        "parent_phone": "0207654321",
    }
    values.update(overrides)
    return values


def valid_teacher(**overrides: str) -> dict[str, str]:
    values = {
        "teacher_id": "tch-001",
        "name": "Kwame Boateng",
        "date_of_birth": "1985-06-01",
        "class_name": "Mathematics",
        "salary": "3000",
        "gender": "Male",
        "address": "Kumasi",
        "phone": "0240000001",
        "email": "kwame@example.com",
        "medical_info": "None",
        "emergency_contact": "0240000002",
    }
    values.update(overrides)
    return values


def valid_score(**overrides: str) -> dict[str, str]:
    values = {
        "student_id": "STU-001",
        "subject": "Mathematics",
        "score": "80",
        "term": "Term 1",
        "academic_year": "2026/2027",
    }
    values.update(overrides)
    return values


class ServiceTestCase(unittest.TestCase):
    """Builds real services on top of throw-away JSON files."""

    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.student_store = JsonStore(self.directory / "student_records.json")
        self.teacher_store = JsonStore(self.directory / "teacher_records.json")
        self.academic_store = JsonStore(self.directory / "academic_records.json")
        self.attendance_store = JsonStore(self.directory / "attendance_records.json")
        ledger_stores: dict[LedgerKind, JsonStore] = {
            "payment": JsonStore(self.directory / "payments.json"),
            "expense": JsonStore(self.directory / "expenses.json"),
        }
        structure_stores: dict[StructureKind, JsonStore] = {
            kind: JsonStore(self.directory / f"{kind}.json")
            for kind in ("class", "subject", "academic_year", "term", "enrollment")
        }
        assessment_stores: dict[AssessmentKind, JsonStore] = {
            "assessment": JsonStore(self.directory / "assessment_records.json"),
            "profile": JsonStore(self.directory / "grading_profiles.json"),
        }
        self.students = StudentService(StudentRepository(self.student_store))
        self.teachers = TeacherService(TeacherRepository(self.teacher_store))
        self.academic_structure = AcademicStructureService(
            AcademicStructureRepository(structure_stores), self.students.exists
        )
        self.academics = AcademicRecordService(
            AcademicRepository(self.academic_store), self.academic_structure
        )
        self.assessments = AssessmentService(
            AssessmentRepository(assessment_stores),
            self.academic_structure,
            self.students.exists,
        )
        self.attendance = AttendanceService(
            AttendanceRepository(self.attendance_store),
            self.academic_structure,
            self.students.exists,
        )
        self.finance = FinanceLedgerService(FinanceRepository(ledger_stores), self.students.exists)
        self.removal = StudentRemovalService(
            self.students,
            self.academics,
            self.academic_structure,
            self.attendance,
            self.finance,
            self.assessments,
        )
