---
name: obsidian-bases
description: "Authors Obsidian Bases .base YAML: global filters, formulas, summaries, and table/cards/list/map views over note properties. Use when creating database-like views of notes, embedding ![[MyBase.base]], or editing Bases filters/formulas. Not for ordinary Markdown note CRUD (obsidian) or Dataview JS queries."
version: 1.0.1
risk: unknown
source: "https://github.com/kepano/obsidian-skills"
date_added: "2026-03-21"
---

## When to Use

- Use when creating or editing `.base` files in an Obsidian vault.
- Use for database-like note views with filters, formulas, summaries, or cards/tables.
- Use when the user asks about Obsidian Bases specifically, or mentions `.base` files, table views, card views, list views, map views, filters, or formulas.
- Use when the user wants to embed a Base in a Markdown note (`![[MyBase.base]]`).

## Prerequisites

- Obsidian installed with Bases support (Obsidian 1.9+ or a build that includes the Bases feature).
- The target vault must be open and accessible on the Windows host (PowerShell).
- For map views, the Maps community plugin must be installed and latitude/longitude properties must exist on the target notes.

## Procedure

### 1. Create the `.base` file

Create a `.base` file in the vault using valid YAML. On Windows (PowerShell):

```powershell
New-Item -Path "C:\path\to\vault\MyBase.base" -ItemType File -Force
```

Then write YAML content into the file. The entire file must be valid YAML.

### 2. Define global filters

Add a top-level `filters` key to select which notes appear across ALL views. Filters can be a single string or a recursive object with `and` / `or` / `not`.

```yaml
# Single filter string
filters: 'status == "done"'

# Recursive object
filters:
  and:
    - 'status == "done"'
    - 'priority > 3'
  or:
    - 'file.hasTag("book")'
    - 'file.hasTag("article")'
  not:
    - 'file.hasTag("archived")'
```

### 3. Define formulas (optional)

Add a `formulas` section to compute values from properties. Formula expressions are strings.

```yaml
formulas:
  total: "price * quantity"
  status_icon: 'if(done, "✅", "⏳")'
  days_until_due: 'if(due_date, (date(due_date) - today()).days, "")'
```

### 4. Configure property display names (optional)

Use the `properties` section to set `displayName` for note properties, file properties, or formula properties.

```yaml
properties:
  status:
    displayName: "Status"
  formula.days_until_due:
    displayName: "Days Until Due"
  file.ext:
    displayName: "Extension"
```

### 5. Define custom summaries (optional)

```yaml
summaries:
  custom_summary_name: 'values.mean().round(3)'
```

### 6. Configure views

Add one or more views under `views`. Each view has a `type` (`table`, `cards`, `list`, or `map`), a `name`, and an `order` list specifying which properties to display.

```yaml
views:
  - type: table
    name: "My Table"
    limit: 10
    groupBy:
      property: status
      direction: ASC
    filters:
      and:
        - 'status != "done"'
    order:
      - file.name
      - status
      - due_date
      - formula.days_until_due
    summaries:
      price: Sum
      formula.days_until_due: Average
```

### 7. Validate the YAML

