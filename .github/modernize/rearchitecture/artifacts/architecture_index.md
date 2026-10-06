# Architecture assessment index

This index describes the current modular V1 runtime and frames the stated
Django/PostgreSQL multi-tenant direction. It does not claim that the V2
wishlist has been implemented or that an executable migration plan is complete.

## Global artifacts

- [Project structure](./project-structure.md)
- [Technology stack](./tech-stack.md)
- [Observed data model](./data-model.md)
- [Unit graph](./unit_graph.yaml)
- [Migration boundary](./migration_boundary.yaml)
- [Wire contracts](./wire_contracts.yaml)
- [Shared modules](./shared_modules.yaml)
- [Cross-unit state](./cross_unit_state.yaml)

## Unit artifacts

| Unit | Behavior | Bindings | Decomposition |
|---|---|---|---|
| Startup | [behavior](./units/startup/behavior.yaml) | [bindings](./units/startup/bindings.yaml) | [decomposition](./units/startup/unit_decomposition.yaml) |
| Dashboard | [behavior](./units/dashboard/behavior.yaml) | [bindings](./units/dashboard/bindings.yaml) | [decomposition](./units/dashboard/unit_decomposition.yaml) |
| Student records | [behavior](./units/student-records/behavior.yaml) | [bindings](./units/student-records/bindings.yaml) | [decomposition](./units/student-records/unit_decomposition.yaml) |
| Teacher records | [behavior](./units/teacher-records/behavior.yaml) | [bindings](./units/teacher-records/bindings.yaml) | [decomposition](./units/teacher-records/unit_decomposition.yaml) |
| Academic records | [behavior](./units/academic-records/behavior.yaml) | [bindings](./units/academic-records/bindings.yaml) | [decomposition](./units/academic-records/unit_decomposition.yaml) |
| Reports | [behavior](./units/reports/behavior.yaml) | [bindings](./units/reports/bindings.yaml) | [decomposition](./units/reports/unit_decomposition.yaml) |
| Finance | [behavior](./units/finance/behavior.yaml) | [bindings](./units/finance/bindings.yaml) | [decomposition](./units/finance/unit_decomposition.yaml) |

## Assessment findings

- Implemented now: local Tkinter CRUD and summaries backed by JSON; shared
  validation; backup/temporary-file replacement for individual JSON saves.
- Known limitations: no authentication, roles, tenant isolation, database
  transactions, audit trail, or relational constraints; finance is not a
  ledger.
- Target direction: Django, PostgreSQL, and multi-tenancy, as separately stated
  by the user. The V2 document is an aspirational feature list, not sufficient
  acceptance criteria for all target workflows.
- Data import is a required design topic. Existing normalizers and tests are
  candidate references; malformed records and conflicts need an explicit
  quarantine/reporting policy.
- Do not delete or rewrite local record files as part of this assessment.
