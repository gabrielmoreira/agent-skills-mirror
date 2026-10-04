---
name: sharepoint-compare-schema-exports
plugin: sharepoint-site-assessment
description: Compares two exported SharePoint schema snapshots (lists, content types, site columns, per-list fields) and reports additions, removals and per-property changes, plus a duplicate-display-name audit. Use to answer what actually differs between two environments before a migration, a promotion or a post-deployment check. Environment labels and compared properties are caller-supplied. Read-only; consumes exports, never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from schema_diff import compare_schema_exports, render_markdown; print(render_markdown(compare_schema_exports(a, b, left_label='baseline', right_label='candidate')))\""
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from duplicate_fields import find_duplicate_fields; print(find_duplicate_fields(export).to_dict())\""
---

# Audit Schema

Compare two schema exports and report the variance; audit a single export for duplicate display names.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only by construction. It consumes exports and never contacts a tenant; there is no remediation
  or write capability, and a test asserts its absence.
- Absence is never a pass. A missing export makes the report `UNAVAILABLE`. Report `EMPTY`,
  `PARTIAL` and `UNAVAILABLE` as what they are.
- No environment names are built in. Pass your own `left_label` and `right_label`, and choose the
  compared properties yourself.
- Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from schema_export import load_schema_export
from schema_diff import compare_schema_exports, render_markdown
report = compare_schema_exports(load_schema_export('exports/baseline'),
    load_schema_export('exports/candidate'), left_label='baseline', right_label='candidate')
print(render_markdown(report))"
```

## Workflow

1. Get two export directories; see [exports and outcomes](references/schema-export-sources-and-outcomes.md).
2. Load them with `load_schema_export` and compare with `compare_schema_exports`.
3. Run `find_duplicate_fields` on an export to surface ambiguous display names.
4. Report additions, removals, per-property changes and duplicates, with each side's status.

## Verification

Check the report status is `OBSERVED` before calling the result clean. The markdown output is
deterministic, so re-running over the same inputs should diff to nothing.

## References

- [Exports and outcomes](references/schema-export-sources-and-outcomes.md): read for where exports
  come from, status meanings and comparison semantics.
- [Audit details](references/schema-audit-details.md): read for labels, the duplicate-field audit
  and the script list.
