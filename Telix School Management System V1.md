# Telix School Management System — V1

## Product scope

Telix V1 is a single-school, local desktop application built with Python,
Tkinter, and JSON persistence. It is not a hosted or coordinated multi-user
service. Its existing layered architecture is:

```text
Tkinter UI → Services → Domain rules → Repositories → JSON storage
```

V1 is being completed and acceptance-tested as an existing product; this
document does not start a rewrite or claim release acceptance before the
remaining manual checks are complete.

## Implemented V1 functionality

- Student and teacher record management, validation, search, and deletion
  safeguards.
- Managed classes, subjects, academic years, terms, effective-dated
  enrollment, and teacher-to-subject assignments by academic year.
- Academic records, configurable assessment components and grading, and
  student-linked academic history.
- Attendance recording, filtering, summaries, and enrollment/date validation.
- Student active/inactive/withdrawn states and transfer/promotion workflows.
- Payment and expense ledgers, balance/credit calculations, finance summaries,
  reports, dashboard metrics, and CSV export.
- JSON persistence with atomic writes, backups, and explicit handling of
  malformed storage.
- Local authentication, salted `scrypt` password hashes, in-memory sessions,
  logout, and five fixed roles:

  ```text
  SUPER_ADMIN
  ADMIN
  TEACHER
  FINANCE_OFFICER
  STUDENT
  ```

Service-layer authorization enforces role capabilities. Student accounts are
linked to existing student records and remain scoped to their own permitted
records.

## User Management and demo accounts

Super Admins can manage V1 accounts and assign supported V1 roles. Admins can
manage Teacher, Finance Officer, and Student accounts but cannot inspect or
manage Admin/Super Admin accounts or create/promote a Super Admin. Student
accounts require an existing student link. Administrators can update account
details and activate/deactivate accounts; the last active Super Admin is
protected from deactivation or demotion.

The User Management access profile is read-only and derived from the selected
account's existing V1 role capabilities. V1 does not have arbitrary
per-account permission editing.

Self-service demo registration is an optional local development/portfolio
feature. Set `TELIX_ENABLE_DEMO_REGISTRATION=1` before launching to display
**Create Local Demo Account**. The form collects a full name, email, and
password confirmation; it always creates a Teacher account and has no role
input. Registration is disabled when the environment flag is unset. Keep it
disabled for production.

The interactive CLI demo bootstrap remains available with
`python -m telix.bootstrap_demo_accounts`. The portfolio-only synthetic Teacher
account is documented in the README as **Development / Portfolio Demo — Not
for Production**. Never run demo bootstrap flows against production data.

Initial Super Admin setup uses `python -m telix.bootstrap_admin`. The account
owner provides the local credentials; no real credential is stored in this
document or in source code.

## Data handling and limitations

- JSON files are stored locally beside the project and are excluded from Git.
- Local JSON data is not encrypted at rest. Operating-system users who can
  access the files can read them.
- Storage does not provide database constraints, inter-process locking, or
  transactions across multiple JSON files.
- Student fees remain a single expected amount per student; invoices and
  academic-period payment allocations are not implemented.
- A consolidated lifecycle audit timeline, backup/restore UI, and
  installer/distribution packaging are not implemented.
- Authentication and V1 roles are local application controls, not protection
  against a person with direct access to the computer, files, or source code.

Protect local data with operating-system permissions and use synthetic data
for development and demonstrations.

## V1 release acceptance status

Local automated checks run for the current implementation:

- `python -m unittest discover -s tests -t .` — 143 tests passed.
- `ruff check .` — passed.
- `ruff format --check .` — passed.
- `mypy telix` — passed.
- Tk UI smoke tests — 10 passed in the local desktop environment.

These automated checks do not replace the full manual desktop acceptance
checklist in [`tests/manual_acceptance.md`](./tests/manual_acceptance.md).
Manual acceptance and a clean-install review remain outstanding; V1 must not
be called release-complete until those checks pass.

## V2 — future work only

V2 is not implemented or started by this document. It may be designed
separately after V1 acceptance. Potential future targets include a web/mobile
application, Django/DRF, PostgreSQL, Redis/Celery, Next.js/React/TypeScript,
Flutter, multi-tenancy, and more granular authorization scopes. None of these
are part of V1.
