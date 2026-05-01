---
type: skill
lifecycle: stable
inheritance: inheritable
name: line-ending-parsing
description: Line ending handling across platforms — CRLF vs LF detection, normalization, and git config
tier: standard
applyTo: '**/*line*,**/*ending*,**/*parsing*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Line Ending Parsing

**Category**: Cross-Platform
**Time Saved**: 30 minutes debugging string comparisons
**Battle-tested**: Yes — breaks pattern matching silently

---

## The Problem

You split a text file into lines and process each one. It works on macOS/Linux. On Windows, your regex patterns fail to match, or string comparisons return false even though the content looks identical.

## Why It Happens

Windows uses `\r\n` (CRLF) for line endings. Unix uses `\n` (LF).

```javascript
// File content on Windows:
"line1\r\nline2\r\nline3"

// After split("\n"):
["line1\r", "line2\r", "line3"]
//      ↑ invisible \r still attached!

// Your pattern fails:
"line1\r" === "line1"  // false
/^line1$/.test("line1\r")  // false
```

## The Rule

**Always use `/\r?\n/` regex for splitting text files into lines.**

```javascript
// ❌ WRONG — leaves \r on Windows
const lines = content.split('\n');

// ✅ CORRECT — handles both CRLF and LF
const lines = content.split(/\r?\n/);
```

## Implementation Pattern

```javascript
const fs = require('fs');

function parseTextFile(filepath) {
  const content = fs.readFileSync(filepath, 'utf8');
  
  // Normalize line endings
  const lines = content.split(/\r?\n/);
  
  // Or use a helper
  return normalizeLines(content);
}

function normalizeLines(text) {
  // Option 1: Split with regex
  return text.split(/\r?\n/);
  
  // Option 2: Normalize then split
  // return text.replace(/\r\n/g, '\n').split('\n');
}
```

## When This Matters

| Use Case | Impact of \r |
|----------|-------------|
| String equality | `"word\r" !== "word"` |
| Regex matching | `/^word$/` fails |
| Hash/checksum | Different hash values |
| JSON parsing | Usually OK (JSON.parse handles it) |
| CSV parsing | Column values have trailing \r |
| Config parsing | Key/value lookups fail |

## Common Symptoms

- "Pattern doesn't match on Windows"
- "String comparison fails but they look the same"
- "Works on Mac, breaks on Windows"
- `console.log` shows correct content but code doesn't match

## Debugging Hidden Characters

```javascript
// Reveal hidden characters
function showHidden(str) {
  return str
    .replace(/\r/g, '\\r')
    .replace(/\n/g, '\\n');
}

console.log(showHidden(line));
// "expected value\r" ← the culprit!
```

## Related Scenarios

### Trimming Doesn't Always Help

```javascript
// trim() removes \r, but only at ends
"  line1\r  ".trim()  // "line1\r" — \r still there if spaces follow!

// Be explicit
line.replace(/\r$/, '').trim()
```

### Reading Streams

```javascript
// readline module handles this automatically
const rl = readline.createInterface({ input: stream });
rl.on('line', (line) => {
  // line has no \r or \n
});
```

### Writing Cross-Platform

```javascript
const os = require('os');

// Write with platform-appropriate line endings
const output = lines.join(os.EOL);

// Or force Unix line endings (common in config files)
const output = lines.join('\n');
```

## Verification Checklist

- [ ] All `split('\n')` calls use `/\r?\n/` instead
- [ ] String comparisons work on Windows test machine
- [ ] Config/CSV parsing tested with CRLF files
- [ ] Git autocrlf settings considered for repos

## Related Skills

- `cloud-storage-paths` — Cross-platform file access
- `terminal-backtick-hazard` — Cross-platform command execution
