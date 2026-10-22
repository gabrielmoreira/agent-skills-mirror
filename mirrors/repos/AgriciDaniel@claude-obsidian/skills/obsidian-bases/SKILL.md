---
name: obsidian-bases
description: Explain, draft, and validate Obsidian Bases .base files with filters, formulas, properties, summaries, and table, card, list, or version-gated kanban views. Use for Obsidian Bases, database-like vault views, dynamic tables, reading lists, task trackers, filters, formulas, summaries, and .base file edits.
---

# Obsidian Bases

Use this as a compact workflow and fallback syntax reference. Prefer a
separately installed `kepano/obsidian-skills` `obsidian-bases` skill, then the
current [official Bases syntax](https://help.obsidian.md/bases/syntax), for
detailed or version-sensitive fields and functions.

Answer design and syntax questions read-only. For a requested `.base` edit,
resolve the user vault and use one inspected transaction; never write the file
directly.

Resolve the installed product root from this skill's own location, not from the
vault or current working directory:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
CORE="$PRODUCT_ROOT/scripts/claude-obsidian.py"
test -f "$CORE"
```

Every `../wiki/references/` link in this file resolves the same way, relative
to this skill's own directory under `$PRODUCT_ROOT`, never relative to the
selected vault's `wiki/` directory.

## Workflow

1. Inspect representative note properties and any existing `.base` file.
2. Define the smallest filter that selects the intended notes.
3. Add formulas only for values that must be computed.
4. Choose views and display order. Do not assume a view type or option is
   supported by the user's Obsidian version or installed plugins.
5. Validate YAML, expression quoting, property names, formula references, and
   null handling.
6. Preview the complete file and expected result set before a mutation.
7. If an edit was requested, read
   [operation-transactions.md](../wiki/references/operation-transactions.md),
   keep the `.base` file under `wiki/`, and build one
   `claude-obsidian.transaction.v1` bundle with `operation_type: base`. Inspect
   it, then set `APPROVAL_SHA256` to the returned `approval_sha256` only after
   review and apply once:

   ```bash
   python3 "$CORE" transaction inspect "$BUNDLE" --vault "$VAULT"
   python3 "$CORE" transaction apply "$BUNDLE" --vault "$VAULT" \
     --approved-plan-sha256 "$APPROVAL_SHA256"
   ```
8. Record static validation separately from native Obsidian rendering. Follow
   [the conformance procedure](../../docs/native-conformance.md) when application
   behavior cannot be verified locally. Never label unobserved output as tested.

## Version boundary

Checked 2026-10-17 against [official view documentation](https://obsidian.md/help/bases/views).
Table and cards require 1.9+, list requires 1.10+, and native kanban requires
1.14+. Map requires the Maps plugin. These are documented minimum versions,
not versions exercised by this package's offline tests. On an older app, keep
an ordinary table fallback. Preserve unknown existing view fields.

## Compact schema

`.base` files are YAML. Common top-level keys are `filters`, `formulas`,
`properties`, `summaries`, and `views`.

```yaml
filters:
  and:
    - file.inFolder("wiki")
    - 'status != "archived"'

formulas:
  status_label: 'if(status == "mature", "Ready", "Review")'

properties:
  status:
    displayName: "Status"

views:
  - type: table
    name: "Wiki pages"
    order:
      - file.name
      - type
      - status
      - updated
      - formula.status_label
```

Global filters apply to every view. A view may also define its own `filters`.
Recursive filter objects use one of `and`, `or`, or `not` at each level.

```yaml
filters:
  or:
    - file.hasTag("concept")
    - and:
        - file.hasTag("source")
        - 'status == "active"'
```

Use note properties by name, file metadata as `file.name`, `file.path`,
`file.folder`, `file.ext`, `file.ctime`, `file.mtime`, or `file.tags`, and
computed properties as `formula.<name>`.

## Formula and YAML rules

- Quote expressions that contain operators, colons, or nested string quotes.
- Guard nullable properties with `if()`.
- Date subtraction has conflicting current source descriptions. Treat the
  examples in the date section below as unverified compatibility candidates,
  and test the user's supported app versions before relying on the output.
- Define every `formula.<name>` before referencing it in a view or property
  display configuration.
- Do not transplant Dataview-only keys such as `from` or `where` into a Base.
- Do not invent properties absent from the selected notes without explaining
  that the resulting column will be empty.

## Date arithmetic needs native evidence

The [Help syntax](https://obsidian.md/help/bases/syntax) checked 2026-10-17
still describes date differences in milliseconds. The official
[1.9.3 changelog](https://obsidian.md/changelog/2025-06-26-desktop-v1.9.3/)
describes a Duration, and the pinned upstream skill also uses a Duration field.
The recorded excerpts of the
[API types at the reviewed commit](https://github.com/obsidianmd/obsidian-api/blob/9abd9605ce081383674aae1ed111c456edde0688/obsidian.d.ts)
do not include a Duration definition, so they are not cited for either reading.
No native app observation in this update resolves that disagreement.

These retained millisecond expressions are candidates for an isolated test,
not a compatibility guarantee:

```yaml
formulas:
  age_days: '((now() - file.ctime) / 86400000).round(0)'
  days_until: 'if(due_date, ((date(due_date) - today()) / 86400000).round(0), "")'
```

Compare direct subtraction/division, the Duration day field, and explicit
`number(date)` subtraction using one-day, multi-month, negative, and missing
values. Record app version, timezone, expression, actual value/type, and errors
using [native-conformance.md](../../docs/native-conformance.md). Do not rewrite
existing formulas or assert that any candidate is correct before that check.

## Additional views

Cards and list examples:

```yaml
views:
  - type: cards
    name: "Reading list"
    order:
      - file.name
      - author
      - status
  - type: list
    name: "Quick list"
    order:
      - file.name
      - status
```

For Obsidian 1.14+, group a kanban by an existing writable note property:

```yaml
filters:
  and:
    - file.inFolder("wiki")
    - 'file.ext == "md"'
views:
  - type: kanban
    name: "Page status"
    groupBy:
      property: note.status
      direction: ASC
    groupOrder:
      - seed
      - developing
      - mature
      - evergreen
      - null
    order:
      - file.name
      - status
```

`groupOrder` lists visible groups in display order. An absent `groupOrder`
shows all groups using the `groupBy` sort; an empty list hides every group.
`null` includes pages without the grouped value. Adding an empty group does not
create a note. Native card moves can change a note property, and grouping by
`file.folder` can move files; agents must still use reviewed transactions for
vault mutations. A formula or other read-only file property is unsuitable for
an editable status board. See [Kanban view](https://obsidian.md/help/bases/views/kanban).

Embed a Base or one named view in a Markdown note:

```markdown
![[Dashboard.base]]
![[Dashboard.base#Wiki pages]]
```

After an applied edit, report the operation ID, exact changed path, validation
performed, and anything that still requires rendering in Obsidian. Do not
commit Git.
