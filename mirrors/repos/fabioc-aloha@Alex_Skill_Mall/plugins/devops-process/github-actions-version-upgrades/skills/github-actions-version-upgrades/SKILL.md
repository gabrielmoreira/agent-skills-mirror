---
name: github-actions-version-upgrades
description: "Older action versions trigger deprecation warnings and will eventually break:"
lastReviewed: 2026-04-30
---

# GitHub Actions Version Upgrades

## The Problem

Older action versions trigger deprecation warnings and will eventually break:

```yaml
# Deprecated - old action majors and pre-24 Node runners
- uses: actions/checkout@vOLD
- uses: actions/setup-node@vOLD
  with:
    node-version: '<24'
```

## The Solution

Proactively use current versions:

```yaml
# Current ACT baseline
- uses: actions/checkout@v6
- uses: actions/setup-node@v6
  with:
    node-version: '24'
```

## Version Reference

| Action | Current | Node.js Runtime |
|--------|---------|-----------------|
| actions/checkout | v6 | Node 24 |
| actions/setup-node | v6 | Node 24 |
| actions/upload-artifact | latest Node 24-compatible major | Node 24 |
| actions/download-artifact | latest Node 24-compatible major | Node 24 |
| actions/cache | latest Node 24-compatible major | Node 24 |
| actions/github-script | latest Node 24-compatible major | Node 24 |

## Migration Script

```bash
# Update core actions to the Node 24-compatible majors
sed -i 's/actions\/checkout@v[0-5]/actions\/checkout@v6/g' .github/workflows/*.yml
sed -i 's/actions\/setup-node@v[0-5]/actions\/setup-node@v6/g' .github/workflows/*.yml
sed -i 's/actions\/upload-artifact@v[0-3]/actions\/upload-artifact@v4/g' .github/workflows/*.yml
sed -i 's/actions\/download-artifact@v[0-3]/actions\/download-artifact@v4/g' .github/workflows/*.yml
```

## Node.js Version Matrix

```yaml
strategy:
  matrix:
    node-version: ['24']

# ACT baseline
node-version: '24'
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
