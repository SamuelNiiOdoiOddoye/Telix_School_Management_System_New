# Changelog

Every change to this project is recorded here, newest first. Format: [Keep a Changelog](https://keepachangelog.com/). Versions follow `MAJOR.MINOR.PATCH`.

**How to add an entry:** add a new `## [version] - date` section at the top, group changes under *Added*, *Changed*, *Fixed*, *Removed* or *Security*, and say *why* when it is not obvious. If a change moves or renames files, add rows to a mapping table so nothing is lost.

---

## [1.1.0] - 2026-10-05: Modular restructure

Goal: stop mixing responsibilities. Before this release one `SchoolManagementSystem` class built every screen and handled every button, and each `*Service` class also did file access, legacy-key conversion, validation and business rules. Now each module, class and function has one main job.

Record formats, file locations, validation rules, error messages and the screens themselves are **unchanged**.

### Changed

- **Project layout.** All code moved from the flat `ui/` folder (which also held non-UI code) into the `telix/` package with layered sub-packages: `core`, `storage`, `students`, `teachers`, `academics`, `finance`, `services`, `ui`.
- **Entry point.** Run `python main.py` (or `python -m telix`) instead of `python ui\main.py`. Imports are now absolute (`from telix.core.errors import ...`) so they no longer depend on the folder the app is started from.
- **Services split by responsibility.** `StudentService`, `TeacherService` and `AcademicRecordService` now only apply business rules. Their other jobs moved to `schema`, `normaliser`, `validator`, `rules`, `repository` modules in each record package.
- **Storage.** `JsonStore.save` was split into small steps (`_create_backup`, `_write_temporary_file`, `_discard`). A new generic `JsonRecordRepository` replaces three copies of "load, skip non-dicts, normalise".
- **User interface.** The single large `main.py` class became one class per tab (`DashboardTab`, `StudentsTab`, `TeachersTab`, `AcademicsTab`, `ReportsTab`, `FinanceTab`) on a common `BaseTab`. Tabs get what they need through a `TabContext` and no longer reach into each other. `app.py` only creates the window and registers the tabs.
- **Cross-record delete.** "Delete student and their academic records" is now its own workflow, `StudentRemovalService`, instead of a nested function inside the UI.
- **Dashboard and Finance.** Each tab now calculates and displays only its own figures. Previously one refresh method wrote into both tabs.
- **Reports tab** now refreshes its own class-filter list (it was previously updated as a side effect of refreshing students).
- **Duplicated code removed:** `_first_value` (was in two modules), the find-by-ID loops (were repeated in six places), the uniqueness-key tuple (was written twice), form/button/table construction (was repeated per tab), and the three separate load-and-normalise `list()` implementations.
- **Magic numbers named:** student and teacher age limits are now constants in their validators.
- `README.md` updated: run command, architecture, project structure, how to add a record type or screen, how to run tests.

### Added

- `tests/`: 40 `unittest` tests (standard library only) covering validators, helpers, JSON store, legacy-key normalising, all three services, the finance summary, and student removal. Run with `python -m unittest discover -s tests -t .`.
- `StudentService.exists()` (used by the academic records tab instead of an inline lambda).
- `core.search.find_index_by_id`, `core.numbers.as_amount`, `academics.defaults.default_academic_year`.
- `calculate_age` and an optional `today` argument on `validate_date_of_birth`, so age rules are testable on any date.
- This changelog.

### Fixed

- **Temp-file leak:** if saving failed while serialising (for example an unserialisable value), the temporary file beside the data file was left behind. It is now removed. (Covered by a test.)
- **Unhandled storage error on student delete:** the student delete flow looked up the record without catching `StorageError` (the teacher flow did). A corrupt file now shows the friendly message instead of an unhandled exception.
- **Crash on non-numeric stored amounts:** the Students and Teachers tables converted `fees` / `salary` with `float()` directly and would raise on a bad value in a record file. They now use the same tolerant conversion as the finance summary (unreadable values show as `GHS 0.00`).

### Removed

- The `ui/` folder (replaced by `telix/`; see the mapping below). Delete it after copying the new files.

### Where things went

| Old location | New location |
|---|---|
| `ui/main.py` (`SchoolManagementSystem`) | `main.py`, `telix/ui/app.py`, `telix/ui/tabs/*.py`, `telix/ui/theme.py`, `telix/ui/window.py`, `telix/ui/feedback.py`, `telix/ui/operations.py`, `telix/ui/widgets/*.py` |
| `ui/config.py` | `telix/config.py` |
| `ui/database.py` (`JsonStore`, `StorageError`) | `telix/storage/json_store.py`, `telix/core/errors.py` |
| `ui/utils.py` | `telix/core/errors.py` (`ValidationError`), `telix/core/text.py` (`clean_text`), `telix/core/identifiers.py` (`generate_id`), `telix/core/formatting.py` (`format_currency`), `telix/core/validators.py` (all `validate_*`, `require_fields`) |
| `ui/search.py` | `telix/core/search.py` |
| `ui/students.py` | `telix/students/{schema,normaliser,validator,repository,service}.py` |
| `ui/teachers.py` | `telix/teachers/{schema,normaliser,validator,repository,service}.py` |
| `ui/academic_records.py` | `telix/academics/{schema,normaliser,validator,rules,defaults,repository,service}.py` |
| `ui/finance.py` | `telix/finance/summary.py` |
| (new) | `telix/services/{container,student_removal}.py`, `telix/storage/repository.py`, `telix/core/numbers.py`, `tests/` |

### Action required by the project owner

1. **Apply the change in Git.** Copy the new files into the repository, delete the old `ui/` folder, then commit, for example:
   ```powershell
   git rm -r ui
   git add main.py telix tests README.md CHANGELOG.md
   git commit -m "refactor: split application into single-purpose modules"
   ```
2. **Stop tracking sensitive and generated files.** The public repository's file list shows `student_records.json` and a `__pycache__` folder at the top level. Run:
   ```powershell
   git rm --cached student_records.json
   git rm -r --cached __pycache__
   git commit -m "chore: stop tracking records and bytecode"
   ```
   If `student_records.json` ever held real names, phone numbers or emails, they remain in the Git history and on the public GitHub page until the history is rewritten (for example with `git filter-repo`). Treat that data as exposed.
3. **Run the app once on a real display** (`python main.py`) and click through each tab. The new tests cover all non-UI logic, and the UI wiring was exercised against a stand-in for Tkinter, but it has not been run on a real window yet.

### Known limitations (unchanged by this release)

- Deleting a student writes two files (academic records, then students). If the second write fails, the first stays applied. A database transaction in a later version removes this risk.
- Every `list()` call re-reads the whole JSON file; fine for a small school, not for large data.
- `Application Load Files/`, the `.docx`/`.md` planning documents and the `assets/` folder were not modified.

---

## [1.0.0] - before 2026-10-05: V1 desktop application

Recorded retrospectively from the README and the V1 task list.

- Tkinter desktop application with Dashboard, Students, Teachers, Academic Records, Reports and Finance tabs.
- JSON persistence with an automatic backup before every save and atomic file replacement.
- Validation for required fields, dates of birth and ages, phone numbers, emails, scores, and duplicate IDs.
- Search by Student ID or Teacher ID, class filter, delete confirmations, window icon.
- `.gitignore` entries for record files and backups.
