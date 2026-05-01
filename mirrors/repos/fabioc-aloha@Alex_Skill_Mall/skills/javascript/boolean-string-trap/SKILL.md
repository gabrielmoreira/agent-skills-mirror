---
type: skill
lifecycle: stable
inheritance: inheritable
name: boolean-string-trap
description: JavaScript boolean-string coercion trap — "false" is truthy, JSON.parse or strict comparison required
tier: standard
applyTo: '**/*boolean*,**/*string*,**/*trap*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Boolean String Trap

**Category**: JavaScript
**Time Saved**: 30+ minutes debugging "why is false truthy?"
**Battle-tested**: Yes — Alex extension, multiple web apps

---

## The Problem

Your feature toggle isn't working. `if (showFeature)` always evaluates to true, even when the user disabled it. You check localStorage and it clearly shows `"false"`.

## Why It Happens

`localStorage`, `sessionStorage`, URL params, and form inputs all return **strings**. The string `"false"` is truthy in JavaScript because it's a non-empty string.

```javascript
// These are all TRUTHY
"false"   // string, non-empty
"0"       // string, non-empty
"null"    // string, non-empty
"undefined" // string, non-empty

// These are FALSY
false     // boolean
0         // number
null      // null
undefined // undefined
""        // empty string
```

## The Rule

**Use strict comparison or explicit parsing — never rely on truthiness for string-sourced values**

```javascript
// ❌ BROKEN — string "false" is truthy
const raw = localStorage.getItem('darkMode'); // "false"
if (raw) { enableDarkMode(); } // ALWAYS runs!

// ✅ CORRECT — strict comparison
const raw = localStorage.getItem('darkMode');
if (raw === 'true') { enableDarkMode(); }

// ✅ ALSO CORRECT — JSON.parse handles "true"/"false"
const darkMode = JSON.parse(localStorage.getItem('darkMode') || 'false');
if (darkMode) { enableDarkMode(); }
```

## Common Sources of String Booleans

| Source | Returns | Solution |
|--------|---------|----------|
| `localStorage.getItem()` | `string \| null` | `=== 'true'` or `JSON.parse()` |
| `sessionStorage.getItem()` | `string \| null` | `=== 'true'` or `JSON.parse()` |
| `URLSearchParams.get()` | `string \| null` | `=== 'true'` |
| `FormData.get()` | `string \| null` | `=== 'true'` |
| `process.env.VAR` | `string \| undefined` | `=== 'true'` |
| `dataset.myAttr` | `string` | `=== 'true'` |

## TypeScript Pattern

```typescript
function parseBooleanParam(value: string | null): boolean {
  if (value === null) return false;
  return value.toLowerCase() === 'true';
}

// Usage
const showAdvanced = parseBooleanParam(localStorage.getItem('showAdvanced'));
```

## VS Code Settings Pattern

`vscode.workspace.getConfiguration().get()` returns the **actual type** (boolean, number, etc.) — no parsing needed. But if you cache it to localStorage, you're back to strings.

```typescript
// ✅ Direct from VS Code config — typed correctly
const enabled = config.get<boolean>('myExtension.enabled');

// ⚠️ After round-trip through localStorage — needs parsing
localStorage.setItem('cached', String(enabled));
const cached = localStorage.getItem('cached') === 'true';
```

## Verification

```javascript
console.log(typeof value, value, Boolean(value));
// "string" "false" true  ← BUG: string coerces to true
// "boolean" false false  ← CORRECT: actual boolean
```

---

**Source**: Promoted from AI-Memory global-knowledge.md (2026-04-27)
