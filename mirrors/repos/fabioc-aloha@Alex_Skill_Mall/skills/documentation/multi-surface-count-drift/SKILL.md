---
type: skill
lifecycle: stable
inheritance: inheritable
name: multi-surface-count-drift
description: When a number (skill count, repo count, test count) appears in multiple files, they WILL diverge:
tier: standard
applyTo: '**/*multi*,**/*surface*,**/*count*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Multi-Surface Count Drift

## The Problem

When a number (skill count, repo count, test count) appears in multiple files, they WILL diverge:

- README says "47 skills"
- CHANGELOG says "added 3 skills, now 49"
- Wiki homepage says "45+ skills"
- Package description says "50 skills"

Manual updates always miss at least one surface.

## The Solution

When updating any count:

```bash
# Grep for the OLD number across all surfaces
grep -rn "47" . --include="*.md" --include="*.json"

# Update ALL occurrences, not just the one you're looking at
```

### Decision: Single-Source vs Manual Sync

**If the count changes frequently (>1x/month)**: Single-source it.

```javascript
// package.json is source of truth
const count = require('./skills').length;

// Build step injects into README
const readme = template.replace('{{SKILL_COUNT}}', count);
```

**If the count is stable**: Accept manual sync but document all surfaces.

```markdown
<!-- Count surfaces (update all when changing):
- README.md line 12
- CHANGELOG.md version header
- package.json description
- wiki/Home.md line 3
-->
```

## Analytical/Historical Docs Are Exempt

Point-in-time documents (changelogs, audit reports, planning docs with dates) should NOT be updated — they're historical records.

```markdown
## v2.1.0 (2026-04-15)
- Added 3 skills, now at 47 total  <!-- This stays 47 forever -->
```

## Verification

```bash
# Check for count drift
grep -rn "47\|48\|49\|50" . --include="*.md" | grep -i "skill"
```

All results should show the same number (except historical docs).

## When to Apply

- Version numbers
- Feature counts
- Contributor counts
- Test counts
- Any number that appears in >2 files

## Tags

`documentation` `drift` `maintenance` `counts`
