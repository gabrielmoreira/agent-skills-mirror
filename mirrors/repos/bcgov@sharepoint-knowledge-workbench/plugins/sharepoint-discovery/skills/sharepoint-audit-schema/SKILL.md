---
name: sharepoint-audit-schema
plugin: sharepoint-schema
description: Compares two exported SharePoint schema snapshots (lists, content types, site columns, per-list fields) and reports additions, removals, and per-property changes, plus a duplicate-display-name audit. Environment labels and compared properties are caller-supplied. Read-only -- consumes exports, never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python -c \"from schema_diff import compare_schema_exports, render_markdown; print(render_markdown(compare_schema_exports(a, b, left_label='baseline', right_label='candidate')))\""
  - "python -c \"from duplicate_fields import find_duplicate_fields; print(find_duplicate_fields(export).to_dict())\""
---

# Audit Schema

## Trigger and Purpose

Use this skill to answer "what actually differs between these two SharePoint
environments?" before a migration, a promotion, or a post-deployment check. It
compares two schema exports and reports the variance; it also audits a single
export for duplicate display names, a common cause of ambiguous column
references.

## Where the exported schema comes from

This skill consumes an already-exported schema directory tree
(`<dir>/summary/lists.json`, `<dir>/lists/<listname>/fields.json`, etc. — see
`schema_export.py`'s `ExportLayout`). That tree is produced by
`sharepoint-discovery`'s `collect-sharepoint-inventory` skill running
`collect-sharepoint-schema-export.ps1` against a live tenant — this plugin
never connects to a tenant itself. Run that script first if you don't
already have an export directory.

## No environment names are built in

`compare_schema_exports(left, right, left_label=..., right_label=...)` takes
**caller-supplied labels**. There is no built-in notion of "prod", "test", or
any specific environment — the source implementation this was extracted from
hardcoded its own environment pair, and that is removed. Which properties are
compared is likewise a caller parameter.

## Honest outcomes -- absence is never a pass

`SectionStatus` distinguishes the states a naive tool conflates:

| Status | Meaning |
|---|---|
| `OBSERVED` | Section read, content present |
| `EMPTY` | Read successfully, genuinely nothing there |
| `PARTIAL` | Some sub-items unreadable; recorded, not hidden |
| `UNAVAILABLE` | Export or section missing entirely |

A missing export makes the report `UNAVAILABLE`, **never a clean pass**. A list
present on only one side is reported, never silently dropped. Duplicate keys
are surfaced as an ambiguity rather than resolved by guessing, and items
missing the comparison key are recorded rather than skipped silently.

`render_markdown` output is deterministic and carries no timestamp or host
identifier, so two runs over the same inputs diff cleanly.

## Duplicate-field audit

`find_duplicate_fields` flags two internal names sharing one display name. The
builtin-column exclusion list is **caller-configurable**; read-only columns are
excluded; fields without a display name are surfaced rather than guessed.

**Read-only by construction.** The source script carried a `-Cleanup` switch
that deleted fields. **No remediation or write capability exists here**, and a
test asserts its absence.

## Usage

```bash
python -c "
from schema_export import load_schema_export
from schema_diff import compare_schema_exports, render_markdown
report = compare_schema_exports(
    load_schema_export('exports/baseline'),
    load_schema_export('exports/candidate'),
    left_label='baseline', right_label='candidate',
)
print(render_markdown(report))
"
```

## Scripts

- `scripts/schema_export.py` -- `load_schema_export`, `SectionStatus`, `ExportLayout`, `SchemaExport`
- `scripts/schema_diff.py` -- `compare_schema_exports`, `compare_named_sets`, `render_markdown`
- `scripts/duplicate_fields.py` -- `find_duplicate_fields`, `DEFAULT_BUILTIN_INTERNAL_NAMES`

## Provenance

Adapted from `sp-auditing-schema` in the originating SharePoint migration
repository. One of that skill's seven symlinks was broken at the pinned source
commit and was not extracted. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.

