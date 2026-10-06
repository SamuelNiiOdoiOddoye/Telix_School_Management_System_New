# Project structure

## Current runtime

This repository contains one desktop application. `main.py` and `python -m telix`
both enter `telix.ui.app.main`, which builds the Tkinter window and notebook.
The notebook registers six tabs: dashboard, students, teachers, academic
records, reports, and finance.

## Layers

- `telix/ui/`: Tkinter application shell, tab views, shared tab context, and UI
  helpers.
- `telix/services/`: application services and JSON-backed record repositories.
- `telix/students/`, `telix/teachers/`, and `telix/academics/`: domain-specific
  normalization, validation, and service behavior.
- `telix/storage/`: JSON file persistence and backup/replace behavior.
- `telix/core/`: shared validation, amount parsing, formatting, and errors.
- `telix/finance/`: financial summary calculation.
- `tests/`: unit and workflow coverage for the active modular application.

## Runtime and persistence boundaries

The desktop UI invokes synchronous services in-process. The services read and
write local JSON record files. Each file save writes a backup, writes a
temporary file, flushes it, and replaces the target; there is no cross-file
transaction or inter-process lock. Student removal updates student and
academic records separately.

The V2 document is a feature wishlist, not a current implementation or a
complete target acceptance specification. Authentication, tenant isolation,
PostgreSQL, attendance, schedules, and online fee payment are not implemented.