Verify the file is valid YAML with no syntax errors. Check that:
- All referenced `formula.X` entries in `order` or `properties` have a matching definition in `formulas`.
- All strings containing special YAML characters (`:`, `{`, `}`, `[`, `]`, `,`, `&`, `*`, `#`, `?`, `|`, `-`, `<`, `>`, `=`, `!`, `%`, `@`, `` ` ``) are quoted.
- Formulas containing double quotes are wrapped in single quotes.

On Windows (PowerShell), you can do a quick YAML lint if Python is available:

```powershell
python -c "import yaml,sys; yaml.safe_load(open(r'C:\path\to\vault\MyBase.base',encoding='utf-8')); print('YAML OK')"
```

### 8. Test in Obsidian

Open the `.base` file in Obsidian to confirm the view renders correctly. If Obsidian shows a YAML error, re-check quoting rules and formula syntax.

## Schema Reference

```yaml
filters:
  and: []
  or: []
  not: []

formulas:
  formula_name: 'expression'

properties:
  property_name:
    displayName: "Display Name"
  formula.formula_name:
    displayName: "Formula Display Name"
  file.ext:
    displayName: "Extension"

summaries:
  custom_summary_name: 'values.mean().round(3)'

views:
  - type: table | cards | list | map
    name: "View Name"
    limit: 10
    groupBy:
      property: property_name
      direction: ASC | DESC
    filters:
      and: []
    order:
      - file.name
      - property_name
      - formula.formula_name
    summaries:
      property_name: Average
```

### Filter Operators

| Operator | Description |
|----------|-------------|
| `==` | equals |
| `!=` | not equal |
| `>` | greater than |
| `<` | less than |
| `>=` | greater than or equal |
| `<=` | less than or equal |
| `&&` | logical and |
| `\|\|` | logical or |
| `!` | logical not |

### Property Types

1. **Note properties** — From frontmatter: `note.author` or just `author`.
2. **File properties** — File metadata: `file.name`, `file.mtime`, etc.
3. **Formula properties** — Computed values: `formula.my_formula`.

### File Properties Reference

| Property | Type | Description |
|----------|------|-------------|
| `file.name` | String | File name |
| `file.basename` | String | File name without extension |
| `file.path` | String | Full path to file |
| `file.folder` | String | Parent folder path |
| `file.ext` | String | File extension |
| `file.size` | Number | File size in bytes |
| `file.ctime` | Date | Created time |
| `file.mtime` | Date | Modified time |
| `file.tags` | List | All tags in file |
| `file.links` | List | Internal links in file |
| `file.backlinks` | List | Files linking to this file |
| `file.embeds` | List | Embeds in the note |
| `file.properties` | Object | All frontmatter properties |

### The `this` Keyword

- In the main content area: refers to the base file itself.
- When embedded: refers to the embedding file.
- In the sidebar: refers to the active file in main content.

### Key Functions

Most commonly used functions. **Load `references/FUNCTIONS_REFERENCE.md` when you need the complete reference for all types (Date, String, Number, List, File, Link, Object, RegExp).**

| Function | Signature | Description |
|----------|-----------|-------------|
| `date()` | `date(string): date` | Parse string to date (`YYYY-MM-DD HH:mm:ss`) |
| `now()` | `now(): date` | Current date and time |
| `today()` | `today(): date` | Current date (time = 00:00:00) |
| `if()` | `if(condition, trueResult, falseResult?)` | Conditional |
| `duration()` | `duration(string): duration` | Parse duration string |
| `file()` | `file(path): file` | Get file object |
| `link()` | `link(path, display?): Link` | Create a link |

### Duration Type

When subtracting two dates, the result is a **Duration** type (not a number).

**Duration Fields:** `duration.days`, `duration.hours`, `duration.minutes`, `duration.seconds`, `duration.milliseconds`

**HARD RULE:** Duration does NOT support `.round()`, `.floor()`, `.ceil()` directly. Access a numeric field first (like `.days`), then apply number functions.

```yaml
# CORRECT
"(date(due_date) - today()).days"
"(now() - file.ctime).days"
"(date(due_date) - today()).days.round(0)"

# WRONG — will cause error
# "((date(due) - today()) / 86400000).round(0)"
# "(now() - file.ctime).round(0)"
```

### Date Arithmetic

Duration units: `y/year/years`, `M/month/months`, `d/day/days`, `w/week/weeks`, `h/hour/hours`, `m/minute/minutes`, `s/second/seconds`.

```yaml
"now() + \"1 day\""
"today() + \"7d\""
"now() - file.ctime"
"(now() - file.ctime).days"
```

### Default Summary Formulas

| Name | Input Type | Description |
|------|------------|-------------|
| `Average` | Number | Mathematical mean |
| `Min` | Number | Smallest number |
| `Max` | Number | Largest number |
| `Sum` | Number | Sum of all numbers |
| `Range` | Number | Max - Min |
| `Median` | Number | Mathematical median |
| `Stddev` | Number | Standard deviation |
| `Earliest` | Date | Earliest date |
| `Latest` | Date | Latest date |
| `Range` | Date | Latest - Earliest |
| `Checked` | Boolean | Count of true values |
| `Unchecked` | Boolean | Count of false values |
| `Empty` | Any | Count of empty values |
| `Filled` | Any | Count of non-empty values |
| `Unique` | Any | Count of unique values |

## Examples

### Task Tracker Base

```yaml
filters:
  and:
    - file.hasTag("task")
    - 'file.ext == "md"'

formulas:
  days_until_due: 'if(due, (date(due) - today()).days, "")'
  is_overdue: 'if(due, date(due) < today() && status != "done", false)'
  priority_label: 'if(priority == 1, "🔴 High", if(priority == 2, "🟡 Medium", "🟢 Low"))'

properties:
  status:
    displayName: Status
  formula.days_until_due:
    displayName: "Days Until Due"
  formula.priority_label:
    displayName: Priority

views:
  - type: table
    name: "Active Tasks"
    filters:
      and:
        - 'status != "done"'
    order:
      - file.name
      - status
      - formula.priority_label
      - due
      - formula.days_until_due
    groupBy:
      property: status
      direction: ASC
    summaries:
      formula.days_until_due: Average

  - type: table
    name: "Completed"
    filters:
      and:
        - 'status == "done"'
    order:
      - file.name
      - completed_date
```

### Reading List Base

```yaml
filters:
  or:
    - file.hasTag("book")
    - file.hasTag("article")

formulas:
  reading_time: 'if(pages, (pages * 2).toString() + " min", "")'
  status_icon: 'if(status == "reading", "📖", if(status == "done", "✅", "📚"))'
  year_read: 'if(finished_date, date(finished_date).year, "")'

properties:
  author:
    displayName: Author
  formula.status_icon:
    displayName: ""
  formula.reading_time:
    displayName: "Est. Time"

views:
  - type: cards
    name: "Library"
    order:
      - cover
      - file.name
      - author
      - formula.status_icon
    filters:
      not:
        - 'status == "dropped"'

  - type: table
    name: "Reading List"
    filters:
      and:
        - 'status == "to-read"'
    order:
      - file.name
      - author
      - pages
      - formula.reading_time
```

### Daily Notes Index

```yaml
filters:
  and:
    - file.inFolder("Daily Notes")
    - '/^\d{4}-\d{2}-\d{2}$/.matches(file.basename)'

formulas:
  word_estimate: '(file.size / 5).round(0)'
  day_of_week: 'date(file.basename).format("dddd")'

properties:
  formula.day_of_week:
    displayName: "Day"
  formula.word_estimate:
    displayName: "~Words"

views:
  - type: table
    name: "Recent Notes"
    limit: 30
    order:
      - file.name
      - formula.day_of_week
      - formula.word_estimate
      - file.mtime
```

### Embedding Bases in Markdown

```markdown
![[MyBase.base]]

<!-- Specific view -->
![[MyBase.base#View Name]]
```

## Pitfalls

### YAML Syntax Errors

**Unquoted special characters:** Strings containing `:`, `{`, `}`, `[`, `]`, `,`, `&`, `*`, `#`, `?`, `|`, `-`, `<`, `>`, `=`, `!`, `%`, `@`, `` ` `` must be quoted.

```yaml
# WRONG — colon in unquoted string
displayName: Status: Active

# CORRECT
displayName: "Status: Active"
```

**Mismatched quotes in formulas:** When a formula contains double quotes, wrap the entire formula in single quotes.

```yaml
# WRONG — double quotes inside double quotes
formulas:
  label: "if(done, "Yes", "No")"

# CORRECT — single quotes wrapping double quotes
formulas:
  label: 'if(done, "Yes", "No")'
```

### Common Formula Errors

**Duration math without field access:** Subtracting dates returns a Duration, not a number. Always access `.days`, `.hours`, etc. before calling number functions.

```yaml
# WRONG — Duration is not a number
"(now() - file.ctime).round(0)"

# CORRECT — access .days first, then round
"(now() - file.ctime).days.round(0)"
```

**Missing null checks:** Properties may not exist on all notes. Use `if()` to guard.

```yaml
# WRONG — crashes if due_date is empty
"(date(due_date) - today()).days"

# CORRECT — guard with if()
'if(due_date, (date(due_date) - today()).days, "")'
```

**Referencing undefined formulas:** Ensure every `formula.X` in `order` or `properties` has a matching entry in `formulas`. Undefined formula references fail silently.

```yaml
# This will fail silently if 'total' is not defined in formulas
order:
  - formula.total

# Fix: define it
formulas:
  total: "price * quantity"
```

## Verification

1. **YAML validity** — Run a YAML parse check (if Python is available):

```powershell
python -c "import yaml; yaml.safe_load(open(r'C:\path\to\vault\MyBase.base',encoding='utf-8')); print('YAML OK')"
```

   Expected output: `YAML OK`

2. **Formula references** — Confirm every `formula.X` referenced in `order`, `properties`, or `summaries` has a matching key in the `formulas` section.

3. **Render check** — Open the `.base` file in Obsidian. The view should render without a YAML error banner. If an error appears, check quoting rules and formula syntax.

4. **Embed check** — Embed the base in a Markdown note with `![[MyBase.base]]` and confirm the view appears inline.

## References

- [Bases Syntax](https://help.obsidian.md/bases/syntax)
- [Functions](https://help.obsidian.md/bases/functions)
- [Views](https://help.obsidian.md/bases/views)
- [Formulas](https://help.obsidian.md/formulas)
- **Load `references/FUNCTIONS_REFERENCE.md`** when you need the complete function reference for all types (Date, String, Number, List, File, Link, Object, RegExp).

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
