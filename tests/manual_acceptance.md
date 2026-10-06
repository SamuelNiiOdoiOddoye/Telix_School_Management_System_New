# Manual desktop acceptance checklist

Use this checklist only in a disposable copy of the repository with no real
school records. The application stores JSON files beside the source code and
creates backups on writes. Do not test against a live data directory.

## Current V1 workflows

- [ ] In a disposable copy, run `python -m telix.bootstrap_demo_accounts`.
      Enter a distinct password and confirmation at each hidden prompt. Confirm
      that no password is echoed, five reserved `.invalid` accounts are created,
      and only the synthetic `DEMO-STU-001` record is added.
- [ ] Run the demo bootstrap a second time. Confirm it skips existing accounts
      without prompting for or changing their passwords or overwriting the
      synthetic student record.
- [ ] Log in separately as each demo role. Confirm the role comes from the
      account, not a login selector, and each role sees only its allowed tabs.
- [ ] As Teacher, confirm student details omit family/medical contact data and
      student-management controls are disabled; confirm direct writes are
      rejected by services.
- [ ] As Finance Officer, confirm only financial reports/finance workflows are
      shown and teacher personal details and academic records are inaccessible.
- [ ] As Student, confirm the Reports view includes only the linked
      `DEMO-STU-001` data. Attempt to query another student ID through the
      service boundary and confirm access is rejected or returns no matching
      record. Confirm finance, teacher, and school-wide reports are inaccessible.
- [ ] Log out from each role and confirm the session is cleared and login is
      shown before the protected workspace.
- [ ] In a disposable checkout with no `users.json`, run
      `python -m telix.bootstrap_admin`. Enter the assigned Super Admin name,
      email, and phone; enter a unique password of at least 12 characters at
      both hidden prompts. Confirm the command reports account creation without
      echoing the password and creates an ignored `users.json`.
- [ ] Run bootstrap again and confirm it does not prompt for or replace the
      existing account.
- [ ] Launch with `python .\main.py` and verify login appears before any school
      management tabs. Try an unknown email, wrong password, and the correct
      email with different letter casing. Failures should show the same generic
      error; only valid credentials should open the workspace.
- [ ] Launch with `python .\main.py` and confirm the window opens with
      Dashboard, Students, Teachers, Academic Records, Assessments, Academic
      Setup, Attendance, Reports, and Finance tabs.
- [ ] Add a synthetic student (for example, ID `TEST-STU-001`, name `Test
      Student`, date of birth `2014-05-04`, class `Grade 1`, fee `125.50`,
      gender `Other`, address `Test Address`, phone `+10000000001`, email
      `student@example.invalid`, medical information `None`, parent/guardian
      name `Test Guardian`, and parent/guardian phone `+10000000003`).
- [ ] Search for that student by ID and verify the row and form are populated.
- [ ] Change the student status to Inactive and verify the status filter and
      Reports table; change it back to Active. Withdraw the student and confirm
      that reactivation must be explicit before setting Active again.
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
- [ ] In Academic Setup, add class `Grade 1`, subject `Mathematics` with code
      `TEST-MATH`, academic year `2026/2027` (2026-09-01 through 2027-06-30),
      and Term 1 (2026-09-01 through 2026-12-20).
- [ ] In Academic Setup > Teacher Assignments, assign `TEST-TCH-001` to
      `Mathematics` for `2026/2027`. Confirm the assignment appears in the
      table, a duplicate assignment is rejected, and deleting the assigned
      teacher, subject, or academic year is blocked until the assignment is
      deleted. Delete the assignment after verifying those protections.
- [ ] Add an academic record for `TEST-STU-001` with managed subject
      `Mathematics`, score `80`, managed Term 1, and academic year `2026/2027`.
      Confirm it appears in the table and linked Reports view.
- [ ] Add a second subject score for the same student and period. Search for
      the student and confirm Academic Records shows the correct subject count
      and average for that saved year and term. Rename a catalog label and
      confirm the existing score's historical period labels remain unchanged.
