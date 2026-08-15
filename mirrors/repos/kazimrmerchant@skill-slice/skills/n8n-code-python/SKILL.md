---
name: n8n-code-python
description: "Writes Python inside n8n Code nodes using _input/_json/_node helpers, the standard library only, and a return of list-of-json dicts. Use when the Code node language is Python, or when choosing Python vs JavaScript for n8n. Not for JavaScript Code nodes (n8n-code-javascript) or {{ }} expressions (n8n-expression-syntax). Do not import pandas or requests; those packages are unavailable."
version: 1.0.1
---

## Overview

Expert guidance for writing Python code in n8n Code nodes. n8n supports two Python execution modes: **Python (Beta)** and **Python (Native) (Beta)**. Both are standard-library-only environments with no external package support.

**Core recommendation**: Use JavaScript for 95% of n8n Code node use cases. Only use Python when you need specific standard library functions (e.g., `statistics`, `re`, `hashlib`), are significantly more comfortable with Python syntax, or are doing data transformations better suited to Python.

JavaScript is preferred because it has full n8n helper functions (`$helpers.httpRequest`, etc.), Luxon DateTime library, no external library limitations, and better n8n documentation and community support.

## When to Use

- Writing Python code inside an n8n Code node
- Using `_input.all()`, `_input.first()`, `_input.item`, `_json`, or `_node` syntax
- Working with Python standard library modules in n8n
- Understanding Python limitations in n8n Code nodes (no external libraries)
- Debugging Python Code node errors (KeyError, ModuleNotFoundError, return format issues)
- Deciding between Python and JavaScript for an n8n Code node

## Prerequisites

- n8n instance with Code node available
- Python language selected in the Code node configuration
- Understanding of n8n item structure: `[{"json": {...}}]`

## Procedure

### 1. Select the Right Execution Mode

Choose the Code node mode based on your use case:

| Mode | When to Use | Data Access | Performance |
|------|-------------|-------------|-------------|
| **Run Once for All Items** (Recommended, Default) | 95% of use cases: aggregation, filtering, batch processing, transformations | `_input.all()` or `_items` (Native) | Faster for multiple items (single execution) |
| **Run Once for Each Item** | Specialized cases only: item-specific logic, independent operations, per-item validation | `_input.item` or `_item` (Native) | Slower for large datasets (multiple executions) |

### 2. Select Python Execution Mode

n8n offers two Python execution modes:

**Python (Beta)** — Recommended for better n8n integration:
- Uses `_input`, `_json`, `_node` helper syntax
- Helpers available: `_now`, `_today`, `_jmespath()`
- Import datetime with `from datetime import datetime`

**Python (Native) (Beta)** — Use when you need pure Python without n8n helpers:
- Uses `_items`, `_item` variables only
- No helpers: no `_input`, `_now`, etc.
- More limited: standard Python only

### 3. Write the Code — Basic Template

```python
# Basic template for Python Code nodes (Beta mode, Run Once for All Items)
items = _input.all()

# Process data
processed = []
for item in items:
    processed.append({
        "json": {
            **item["json"],
            "processed": True,
            "timestamp": datetime.now().isoformat()
        }
    })

return processed
```

### 4. Access Input Data Correctly

Use the correct data access pattern for your mode:

**Pattern 1: `_input.all()` — Most Common** (All Items mode)
```python
all_items = _input.all()
valid = [item for item in all_items if item["json"].get("status") == "active"]

processed = []
for item in valid:
    processed.append({
        "json": {
            "id": item["json"]["id"],
            "name": item["json"]["name"]
        }
    })
return processed
```

**Pattern 2: `_input.first()` — Single Object/API Response**
```python
first_item = _input.first()
data = first_item["json"]

return [{
    "json": {
        "result": process_data(data),
        "processed_at": datetime.now().isoformat()
    }
}]
```

**Pattern 3: `_input.item` — Each Item Mode Only**
```python
current_item = _input.item

return [{
    "json": {
        **current_item["json"],
        "item_processed": True
    }
}]
```

**Pattern 4: `_node` — Reference Other Nodes**
```python
webhook_data = _node["Webhook"]["json"]
http_data = _node["HTTP Request"]["json"]

return [{
    "json": {
        "combined": {
            "webhook": webhook_data,
            "api": http_data
        }
    }
}]
```

