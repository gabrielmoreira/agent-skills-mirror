---
type: skill
lifecycle: stable
inheritance: inheritable
name: terminal-backtick-hazard
description: Backticks break in all shells — bash treats them as command substitution, PowerShell as escape character
tier: standard
applyTo: '**/*terminal*,**/*backtick*,**/*hazard*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Terminal Backtick Hazard

**Category**: Cross-Platform
**Time Saved**: 1-2 hours debugging shell escaping
**Battle-tested**: Yes — affects all shells differently

---

## The Problem

You run a command with backticks in the content — maybe a git commit message with code, or a GitHub issue body with markdown. The command fails mysteriously, or worse, executes something unexpected.

## Why It Happens

Backticks have special meaning in **every shell**:

| Shell | Backtick Meaning | Risk |
|-------|-----------------|------|
| Bash/Zsh | Command substitution: `` `command` `` | Executes content as command |
| PowerShell | Escape character: `` `n `` = newline | Corrupts content |
| cmd.exe | Literal (usually) | Still problematic in some contexts |

## The Rule

**Never place raw backticks inside terminal command arguments. Use file-based input.**

### GitHub CLI

```powershell
# ❌ WRONG — backticks interpreted
gh issue create --body "Fix the `config` module"

# ✅ CORRECT — use file
$body = "Fix the `config` module"
$body | Out-File -FilePath body.txt -Encoding utf8
gh issue create --body-file body.txt
Remove-Item body.txt
```

### Git Commit

```powershell
# ❌ WRONG — backticks interpreted
git commit -m "docs: update `README` section"

# ✅ CORRECT — use file
$msg = "docs: update `README` section"
$msg | Out-File -FilePath msg.txt -Encoding utf8
git commit -F msg.txt
Remove-Item msg.txt
```

### Any CLI

```powershell
# General pattern: file-based input
$content | Out-File -FilePath temp.txt -Encoding utf8
some-cli --input-file temp.txt
Remove-Item temp.txt
```

## When to Use Temp Files

| Content Contains | Action |
|-----------------|--------|
| Backticks | Always use temp file |
| Multi-line text | Prefer temp file |
| Both quote types | Use temp file |
| Dollar signs `$` | Use single-quoted heredoc or temp file |
| Plain text only | Inline is safe |

## Shell-Specific Escaping (Last Resort)

If you must inline, know your shell:

### PowerShell

```powershell
# Double the backtick to escape
"Fix the ``config`` module"

# Or use single quotes (no interpolation)
'Fix the `config` module'
```

### Bash/Zsh

```bash
# Use $'...' syntax
$'Fix the `config` module'

# Or escape with backslash
"Fix the \`config\` module"
```

## Implementation Pattern

```javascript
const fs = require('fs');
const { execFileSync } = require('child_process');
const path = require('path');
const os = require('os');

function ghIssueCreate(title, body) {
  const tempFile = path.join(os.tmpdir(), `gh-body-${Date.now()}.txt`);
  try {
    fs.writeFileSync(tempFile, body, 'utf8');
    execFileSync('gh', ['issue', 'create', '--title', title, '--body-file', tempFile]);
  } finally {
    fs.unlinkSync(tempFile);
  }
}
```

## Common CLI File Input Flags

| CLI | Flag |
|-----|------|
| `gh issue create` | `--body-file` |
| `gh pr create` | `--body-file` |
| `git commit` | `-F <file>` |
| `curl` | `--data-binary @file` |
| `az rest` | `--body @file` |

## Verification Checklist

- [ ] Check all CLI calls for backtick content
- [ ] Use file-based input for markdown content
- [ ] Test commands on both Windows and Unix
- [ ] Clean up temp files in finally block

## Related Skills

- `shell-injection-prevention` — Command safety
- `line-ending-parsing` — Cross-platform text
