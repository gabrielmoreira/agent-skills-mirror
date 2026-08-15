---
name: xlsx-parsing
version: 1.1.1
description: "Ingests Microsoft Excel .xlsx workbooks with openpyxl (or pandas) into list-of-dict rows, handling multi-sheet books, sparse rows, merged cells, and composite list or JSON cells. Use when a task input is .xlsx rather than a database. Not for .csv, .json, or legacy .xls; never mix openpyxl and pandas objects in one pipeline or load untrusted files with read_only=False."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-14
---

# xlsx-parsing

Excel workbooks are the lingua franca of operational documents that nobody bothered to put in a database — playbooks, rate cards, deviation policies, finance models, SLAs. They show up in tasks with three properties that trip up naive readers:

1. **Multiple sheets**, only one of which is the data you actually want.
2. **Sparse cells** — a row that uses a column may sit next to a row that doesn't, leaving `None` cells. Empty is meaningful (the rule does not apply), not an error.
3. **Composite cells** — a single cell that contains a comma-separated list, a JSON blob, or a sentence rather than an atomic value.

Treat the workbook as a *typed table* with declared columns, not a free-form spreadsheet. Read every sheet you need, normalise it to `list[dict[str, Any]]`, then operate on that.

## When to Use

- You need to ingest data from a Microsoft Excel `.xlsx` file.
- The workbook contains multiple sheets, sparse rows, merged cells, or cells with embedded lists/JSON.
- You prefer a pure-Python solution (`openpyxl` >= 3.1) or already have `pandas` >= 2.2 available for richer data manipulation.

**Do NOT use this skill when:**

- The file is `.csv` — use `csv.DictReader` directly.
- The file is `.json` or `.jsonl` — use `json.loads`.
- The file is `.xls` (legacy binary) — `openpyxl` will refuse; use `xlrd<2` or convert to `.xlsx` first.
- **Do not** mix `openpyxl` and `pandas` objects in the same processing pipeline; this can cause subtle type-conversion bugs.
- **Avoid** loading workbooks with `read_only=False` on large files; it can exhaust memory and expose you to DoS-style attacks if untrusted files are processed.

## Prerequisites

Install the required library. On a Windows PowerShell host:

```powershell
pip install "openpyxl>=3.1"
# OR, if you prefer pandas:
pip install "pandas>=2.2" "openpyxl>=3.1"
```

Verify installation:

```powershell
python -c "import openpyxl; print(openpyxl.__version__)"
```

## Procedure

### Step 1 — Load the workbook with safe flags

Always use `data_only=True`, `read_only=True`, and `keep_links=False`. These three flags are mandatory for security and performance:

```python
from pathlib import Path
import openpyxl
from typing import Any, List, Dict

def load_sheet_as_records(path: Path, sheet_name: str) -> List[Dict[str, Any]]:
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True, keep_links=False)
    ws = wb[sheet_name]
    rows = ws.iter_rows(values_only=True)
    header = [str(c).strip() if c else "" for c in next(rows)]
    return [
        dict(zip(header, row))
        for row in rows
        if any(cell is not None for cell in row)
    ]

# Example usage
records = load_sheet_as_records(Path("workbook.xlsx"), "Rules")
```

**Why these flags:**

- `data_only=True` returns the cached value of formula cells instead of the formula expression.
- `read_only=True` is faster on big workbooks and avoids loading styles you don't need.
- `keep_links=False` drops external link metadata, mitigating a class of XML-entity attacks.
- The `any(cell is not None ...)` filter drops entirely-blank rows that Excel preserves at the bottom of a sheet.
- `dict(zip(header, row))` handles trailing empty columns gracefully when a row is shorter than the header.

### Step 2 — (Alternative) Load with pandas

If `pandas` is installed and you need grouping, joins, or numeric aggregation:

```python
import pandas as pd
from pathlib import Path
from typing import Any, List, Dict

def load_excel_sheets(path: Path) -> Dict[str, List[Dict[str, Any]]]:
    sheets = pd.read_excel(
        path,
        sheet_name=None,
        dtype=object,
        engine="openpyxl",          # explicit engine for security
        keep_default_na=False,      # treat empty strings as empty, not NaN
    )
    result: Dict[str, List[Dict[str, Any]]] = {}
    for name, df in sheets.items():
        df = df.dropna(how="all")
        records: List[Dict[str, Any]] = (
            df.where(df.notna(), None)
            .to_dict(orient="records")
        )
        result[name] = records
    return result

# Example usage
all_records = load_excel_sheets(Path("workbook.xlsx"))
rules = all_records["Rules"]
```

**HARD RULE:** Do not mix `openpyxl` and `pandas` objects in the same module. Pick one library per processing pipeline.

### Step 3 — Handle empty cells safely

Compare against `is None` or call `.strip()` rather than truthiness — `0` and `False` are valid values that fail truthy tests:

```python
def get(rec: dict, key: str, default: Any = None) -> Any:
    """Return a safe value for possibly-empty cells."""
    val = rec.get(key)
    return default if val is None or (isinstance(val, str) and not val.strip()) else val
```

### Step 4 — Parse composite cells

