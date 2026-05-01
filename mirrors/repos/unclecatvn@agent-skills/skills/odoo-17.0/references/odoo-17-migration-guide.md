---
name: odoo-17-migration
description: Migration scripts for Odoo 17 modules — folder layout migrations/17.0.X.Y.Z/{pre,post,end}-*.py, migrate(cr, version) signature, raw SQL patterns, idempotency, field rename / type change / model rename, recomputing stored computes, and util helpers from odoo.upgrade (odoo-upgrade-util).
globs: "**/migrations/**/*.py"
topics:
  - Migration script discovery and execution in Odoo 17
  - migrate(cr, installed_version) signature
  - Folder layout `migrations/17.0.X.Y.Z/{pre,post,end}-*.py`
  - The special 0.0.0 folder (any-version change)
  - Raw SQL patterns and when to use ORM
  - Idempotency (IF NOT EXISTS, ON CONFLICT, existence checks)
  - Renaming a field / changing its type / renaming a model
  - Recomputing stored compute fields
  - `odoo.upgrade` / `odoo-upgrade-util` helpers
  - Module lifecycle hooks vs migration scripts
when_to_use:
  - Shipping a new version of an Odoo 17 module
  - Renaming fields, models, or tables
  - Backfilling data during upgrades
  - Recovering from a broken schema transition
---

# Odoo 17 Migration Guide

Comprehensive guide to writing migration scripts for Odoo 17 modules. Covers
folder layout, the `migrate()` signature, stage execution order, idempotent
SQL patterns, schema evolution recipes, and integration with the
`odoo.upgrade` / `odoo-upgrade-util` helper library.

For module structure and hooks overview see
[`odoo-17-development-guide.md`](./odoo-17-development-guide.md). For manifest
field semantics see [`odoo-17-manifest-guide.md`](./odoo-17-manifest-guide.md).

## Table of Contents

