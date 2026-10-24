# Widget Formula Expressions

A formula expression can appear anywhere a `{!...}` binding is written — `attributes` values, string interpolation, and `meta.if`. Read this file when a widget needs formulas.

---

## Syntax

Every formula expression is wrapped in `{!...}`, similar to a plain binding:

```text
{!FUNCTION($attrs.fieldName)}
```

- **Field references inside a formula** use the same `$attrs.<path>` convention as plain bindings.
- Inside a `forEach`, use the loop variable instead of `$attrs` — e.g. `{!UPPER($item.property)}`. Formulas inside `forEach` evaluate once per iteration against the current loop item — not the whole array.
- Functions and operators are case-sensitive UPPERCASE.
- A formula can nest functions and mix functions with operators: `{!TEXT(ROUND($attrs.property, 2))}`, `{!LEFT($attrs.property, 5) & "..."}`.
- A formula-bearing attribute is still bound to schema properties the same way as a plain binding — every `$attrs.X` / `$item.X` referenced inside a formula must resolve to a real schema property or loop variable, per the `bindings-resolve` self-validation check.
- A Custom Label reference `$Label.c.<LabelName>` can be used as a text value inside a formula. See `references/widget-labels.md`.

---

## Supported functions and operators, by category

Only the operators/functions listed here are confirmed supported — do not invent variants.

### 1. Arithmetic operators

| Operator | Meaning | Example                             |
|---|---|-------------------------------------|
| `+` | Add | `$attrs.operand1 + $attrs.operand2` |
| `-` | Subtract | `$attrs.operand1 - $attrs.operand2` |
| `*` | Multiply | `$attrs.operand1 * $attrs.operand2` |
| `/` | Divide | `$attrs.operand1 / $attrs.operand2` |
| `^` | Exponent | `$attrs.operand1 ^ $attrs.operand2` |

Unary minus (`-$attrs.fieldName`) is also supported. Precedence, lowest to highest: `||`, `&&`, equality, relational, `+` `-` `&`, `^`, `*` `/`, unary. Note that `*` and `/` bind tighter than `^`, so `2 * 3 ^ 2` is `(2 * 3) ^ 2`; parenthesize to be explicit.

### 2. Comparison operators

Return `true`/`false`; commonly used inside `IF()` or `meta.if`.

| Operator | Meaning | Example                                |
|---|---|----------------------------------------|
| `=` | Equal | `$attrs.property = 'constantValue'`    |
| `<>` | Not equal | `$attrs.property <> 'constantValue'`   |
| `>` / `<` | Greater / less than | `$attrs.property > 1000`               |
| `>=` / `<=` | Greater-or-equal / less-or-equal | `$attrs.property1 >= $attrs.property2` |

`==` and `!=` are accepted as aliases for `=` and `<>`. Both operands must have the same type; text is never compared with a number.

### 3. Logical functions

| Function | Description | Example                                                                                              |
|---|---|------------------------------------------------------------------------------------------------------|
| `IF(cond, then, else)` | Conditional value; nests for multi-branch logic. `cond` must be a boolean (`IF($attrs.count > 0, …)`, not `IF($attrs.count, …)`) and both branches must have the same type | `IF($attrs.property > value, 'result1', 'result2')`                                                  |
| `CASE(expr, val1, res1, val2, res2, ..., default)` | Multi-way match, cleaner than nested `IF` for 3+ branches | `CASE($attrs.property, 'value1', 'result1', 'value2', 'result2', 'value3', 'result3', 'defaultResult')` |
| `AND(...)` | All conditions true | `AND($attrs.property1, $attrs.property2 > value)`                                                    |
| `OR(...)` | Any condition true | `OR($attrs.property1, $attrs.property2 > value)`                                                     |
| `NOT(val)` | Negate a boolean | `NOT($attrs.property)`                                                                               |
| `&&` / `\|\|` / `!` (operators) | Aliases for `AND` / `OR` / `NOT` | `$attrs.property1 && !$attrs.property2` |
| `ISNULL(val)` | True if the value is null. Always false for text — use `ISBLANK` for strings | `IF(ISNULL($attrs.property), 'null', 'has-value')`                                                   |
| `ISBLANK(val)` | True if null or empty string | `IF(ISBLANK($attrs.property), 'blank', 'has-value')`                                                 |

### 4. Text functions

| Function | Description | Example                                             |
|---|---|-----------------------------------------------------|
| `UPPER(str[, locale])` / `LOWER(str[, locale])` | Case conversion, optionally for a locale such as `'tr'` | `UPPER($attrs.property)`                            |
| `LEFT(str, n)` / `RIGHT(str, n)` | First/last `n` characters | `LEFT($attrs.property, 3)`                          |
| `MID(str, start, len)` | Substring, **1-based** start index (first character is position 1, not 0) | `MID($attrs.property, 1, 3)`                        |
| `SUBSTR(str, start[, len])` | Substring with a **1-based** start; a negative `start` counts from the end; without `len`, runs to the end | `SUBSTR($attrs.property, -4)` |
| `LEN(val)` | Length of a string | `LEN($attrs.property)`                              |
| `TRIM(str)` | Strip leading/trailing whitespace | `TRIM($attrs.property)`                             |
| `REVERSE(str)` | Reverse a string | `REVERSE($attrs.property)`                          |
| `SUBSTITUTE(str, old, new)` | Replace all occurrences | `SUBSTITUTE($attrs.property, 'string1', 'string2')` |
| `FIND(search, str[, start])` | 1-based index of `search` in `str`, or `0` if absent; optional 1-based `start` position | `FIND('string', $attrs.property)`                   |
| `LPAD(str, len, pad)` / `RPAD(str, len, pad)` | Pad to a fixed width | `LPAD($attrs.property, 12, '.')`                    |
| `TEXT(val)` | Coerce a non-string value to text (commonly paired with `ROUND`) | `TEXT(ROUND($attrs.property, 2))`                   |
| `VALUE(str)` | Parse text to a number (inverse of `TEXT`) | `VALUE($attrs.property)`                            |
| `CONTAINS(str, sub)` | String contains substring — boolean, pair with `IF` | `CONTAINS($attrs.property, 'string')`               |
| `BEGINS(str, prefix)` | String starts with — boolean, pair with `IF` | `BEGINS($attrs.property, 'string')`                 |
| `&` (operator) | Concatenate strings. Both sides must be text, so wrap numbers and dates in `TEXT()` — `'Total: ' & TEXT($attrs.total)` | `$attrs.property1 & ' — ' & $attrs.property2`       |