A single cell may contain a comma-separated list, a JSON blob, or a single token. Try the simple split first, then fall back to JSON:

```python
import json
from typing import List

def split_list_cell(value: Any) -> List[str]:
    """Split a comma-separated list cell, falling back to JSON if appropriate."""
    if value is None:
        return []
    text = str(value).strip()
    if "," in text:
        return [item.strip() for item in text.split(",") if item.strip()]
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed]
    except json.JSONDecodeError:
        pass
    return [text]  # single token
```

If you see a cell with curly-brace text, it is probably an embedded JSON document; parse with `json.loads`.

### Step 5 — Propagate merged cells

Merged cells in Excel only store the value in the top-left cell; the rest are `None`. Fill down:

```python
def propagate_merged_column(records: List[dict], column: str) -> None:
    """Fill down values for a column that was merged in Excel."""
    last = None
    for row in records:
        if row.get(column) is None:
            row[column] = last
        else:
            last = row[column]
```

To check whether a cell is in a merged range, inspect `ws.merged_cells.ranges`.

### Step 6 — Read all needed sheets before processing

Use the metadata sheet (often named `Metadata`, `Info`, or `README`) for workbook-level fields, and the data sheet(s) for per-record rows. **Read all sheets you need before processing — do not assume the schema of one sheet is described inside another sheet you have not opened.**

### Step 7 — Full example: configuration-style workbook

```python
from pathlib import Path
import openpyxl
from typing import Any, Dict, List

def load_sheet_as_records(wb: openpyxl.Workbook, sheet_name: str) -> List[Dict[str, Any]]:
    ws = wb[sheet_name]
    rows = ws.iter_rows(values_only=True)
    header = [str(c).strip() if c else "" for c in next(rows)]
    return [
        dict(zip(header, row))
        for row in rows
        if any(cell is not None for cell in row)
    ]

path = Path("workbook.xlsx")
wb = openpyxl.load_workbook(path, data_only=True, read_only=True, keep_links=False)

metadata = {
    row[0]: row[1]
    for row in wb["Metadata"].iter_rows(min_row=2, values_only=True)
    if row[0] is not None
}
definitions = load_sheet_as_records(wb, "Definitions")
rules = load_sheet_as_records(wb, "Rules")
propagate_merged_column(rules, "section")
```

After this, `rules[0]["key"]`, `rules[0]["rule_type"]`, etc. are plain Python values you can branch on. The rest of your code does not need to know the input was Excel.

## Examples

```python
# Print each rule's key and type
for rule in rules:
    print(f"{rule['key']}: {rule['rule_type']}")
```

```python
# Split a composite cell containing a state list
states = split_list_cell(rules[0]["states"])
print(states)  # ['Delaware', 'New York', 'California']
```

```python
# Safe access to a possibly-empty cell
threshold = get(rules[0], "threshold", default=0)
```

## Pitfalls

1. **Truthiness on `0` or `False`** — These are valid cell values. Always compare with `is None` or `.strip()`, never bare `if cell:`.
2. **Mixing `openpyxl` and `pandas` in one pipeline** — Causes subtle type-conversion bugs. Pick one per module.
3. **Forgetting `keep_links=False`** — Exposes you to XML-entity attacks from untrusted workbooks.
4. **Using `read_only=False` on large files** — Exhausts memory. Always use `read_only=True` unless you need to write.
5. **Assuming sheet order** — Sheet indices can change. Always reference sheets by name, not position.
6. **Merged cells producing `None`** — Only the top-left cell of a merge range holds the value. Call `propagate_merged_column` before processing.
7. **Formula cells without `data_only=True`** — You get the formula string (e.g., `=A1+B1`) instead of the computed value.
8. **`.xls` files** — `openpyxl` will refuse them. Use `xlrd<2` or convert to `.xlsx` first.
9. **Trailing blank rows** — Excel preserves them. The `any(cell is not None ...)` filter removes them, but only if you include it.
10. **Header row not on row 1** — If headers start on a different row, adjust `min_row` in `iter_rows` or use `pandas` with `header=<row_index>`.

## Verification

Run these checks after implementing the parser:

```powershell
# 1. Verify openpyxl is installed and importable
python -c "import openpyxl; print(f'openpyxl {openpyxl.__version__}')"

# 2. Run a quick parse test on a sample workbook
python -c "from pathlib import Path; import openpyxl; wb = openpyxl.load_workbook(Path('workbook.xlsx'), data_only=True, read_only=True, keep_links=False); print(wb.sheetnames)"
```

Checklist:

- [ ] Records are correctly parsed from a sample workbook — sheet names print as expected.
- [ ] Empty cells become `None` (not `NaN`, not empty string unless explicitly kept).
- [ ] Merged cells are propagated correctly — no `None` values in columns that were merged.
- [ ] Composite list cells are split as expected — `split_list_cell` returns a list, not a string.
- [ ] `0` and `False` values are preserved — not dropped by truthiness checks.
- [ ] No `openpyxl`/`pandas` mixing in the same module.

## Related skills

- **csv-parsing** — for handling comma-separated value files.
- **json-parsing** — for reading JSON or JSONL inputs.
- **xls-parsing** — for legacy Excel `.xls` files (requires `xlrd`).
