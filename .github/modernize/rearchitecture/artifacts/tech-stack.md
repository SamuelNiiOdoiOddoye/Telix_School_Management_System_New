# Technology stack

## Observed implementation

- Language/runtime: Python; `.python-version` pins the development baseline to
  Python 3.13.
- UI: synchronous desktop application using Python's Tkinter and ttk.
- Persistence: JSON files on the local filesystem, with per-file backups and
  temporary-file replacement.
- Money: `Decimal` in parsing, validation, and financial aggregation; JSON
  monetary values are serialized as decimal strings.
- Quality tooling: unittest, Ruff, mypy, and GitHub Actions CI, configured in
  `pyproject.toml` and `.github/workflows/ci.yml`.

## Not observed / future direction

The current runtime has no Django web server, ORM, PostgreSQL database,
authentication service, tenant middleware, or API. The project V2 document
mentions replacing JSON with SQLite and later PostgreSQL. The user separately
identified Django, PostgreSQL, and multi-tenancy as the intended rebuild
direction. Those are target constraints for future design, not implemented
dependencies.

## Migration implication

The desktop presentation and local file persistence need replacement for a
web/multi-tenant deployment. Existing domain validators, normalizers, and
service behavior are candidate inputs to the rebuild, but compatibility and
data-import behavior must be verified rather than assumed.