### 5. Math functions

| Function | Description | Example                                        |
|---|---|------------------------------------------------|
| `MOD(num, div)` | Remainder | `MOD($attrs.fieldName, 100)`                   |
| `MAX(...)` / `MIN(...)` | Largest/smallest of the arguments | `MAX($attrs.fieldName, 2000)`                  |
| `ROUND(num, digits)` | Round to `digits` decimal places | `ROUND($attrs.fieldName, 1)`                   |
| `ABS(num)` | Absolute value | `ABS($attrs.fieldName)`                        |
| `SQRT(num)` | Square root | `SQRT($attrs.fieldName)`                       |
| `CEILING(num)` / `FLOOR(num)` | Round away from / toward zero on the *magnitude* | `CEILING($attrs.fieldName)`|
| `MCEILING(num)` / `MFLOOR(num)` | Round toward +∞ / −∞ ("mathematical" ceiling/floor) — matters for negative numbers | `MCEILING($attrs.fieldName)`, `MFLOOR($attrs.fieldName)`|
| `LOG(num)` / `EXP(num)` / `LN(num)` | Base-10 log, e^x, natural log | `LOG($attrs.fieldName)`                              |

### 6. Date & time functions

| Function | Description | Example                                         |
|---|---|-------------------------------------------------|
| `DATEVALUE(str)` / `DATETIMEVALUE(str)` / `TIMEVALUE(str)` | Parse a date/datetime/time string into a value | `DATEVALUE($attrs.fieldName)`                   |
| `DAY(date)` / `MONTH(date)` / `YEAR(date)` | Extract date components | `DAY(DATEVALUE($attrs.fieldName))`              |
| `WEEKDAY(date)` | Day of week, `1`=Sunday … `7`=Saturday | `WEEKDAY(DATEVALUE($attrs.fieldName))`      |
| `ADDMONTHS(date, n)` | Add `n` whole months to a date | `ADDMONTHS(DATEVALUE($attrs.fieldName), 3)` |
| `TODAY()` / `NOW()` / `TIMENOW()` | Current date / datetime / time in UTC — no arguments | `TODAY()`                                       |
| `DATE(year, month, day)` | Construct a date literal | `DATE(2026, 12, 31)`                            |
| `HOUR(dt)` / `MINUTE(dt)` / `SECOND(dt)` / `MILLISECOND(dt)` | Extract time components from a datetime | `HOUR(NOW())`                                   |

A raw date/datetime **string** attribute (e.g. an ISO string from `$attrs`) must be parsed with `DATEVALUE`/`DATETIMEVALUE`/`TIMEVALUE` before date-math or extractor functions can operate on it.

### 7. Validation & encoding functions

| Function | Description | Example                                      |
|---|---|----------------------------------------------|
| `NULLVALUE(val, fallback)` | `fallback` only when `val` is null | `NULLVALUE($attrs.fieldName, 'fallback')`    |
| `BLANKVALUE(val, fallback)` | `fallback` when `val` is null or an empty string | `BLANKVALUE($attrs.fieldName, 'fallback')`   |
| `HTMLENCODE(str)` | Escape for literal HTML display — use on any text binding that must render literally rather than as markup | `HTMLENCODE($attrs.fieldName & ' <b>tag</b>')` |
| `JSENCODE(str)` | Escape for safe embedding in a JS-string context | `JSENCODE($attrs.fieldName & "'quote")`        |

### 8. Pattern matching functions

| Function | Description | Example |
|---|---|---|
| `ISNUMBER(val)` | True if the value parses as a number | `ISNUMBER($attrs.fieldName)` |
| `REGEX(str, pattern)` | True if `str` matches the regex `pattern` (standard regex string) | `REGEX($attrs.fieldName, '^[A-Z]{2} [0-9]+$')` |

### 9. Locale formatting functions

Format values for the viewer's locale. A null or blank input returns null. The optional last argument is a decimal count for the number functions and `'short'` (default), `'medium'` or `'long'` for the date and time functions.

| Function | Description | Example |
|---|---|---|
| `FORMATNUMBER(num[, decimals])` | Locale-formatted number | `FORMATNUMBER($attrs.fieldName, 2)` |
| `FORMATPERCENT(num[, decimals])` | Locale-formatted percent (`0.25` → `25%`) | `FORMATPERCENT($attrs.fieldName, 1)` |
| `FORMATCURRENCY(num)` | Currency code followed by the amount, e.g. `USD 1,234.50` (no currency symbol) | `FORMATCURRENCY($attrs.fieldName)` |
| `FORMATDATE(date[, style])` | Locale date | `FORMATDATE($attrs.fieldName, 'medium')` |
| `FORMATDATETIME(dt[, style])` | Locale date and time | `FORMATDATETIME($attrs.fieldName, 'long')` |
| `FORMATTIME(time[, style])` | Locale time | `FORMATTIME($attrs.fieldName)` |
