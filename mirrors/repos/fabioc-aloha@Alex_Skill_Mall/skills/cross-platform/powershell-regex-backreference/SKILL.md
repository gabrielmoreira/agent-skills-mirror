---
type: skill
lifecycle: stable
inheritance: inheritable
name: powershell-regex-backreference
description: PowerShell regex backreference syntax pitfalls — dollar-sign escaping in replacement strings
tier: standard
applyTo: '**/*powershell*,**/*regex*,**/*backreference*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# PowerShell Regex Backreference Ambiguity

**Category**: Cross-Platform
**Time Saved**: 30+ minutes debugging "wrong capture group"
**Battle-tested**: Yes — Alex extension scripts

---

## The Problem

Your PowerShell regex replacement isn't working right. You want to capture a group and append "0" to it, but the output is wrong or empty.

```powershell
# You want: "v1" → "v10"
$version = "v1"
$result = $version -replace 'v(\d+)', 'v$10'
# Expected: "v10"
# Actual: "" or garbage — $10 is capture group 10, not $1 + "0"
```

## Why It Happens

PowerShell (and many regex engines) interpret `$1` followed by a digit as a **multi-digit backreference**. `$10` means "capture group 10", not "capture group 1 followed by the character 0".

## The Rule

**Use `${n}` syntax or named groups when backreference is followed by a digit**

```powershell
# ❌ AMBIGUOUS — $10 = capture group 10
$result = $version -replace 'v(\d+)', 'v$10'

# ✅ EXPLICIT — ${1} clearly separates backreference from literal
$result = $version -replace 'v(\d+)', 'v${1}0'

# ✅ NAMED GROUP — even clearer
$result = $version -replace 'v(?<major>\d+)', 'v${major}0'
```

## Safe Patterns

| Scenario | Pattern | Replacement |
|----------|---------|-------------|
| Backreference + digit | `(\d+)` | `${1}0` |
| Backreference + letter | `(\d+)` | `$1x` (safe, no ambiguity) |
| Multiple groups | `(\d+)\.(\d+)` | `${1}_${2}` |
| Named groups | `(?<major>\d+)` | `${major}` |

## Real-World Example

Bumping a version number:

```powershell
# Increment patch version: 1.2.3 → 1.2.4
$version = "1.2.3"

# ❌ BROKEN — if you tried to append to group
$result = $version -replace '(\d+)\.(\d+)\.(\d+)', '$1.$2.$30'  # $30!

# ✅ CORRECT — use script block for arithmetic
$result = $version -replace '(\d+)\.(\d+)\.(\d+)', {
    "$($_.Groups[1].Value).$($_.Groups[2].Value).$([int]$_.Groups[3].Value + 1)"
}
```

## Cross-Platform Note

This ambiguity exists in:

- PowerShell (`-replace`)
- .NET (`Regex.Replace`)
- JavaScript (`String.replace` with function)
- Python (`re.sub`)

The `${n}` syntax works in PowerShell and .NET. JavaScript and Python have their own escaping rules.

## Verification

```powershell
# Test your pattern with simple input first
"test1" -replace '(\w+)(\d)', '${1}X${2}Y'
# Expected: "testX1Y"
```

---

**Source**: Promoted from AI-Memory global-knowledge.md (2026-04-27)
