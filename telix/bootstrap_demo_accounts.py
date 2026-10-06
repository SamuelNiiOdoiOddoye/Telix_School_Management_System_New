"""Create repeatable, development-only V1 demonstration accounts."""

from __future__ import annotations

import argparse
import getpass
import os
from collections.abc import Callable

from telix.authentication.roles import (
    ADMIN,
    FINANCE_OFFICER,
    STUDENT,
    SUPER_ADMIN,
    TEACHER,
)
from telix.authentication.service import AuthenticationService
from telix.core.errors import ValidationError
from telix.students.service import StudentService

DEMO_STUDENT_ID = "DEMO-STU-001"
PORTFOLIO_DEMO_EMAIL = "demo-teacher@telix.example.invalid"
PORTFOLIO_DEMO_PASSWORD = "TelixDemo!2026"
DEMO_ACCOUNTS = (
    ("Demo Super Admin", "demo-super-admin@telix.example.invalid", "+12025550120", SUPER_ADMIN),
    ("Demo Administrator", "demo-admin@telix.example.invalid", "+12025550121", ADMIN),
    ("Demo Teacher", "demo-teacher@telix.example.invalid", "+12025550122", TEACHER),
    (
        "Demo Finance Officer",
        "demo-finance@telix.example.invalid",
        "+12025550123",
        FINANCE_OFFICER,
    ),
    ("Demo Student", "demo-student@telix.example.invalid", "+12025550124", STUDENT),
)


def run_demo_bootstrap(
    authentication: AuthenticationService,
    students: StudentService,
    password_prompt: Callable[[str], str] = getpass.getpass,
    message: Callable[[str], None] = print,
    *,
    portfolio_only: bool = False,
) -> list[str]:
    """Create missing demo users without changing existing accounts or passwords."""
    if os.environ.get("TELIX_DEVELOPMENT_DEMO_BOOTSTRAP") != "1":
        raise ValidationError("Run the explicit development demo bootstrap command.")
    accounts = (
        (("Portfolio Demo Teacher", PORTFOLIO_DEMO_EMAIL, "+12025550122", TEACHER),)
        if portfolio_only
        else DEMO_ACCOUNTS
    )
    if portfolio_only:
        existing = authentication.repository.find_by_email(PORTFOLIO_DEMO_EMAIL)
        if existing is not None and existing.get("role") != TEACHER:
            raise ValidationError(
                f"The reserved demo email {PORTFOLIO_DEMO_EMAIL} is already assigned "
                "to another role."
            )
        if existing is not None:
            message("The portfolio Teacher account already exists; its password was not changed.")
            return []
        authentication.create_development_demo_account(
            "Portfolio Demo Teacher",
            PORTFOLIO_DEMO_EMAIL,
            "+12025550122",
            PORTFOLIO_DEMO_PASSWORD,
            TEACHER,
        )
        message(f"Created portfolio Teacher account: {PORTFOLIO_DEMO_EMAIL}")
        return [PORTFOLIO_DEMO_EMAIL]

    for _, email, _, role in accounts:
        existing = authentication.repository.find_by_email(email)
        if existing is not None and existing.get("role") != role:
            raise ValidationError(
                f"The reserved demo email {email} is already assigned to another role."
            )
        if (
            existing is not None
            and role == STUDENT
            and str(existing.get("student_id", "")).casefold() != DEMO_STUDENT_ID.casefold()
        ):
            raise ValidationError("The demo student account has an unexpected student link.")
    existing_demo = students.get(DEMO_STUDENT_ID)
    if existing_demo is not None and (
        existing_demo.get("name") != "Synthetic Demo Student"
        or existing_demo.get("email") != "demo-student-record@telix.example.invalid"
        or existing_demo.get("address") != "Synthetic development-only record"
    ):
        raise ValidationError(
            f"{DEMO_STUDENT_ID} exists but is not the expected synthetic demo record."
        )
    if existing_demo is None:
        students.add(
            {
                "student_id": DEMO_STUDENT_ID,
                "name": "Synthetic Demo Student",
                "date_of_birth": "2014-05-04",
                "class_name": "Demo Class",
                "fees": "0.00",
                "status": "Active",
                "gender": "Other",
                "address": "Synthetic development-only record",
                "phone": "+12025550125",
                "email": "demo-student-record@telix.example.invalid",
                "medical_info": "None",
                "parent_name": "Synthetic Demo Guardian",
                "parent_phone": "+12025550126",
            }
        )

    created: list[str] = []
    for name, email, phone, role in accounts:
        existing = authentication.repository.find_by_email(email)
        if existing is not None:
            continue

        password = password_prompt(f"Set a password for {role.replace('_', ' ').title()}: ")
        confirmation = password_prompt("Confirm password: ")
        if password != confirmation:
            raise ValidationError("The passwords did not match; no account was created.")
        authentication.create_development_demo_account(
            name,
            email,
            phone,
            password,
            role,
            student_id=DEMO_STUDENT_ID if role == STUDENT else "",
        )
        created.append(email)
        message(f"Created {role.replace('_', ' ').title()} demo account: {email}")
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Create development-only V1 demo accounts.")
    parser.add_argument(
        "--portfolio-only",
        action="store_true",
        help="Create only the synthetic portfolio Teacher account.",
    )
    args = parser.parse_args()

    from telix.services.container import build_services

    services = build_services()
    previous_flag = os.environ.get("TELIX_DEVELOPMENT_DEMO_BOOTSTRAP")
    os.environ["TELIX_DEVELOPMENT_DEMO_BOOTSTRAP"] = "1"
    try:
        authentication = AuthenticationService(student_exists=services.students.exists)
        created = run_demo_bootstrap(
            authentication,
            services.students,
            portfolio_only=args.portfolio_only,
        )
    finally:
        if previous_flag is None:
            os.environ.pop("TELIX_DEVELOPMENT_DEMO_BOOTSTRAP", None)
        else:
            os.environ["TELIX_DEVELOPMENT_DEMO_BOOTSTRAP"] = previous_flag
    print(f"Demo bootstrap complete. {len(created)} account(s) created.")


if __name__ == "__main__":
    main()
