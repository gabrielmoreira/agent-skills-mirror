---
type: skill
lifecycle: stable
inheritance: inheritable
name: fix-once-auto-inject
description: One-time fixes get repeated manually:
tier: standard
applyTo: '**/*fix*,**/*once*,**/*auto*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Fix-Once + Auto-Inject-Future

## The Problem

One-time fixes get repeated manually:

- "Add the missing import to every new file"
- "Remember to set the flag when creating services"
- Relies on human memory → fails over time

## The Solution

Pair an idempotent one-time fix with a build-time auto-inject fallback.

### Prong 1: One-Time Fix Script

```javascript
// scripts/fix-missing-headers.cjs
const fs = require('fs');
const glob = require('glob');

const header = '// Copyright 2026 Company\n\n';

glob.sync('src/**/*.ts').forEach(file => {
  const content = fs.readFileSync(file, 'utf8');
  if (!content.startsWith('// Copyright')) {
    fs.writeFileSync(file, header + content);
    console.log(`Fixed: ${file}`);
  }
});
```

Run once to fix existing files.

### Prong 2: Auto-Inject at Build

```javascript
// In build pipeline or git hook
const files = getChangedFiles();
files.filter(f => f.endsWith('.ts')).forEach(file => {
  const content = fs.readFileSync(file, 'utf8');
  if (!content.startsWith('// Copyright')) {
    // Auto-fix or fail the build
    console.error(`Missing header: ${file}`);
    process.exit(1);
  }
});
```

### Git Hook Version

```bash
#!/bin/bash
# .git/hooks/pre-commit

for file in $(git diff --cached --name-only | grep '\.ts$'); do
  if ! head -1 "$file" | grep -q "Copyright"; then
    echo "Missing copyright header: $file"
    exit 1
  fi
done
```

## Pattern

```
┌─────────────────────────────────────┐
│  Fix existing files (one-time)      │
│  node scripts/fix-all.cjs           │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Enforce on new files (ongoing)     │
│  build hook / pre-commit / CI       │
└─────────────────────────────────────┘
```

## Verification

1. Running fix script on already-fixed files is idempotent
2. Creating a new file without the fix fails the hook
3. No manual enforcement needed after setup

## When to Apply

- License headers
- Required imports
- Configuration defaults
- Any "every file must have X" rule

## Tags

`build` `automation` `enforcement` `hooks`
