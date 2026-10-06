# Manual desktop acceptance checklist

Use this checklist only in a disposable copy of the repository with no real
school records. The application stores JSON files beside the source code and
creates backups on writes. Do not test against a live data directory.

## Current V1 workflows

- [ ] Launch with `python .\main.py` and confirm the window opens with
      Dashboard, Students, Teachers, Academic Records, Assessments, Academic
      Setup, Attendance, Reports, and Finance tabs.
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
- [ ] In Academic Setup, add class `Grade 1`, subject `Mathematics` with code
      `TEST-MATH`, academic year `2026/2027` (2026-09-01 through 2027-06-30),
      and Term 1 (2026-09-01 through 2026-12-20).
- [ ] Add an academic record for `TEST-STU-001` with managed subject
      `Mathematics`, score `80`, managed Term 1, and academic year `2026/2027`.
      Confirm it appears in the table and linked Reports view.
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
- [ ] Open Reports and check the attendance and financial tables. Export the
      student, academic, attendance, and finance reports to CSV; verify each
      file has headings and the visible report rows.
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

## Not yet available for manual acceptance

Teacher/subject assignments, dedicated student transfers/promotions/withdrawals,
invoices and academic-period payment allocations remain roadmap items. Do not
mark those items accepted until their UI and service workflows are implemented
and tested. Attendance's automated service tests do not replace the real-desktop
checklist above.
