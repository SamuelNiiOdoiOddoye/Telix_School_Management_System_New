Telix School Management System V1 finishing

In V1 Fix the following :

&#x09;1. Continue and make the modify student record work

&#x09;2. Continue the modify academic records and make it work

&#x09;3. Save all other records into teacher and student json record files respectively

&#x09;4. After the deletion of a record it should actually be deleted

&#x09;5. Use student id's for search keys to prevent wrong selections

&#x09;6. Use .gitignore on student and teacher record files because of their level of sensitivity

***CORE FUNCTIONALITY***

&#x09;*- Add Student*

&#x09;*- Add Teacher*

&#x09;*- Edit Student*

&#x09;*- Delete Student*

&#x09;*- Delete Teacher*

&#x09;*- Search Functionality for students and teachers by either student\_id or teacher\_id*

&#x09;*- View records by class of the student*

&#x09;*- Profit / Loss Calculation*

***DATA VALIDATION***

&#x09;*- Prevent empty fields from being submitted*

&#x09;*- validate ages*

&#x09;*- validate phone numbers*

&#x09;*- prevent duplicate student id's*

&#x09;*- prevent duplicate teacher id's*

&#x09;*- friendly error messages instead of crashes*

**UI IMPROVEMENTS**

&#x09;- confirmation before deleting records

&#x09;- application icons

**BETTER FILE STRUCTURE**

&#x09;*- main.py*

&#x09;*- students.py*

&#x09;*- teachers.py*

&#x09;*- finance.py*

&#x09;*- utils.py*

&#x09;*- database.py*

&#x09;*- assets/*

**DOCUMENTATION**

&#x09;*- create README.md (include screenshots, features, installation, technologies used, future improvements)*

**ERROR HANDLING**

&#x09;**-** *use "try except"*

&#x09;*- automatic backup of the JSON data before writing*

&#x09;*- remove duplicated code*

&#x09;*- better function names*

&#x09;*- comments where necessary*

&#x09;*- remove unused variables*

**PORTFOLIO QUALITY**

&#x09;*- Dashboard*

&#x09;*- Student Page*

&#x09;*- Teacher Page*

&#x09;*- Finance Page*

&#x09;*- Reports*

&#x09;

**LINK ALL TABLES SO WE CAN SEE OUTPUTS FOR SOMETHING LIKE STUDENT DETAILS, PARENT DETAILS, TEACHER DETAILS, ACADEMIC RECORDS AND ALL OTHER RELEVANT DATA**

## V1 local authentication and release-hardening addition (2026-10-06)

The local desktop app requires a Super Admin login before opening the school
workspace. The initial account is created with `python -m
telix.bootstrap_admin`; the password is entered through a hidden prompt and
stored only as a salted `scrypt` hash in the ignored local `users.json` file.
Login errors do not distinguish missing users from incorrect passwords, and
logout clears the in-memory session.

This addition uses local JSON-backed authentication and V1 roles only. It does
not introduce V2 organizations, tenant isolation, hosted services, APIs,
multi-tenant permission scopes, or subscription behavior. The local JSON data
remains unencrypted at rest and accessible to operating-system users who can
read the files. Full V1 manual acceptance and release checks are still required
before calling V1 release-ready.

## Current V1 account-management addition

Super Admins and Admins can open the V1 User Management tab. Super Admins can
assign the supported V1 roles. Admins can manage Teacher, Finance Officer, and
Student accounts, but cannot view or manage Admin/Super Admin accounts or
create/promote a Super Admin. Student accounts require an existing linked
student record. Administrators can update contact/role information and
activate/deactivate accounts; passwords are never displayed, and the last
active Super Admin cannot be deactivated or demoted.

For a disposable development checkout only, `python -m
telix.bootstrap_demo_accounts --portfolio-only` creates the synthetic Teacher
account `demo-teacher@telix.example.invalid` with password `TelixDemo!2026`.
These public portfolio credentials are not for production use. The bootstrap
does not reset an existing account password. Do not run the demo bootstrap
against production data.
