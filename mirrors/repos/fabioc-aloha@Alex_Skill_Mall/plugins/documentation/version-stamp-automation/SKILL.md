---
type: skill
lifecycle: stable
inheritance: inheritable
name: version-stamp-automation
description: Version numbers in 5+ files WILL drift with manual edits:
tier: standard
applyTo: '**/*version*,**/*stamp*,**/*automation*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Version Stamp Automation

## The Problem

Version numbers in 5+ files WILL drift with manual edits:

- `package.json` says 2.1.0
- README badge says 2.0.0
- CHANGELOG header says 2.1.0-beta
- Extension manifest says 2.0.1

## The Solution

### 1. Single Source of Truth

```json
// package.json is the ONE source
{
  "version": "2.1.0"
}
```

### 2. Bump Script That Derives All Locations

```javascript
// scripts/bump-version.cjs
const fs = require('fs');
const path = require('path');

const newVersion = process.argv[2];
if (!newVersion) {
  console.error('Usage: node bump-version.cjs <version>');
  process.exit(1);
}

// Define all version locations
const locations = [
  {
    file: 'package.json',
    pattern: /"version":\s*"[^"]+"/,
    replace: `"version": "${newVersion}"`
  },
  {
    file: 'README.md',
    pattern: /version-v[\d.]+/g,
    replace: `version-v${newVersion}`
  },
  {
    file: 'src/extension.ts',
    pattern: /VERSION\s*=\s*['"][^'"]+['"]/,
    replace: `VERSION = '${newVersion}'`
  }
];

locations.forEach(({ file, pattern, replace }) => {
  const filePath = path.resolve(file);
  if (!fs.existsSync(filePath)) return;
  
  let content = fs.readFileSync(filePath, 'utf8');
  content = content.replace(pattern, replace);
  fs.writeFileSync(filePath, content);
  console.log(`Updated: ${file}`);
});
```

### 3. Classify Each Reference

| Type | Action | Example |
|------|--------|---------|
| **Auto-derivable** | Script updates | README badge, package.json |
| **Manually dated** | Leave alone | CHANGELOG entries, planning docs |
| **Build-time** | Inject at build | Extension about page |

## Verification

```bash
# After running bump script
grep -rn "2.1.0" . --include="*.json" --include="*.md" --include="*.ts"

# Should see consistent version everywhere (except historical docs)
```

## When to Apply

- Any project with version in 3+ files
- Before any release process
- When you notice drift

## Tags

`versioning` `automation` `documentation` `devops`
