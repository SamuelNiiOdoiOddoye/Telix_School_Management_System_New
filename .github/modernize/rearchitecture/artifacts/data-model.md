# Data model (observed)

The active V1 model consists of records represented as dictionaries and stored
in JSON lists. There is no database schema, foreign-key enforcement, academic
year entity, branch entity, tenant entity, or effective-dated enrollment.

## Record groups

- **Student**: student identifier, name, date of birth/age-related inputs,
  class text, contact/guardian fields, and fee-related amount. The stored
  student identifier is used to associate academic records.
- **Teacher**: teacher identifier and personal/contact fields plus the
  financial amount used in the current summary.
- **Academic record**: academic identifier, student identifier, subject, term,
  academic year, and score. Service validation uses the student lookup and
  enforces the student/subject/term/year uniqueness rule.

Exact optional fields and legacy aliases are handled by the domain normalizers;
they are not equivalent to database constraints. Medical information, where
present in existing records, is plain text.

## Relationships and integrity

- Academic records refer to students by identifier; the relationship is
  application-enforced rather than a foreign key.
- Student removal also removes associated academic records, but writes the two
  JSON files sequentially without a shared transaction.
- Identifiers and uniqueness are enforced in application code only.
- Classes are free text. There are no Branch, Academic Year, Guardian, Invoice,
  Payment, or Ledger entities.
- Finance is a summary over stored student/teacher amounts, not an invoice and
  payment ledger. The displayed profit/loss is therefore an estimate.

## Target-design gaps

The V2 wishlist mentions fee-payment history, attendance, timetables, report
cards, enrollment history, and student photos. The intended Django/PostgreSQL
multi-tenant design additionally needs explicit tenant/branch boundaries and
scoped permissions. A normalized target schema, retention policy, import
conflict policy, and financial accounting rules remain to be specified; this
assessment does not invent them.
