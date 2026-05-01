---
type: skill
lifecycle: stable
inheritance: inheritable
name: github-actions-version-upgrades
description: Older action versions trigger deprecation warnings and will eventually break:
tier: standard
applyTo: '**/*github*,**/*actions*,**/*version*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# GitHub Actions Version Upgrades

## The Problem

Older action versions trigger deprecation warnings and will eventually break:

```yaml
# Deprecated - Node.js 16 warnings
- uses: actions/checkout@v3
- uses: actions/setup-node@v3
  with:
    node-version: '18'
```

## The Solution

Proactively use current versions:

```yaml
# Current as of 2024
- uses: actions/checkout@v5
- uses: actions/setup-node@v5
  with:
    node-version: '22'
```

## Version Reference

| Action | Current | Node.js Runtime |
|--------|---------|-----------------|
| actions/checkout | v5 | Node 20 |
| actions/setup-node | v5 | Node 20 |
| actions/upload-artifact | v4 | Node 20 |
| actions/download-artifact | v4 | Node 20 |
| actions/cache | v4 | Node 20 |
| actions/github-script | v7 | Node 20 |

## Migration Script

```bash
# Update all common actions to v5/v4
sed -i 's/actions\/checkout@v[0-4]/actions\/checkout@v5/g' .github/workflows/*.yml
sed -i 's/actions\/setup-node@v[0-4]/actions\/setup-node@v5/g' .github/workflows/*.yml
sed -i 's/actions\/upload-artifact@v[0-3]/actions\/upload-artifact@v4/g' .github/workflows/*.yml
sed -i 's/actions\/download-artifact@v[0-3]/actions\/download-artifact@v4/g' .github/workflows/*.yml
```

## Node.js Version Matrix

```yaml
strategy:
  matrix:
    node-version: ['18', '20', '22']  # LTS versions
    
# Or just latest LTS
node-version: '22'
```

## Verification

```bash
# Check for old versions
grep -rn 'actions/.*@v[0-3]' .github/workflows/

# Should return nothing after upgrade
```

## When to Apply

- New repository setup
- Quarterly maintenance
- When seeing deprecation warnings
- Before Node.js version EOL dates

## Tags

`github-actions` `ci-cd` `maintenance` `node`
