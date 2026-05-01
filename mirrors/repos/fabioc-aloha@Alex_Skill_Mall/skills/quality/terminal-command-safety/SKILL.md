---
type: skill
lifecycle: stable
inheritance: inheritable
name: terminal-command-safety
description: Safe terminal command patterns — backtick escaping, output capture, and hang prevention
tier: standard
applyTo: '**/*terminal*,**/*command*,**/*safety*'
currency: 2026-04-20
lastReviewed: 2026-04-30
---

# Terminal Command Safety


Detailed patterns and examples for safe terminal command execution in AI agent contexts.

## Decision Table

| Content Type | Safe Approach | Why |
|--------------|---------------|-----|
| Contains backticks | Use temp file | Backticks break in all shells |
| Multi-line text | Use temp file | Heredocs can desync terminal |
| Both quote types | Use temp file | Can't escape both cleanly |
| Dollar signs (`$`) | Single-quoted heredoc or temp file | Prevents interpolation |
| Plain text only | Inline is safe | No shell metacharacters |
| Long-running (>15s) | `mode=async` | Prevents timeout |
| Interactive prompt | Pre-answer with flags | `--yes`, `--no-edit` |
| Needs full output | Redirect to file, then read | Output can be truncated |

## Backtick Hazard — Details

Backticks in terminal command arguments break across all shells:

- **bash/zsh**: backtick = command substitution (`echo "use`ls`here"` executes `ls`)
- **PowerShell**: backtick = escape character (`echo "use`n here"` inserts newline)

**Ref**: [vscode#295620](https://github.com/microsoft/vscode/issues/295620)

### Safe Pattern (bash)

```bash
# Write content to temp file (single-quoted delimiter prevents interpolation)
cat > /tmp/body.md << 'EOF'
## Changes
- Added `MyClass` to the module
- Updated `config.py`
EOF

# Pass file to command
gh pr create --title "My PR" --body-file /tmp/body.md
rm /tmp/body.md
```

### Safe Pattern (PowerShell)

```powershell
$body = @'
## Changes
- Added `MyClass` to the module
'@
$body | Out-File -Encoding utf8 "$env:TEMP\body.md"
gh pr create --title "My PR" --body-file "$env:TEMP\body.md"
Remove-Item "$env:TEMP\body.md"
```

## Output Capture — Examples

**Refs**: [vscode#308610](https://github.com/microsoft/vscode/issues/308610), [vscode#308048](https://github.com/microsoft/vscode/issues/308048), [vscode#307173](https://github.com/microsoft/vscode/issues/307173)

### Redirect to file

```powershell
npm run build 2>&1 | Out-File -Encoding utf8 "$env:TEMP\build-output.txt"
Get-Content "$env:TEMP\build-output.txt" -Tail 50
```

### Pipe through Out-String

```powershell
git log --oneline -20 | Out-String
```

### Sentinel pattern

```powershell
npm test 2>&1; echo "EXIT_CODE:$LASTEXITCODE"
```

### Alt-buffer avoidance

- `git log` not `git log | less` (set `$env:GIT_PAGER="cat"`)
- `Get-Help` not `man`
- `gh issue view --json` not `gh issue view` (which opens a pager)

## Terminal Hanging — Examples

**Refs**: [vscode#308610](https://github.com/microsoft/vscode/issues/308610), [vscode#306490](https://github.com/microsoft/vscode/issues/306490)

### Async mode selection

```text
mode=async for: npm start, dotnet run, docker compose up, long test suites
mode=sync with timeout=30000 for: npm install, git operations, single test files
```

### Pre-answer interactive prompts

```text
npm install --yes
rm -rf (not rm -ri)
az login --use-device-code
git commit --no-edit (merge commits)
```

### Network timeouts

```powershell
npm install --prefer-offline --no-audit
curl --max-time 30 --connect-timeout 10 $url
```
