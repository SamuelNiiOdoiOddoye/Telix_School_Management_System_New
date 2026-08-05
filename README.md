# Telix School Management System V1

Telix School Management System is a desktop application for keeping student, teacher, academic, and finance records in one place. V1 is built with Python and Tkinter and stores operational data locally in JSON files.

## Features

- Dashboard with student and teacher totals plus expected profit or loss
- Student records with parent or guardian contact details
- Teacher records with salary and emergency contact details
- Add, select, edit, and delete student and teacher records
- Search students strictly by Student ID and teachers strictly by Teacher ID
- View student records by class
- Academic records linked to a student by Student ID
- Add, edit, and delete academic scores for any subject, term, and academic year
- Linked reports for student and parent details, teacher details, and academic results
- Profit or loss calculation from student fees less teacher salaries
- Validation for required fields, dates of birth, ages, phone numbers, emails, scores, and duplicate IDs
- Confirmation before every deletion and friendly error messages for invalid input
- Automatic JSON backup before each successful save

## Screenshots

Run the application and capture the Dashboard, Students, Teachers, Academic Records, Reports, and Finance tabs before publishing the project. Save screenshots under `assets/screenshots/` and add them to this section.

## Requirements

- Python 3.10 or later
- Tkinter, which is included with standard Windows Python installations

No third-party packages are required for V1.

## Run Locally

Clone the repository, open a terminal in the project directory, then run:

```powershell
python .\ui\main.py
```

With a specific Python installation, use:

```powershell
& "C:\Program Files\Python313\python.exe" .\ui\main.py
```

## How To Use V1

1. Add students and teachers from their respective tabs. IDs are generated automatically but can be replaced with your own unique IDs before saving.
2. Click a table row to load its values into the form, edit the required fields, then choose **Update Selected**.
3. Search by an exact Student ID or Teacher ID to avoid matching the wrong person.
4. Add academic scores using a valid Student ID. Each student, subject, term, and academic year combination is unique.
5. Open **Reports** to see linked student, parent, teacher, and academic information. Use the class filter to narrow student-related reports.
6. Open **Finance** to see expected fee income, teacher salary expense, and profit or loss.

## Data and Privacy

Local records are stored at the project root:

- `student_records.json`
- `teacher_records.json`
- `academic_records.json`

Each save creates or refreshes a matching `*.backup.json` file first. The included `.gitignore` protects new record files and backups because they can contain sensitive personal information. Do not commit real student or teacher data to a public repository.

If `student_records.json` was committed before adding `.gitignore`, run the following once from your own terminal. It keeps the local file but removes it from future Git commits:

```powershell
git rm --cached student_records.json
git commit -m "Stop tracking sensitive student records"
```

If the file was already pushed to a public repository, remove the sensitive data from the repository history before sharing the project further.

## Project Structure

```text
Telix_School_Management_System_new/
├── assets/
│   └── images/
├── ui/
│   ├── main.py                 # Tkinter tabs and user workflows
│   ├── students.py             # Student record service
│   ├── teachers.py             # Teacher record service
│   ├── academic_records.py     # Academic record service
│   ├── finance.py              # Profit/loss calculation
│   ├── database.py             # JSON storage and backups
│   ├── search.py               # ID and class search helpers
│   ├── utils.py                # Validation and formatting helpers
│   └── config.py               # Paths and application assets
├── .gitignore
└── README.md
```

## Technologies

- Python
- Tkinter and ttk
- JSON file storage
- Object-oriented application structure

## Future Improvements

- User authentication and role-based access
- SQLite or hosted database support
- Attendance, timetable, and report-card modules
- Fee payment and expense transaction ledgers
- Export reports to PDF and Excel
- Automated tests and continuous integration
