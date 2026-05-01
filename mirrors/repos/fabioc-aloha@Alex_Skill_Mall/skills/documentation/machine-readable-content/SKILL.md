---
type: skill
lifecycle: stable
inheritance: inheritable
name: machine-readable-content
description: Emoji, color codes, and visual markers in files parsed by regex or LLMs break tooling:
tier: standard
applyTo: '**/*machine*,**/*readable*,**/*content*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Machine-Readable Content

## The Problem

Emoji, color codes, and visual markers in files parsed by regex or LLMs break tooling:

```markdown
<!-- Breaks JSON extraction -->
| Status | Count |
|--------|-------|
| ✅ Done | 47 |
| 🚧 WIP | 12 |
```

```bash
# Regex expects plain text
grep -E "Done\s+\d+" file.md  # Misses "✅ Done"
```

## The Solution

Keep machine-consumed files decoration-free:

```markdown
<!-- Machine-readable version -->
| Status | Count |
|--------|-------|
| Done | 47 |
| WIP | 12 |
```

### If You Need Both

Separate the machine-readable data from the display version:

```javascript
// data/status.json (machine-readable)
{
  "done": 47,
  "wip": 12
}

// Display layer adds emoji
const statusEmoji = { done: '✅', wip: '🚧' };
```

## What Breaks

| Decoration | What It Breaks |
|------------|----------------|
| Emoji | Regex, some parsers, terminal output |
| ANSI colors | Log aggregators, plain-text tools |
| Unicode symbols | Older systems, some APIs |
| Smart quotes | JSON parsers, shell scripts |
| Non-breaking spaces | String comparison, whitespace-sensitive parsers |

## File Types to Keep Clean

- JSON configuration
- CSV/TSV data files
- Markdown tables read by scripts
- Log output parsed by aggregators
- YAML consumed by CI/CD

## Verification

```bash
# Check for common decorations
grep -P '[\x{1F300}-\x{1F9FF}]' file.md  # Emoji
grep -P '[\x{2700}-\x{27BF}]' file.md     # Dingbats
```

## When to Apply

- Any file consumed by scripts or automation
- Data files read by multiple systems
- Content that might be parsed by LLMs

## Tags

`documentation` `automation` `parsing` `data`
