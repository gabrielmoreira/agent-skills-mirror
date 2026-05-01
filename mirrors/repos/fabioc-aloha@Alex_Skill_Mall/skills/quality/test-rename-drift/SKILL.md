---
type: skill
lifecycle: stable
inheritance: inheritable
name: test-rename-drift
description: When renaming a function, test files have references that survive find-and-replace:
tier: standard
applyTo: '**/*test*,**/*rename*,**/*drift*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Test Rename Drift

## The Problem

When renaming a function, test files have references that survive find-and-replace:

```javascript
// Old function: calculateTotal()
// New function: computeTotal()

// Find-and-replace catches: calculateTotal(
// But misses:
describe('calculateTotal', () => {  // Describe block
  // tests for calculateTotal    // Comment
  it('calculateTotal returns sum', () => { // It block text
```

## The Solution

Grep for BOTH the old AND new name after renaming.

```bash
# After renaming calculateTotal → computeTotal

# Find remaining old references
grep -rn "calculateTotal" . --include="*.test.*" --include="*.spec.*"

# Verify new references exist
grep -rn "computeTotal" . --include="*.test.*" --include="*.spec.*"
```

## Checklist

| Location | Find Pattern | Replace? |
|----------|--------------|----------|
| Function calls | `oldName(` | ✅ Auto |
| Import statements | `import { oldName }` | ✅ Auto |
| Describe blocks | `describe('oldName'` | ❌ Manual |
| It block text | `it('oldName should'` | ❌ Manual |
| Comments | `// oldName does X` | ❌ Manual |
| Variable names | `const oldNameResult` | Depends |
| Mock names | `jest.mock('oldName')` | ❌ Manual |
| Snapshot files | Contains "oldName" | ❌ Manual |

## Automated Check

```javascript
// scripts/check-rename-drift.cjs
const oldName = process.argv[2];
const newName = process.argv[3];

const { execSync } = require('child_process');

const oldRefs = execSync(
  `grep -rn "${oldName}" . --include="*.test.*" --include="*.spec.*" || true`,
  { encoding: 'utf8' }
);

if (oldRefs.trim()) {
  console.error(`Found ${oldRefs.split('\n').length - 1} remaining references to "${oldName}":`);
  console.error(oldRefs);
  process.exit(1);
}

console.log(`No remaining references to "${oldName}" in test files.`);
```

## Verification

```bash
# Run after any rename
node scripts/check-rename-drift.cjs oldFunctionName newFunctionName

# Should report: "No remaining references"
```

## When to Apply

- After any function/class/method rename
- Before committing renamed code
- During code review of renames

## Tags

`quality` `testing` `refactoring` `rename`
