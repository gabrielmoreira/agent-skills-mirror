---
type: skill
lifecycle: stable
inheritance: inheritable
name: dual-surface-docs-drift
description: Two READMEs covering overlapping scope will diverge:
tier: standard
applyTo: '**/*dual*,**/*surface*,**/*docs*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Dual-Surface Docs Drift

## The Problem

Two READMEs covering overlapping scope will diverge:

- Root README describes feature X
- Wiki page also describes feature X
- One gets updated, the other doesn't

## The Solution

### Option 1: Cross-Reference (Preferred)

The less-detailed doc points to the more-detailed:

```markdown
<!-- README.md (brief) -->
## Configuration

For basic setup, set `API_KEY` in your environment.

For advanced configuration options, see the 
[Configuration Guide](https://github.com/org/repo/wiki/Configuration).
```

```markdown
<!-- wiki/Configuration.md (detailed) -->
## Configuration

Complete reference for all configuration options...
```

### Option 2: Consolidate

If both documents serve the same audience, merge them:

```markdown
<!-- Keep ONE source, delete or redirect the other -->
## Configuration

[Full content here, single location]
```

### Option 3: Audience Separation

If audiences differ, make the separation explicit:

```markdown
<!-- README.md header -->
> **Developer docs**: This README is for contributors.
> **User docs**: See the [Wiki](./wiki) for end-user documentation.
```

## Decision Table

| README Audience | Wiki Audience | Action |
|-----------------|---------------|--------|
| Developers | Developers | Consolidate |
| Developers | End users | Separate + cross-ref |
| End users | End users | Consolidate |

## Verification

Search for duplicated headers:

```bash
# Find potential overlaps
grep -h "^##" README.md wiki/*.md | sort | uniq -d
```

If the same H2 appears in both, you have drift risk.

## When to Apply

- Adding documentation to an existing repo
- Noticing outdated info in one of two places
- Documentation audit

## Tags

`documentation` `drift` `maintenance` `wiki`