- [ ] In Assessments, save a 2026/2027 grading profile with weighted
      components `Coursework=40, Exam=60` and bands
      `0=F:Needs improvement;50=C:Satisfactory;80=A:Excellent`. Add component
      scores 90 and 70 for the test student in Mathematics, then calculate the
      grade and confirm the score is 78.00 and the grade is C. Export the
      assessment report to CSV.
- [ ] Add an enrollment linking `TEST-STU-001` to that class and academic year
      starting 2026-09-01. Verify the row and its IDs remain stable after
      refresh.
- [ ] Record Present attendance for `TEST-STU-001` on 2026-10-06. Confirm it is
      linked to the enrollment, appears in Attendance history, and contributes
      to the summary. Try Absent for the same date and confirm it is rejected as
      a duplicate. Record Late on 2026-10-07 and Excused on 2026-10-08; verify
      filters and that Excused does not affect the attendance percentage.
- [ ] Select the 2026-10-07 record, update its status to Present, then delete
      that record and confirm the history and summary update. Try recording
      attendance before the enrollment start and after the academic year ends;
      both should be rejected.
- [ ] Attempt a second overlapping enrollment for the student in the same
      year and confirm it is rejected.
- [ ] Transfer/promote the test student to `Grade 2` effective 2027-01-15.
      Confirm the original enrollment ends 2027-01-14 with transferred status
      and the new enrollment starts on the selected date. In a separate test,
      withdraw on a selected effective date and confirm the enrollment history
      remains visible.
- [ ] Attempt a term outside the academic-year dates and confirm it is
      rejected. Attempt to delete the referenced class/year and confirm it is
      protected.
- [ ] In Finance, record two partial payments totaling less than the student's
      expected fee. Verify received income and outstanding balance. Add a
      payment that takes the total above the expected fee and verify the excess
      appears as student credit. Select and update a payment, then verify the
      balance recalculates.
- [ ] Add a categorized school expense and verify it affects other expenses,
      total expenses, and profit/loss. Select/update/delete the expense and
      confirm the summary changes.
- [ ] Verify the dashboard shows total expenses as salaries plus other
      expenses, and that the displayed profit/loss matches collected payments
      less total expenses.
- [ ] Open Reports and check the attendance and financial tables. Export the
      student, academic, attendance, and finance reports to CSV; verify each
      file has headings and the visible report rows.
- [ ] Filter Reports by student ID/status, teacher ID/name, academic
      subject/term/year, attendance status/date range, and finance category/date
      range. Verify each filter independently and confirm unmatched filters show
      an empty-state message rather than stale rows.
- [ ] Close and relaunch the application while the synthetic records still
      exist. Log in and confirm the saved student, teacher, assessment,
      attendance, and finance entries persist.
- [ ] Attempt to delete the student while a payment exists. Confirm deletion is
      blocked and the student's academic/enrollment/attendance data remains.
- [ ] Delete the test payments before deleting the student; verify finance
      totals recalculate.
- [ ] Delete the test student and confirm the UI removes the linked academic
      record, assessment scores, enrollment, and attendance records. Verify
      unrelated test teacher data remains.
- [ ] Delete the test teacher after confirming the deletion prompt.
- [ ] Delete test Term 1, `TEST-MATH`, `Grade 1`, and the test academic year
      after confirming the enrollment has been removed.
- [ ] Close and relaunch the application; confirm the disposable records are
      gone and no unexpected errors appeared.
- [ ] Log out and confirm the login screen returns and the protected tabs are
      no longer visible. Log in again and confirm deleted synthetic records do
      not reappear.

## Not yet available for manual acceptance

A consolidated student-status and enrollment lifecycle timeline, invoices, and
academic-period payment allocations remain roadmap items. Automated service
and UI smoke tests do not replace the real-desktop checklist above.