1. [When Migrations Run](#when-migrations-run)
2. [Folder Layout](#folder-layout)
3. [`migrate(cr, version)` Signature](#migratecr-version-signature)
4. [Stages: `pre-`, `post-`, `end-`](#stages-pre--post--end-)
5. [The Special `0.0.0` Folder](#the-special-000-folder)
6. [Module Lifecycle Hooks vs Migrations](#module-lifecycle-hooks-vs-migrations)
7. [Raw SQL Patterns](#raw-sql-patterns)
8. [Idempotency](#idempotency)
9. [Recipes](#recipes)
    - [Rename a field](#rename-a-field)
    - [Change a field type](#change-a-field-type)
    - [Rename a model (and its table)](#rename-a-model-and-its-table)
    - [Drop an obsolete field/model](#drop-an-obsolete-fieldmodel)
    - [Recompute a stored compute](#recompute-a-stored-compute)
    - [Batched data backfill](#batched-data-backfill)
10. [`odoo.upgrade` / `odoo-upgrade-util`](#odooupgrade--odoo-upgrade-util)
11. [Testing Migrations](#testing-migrations)
12. [Version Management](#version-management)
13. [Base Code Reference](#base-code-reference)

---

## When Migrations Run

Migration scripts run when `--update=<module>` (or `-u`) is invoked **and**
the installed module version (from `ir_module_module.latest_version`) is
strictly less than the manifest version.

The loader walks every version folder and runs only the ones where:

```
installed_version < version_folder <= manifest_version
```

Fresh installs (`installed_version is None`) **skip** migrations entirely —
use `post_init_hook` for initial data in that case.

The dispatcher is `odoo.modules.migration.MigrationManager.migrate_module`.

---

## Folder Layout

```
my_module/
├── __manifest__.py                  # 'version': '17.0.1.2.0'
├── migrations/
│   ├── 17.0.1.0.0/
│   │   ├── pre-migrate.py           # before schema sync
│   │   ├── post-migrate_data.py     # after schema sync
│   │   └── end-cleanup.py           # after ALL modules updated
│   ├── 17.0.1.1.0/
│   │   └── post-rename_fields.py
│   ├── 17.0.1.2.0/
│   │   ├── pre-fix_constraint.py
│   │   └── post-backfill.py
│   ├── 0.0.0/                       # runs on every version change
│   │   ├── pre-always.py
│   │   └── end-always.py
│   └── tests/                       # ignored by the dispatcher
│       └── test_17_0_1_1_0.py
└── upgrades/                        # optional alternative root
    └── 17.0.1.1.0/
        └── pre-migrate.py
```

Rules:

1. Folder name must match the regex in `odoo/modules/migration.py:VERSION_RE`.
   Accepted shapes: `x.y`, `x.y.z`, `17.0.x.y`, `17.0.x.y.z`, and the literal
   `0.0.0`. A folder named `tests` is ignored.
2. Scripts are `.py` files whose basename **starts with** `pre-`, `post-`, or
   `end-`. Everything after the prefix is free-form (typically a short
   description).
3. Both `module/migrations/` and `module/upgrades/` are scanned (same script
   discovery).
4. The version folder is compared against the module's manifest version after
   being normalized via `convert_version` (prepending `17.0.` when needed).

---

## `migrate(cr, version)` Signature

Every migration script **must** expose a module-level function named
`migrate` with this signature:

```python
# migrations/17.0.1.1.0/post-migrate_rename.py

def migrate(cr, version):
    """
    cr:      odoo.sql_db.Cursor — raw DB cursor. NO environment.
    version: str or None — the previously installed version, e.g. '17.0.1.0.0'.
             None means fresh install (migrations do not run in that case
             anyway, but the contract allows checking).
    """
    if version is None:
        return
    cr.execute("UPDATE my_model SET state = 'confirmed' WHERE state = 'validated'")
```

Accepted parameter name variants (use underscore prefix for unused ones):

```python
def migrate(cr, version): ...
def migrate(cr, _version): ...     # version not read
def migrate(_cr, version): ...     # rare
def migrate(_cr, _version): ...    # rare
```

The dispatcher calls `mod.migrate(cr, installed_version)` — a missing `migrate`
function logs an error and skips the file (see
`odoo/modules/migration.py:exec_script`).

### Getting an ORM Environment inside a script

`migrate()` only receives a cursor. To use the ORM:

```python
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # now: env['res.partner'], env.ref('my_module.foo'), ...
```

Caveats:

- In `pre-` scripts, **models of the module being upgraded are not yet
  reloaded** — ORM access is safe for *other* already-loaded models but may
  see stale schema for the current module.
- In `post-` scripts, models are fully loaded. This is the best place for ORM
  work.

---

## Stages: `pre-`, `post-`, `end-`

For a given module upgrade, the loader executes migration scripts in this
order (see `odoo/modules/loading.py`):

```
For each module being upgraded:
  1. pre-*.py   ← before schema sync (tables may lack new columns)
  2. <schema sync>
  3. Load data files (XML/CSV)
  4. post-*.py  ← after schema sync, models are fully loaded

After ALL modules have been upgraded:
  5. end-*.py   ← cross-module invariants
```

### `pre-` scripts

- Tables/columns declared by the **current** new manifest may not yet exist.
- The old schema is still in place.
- Best for:
  - Renaming columns/tables BEFORE Odoo's ORM creates new ones.
  - Converting column types to avoid destructive auto-migrations.
  - Dropping obsolete columns/tables so the ORM doesn't complain.
  - Pre-computing data that the new schema sync will consume.

### `post-` scripts

- Schema is up to date, data files (XML/CSV) have been loaded.
- Models from the current module are usable via the ORM.
- Best for:
  - Backfilling new fields.
  - Data transformations that need high-level ORM features.
  - Recomputing stored compute fields.

### `end-` scripts

- Run **after all modules** are upgraded.
- Use for cross-module consistency fixes: e.g. you need models from another
  module whose migration also runs in this batch.

---

## The Special `0.0.0` Folder

Scripts in `migrations/0.0.0/` run **on every version change** of the module
(any bump). Execution order relative to other folders (per
`odoo/modules/migration.py:_get_migration_versions`):

- `pre` stage: `0.0.0/pre-*.py` runs **FIRST** (before any versioned
  `pre-*.py`).
- `post` stage: `0.0.0/post-*.py` runs **LAST**.
- `end` stage: `0.0.0/end-*.py` runs **LAST**.

Use sparingly. Typical use cases:

- Always-run sanity checks.
- Drop a legacy column that may linger from any prior version.
- Emit log markers during every upgrade.

---

## Module Lifecycle Hooks vs Migrations

| | Manifest hook | Migration script |
|---|---------------|------------------|
| Declared in | `__manifest__.py` → `pre_init_hook` / `post_init_hook` / `uninstall_hook` | `migrations/<ver>/{pre,post,end}-*.py` |
| Runs on | Fresh install (hooks) or uninstall. | Module upgrade (version bump). |
| Fresh install | ✅ Runs. | ❌ Does not run. |
| Upgrade | ❌ Does not run. | ✅ Runs (stages `pre`, `post`, `end`). |
| Signature | `hook(env)` (v17). | `migrate(cr, version)`. |

**Rule of thumb:** code that should run once per database (initial data,
default config) goes in `post_init_hook`; code that fixes data from a prior
version goes in a migration script.

---

## Raw SQL Patterns

### Why SQL (often) beats ORM in migrations

- 10–100× faster for bulk updates (no Python per-record overhead).
- Does not trigger `compute`, `tracking`, `_log_access`, email notifications,
  or `ir.rule` filters — which is usually what you want during an upgrade.
- Schema operations (ALTER TABLE) have to be SQL.

### Cursor API quick reference

```python
def migrate(cr, version):
    # Parameterize everything that is not a static SQL token.
    cr.execute("UPDATE my_model SET state = %s WHERE state = %s",
               ('confirmed', 'validated'))

    # Fetch values after a SELECT.
    cr.execute("SELECT id, name FROM my_model WHERE state = 'draft'")
    for row_id, name in cr.fetchall():
        ...

    # Multiple rows in one statement.
    cr.executemany(
        "INSERT INTO my_log (record_id, message) VALUES (%s, %s)",
        [(1, 'hello'), (2, 'world')],
    )

    # Commit is NOT needed — the outer transaction is managed by Odoo.
    # Use cr.commit() only for long migrations where you want to checkpoint.
```

### Useful SQL skeletons

```sql
-- Add a column safely
ALTER TABLE my_model ADD COLUMN IF NOT EXISTS new_field VARCHAR;

-- Drop a column safely
ALTER TABLE my_model DROP COLUMN IF EXISTS old_field;

-- Rename a column (PostgreSQL)
ALTER TABLE my_model RENAME COLUMN old_name TO new_name;

-- Change a column type with explicit cast
ALTER TABLE my_model
    ALTER COLUMN amount TYPE NUMERIC USING amount::NUMERIC;

-- Upsert
INSERT INTO ir_config_parameter (key, value)
VALUES ('my_module.version', '17.0.1.1.0')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;
```

---

## Idempotency

Migration scripts must be **safe to re-run**. Odoo does not guarantee
exactly-once execution (DBs can be replayed, upgrades can be re-triggered
after a crash). Patterns:

```python
def migrate(cr, version):
    # 1. Guard DDL with IF (NOT) EXISTS
    cr.execute("ALTER TABLE my_model ADD COLUMN IF NOT EXISTS new_field VARCHAR")

    # 2. Guard DML with a predicate that becomes false after the first run
    cr.execute("""
        UPDATE my_model
           SET new_field = old_field
         WHERE new_field IS NULL
           AND old_field IS NOT NULL
    """)

    # 3. Check existence before acting
    cr.execute("""
        SELECT 1 FROM information_schema.columns
         WHERE table_name = 'my_model' AND column_name = 'legacy_field'
    """)
    if cr.fetchone():
        cr.execute("ALTER TABLE my_model DROP COLUMN legacy_field")

    # 4. Use ON CONFLICT for inserts
    cr.execute("""
        INSERT INTO ir_config_parameter (key, value)
        VALUES (%s, %s)
        ON CONFLICT (key) DO NOTHING
    """, ('my_module.feature_x', 'enabled'))
```

---

## Recipes

### Rename a field

Rename in `pre-` so the ORM's schema sync does not create an empty new column
alongside:

```python
# migrations/17.0.1.1.0/pre-rename_customer.py

def migrate(cr, version):
    # Only rename if the old column still exists and the new one doesn't.
    cr.execute("""
        SELECT
            (SELECT 1 FROM information_schema.columns
              WHERE table_name='sale_order' AND column_name='customer_id') AS old_col,
            (SELECT 1 FROM information_schema.columns
              WHERE table_name='sale_order' AND column_name='partner_id') AS new_col
    """)
    old_col, new_col = cr.fetchone()
    if old_col and not new_col:
        cr.execute("ALTER TABLE sale_order RENAME COLUMN customer_id TO partner_id")

    # Also rename the metadata so audit logs stay consistent.
    cr.execute("""
        UPDATE ir_model_fields
           SET name = 'partner_id'
         WHERE model = 'sale.order' AND name = 'customer_id'
    """)
    cr.execute("""
        UPDATE ir_translation
           SET name = REPLACE(name, ',customer_id', ',partner_id')
         WHERE name LIKE 'sale.order,customer_id'
    """)
```

If the field is declared with `oldname=` in v17, the ORM handles the rename
for you — but writing an explicit migration is more robust.

### Change a field type

```python
# migrations/17.0.1.1.0/pre-change_amount_type.py

def migrate(cr, version):
    # amount: Integer -> Float. USING clause forces the cast.
    cr.execute("""
        ALTER TABLE my_model
        ALTER COLUMN amount TYPE DOUBLE PRECISION
        USING amount::DOUBLE PRECISION
    """)
```

If the conversion can fail (Char → Integer with non-numeric rows), materialize
a temporary column, backfill, then swap:

```python
def migrate(cr, version):
    cr.execute("ALTER TABLE my_model ADD COLUMN IF NOT EXISTS amount_int INTEGER")
    cr.execute("""
        UPDATE my_model
           SET amount_int = CASE
               WHEN amount ~ '^[0-9]+$' THEN amount::INTEGER
               ELSE 0
           END
    """)
    cr.execute("ALTER TABLE my_model DROP COLUMN amount")
    cr.execute("ALTER TABLE my_model RENAME COLUMN amount_int TO amount")
```

### Rename a model (and its table)

```python
# migrations/17.0.1.1.0/pre-rename_model.py

def migrate(cr, version):
    # 1. Table
    cr.execute("ALTER TABLE IF EXISTS old_model RENAME TO new_model")

    # 2. ir_model
    cr.execute("""
        UPDATE ir_model SET model = 'new.model' WHERE model = 'old.model'
    """)

    # 3. ir_model_fields references
    cr.execute("""
        UPDATE ir_model_fields SET model = 'new.model' WHERE model = 'old.model'
    """)
    cr.execute("""
        UPDATE ir_model_fields SET relation = 'new.model' WHERE relation = 'old.model'
    """)

    # 4. ir_model_data XML IDs
    cr.execute("""
        UPDATE ir_model_data SET model = 'new.model' WHERE model = 'old.model'
    """)

    # 5. ir_attachment
    cr.execute("""
        UPDATE ir_attachment SET res_model = 'new.model' WHERE res_model = 'old.model'
    """)

    # 6. mail tables that reference the model name
    for table in ('mail_followers', 'mail_message', 'mail_activity'):
        cr.execute(f"""
            UPDATE {table} SET res_model = 'new.model' WHERE res_model = 'old.model'
        """)

    # 7. ir_act_window.res_model, binding_model_id references, etc. as applicable
    cr.execute("""
        UPDATE ir_act_window SET res_model = 'new.model' WHERE res_model = 'old.model'
    """)
```

The `odoo.upgrade.util` helper `rename_model` (see next section) bundles all
these steps.

### Drop an obsolete field/model

```python
# migrations/17.0.2.0.0/pre-drop_legacy.py

def migrate(cr, version):
    cr.execute("ALTER TABLE my_model DROP COLUMN IF EXISTS legacy_ref")
    cr.execute("DELETE FROM ir_model_fields WHERE model='my.model' AND name='legacy_ref'")
    cr.execute("DELETE FROM ir_model_data WHERE model='my.model' AND name LIKE 'legacy_%'")
```

### Recompute a stored compute

When a new version changes the formula of a stored computed field, run the
recompute in `post-`:

```python
# migrations/17.0.1.1.0/post-recompute_margin.py
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    SaleOrder = env['sale.order']
    # Mark the field for recomputation, then flush.
    orders = SaleOrder.search([])
    SaleOrder.invalidate_model(['margin'])
    orders._compute_margin()
    orders.flush_model(['margin'])
```

Alternatively, mark fields for lazy recomputation via `ir_attachment`-like
SQL trick:

```python
def migrate(cr, version):
    # Force re-init by clearing the stored values; compute will re-run on read.
    cr.execute("UPDATE sale_order SET margin = NULL")
```

### Batched data backfill

For very large tables, commit in batches to avoid long locks and huge
transactions:

```python
def migrate(cr, version):
    BATCH = 5000
    offset = 0
    while True:
        cr.execute("""
            WITH batch AS (
                SELECT id FROM my_model
                 WHERE new_field IS NULL
                 ORDER BY id
                 LIMIT %s OFFSET %s
            )
            UPDATE my_model m
               SET new_field = LOWER(m.old_field)
              FROM batch
             WHERE m.id = batch.id
            RETURNING m.id
        """, (BATCH, offset))
        rows = cr.fetchall()
        if not rows:
            break
        cr.commit()
        offset += BATCH
```

---

## `odoo.upgrade` / `odoo-upgrade-util`

Odoo 17 exposes an `odoo.upgrade` namespace (see
`odoo/modules/module.py:initialize_sys_path`). The namespace is populated
from:

- `--upgrade-path` CLI option (server config), or
- the legacy `odoo/addons/base/maintenance/migrations/` path.

The standard helper library loaded there is **`odoo-upgrade-util`** (the same
library Odoo S.A. uses in its enterprise upgrade service; distributed as a
separate repository). When installed, you can import it from any migration
script:

```python
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, 'sale.order', 'old_field', 'new_field')
    util.remove_field(cr, 'sale.order', 'deprecated_field')
    util.rename_model(cr, 'old.model', 'new.model')
    util.remove_model(cr, 'old.model')
    util.recompute_fields(cr, 'sale.order', ['margin'])
    util.merge_groups(cr, ['base.group_old'], 'base.group_new')
    util.force_install_module(cr, 'new_dependency')
```

Commonly used helpers (all live in `odoo.upgrade.util`):

| Helper | Purpose |
|--------|---------|
| `rename_field(cr, model, old, new)` | Rename a field + all metadata. |
| `rename_model(cr, old, new)` | Rename a model + update every reference. |
| `rename_module(cr, old, new)` | Rename a whole module. |
| `rename_xmlid(cr, old_xmlid, new_xmlid)` | Move a record's `ir.model.data` entry. |
| `remove_field(cr, model, name)` | Drop a field + metadata + column. |
| `remove_model(cr, model)` | Drop a model, its table, all references. |
| `remove_record(cr, xmlid)` | Delete a record and its `ir.model.data` row. |
| `recompute_fields(cr, model, fields)` | Re-queue stored computes. |
| `invalidate(cr, model)` | Invalidate cache for a model. |
| `force_install_module(cr, name)` | Flip a module to `to install` during upgrade. |
| `module_installed(cr, name)` | Check install state. |
| `ENVIRON` / `env(cr)` | Shortcut to build an `api.Environment`. |
| `explode_query`, `chunks` | Split big queries/IN lists for batching. |

Availability: the helpers are **not** shipped inside the Odoo 17 community
repo — you install `odoo-upgrade-util` alongside (either by placing the repo
on `--upgrade-path` or by installing the Python package). If the library is
not present, `from odoo.upgrade import util` raises `ImportError`; write
scripts that either require it explicitly or fall back to raw SQL.

Fallback-friendly pattern:

```python
try:
    from odoo.upgrade import util
except ImportError:
    util = None


def migrate(cr, version):
    if util is not None:
        util.rename_field(cr, 'sale.order', 'old_f', 'new_f')
        return

    # Manual fallback
    cr.execute("ALTER TABLE sale_order RENAME COLUMN old_f TO new_f")
    cr.execute("UPDATE ir_model_fields SET name='new_f' "
               "WHERE model='sale.order' AND name='old_f'")
```

---

## Testing Migrations

Odoo 17 does not ship an `upgrade_code` CLI (that tool was added in v18+).
Instead, test migrations by re-running the upgrade locally:

```bash
# 1. Install the OLD version on a scratch DB
./odoo-bin -d test_upgrade --init=my_module --stop-after-init

# 2. Replace the code on disk with the NEW version (git checkout).

# 3. Run the upgrade and capture logs.
./odoo-bin -d test_upgrade \
           --update=my_module \
           --log-level=debug \
           --log-handler=odoo.modules.migration:DEBUG \
           --stop-after-init
```

### Unit-testing a migration script

Scripts are plain Python. Import and call `migrate()` with a mocked cursor
from a regular Odoo test — this lets you assert on the emitted SQL:

```python
# tests/test_migration_17_0_1_1_0.py
from unittest.mock import MagicMock

from odoo.tests.common import TransactionCase

# Migration scripts are not standard importable modules; load via importlib.
import importlib.util, pathlib

_spec = importlib.util.spec_from_file_location(
    'pre_rename',
    pathlib.Path(__file__).parents[1] / 'migrations/17.0.1.1.0/pre-rename_customer.py',
)
_mod = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_mod)


class TestMigrationRename(TransactionCase):
    def test_idempotent(self):
        # Running twice must not raise.
        _mod.migrate(self.cr, '17.0.1.0.0')
        _mod.migrate(self.cr, '17.0.1.0.0')
```

---

## Version Management

### Bumping the manifest

Always bump `version` in `__manifest__.py` before the migration folder you
want to trigger:

```python
# __manifest__.py
'version': '17.0.1.1.0',   # <-- activates migrations/17.0.1.1.0/*
```

The rule (from `MigrationManager.migrate_module`):

```
installed_version < convert_version(folder_name) <= manifest_version
```

`convert_version` prepends `17.0.` when the folder name has only 2–3
components.

### Comparing versions inside a script

```python
from odoo.tools.parse_version import parse_version


def migrate(cr, version):
    if version is None:
        return

    if parse_version(version) < parse_version('17.0.1.0.0'):
        # migrating from a pre-1.0 internal release
        cr.execute("UPDATE my_model SET state='draft' WHERE state IS NULL")

    if parse_version(version) < parse_version('17.0.1.1.0'):
        cr.execute("ALTER TABLE my_model ADD COLUMN IF NOT EXISTS note TEXT")
```

Note: the version folder name already gates execution. Compare only when you
need to split logic inside a single script.

---

## Base Code Reference

- `odoo/modules/migration.py` — migration dispatcher:
  - `VERSION_RE` (accepted folder names).
  - `MigrationManager.migrate_module(pkg, stage)` (stage ∈ `pre`, `post`,
    `end`).
  - `_get_migration_versions` (handles the `0.0.0` reordering).
  - `exec_script` — loads the `.py`, calls `migrate(cr, installed_version)`,
    raises `AttributeError` if `migrate` is missing.
- `odoo/modules/loading.py` — the orchestrator that calls
  `migrations.migrate_module(package, 'pre')` (before data load) and
  `migrations.migrate_module(package, 'post')` (after data load). `end-*.py`
  scripts run after all modules have been processed.
- `odoo/modules/module.py` — `initialize_sys_path` wires `odoo.upgrade` to the
  `--upgrade-path` directory (enabling `from odoo.upgrade import util`).
  `adapt_version` normalizes `x.y(.z)` to `17.0.x.y(.z)`.
- `odoo/tools/parse_version.py` — `parse_version()` for intra-script
  comparisons.
- `odoo/release.py` — `version_info = (17, 0, 0, FINAL, 0, '')`,
  `major_version = '17.0'`.
- External: [`odoo-upgrade-util`](https://github.com/odoo/upgrade-util) — the
  Odoo-maintained helper library loaded via the `odoo.upgrade` namespace.
