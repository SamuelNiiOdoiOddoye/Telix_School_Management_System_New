# Telix School Management System

Telix is a desktop school-records application built with Python and Tkinter. It provides a single-user workspace for maintaining student, teacher, and academic records, viewing linked reports, and calculating a simple expected income summary.

> **Project status:** This is a local desktop application backed by JSON files. It is not yet a multi-user or hosted school-management platform. Review [Known limitations](#known-limitations-and-roadmap) and [Data handling and privacy](#data-handling-and-privacy) before using real student information.

## Contents

- [Current features](#current-features)
- [How the application works](#how-the-application-works)
- [Requirements and installation](#requirements-and-installation)
- [Run the application](#run-the-application)
- [Run the tests](#run-the-tests)
- [Data files and privacy](#data-files-and-privacy)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Changes in the modular restructure](#changes-in-the-modular-restructure)
- [Known limitations and roadmap](#known-limitations-and-roadmap)
- [Contributing](#contributing)
- [License and usage](#license-and-usage)

## Current features

### Dashboard

- Displays the number of saved students and teachers.
- Shows expected fee income and the calculated profit or loss.
- Provides quick navigation to Students, Teachers, and Academic Records.
- Refreshes the application views after successful record changes.

### Student records

- Create, view, search, update, and delete student records.
- Stores Student ID, name, date of birth, class, fees, gender, address, phone, email, medical information, and parent or guardian contact details.
- Generates an ID when the ID field is left blank; manually supplied IDs are accepted.
- Searches by Student ID and filters the table by class.
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

### Reports

- Shows student and parent or guardian contact details.
- Shows teacher contact and emergency-contact details.
- Shows academic records alongside the related student's name and class.
- Filters student and linked academic report rows by class; teacher records remain visible across classes.

### Finance summary

- Totals the fees recorded on student records as **expected fee income**.
- Totals the salaries recorded on teacher records as **teacher salary expense**.
- Calculates **profit / loss** as expected fee income minus recorded teacher salaries.
- Displays monetary values in Ghana cedis (GHS).

This is a summary of the values in the records, not an accounting ledger. It does not track payments received, outstanding balances, expenses other than teacher salaries, or financial periods.

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

1. Start the app from the project root. The dashboard loads saved records and calculates its current summary.
2. In **Students** or **Teachers**, complete the form and choose **Add Student** or **Add Teacher**. IDs are generated when blank; otherwise enter a unique ID.
3. To edit a record, select its row in the table, change the form values, and choose **Update Selected**. The original ID is kept unchanged.
4. Use the exact-ID search controls to find a student or teacher. The Students tab also supports filtering by class.
5. In **Academic Records**, search for and confirm a student, enter a subject, score, term, and academic year, then choose **Add Score**. Existing entries can be selected and updated or deleted.
6. Open **Reports** to view linked student, teacher, and academic information. Choose a class filter to narrow the student and academic views.
7. Open **Finance** to recalculate the expected fee income, teacher salary expense, and resulting profit or loss.

Successful changes trigger refreshes of the relevant tables and summary views. Delete actions ask for confirmation. Deleting a student also removes academic records linked to that student's ID.

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

## Data files and privacy

The application reads and writes these files in the project root:

| File | Contents |
|---|---|
| `student_records.json` | Student and parent/guardian records |
| `teacher_records.json` | Teacher records |
| `academic_records.json` | Student academic records |

If a file does not exist yet, it is treated as an empty record list. Before overwriting an existing file, the application copies it to the corresponding `*.backup.json` file. Saves are written to a temporary file in the same directory and then replace the main file. A backup is a recovery aid, not a substitute for regular off-device backups.

Money is held and calculated as `Decimal` in application code. New fee and salary values are serialized as strings in JSON (for example, `"1250.50"`), preserving exact cents. Existing JSON numbers and legacy field names remain readable. A subsequent successful save writes normalized records. Invalid JSON is reported as a storage error; the app does not automatically restore a backup.

These files may contain sensitive personal information about children, families, and staff. Keep them out of public repositories and untrusted backups. The `.gitignore` excludes the record files, legacy data directory, backups, logs, Python bytecode, local environments, and the bundled `ai changes/` directory from future untracked additions. The `ai changes/` directory is personal local material: it is intentionally not part of the project source. **Ignoring a path does not untrack files already committed or staged by Git.** Check tracked files and repository history before publishing; removing a sensitive file from the latest commit does not remove it from earlier commits.

The application currently provides no user accounts, access controls, encryption at rest, or audit history. Use only in a controlled local environment with appropriate operating-system account security until those protections are implemented.

## Architecture

The code is separated by responsibility:

1. **`telix/core/`** — shared validation, text normalization, identifiers, search, amount conversion, formatting, and application errors.
2. **`telix/storage/`** — JSON file persistence and a generic repository that normalizes loaded records.
3. **`telix/students/`, `telix/teachers/`, `telix/academics/`** — field definitions, legacy normalization, validation, repositories, and record-specific business rules.
4. **`telix/finance/`** — the expected-income and salary summary calculation.
5. **`telix/services/`** — service construction and workflows spanning record types, including student deletion with linked academic records.
6. **`telix/ui/`** — the Tkinter app shell, shared tab context, reusable forms and tables, feedback, and one tab module per screen.

The UI calls services; services apply business rules through repositories; repositories use the JSON storage layer. This keeps validation and record rules out of screen event handlers. `telix/ui/app.py` composes the services and registers the tabs. `main.py` and `telix/__main__.py` provide the two launch commands.

## Project structure

```text
Telix_School_Management_System_new/
├── main.py
├── telix/
│   ├── __main__.py
│   ├── config.py
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

## Known limitations and roadmap

The following are not implemented in the current application:

- User authentication, role-based permissions, and multi-user access.
- Encryption at rest, audit logging, and configurable privacy/retention controls.
- Transactional storage for operations that update multiple JSON files. Student deletion updates academic and student files separately; if the second save fails, the first may already have completed.
- A database backend, schema migration tooling, or support for concurrent writers. Each list operation reads the complete JSON file, there is no inter-process locking, and application-level ID checks do not provide database-enforced uniqueness.
- Attendance, timetable, fees received, balances, expense ledgers, and broader financial reporting.
- Report export to PDF, spreadsheet, or other formats.
- Automated installer/distribution package and real-desktop GUI acceptance tests.
- Dedicated restore/backup management UI and production operations documentation.
- Multi-tenant organization/branch scoping and scoped access to student, parent, teacher, and finance data.
- Import/data-quality tooling for legacy records. Existing JSON may contain incomplete or nonstandard records; review and clean such records before migrating them.

These items are future work, not current features. In particular, the financial summary must not be treated as a complete accounting system, and the JSON storage model should not be used for concurrent or networked multi-user operation.

## Contributing

Contributions are welcome. For substantial changes, open an issue to discuss the approach first. Keep changes focused, follow the existing package responsibilities, and add or update tests for behavior changes. Run the test suite before submitting a pull request:

```powershell
python -m unittest discover -s tests -t .
```

## License and usage

No open-source license file is currently included in this repository. Do not assume that the source or project assets may be redistributed or used commercially without permission. Contact the project owner through GitHub to discuss licensing or commercial use.

## Contact

For bug reports, feature suggestions, collaboration, or licensing questions, open an issue in the repository or contact the project owner through GitHub.