Use Pattern 1–4 above for `$input` / `$node`. Webhook payloads are under `.body` (Pitfall #3).

### 5. Handle Webhook Data Correctly

**CRITICAL**: Webhook data is nested under `["body"]`, not accessible directly from `_json`.

```python
# WRONG — Will raise KeyError
name = _json["name"]

# CORRECT — Webhook data is under ["body"]
name = _json["body"]["name"]

# SAFER — Use .get() for safe access
webhook_data = _json.get("body", {})
name = webhook_data.get("name")
```

The Webhook node wraps all request data (POST data, query parameters, JSON payloads) under the `body` property.

### 6. Return Data in the Correct Format

**CRITICAL RULE**: Always return a list of dictionaries with a `"json"` key.

```python
# Single result
return [{"json": {"field1": value1, "field2": value2}}]

# Multiple results
return [
    {"json": {"id": 1, "data": "first"}},
    {"json": {"id": 2, "data": "second"}}
]

# List comprehension
transformed = [
    {"json": {"id": item["json"]["id"], "processed": True}}
    for item in _input.all()
    if item["json"].get("valid")
]
return transformed

# Empty result
return []

# Conditional return
if should_process:
    return [{"json": processed_data}]
else:
    return []
```

### 7. Use Only Standard Library Modules

**CRITICAL LIMITATION**: No external libraries are available. Attempting to import `requests`, `pandas`, `numpy`, `scipy`, `bs4`, `lxml`, or any other external package will raise `ModuleNotFoundError`.

Available standard library modules:
```python
import json              # JSON parsing
import datetime          # Date/time operations
import re                # Regular expressions
import base64            # Base64 encoding/decoding
import hashlib           # Hashing functions
import urllib.parse      # URL parsing
import math              # Math functions
import random            # Random numbers
import statistics        # Statistical functions
```

Stay on this standard-library list. There is no extra module catalog in this pack.

### 8. Work Around Missing Libraries

| Need | Workaround |
|------|------------|
| HTTP requests | Use **HTTP Request node** before Code node, or switch to JavaScript with `$helpers.httpRequest()` |
| Data analysis (pandas/numpy) | Use Python `statistics` module for basic stats, or switch to JavaScript, or manual calculations with lists/dicts |
| Web scraping (BeautifulSoup) | Use **HTTP Request node** + **HTML Extract node**, or switch to JavaScript with regex/string methods |

## Examples

### Data Transformation with List Comprehensions

```python
items = _input.all()

return [
    {
        "json": {
            "id": item["json"].get("id"),
            "name": item["json"].get("name", "Unknown").upper(),
            "processed": True
        }
    }
    for item in items
]
```

### Filtering and Aggregation

```python
items = _input.all()
total = sum(item["json"].get("amount", 0) for item in items)
valid_items = [item for item in items if item["json"].get("amount", 0) > 0]

return [{
    "json": {
        "total": total,
        "count": len(valid_items)
    }
}]
```

### String Processing with Regex

```python
import re

items = _input.all()
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

all_emails = []
for item in items:
    text = item["json"].get("text", "")
    emails = re.findall(email_pattern, text)
    all_emails.extend(emails)

unique_emails = list(set(all_emails))

return [{
    "json": {
        "emails": unique_emails,
        "count": len(unique_emails)
    }
}]
```

### Data Validation

```python
items = _input.all()
validated = []

for item in items:
    data = item["json"]
    errors = []

    if not data.get("email"):
        errors.append("Email required")
    if not data.get("name"):
        errors.append("Name required")

    validated.append({
        "json": {
            **data,
            "valid": len(errors) == 0,
            "errors": errors if errors else None
        }
    })

return validated
```

### Statistical Analysis

```python
from statistics import mean, median, stdev

items = _input.all()
values = [item["json"].get("value", 0) for item in items if "value" in item["json"]]

if values:
    return [{
        "json": {
            "mean": mean(values),
            "median": median(values),
            "stdev": stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "count": len(values)
        }
    }]
else:
    return [{"json": {"error": "No values found"}}]
```

### Native Mode Example

```python
# Python (Native) — uses _items instead of _input
processed = []

for item in _items:
    processed.append({
        "json": {
            "id": item["json"].get("id"),
            "processed": True
        }
    })

return processed
```

The Examples section above covers transformation, filtering, regex, validation, stats, and Native mode.

## Pitfalls

### 1. Importing External Libraries (Python-Specific)

```python
# WRONG — Will raise ModuleNotFoundError
import requests
import pandas
import numpy

# CORRECT — Use HTTP Request node before Code node, or switch to JavaScript
```

### 2. Empty Code or Missing Return

```python
# WRONG — No return statement
items = _input.all()
# Processing...
# Forgot to return!

# CORRECT — Always return data
items = _input.all()
return [{"json": item["json"]} for item in items]
```

### 3. Incorrect Return Format

```python
# WRONG — Returning dict instead of list
return {"json": {"result": "success"}}

# WRONG — List without json wrapper
return [{"field": value}]

# WRONG — Plain string
return "processed"

# CORRECT — List wrapper with json key required
return [{"json": {"result": "success"}}]
```

### 4. KeyError on Dictionary Access

```python
# WRONG — Direct access crashes if missing
name = _json["user"]["name"]

# CORRECT — Use .get() for safe access
name = _json.get("user", {}).get("name", "Unknown")
```

### 5. Webhook Body Nesting

```python
# WRONG — Direct access to webhook data
email = _json["email"]

# CORRECT — Webhook data under ["body"]
email = _json["body"]["email"]

# BETTER — Safe access with .get()
email = _json.get("body", {}).get("email", "no-email")
```

### 6. Using JavaScript-Only Helpers in Python

Python Code nodes do NOT have access to `$helpers.httpRequest()`, Luxon, or other JavaScript-specific n8n helpers. Use `_now`, `_today`, `_jmespath()` in Beta mode only. Native mode has no helpers at all.

### 7. Not Handling None/Null Values

```python
# RISKY — None can propagate and cause errors
amount = item["json"].get("amount")

# GOOD — Default to 0 if None
amount = item["json"].get("amount") or 0

# GOOD — Check for None explicitly
text = item["json"].get("text")
if text is None:
    text = ""
```

Use the Pitfalls section above when troubleshooting execution errors, validation failures, or unexpected output from Python Code nodes.

## Verification

Before deploying a Python Code node, verify each item on this checklist:

1. **Considered JavaScript first** — Using Python only when necessary
2. **Code is not empty** — Must have meaningful logic
3. **Return statement exists** — Must return a list of dictionaries
4. **Proper return format** — Each item structured as `{"json": {...}}`
5. **Data access correct** — Using `_input.all()`, `_input.first()`, or `_input.item` (Beta mode); `_items` or `_item` (Native mode)
6. **No external imports** — Only standard library (`json`, `datetime`, `re`, `base64`, `hashlib`, `urllib.parse`, `math`, `random`, `statistics`)
7. **Safe dictionary access** — Using `.get()` to avoid KeyError
8. **Webhook data** — Access via `["body"]` if data comes from a Webhook node
9. **Mode selection** — "All Items" for most cases; "Each Item" only for per-item independent logic
10. **Output consistent** — All code paths return the same structure

**Debug technique**: Use `print()` statements. Output appears in the browser console (F12).

```python
items = _input.all()
print(f"Processing {len(items)} items")
print(f"First item: {items[0] if items else 'None'}")
```

**Test execution**: Run the node in the n8n editor with sample input data and confirm:
- No `ModuleNotFoundError` (no external imports)
- No `KeyError` (safe `.get()` access used)
- No "missing return" error
- Output is a valid list of `{"json": {...}}` items
- Webhook-sourced data accessed via `_json["body"]` or `_json.get("body", {})`

## Related Skills

- **n8n Expression Syntax** — Expressions use `{{ }}` syntax in other nodes; Code nodes use Python directly (no `{{ }}`)
- **n8n MCP Tools Expert** — Find Code node with `search_nodes({query: "code"})`, get config help with `get_node_essentials("nodes-base.code")`, validate with `validate_node_operation()`
- **n8n Node Configuration** — Mode selection (All Items vs Each Item), language selection (Python vs JavaScript)
- **n8n Workflow Patterns** — Code nodes in transformation steps, when to use Python vs JavaScript
- **n8n Validation Expert** — Validate Code node configuration, handle validation errors, auto-fix common issues
- **n8n Code JavaScript** — When to use JavaScript instead, feature comparison, migration from Python to JavaScript

## Limitations

- Use this skill only when the task clearly involves writing Python in n8n Code nodes.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
