# Telix School Management System

Telix is a desktop school-records application built with Python and Tkinter. It provides a single-user workspace for maintaining student, teacher, and academic records, viewing linked reports, and calculating a simple expected income summary.

> **Project status:** This is a local desktop application backed by JSON files. It is not yet a multi-user or hosted school-management platform. Review [Known limitations](#known-limitations-and-roadmap) and [Data handling and privacy](#data-handling-and-privacy) before using real student information.

## Contents

- [Current features](#current-features)
- [Authentication and first-run setup](#authentication-and-first-run-setup)
- [How the application works](#how-the-application-works)
- [Requirements and installation](#requirements-and-installation)
- [Run the application](#run-the-application)
- [Run the tests](#run-the-tests)
- [Manual desktop acceptance checklist](#manual-desktop-acceptance-checklist)
- [Data files and privacy](#data-files-and-privacy)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Changes in the modular restructure](#changes-in-the-modular-restructure)
- [Development phases](#development-phases)
- [V2 — Telix platform](#v2--telix-platform)
- [Known limitations](#known-limitations)
- [Contributing](#contributing)
- [License and usage](#license-and-usage)

## Current features

### Authentication

- Requires a local Super Admin login before creating the school-management
  workspace. Logging out clears the in-memory session and returns to login.
- Compares account emails case-insensitively and uses the same failure message
  for missing, disabled, and incorrectly authenticated accounts.
- Stores salted `scrypt` password hashes only. Passwords are excluded from the
  session object, reports, and application log messages.
- Provides a one-time bootstrap command and refuses to overwrite an existing
  Super Admin account.

This is a single local desktop account, not V2 role-based access control, and
does not protect files from someone with direct access to the computer.

### Dashboard

- Displays total and active student counts, teacher count, and attendance percentage.
- Shows expected fees, receipts, outstanding balance, salaries, other expenses,
  total expenses, and collected-cash profit or loss.
- Provides quick navigation to student, teacher, academics, assessment,
  attendance, and finance workflows.
- Refreshes the application views after successful record changes.

### Student records

- Create, view, search, update, and delete student records.
- Stores Student ID, name, date of birth, class, fees, gender, address, phone, email, medical information, and parent or guardian contact details.
- Generates an ID when the ID field is left blank; manually supplied IDs are accepted.
- Searches by Student ID and filters the table by class.
- Tracks Active, Inactive, or Withdrawn status and supports filtering by status.
- Allows Active/Inactive changes and withdrawal; a withdrawn student can only
  remain withdrawn or be explicitly reactivated.
- Prevents duplicate IDs without regard to case and does not allow an existing Student ID to be changed during an update.
- Requires a selected record before updating. Deletion requires confirmation.

### Teacher records

- Create, view, search, update, and delete teacher records.
- Stores Teacher ID, name, date of birth, class or subject, salary, gender, address, phone, email, medical information, and emergency contact.
- Generates an ID when the ID field is left blank; manually supplied IDs are accepted.
- Searches by Teacher ID.
- Prevents duplicate IDs without regard to case and does not allow an existing Teacher ID to be changed during an update.
- Requires a selected record before updating. Deletion requires confirmation.

### Academic records

- Create, view, update, and delete a student's score records.
- Associates each score with an existing student by Student ID.
- Stores subject, whole-number score from 0 to 100, term, and academic year.
- Searches for a student by ID and displays that student's linked academic records.
- Prevents duplicate subject entries for the same student, term, and academic year.
- Removes a student's linked academic records when that student is deleted.

### Academic setup and enrollment

- Create, view, update, and delete classes, subjects, academic years, and terms
  from the **Academic Setup** tab.
- Create and maintain student enrollments linked by explicit student, class,
  and academic-year IDs.
- Keep enrollment history through effective start/end dates; transfers within
  an academic year must not overlap.
- Validate term/enrollment dates against the selected academic year and prevent
  deleting classes or years that are still referenced.

New academic records select a managed subject, term, and academic year and
persist their stable catalog IDs with display names. Existing legacy records
without those IDs remain readable and can still be edited using their saved
text values.

### Assessments and grading

- Configure weighted or unweighted grading per academic year, with an optional
  term-specific override.
- Define assessment components and weights (for example, Coursework 40% and
  Exam 60%) and school grading bands.
- Record and maintain per-student, per-subject component scores from 0 to 100.
- Calculate a subject grade once all configured components have scores;
  weighted mode applies configured weights, while unweighted mode averages
  components equally.
- View assessment component scores in Reports and export the visible rows to CSV.

Profiles and component scores are stored separately from legacy academic
records; the existing one-score-per-subject/term/year records remain supported.

### Attendance

- Record Present, Absent, Late, or Excused attendance for a student on a date.
- Attendance is linked to the student's enrollment effective on that date;
  dates outside the academic year or enrollment are rejected.
- Prevents duplicate records for the same student and date.
- View attendance history with date, student, and class filters; select records
  to update or delete them.
- Displays status counts and an attendance percentage. Present and Late count
  as attended; Excused records are excluded from the percentage denominator.
- Student deletion also removes linked attendance records.

Attendance, explicit transfer/promotion, withdrawal, re-enrollment, and student
status are available as separate workflows. Status is Active, Inactive, or
Withdrawn; enrollment history remains effective-dated. A consolidated lifecycle
timeline/report and teacher/subject assignments are not yet available.

### Reports

- Shows student and parent or guardian contact details.
- Shows teacher contact and emergency-contact details.
- Shows academic records alongside the related student's name and class.
- Shows attendance history with counts and attendance percentage.
- Shows payment and expense entries with a financial summary.
- Filters students by ID, status, and class; teachers by ID/name; academic and
  assessment records by student filters and subject/term/year search; attendance
  by student filters, class, status, and date range; and finance by student ID,
  category, and date range.
- Exports visible report table data to CSV.
- Displays a clear empty-state row when a report has no matching records.

### Finance

- Records student payments, including partial payments, dates, amounts, and
  optional descriptions.
- Calculates expected fees from student records, received payments, remaining
  balances, and overpayments retained as student credit.
- Records, updates, and deletes categorized school expenses.
- Includes teacher salaries and other expenses in the financial summary;
  profit/loss is calculated from received income minus those expenses.
- Uses `Decimal` values and displays totals in Ghana cedis (GHS).

This is a basic cash summary, not an invoicing or accounting system. Fees are
still one expected amount per student; there are no fee schedules, invoices,
academic-period allocations, payment receipts, or audit trail.

### Validation and data handling

- Checks required fields, date format and supported age ranges, phone numbers, email format, non-negative amounts, and score range.
- Parses, rounds, persists, and totals money using `Decimal` at two decimal places; JSON stores exact decimal values as strings to avoid binary floating-point drift.
- Normalizes IDs and supports legacy field names when reading older student, teacher, and academic JSON records.
- Creates a JSON backup before saving over an existing data file.
- Writes through a temporary file and replaces the target file after a successful write.
- Reports malformed JSON and file access errors to the user instead of silently treating the file as empty.
- Emits operational log messages to stderr without writing record values or exception messages to a log file.
- Includes automated tests for core helpers, validation, storage, record services, financial calculations, and workflows.

## How the application works

### Typical workflow

1. Bootstrap the first Super Admin if needed, launch the app, and sign in. The
   dashboard then loads saved records and calculates its current summary.
2. In **Students** or **Teachers**, complete the form and choose **Add Student** or **Add Teacher**. IDs are generated when blank; otherwise enter a unique ID.
3. To edit a record, select its row in the table, change the form values, and choose **Update Selected**. The original ID is kept unchanged.
4. Use the exact-ID search controls to find a student or teacher. The Students
   tab supports class and lifecycle-status filters.
5. In **Academic Setup**, create the classes, academic years, subjects, and terms your school uses. Add a student enrollment by selecting its student, class, and year and setting its effective start date.
6. In **Academic Records**, search for and confirm a student, select a managed subject, term, and academic year, enter a score, then choose **Add Score**. Existing entries can be selected and updated or deleted.
7. In **Assessments**, configure grading components and bands for an academic year or term, enter component scores, and calculate the grade once all components are recorded.
8. In **Academic Setup → Enrollments**, use **Transfer / Promote** to close the current enrollment and create its successor, or record a withdrawal effective on the selected date.
9. In **Attendance**, choose an enrolled student, date, and status to record attendance. Filter history by date, student, or class; select a record to update or delete it.
10. In **Students**, set a student's status to Active, Inactive, or Withdrawn.
    Use the status filter and confirm reports show the selected population.
11. Open **Reports** to view linked student, teacher, academic, assessment,
    attendance, and finance data. Use the report filters for student, teacher,
    academic text, attendance status and dates, and finance category and dates.
12. In **Finance**, record payments and school expenses, then review expected
    income, received income, outstanding balances, student credit, expenses,
    and profit/loss.

Successful changes trigger refreshes of the relevant tables and summary views. Delete actions ask for confirmation. Deleting a student also removes linked academic records, assessment component scores, enrollments, and attendance records; payment history blocks deletion. These JSON file updates are sequential and are not a cross-file transaction.

### Validation rules

- Required form fields must be completed.
- Dates of birth use `YYYY-MM-DD`. Students must be between 3 and 25 years old; teachers must be between 18 and 100 years old.
- Phone numbers must contain 10 to 15 digits, optionally prefixed with `+`. Spaces and hyphens are removed when validating.
- Email addresses must follow a basic `local@domain.suffix` format.
- Fees and salaries must be numeric, finite, and non-negative.
- Academic scores must be whole numbers from 0 through 100.
- Student, teacher, and academic identifiers are compared without regard to case for lookup and duplicate checks.

## Requirements and installation

- Python 3.10 or later.
- Tkinter/ttk, normally included with standard Windows and many desktop Python distributions.
- No third-party Python packages are required to run the application or unit tests.
- The contributor baseline is Python 3.13, recorded in `.python-version`; CI tests Python 3.10 and 3.13.

Clone or download the repository, then open a terminal in the repository root. No installation is required for the application itself. To install the pinned development tools for linting, formatting, and type checking:

```powershell
python -m pip install -e ".[dev]"
```

## Run the application

Create the initial local administrator once:

```powershell
python -m telix.bootstrap_admin
```

The command prompts for the administrator name, email, and phone, then prompts
twice for a password without echoing it. Enter the Telix Super Admin details
provided by the account owner. Passwords must be at least 12 characters. The
password is never shown or stored in plaintext. Do not pass it as a
command-line argument. Alternatively, set `TELIX_SUPERADMIN_NAME`,
`TELIX_SUPERADMIN_EMAIL`, `TELIX_SUPERADMIN_PHONE`, and
`TELIX_SUPERADMIN_PASSWORD` in the environment for a controlled automated
bootstrap; unset the password variable afterward. If an account already
exists, bootstrap makes no changes.

Then launch:

From the project root:

```powershell
python .\main.py
```

Alternatively:

```powershell
python -m telix
```

On systems where the `python` launcher points to the wrong interpreter, use the full path to the desired Python executable in place of `python`.

The app requires a graphical desktop session. The current test suite does not need to open a Tkinter window.

## Run the tests

Run the complete standard-library test suite from the project root:

```powershell
python -m unittest discover -s tests -t .
```

Tests use temporary data files so they do not intentionally read or overwrite the application's local school records.

Run the configured code-quality checks with:

```powershell
ruff check .
ruff format --check .
mypy telix
```

These checks also run in GitHub Actions for pull requests and pushes.

### Manual desktop acceptance checklist

Automated Tk smoke tests cover startup, tab registration, login success/failure,
logout, and report rendering. Use the
[manual desktop acceptance checklist](tests/manual_acceptance.md) in a
disposable copy of the repository for full acceptance; do not use live school
records.

## Data files and privacy

The application reads and writes these files in the project root:

| File | Contents |
|---|---|
| `student_records.json` | Student and parent/guardian records |
| `teacher_records.json` | Teacher records |
| `academic_records.json` | Student academic records, with managed catalog IDs on newly linked records |
| `classes.json` | Managed class catalog |
| `subjects.json` | Managed subject catalog |
| `academic_years.json` | Academic-year definitions |
| `terms.json` | Terms linked to academic years |
| `enrollments.json` | Effective-dated student class enrollments |
| `attendance_records.json` | Student attendance linked to the effective enrollment |
| `assessment_records.json` | Per-student assessment component scores |
| `grading_profiles.json` | Grading components, weights, and grade bands |
| `payments.json` | Student payments and payment descriptions |
| `expenses.json` | Categorized school expense entries |
| `users.json` | Local account data; contains salted password hashes |

If a file does not exist yet, it is treated as an empty record list. Before overwriting an existing file, the application copies it to the corresponding `*.backup.json` file. Saves are written to a temporary file in the same directory and then replace the main file. A backup is a recovery aid, not a substitute for regular off-device backups.

Money is held and calculated as `Decimal` in application code. New fee and salary values are serialized as strings in JSON (for example, `"1250.50"`), preserving exact cents. Existing JSON numbers and legacy field names remain readable. A subsequent successful save writes normalized records. Invalid JSON is reported as a storage error; the app does not automatically restore a backup.

These files may contain sensitive personal information about children, families, and staff. Keep them out of public repositories and untrusted backups. The `.gitignore` excludes the record files, legacy data directory, backups, logs, Python bytecode, local environments, and the bundled `ai changes/` directory from future untracked additions. The `ai changes/` directory is personal local material: it is intentionally not part of the project source. **Ignoring a path does not untrack files already committed or staged by Git.** Check tracked files and repository history before publishing; removing a sensitive file from the latest commit does not remove it from earlier commits.

The application provides one local Super Admin login, but has no encryption at
rest, audit history, account recovery, or full role/permission management.
Keep the repository and local data files private and use operating-system
account security. The account file and its backups are ignored by Git.

## Architecture

The code is separated by responsibility:

1. **`telix/core/`** — shared validation, text normalization, identifiers, search, amount conversion, formatting, and application errors.
2. **`telix/storage/`** — JSON file persistence and a generic repository that normalizes loaded records.
3. **`telix/students/`, `telix/teachers/`, `telix/academics/`** — field definitions, legacy normalization, validation, repositories, and record-specific business rules. Academic setup and enrollment rules are implemented in `academics/structure_service.py`.
4. **`telix/attendance/`** — attendance validation, JSON repository, and service summaries linked to effective-dated enrollment.
5. **`telix/finance/`** — expected fee, payment, balance, credit, salary, expense, and profit/loss calculations with ledger repositories and services.
6. **`telix/services/`** — service construction and workflows spanning record types, including student deletion with linked academic and attendance records.
7. **`telix/authentication/`** — local account persistence, salted password
   hashing, login verification, and in-memory session state.
8. **`telix/ui/`** — the login screen, Tkinter app shell, shared tab context,
   reusable forms and tables, feedback, and one tab module per screen.

The UI calls services; services apply business rules through repositories; repositories use the JSON storage layer. This keeps validation and record rules out of screen event handlers. `telix/ui/app.py` composes the services and registers the tabs. `main.py` and `telix/__main__.py` provide the two launch commands.

## Project structure

```text
Telix_School_Management_System_new/
├── main.py
├── telix/
│   ├── __main__.py
│   ├── bootstrap_admin.py
│   ├── config.py
│   ├── authentication/
│   ├── core/
│   ├── storage/
│   ├── students/
│   ├── teachers/
│   ├── academics/
│   ├── finance/
│   ├── services/
│   └── ui/
│       ├── app.py
│       ├── feedback.py
│       ├── operations.py
│       ├── theme.py
│       ├── window.py
│       ├── tabs/
│       └── widgets/
├── tests/
├── assets/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .python-version
├── pyproject.toml
├── CHANGELOG.md
├── .gitignore
└── README.md
```

`assets/` contains application assets such as window icons. `Telix School Management System V1.md` and `Telix School Management System V2.md` preserve the project's Markdown specifications. Personal change bundles and live record files are local-only and ignored.

## Changes in the modular restructure

The modular restructure recorded in [CHANGELOG.md](CHANGELOG.md) reorganized the original flat `ui/` code into the `telix` package and moved the launch point to the project root. Its notable changes include:

- Split the single application shell into a small app composition root and separate dashboard, students, teachers, academics, reports, and finance tabs.
- Separated record schemas, normalization, validation, repositories, and business services for students, teachers, and academics.
- Consolidated JSON persistence and normalization in reusable storage components.
- Extracted shared helpers for identifiers, validation, searching, text handling, formatting, and amounts.
- Moved linked student/academic deletion into a dedicated workflow service.
- Added `unittest` coverage for core helpers, JSON storage, normalization, record services, finance calculations, and cross-record workflows.
- Removed the obsolete flat `ui/` implementation and its superseded service test, which imported old modules; the active application and tests now use `telix/`.
- Changed fees, salaries, and summary calculations to `Decimal`, serializing decimal amounts exactly as JSON strings.
- Added privacy-conscious operational logging, pinned development tooling, Ruff and mypy configuration, and a GitHub Actions quality/test workflow.
- Added ignore rules for the personal `ai changes/` bundle, generated archive, legacy data directory, backups, and logs.

The restructure is intended to preserve the existing screens, record locations, validation behavior, and application workflows while making the code easier to maintain. Existing numeric JSON amounts remain readable; newly written monetary amounts are represented as decimal strings.

## Development phases

Telix is being developed in stages. The current product is **V1: a local,
single-user desktop application**. V1.x progressively completes and hardens
that application; it is not an enterprise SaaS product. **V2 is a separate
planned evolution** into the larger multi-user, multi-tenant Telix platform.
Roadmap items below are planned unless explicitly identified as implemented.

### V1 — Local desktop school-management foundation

**Purpose:** Build a reliable, modular school-management application for
fundamental school records and workflows on one local desktop.

#### V1.0 — Core foundation

**Status: Substantially complete.** V1.0 established the current architectural
foundation:

- Python desktop application using Tkinter/ttk.
- Modular student, teacher, and academic-record domains.
- JSON persistence behind repository/service boundaries.
- Student and teacher record CRUD, search, field validation, and legacy-data
  normalization.
- Academic score records associated with students, with term/year fields and
  duplicate checks.
- Finance summary foundations using `Decimal` rather than binary floating
  point.
- Shared error handling, reusable form/table widgets, and operational logging
  that avoids record values.
- Automated unit and workflow tests, Ruff linting and formatting, mypy, and
  GitHub Actions CI.
- Ignore rules for local school records, backups, and personal change files.

“Substantially complete” describes the foundation, not completion of the full
V1 acceptance criteria below.

#### V1.1 — Core records completion

**Status: In progress.** Student and teacher create/view/search/update/delete
workflows and basic academic-record CRUD are present. The Academic Setup tab
now manages class, subject, academic-year, and term catalogs plus
effective-dated enrollments. Service tests cover core constraints and
enrollment history. Automated UI checks cover startup and report rendering,
but full GUI acceptance remains outstanding.
Remaining:

- Integration of the managed subject, term, and academic-year catalogs with
  academic records rather than relying on free-text values.
- Complete validation, meaningful errors, persistence, UI integration, and
  tests across all core records and their relationships.

#### V1.2 — Academic management

**Status: In progress.** Managed classes, subjects, academic years, terms, and
effective-dated enrollment are present in Academic Setup. New academic records
can be linked to managed subjects, terms, and academic years, while legacy
records retain their text-based compatibility. Configurable assessment
components, year/term grading profiles, weighted or unweighted grade
calculations, and assessment reporting are implemented. Teacher/subject
assignments, academic summaries, and broader academic history/reporting remain
outstanding.

This phase remains local desktop V1 work. It does not add V2 multi-tenancy,
APIs, or mobile apps.

#### V1.3 — Attendance and student lifecycle

**Status: In progress.** Attendance is implemented for Present, Absent, Late,
and Excused statuses, linked to the effective enrollment and academic year.
Explicit transfer/promotion and withdrawal actions preserve effective-dated
enrollment history, and re-enrollment can be added without overlap. Student
status (Active, Inactive, Withdrawn), status filtering, duplicate attendance
prevention, filters, summaries, and student-removal cleanup are implemented.
The consolidated lifecycle timeline, teacher/subject assignments, and full
phase acceptance remain outstanding.

#### V1.4 — Finance

**Status: In progress.** Student payment and expense records support
create/update/delete and JSON persistence. The finance summary reports expected
fees, receipts, outstanding balances, overpayment credit, salary expense,
other expenses, total expenses, and collected-cash profit/loss using `Decimal`.
Student deletion is blocked while payment history remains, avoiding an orphaned
financial record. Fee schedules, invoices, payment allocation by academic
period, audit history, and phase-wide acceptance remain outstanding.

#### V1.5 — Reports and administration

**Status: In progress.** Reports include linked student/guardian, teacher,
academic, assessment, attendance, payment, and expense data; student, teacher,
academic, attendance, and finance filters; empty-state feedback; CSV export of
displayed rows; and dashboard financial statistics. Academic performance
summaries and complete phase-wide GUI acceptance remain outstanding.

#### V1.6 — UX/UI completion

**Status: In progress.** The current application has reusable widgets,
navigation, validation feedback, delete confirmations, and table empty states.
A V1 release still needs a systematic review of navigation, layout, typography,
spacing, error states, dialogs, icons, keyboard usability, accessibility
basics, and supported desktop window sizes. Continue to prefer shared UI
components over duplicated behavior.

#### V1.7 — Testing, reliability, and release hardening

**Status: In progress.** CI currently runs tests, Ruff lint and format checks,
and mypy on Python 3.10 and 3.13. Local automated tests cover authentication,
core helpers, JSON storage, normalization, record services, finance
calculations, selected workflows, and report/login UI smoke tests. The latest
CI checks reported on the open PR failed; their logs were unavailable during
this verification. The remaining work includes resolving/confirming CI status,
broader failure-path and workflow coverage, backup/restore and financial edge
cases, full desktop acceptance, and clean-install verification.

A phase is complete only when its behavior, UI workflow, validation,
persistence, error handling, relevant tests, CI, lint, format, type checks,
and documentation meet its acceptance criteria.

#### V1.8 — Documentation and release

**Status: In progress.** This README documents the current product, its
limitations, authentication setup, and the staged V1-to-V2 boundary. Local V1
Super Admin login, logout, and secure bootstrap are implemented. Before
declaring and tagging a V1 release, complete the full acceptance criteria,
verify manual desktop workflows and clean-install behavior, confirm passing
CI, and review documentation against the shipped behavior. No V1 release tag
is claimed by this roadmap.

### V1 completion criteria

V1 is not complete until the application reliably demonstrates secure local
Super Admin login/logout/bootstrap; core student and teacher records; managed
classes, subjects, years, terms and enrollment; academics and student history;
attendance and lifecycle workflows; fees, charges, payments, balances,
expenses and accurate summaries; useful reports; coherent UI behavior;
automated unit, service, repository and workflow tests; practical GUI
acceptance coverage; passing CI/lint/format/type checks; and documentation
consistent with the implementation.

## V2 — Telix platform

V2 is a separate planned architectural stage, not functionality in this
desktop application. It is intended to evolve Telix into a multi-user,
multi-tenant school-management platform. The current V1 domain rules and
storage abstraction are inputs to that design, not proof that its features
already exist.

### Planned platform architecture

The intended direction includes Django and Django REST Framework,
PostgreSQL, Redis, Celery, a Next.js/React/TypeScript web experience with
Tailwind CSS, and Flutter mobile applications. These are roadmap technologies;
they are not current runtime dependencies.

### Planned identity and tenant capabilities

- Cross-organization identity, role-based access control, authentication
  management, and security administration beyond the single local V1 Super
  Admin.
- Role-based access control, permission scopes, organization membership, and
  audit logging, with authorization designed centrally rather than scattered
  across UI code.
- Organizations, schools, branches, tenant-isolated data, school-specific
  configuration, academic years, terms, and settings.
- Explicit, enforceable ownership boundaries for every tenant-owned record.
- A conceptual access chain of user → membership → role → permissions → scope.

### Planned applications and functional areas

The eventual platform may include a Telix Admin control plane, school web
application, teacher, student, and parent/guardian experiences, an API layer,
and mobile applications. Planned functional areas include administration,
staff, academics, attendance, assessments, grading, assignments, timetables,
finance, invoices, payments, reports, communications, notifications,
documents, analytics, search, and settings. These are V2 goals and must not
be represented as current V1 features.

## Known limitations

- The current application is local and single-user with one Super Admin
  account. It has no role/permission management, tenant isolation, or
  multi-user access. Authentication does not encrypt local JSON data at rest
  or prevent access by a person who can read the account file or application
  source on the same computer.
- Local JSON persistence has no database constraints, inter-process locking,
  or transaction spanning multiple files. Student deletion updates academic
  and student records separately and may be interrupted partway through.
- Each list operation reads its full JSON file. Backups are made during saves,
  but there is no backup/restore management UI.
- Finance tracks student payments and categorized expenses, but fees are still
  a single expected amount per student. There are no invoices, payment
  allocations by academic period, refunds, or financial audit history.
- Attendance and enrollment transitions have basic workflows but do not yet
  provide a consolidated student lifecycle timeline. Teacher/subject
  assignments remain planned; other features are not current unless stated
  above.
- The app provides no encryption at rest or audit history. Keep local record
  files private, excluded from Git, and protected by operating-system account
  security.
- Existing JSON records may be incomplete or nonstandard. Review and clean
  records before any future import; import tooling and conflict handling are
  not yet implemented.
- Automated installer/distribution packaging and real-desktop GUI acceptance
  tests are not yet in place.

## Contributing

Contributions are welcome. For substantial changes, open an issue to discuss the approach first. Keep changes focused, follow the existing package responsibilities, and add or update tests for behavior changes. Run the test suite before submitting a pull request:

```powershell
python -m unittest discover -s tests -t .
```

## License and usage

No open-source license file is currently included in this repository. Do not assume that the source or project assets may be redistributed or used commercially without permission. Contact the project owner through GitHub to discuss licensing or commercial use.

## Contact

For bug reports, feature suggestions, collaboration, or licensing questions, open an issue in the repository or contact the project owner through GitHub.
