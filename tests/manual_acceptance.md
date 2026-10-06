# Manual desktop acceptance checklist

Use this checklist only in a disposable copy of the repository with no real
school records. The application stores JSON files beside the source code and
creates backups on writes. Do not test against a live data directory.

## Current V1 workflows

- [ ] Launch with `python .\main.py` and confirm the window opens with
      Dashboard, Students, Teachers, Academic Records, Academic Setup, Reports,
      and Finance tabs.
- [ ] Add a synthetic student (for example, ID `TEST-STU-001`, name `Test
      Student`, date of birth `2014-05-04`, class `Grade 1`, fee `125.50`,
      gender `Other`, address `Test Address`, phone `+10000000001`, email
      `student@example.invalid`, medical information `None`, parent/guardian
      name `Test Guardian`, and parent/guardian phone `+10000000003`).
- [ ] Search for that student by ID and verify the row and form are populated.
- [ ] Change a non-ID field, update the record, and verify the changed value
      persists after navigating away and returning.
- [ ] Attempt to add a duplicate student ID and confirm a clear validation
      message is shown.
- [ ] Add a synthetic teacher (for example, ID `TEST-TCH-001`, name `Test
      Teacher`, date of birth `1980-05-04`, class/subject `Mathematics`, salary
      `50.25`, gender `Other`, address `Test Address`, phone `+10000000002`,
      email `teacher@example.invalid`, medical information `None`, and
      emergency contact `+10000000004`); search, update, and verify it in
      Reports.
- [ ] Add an academic record for `TEST-STU-001` with subject `Mathematics`,
      score `80`, term `Term 1`, and academic year `2026/2027`. Confirm it
      appears in the table and linked Reports view.
- [ ] In Academic Setup, add class `Grade 1`, subject `Mathematics` with code
      `TEST-MATH`, academic year `2026/2027` (2026-09-01 through 2027-06-30),
      and Term 1 (2026-09-01 through 2026-12-20).
- [ ] Add an enrollment linking `TEST-STU-001` to that class and academic year
      starting 2026-09-01. Verify the row and its IDs remain stable after
      refresh.
- [ ] Attempt a second overlapping enrollment for the student in the same
      year and confirm it is rejected.
- [ ] Attempt a term outside the academic-year dates and confirm it is
      rejected. Attempt to delete the referenced class/year and confirm it is
      protected.
- [ ] Open Finance and verify the current estimate uses the recorded student
      fee and teacher salary. This is not a payment or accounting workflow.
- [ ] Delete the test student and confirm the UI removes the linked academic
      record and enrollment. Verify unrelated test teacher data remains.
- [ ] Delete the test teacher after confirming the deletion prompt.
- [ ] Delete test Term 1, `TEST-MATH`, `Grade 1`, and the test academic year
      after confirming the enrollment has been removed.
- [ ] Close and relaunch the application; confirm the disposable records are
      gone and no unexpected errors appeared.

## Not yet available for manual acceptance

Attendance, teacher/subject assignments, assessments and grade calculations,
student transfers/promotions as dedicated workflows, invoices, payments,
balances, expenses, and their reports are roadmap items. Do not mark those
items accepted until their UI and service workflows are implemented and
tested.
