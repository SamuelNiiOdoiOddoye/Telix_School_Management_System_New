"""Student field definitions."""

STUDENT_FIELD_LABELS = {
    "student_id": "Student ID",
    "name": "Student name",
    "date_of_birth": "Date of birth",
    "class_name": "Class",
    "fees": "School fees",
    "status": "Student status",
    "gender": "Gender",
    "address": "Address",
    "phone": "Student phone number",
    "email": "Email address",
    "medical_info": "Medical information",
    "parent_name": "Parent or guardian name",
    "parent_phone": "Parent or guardian phone number",
}

STUDENT_STATUSES = ("Active", "Inactive", "Withdrawn")
DEFAULT_STUDENT_STATUS = "Active"
STUDENT_STATUS_TRANSITIONS = {
    "Active": frozenset({"Active", "Inactive", "Withdrawn"}),
    "Inactive": frozenset({"Active", "Inactive", "Withdrawn"}),
    "Withdrawn": frozenset({"Active", "Withdrawn"}),
}
