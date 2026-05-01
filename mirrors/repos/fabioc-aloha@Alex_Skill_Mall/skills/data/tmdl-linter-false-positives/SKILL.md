---
type: skill
lifecycle: stable
inheritance: inheritable
name: tmdl-linter-false-positives
description: VS Code's TMDL (Tabular Model Definition Language) linter reports valid syntax as errors:
tier: standard
applyTo: '**/*tmdl*,**/*linter*,**/*false*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# TMDL Linter False Positives

## The Problem

VS Code's TMDL (Tabular Model Definition Language) linter reports valid syntax as errors:

```tmdl
measure 'Total Sales' = SUM('Sales'[Amount])
    description = "Sum of all sales amounts"  // Linter: "Invalid property 'description'"
```

The `description` property IS valid — this is a linter limitation.

## The Solution

Ignore these specific false positives:

### Known False Positives

| Property | Context | Actual Status |
|----------|---------|---------------|
| `description` | On measures | ✅ Valid |
| `description` | On columns | ✅ Valid |
| `formatString` | Some contexts | ✅ Valid |
| `displayFolder` | On measures | ✅ Valid |

### Verification

Test in Power BI Desktop or Tabular Editor:

1. Apply the TMDL
2. If it loads without error, the syntax is correct
3. The VS Code linter is wrong, not your code

## Workaround Options

### Option 1: Ignore the Squiggles

The TMDL will work — the linter is just incomplete.

### Option 2: Suppress in Settings

```json
// .vscode/settings.json
{
  "tmdl.validate": false
}
```

### Option 3: Use Tabular Editor

Tabular Editor's TMDL support is more complete.

## When Linter IS Correct

| Error | Likely Real |
|-------|-------------|
| Syntax errors (missing `=`, unmatched quotes) | Yes |
| Unknown table/column references | Yes |
| DAX function errors | Yes |
| Property on wrong object type | Maybe |

## Verification

```bash
# Deploy to test
# If no error in Power BI/SSAS, linter was wrong
```

## When to Apply

- TMDL development in VS Code
- Any unexpected linter error on common properties
- When syntax looks correct but shows errors

## Tags

`data` `tmdl` `power-bi` `linting` `false-positive`
