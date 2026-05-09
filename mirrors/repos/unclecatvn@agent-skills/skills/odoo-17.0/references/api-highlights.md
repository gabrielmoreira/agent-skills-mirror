---
name: odoo-17-api-highlights
description: Version-distinguishing API patterns for Odoo 17. Read this when the target version is 17.0 so the reviewer/tracer applies the right rules.
---

# Odoo 17 API Highlights

Use this file as the version-specific ruleset when the resolved Odoo version is `17.0`. It supplements — not replaces — the general review checklist.

## Views

- **List view tag: `<tree>`** — Odoo 17 still uses `<tree>`. The rename to `<list>` happens in 18.
  - Applies everywhere: view records, `xpath` expressions, action `view_mode="tree,form"`.
- **Legacy `attrs=` / `states=` are rejected by the view validator in 17.** Use direct-expression attributes:
  - `attrs="{'invisible': [('state','=','done')]}"` → `invisible="state == 'done'"`
  - `attrs="{'readonly': [('locked','=',True)]}"` → `readonly="locked"`
  - `states="draft,confirmed"` → `invisible="state not in ('draft','confirmed')"`
- Reference: `references/odoo-17-view-guide.md`.

## Fields

- **Aggregation parameter: `group_operator=`** (numeric fields default to `'sum'`). The parameter is renamed to `aggregator=` in later versions — in v17 source, `aggregator=` will fail or be silently ignored.
- Reference: `references/odoo-17-field-guide.md`.

## Decorators

- **`@api.model_create_multi`** is required when overriding `create()`. Do not rely on the `@api.model` fallback.
- **`@api.ondelete(at_uninstall=False)`** is available (since 15) and preferred over overriding `unlink()` for validation.
- Reference: `references/odoo-17-decorator-guide.md`.

## Frontend

- OWL 2.8 is the frontend framework version shipped with Odoo 17.

## Quick review checks (v17-specific)

- ❌ `<list>` tag (belongs in 18+) — flag as wrong version.
- ❌ `attrs="..."` / `states="..."` — must be rewritten to direct expressions.
- ❌ `aggregator=` — use `group_operator=` in 17.
- ✅ `@api.model_create_multi` on `create()` overrides.
- ✅ `@api.ondelete` for delete validation.
