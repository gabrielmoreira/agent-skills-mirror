---
name: odoo-18-api-highlights
description: Version-distinguishing API patterns for Odoo 18. Read this when the target version is 18.0 so the reviewer/tracer applies the right rules.
---

# Odoo 18 API Highlights

Use this file as the version-specific ruleset when the resolved Odoo version is `18.0`. It supplements — not replaces — the general review checklist.

## Views

- **List view tag: `<list>`** — `<tree>` is deprecated in 18. Use `<list>` everywhere, including `xpath` expressions and action `view_mode="list,form"`.
- **Direct-expression attrs only** — legacy `attrs=` / `states=` are rejected (carried from 17). Use `invisible="..."`, `readonly="..."`, `required="..."`.
- Reference: `references/odoo-18-view-guide.md`.

## Fields

- **Aggregation parameter: `aggregator=`** (replaces `group_operator=` from v17). Numeric fields default to `'sum'`.
- Reference: `references/odoo-18-field-guide.md`.

## Decorators

- **`@api.ondelete(at_uninstall=False)`** — preferred over overriding `unlink()` for validation. Overriding `unlink()` for checks breaks module uninstallation.
- **`@api.model_create_multi`** — overriding `create()` without it emits a deprecation warning in 18.
- Reference: `references/odoo-18-decorator-guide.md`.

## Quick review checks (v18-specific)

- ❌ `<tree>` tag — must be `<list>` in 18.
- ❌ `attrs="..."` / `states="..."` — rewrite to direct expressions.
- ❌ `group_operator=` — use `aggregator=` in 18.
- ❌ Overriding `unlink()` for validation — use `@api.ondelete`.
- ❌ Overriding `create()` without `@api.model_create_multi`.
- ✅ `<list>` in view records, xpath, and action `view_mode`.
- ✅ `@api.ondelete(at_uninstall=False)` for delete rules.
- ✅ `@api.model_create_multi` for batch create.
