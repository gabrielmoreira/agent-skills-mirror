# Policy Templates — Index

Evidence levels differ by file. Prefer API 69.0 retrieved examples for OLS, FLS deny, masking, and RLS; treat remaining templates as fixture-only references that require target-org validation.

| File | What's inside |
|------|---------------|
| [`templates-access.md`](templates-access.md) | ACCESS and GOVERNANCE: simple Permit, TupleRead "objects + all fields", tag/classification/permission gates |
| [`templates-record.md`](templates-record.md) | RECORD: basic RLS (record field = user attribute), RLS via PROJECTION join |
| [`templates-transform.md`](templates-transform.md) | TRANSFORM: field masking gates and validated `LAST_N_CHARS` ARGLIST shape |
| [`templates-advanced.md`](templates-advanced.md) | Multi-condition with custom conjunction (AND/OR mix), hierarchy traversal, IDENTIFIED_RECORD (not authorable via MDAPI) |
