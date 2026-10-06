"""Filesystem locations used by the application."""

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"

TELIX_ICON_PATH = IMAGES_DIR / "telix_image.ico"
TELIX_ICON_IMAGE_PATH = IMAGES_DIR / "telix_image.png"

STUDENT_FILE = PROJECT_DIR / "student_records.json"
TEACHER_FILE = PROJECT_DIR / "teacher_records.json"
ACADEMIC_FILE = PROJECT_DIR / "academic_records.json"
CLASS_FILE = PROJECT_DIR / "classes.json"
SUBJECT_FILE = PROJECT_DIR / "subjects.json"
ACADEMIC_YEAR_FILE = PROJECT_DIR / "academic_years.json"
TERM_FILE = PROJECT_DIR / "terms.json"
ENROLLMENT_FILE = PROJECT_DIR / "enrollments.json"
TEACHER_ASSIGNMENT_FILE = PROJECT_DIR / "teacher_assignments.json"
ATTENDANCE_FILE = PROJECT_DIR / "attendance_records.json"
PAYMENT_FILE = PROJECT_DIR / "payments.json"
EXPENSE_FILE = PROJECT_DIR / "expenses.json"
ASSESSMENT_FILE = PROJECT_DIR / "assessment_records.json"
GRADING_PROFILE_FILE = PROJECT_DIR / "grading_profiles.json"
USERS_FILE = PROJECT_DIR / "users.json"
