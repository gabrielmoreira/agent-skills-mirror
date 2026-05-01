---
applyTo: "research/**,*.md"
---

# Research & Documentation Instructions

## ADR Format

```markdown
# ADR-NNN: Title

**Status**: Proposed | Accepted | Deprecated
**Date**: YYYY-MM-DD

## Context
Why this decision is needed.

## Decision
What we decided.

## Consequences
Trade-offs and implications.
```

## Research Doc Format

- Title and date at top
- Summary table for quick reference
- Detailed findings with source links
- Last-updated timestamp
- Clear "Actionable Next Steps" section

## Inventory Updates

When new services or devices are evaluated:
1. Update `inventory/services.json` or `inventory/devices.json`
2. Update relevant research doc
3. Note the change in CHANGELOG.md
