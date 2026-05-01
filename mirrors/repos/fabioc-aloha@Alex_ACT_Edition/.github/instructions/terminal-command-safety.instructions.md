---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Prevent terminal command failures from shell metacharacter interpretation, output capture issues, and hanging commands"
application: "When running terminal commands, especially those with special characters or long output"
applyTo: "**"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Terminal Command Safety

## Backtick Hazard (Critical)

Backticks break in ALL shells (bash=command substitution, PowerShell=escape char). NEVER place raw backticks inside double-quoted terminal arguments.

| Content contains | Action |
|---|---|
| Backticks | Always use temp file |
| Multi-line text | Prefer temp file |
| Both quote types | Use temp file |
| Dollar signs (`$`) | Single-quoted heredoc or temp file |
| Plain text only | Inline is safe |

Rules: `gh` → `--body-file`, `git commit` → `-F <file>`, any CLI → file-based input over inline.

## Output Capture Failures

Terminal output can be silently lost or truncated.

1. Redirect to file, then read: `cmd 2>&1 | Out-File $env:TEMP\out.txt`
2. Pipe pagers through `Out-String`
3. Sentinel: `; echo "EXIT_CODE:$LASTEXITCODE"`
4. Limit volume: `Select-Object -First`, `-Tail`, `Format-Table`
5. Avoid alt-buffer programs (`less`, `vim`, `man`) — use non-interactive equivalents
6. If empty: retry with `get_terminal_output`, then redirect to file, then check stderr

## Terminal Hanging

1. `mode=async` for commands >15s (servers, builds, test suites)
2. Never run interactive commands — pre-answer with flags (`--yes`, `--no-edit`)
3. Set network timeouts (`--max-time`, `--prefer-offline`)
4. Avoid heredoc blocks (desync terminal parser)
5. One command at a time — no chaining unrelated commands
6. Kill stuck: `send_to_terminal` with Ctrl+C, or start fresh terminal

## VS Code 1.117 Terminal Improvements

Two behavioral changes reduce manual output handling:

1. **Auto-include output after `send_to_terminal`**: Terminal output is automatically included in the next turn after `send_to_terminal`. No need to call `get_terminal_output` immediately after — the output arrives with the next user/system message.
2. **Background terminal notifications**: When an async terminal command completes, a system notification fires automatically. No need to poll with `get_terminal_output` — wait for the notification instead.

These reduce the need for manual output capture patterns in 1.117+ environments. The redirect-to-file fallback remains valid for edge cases.

## Falsifier — Backtick Hazard

The Backtick Hazard rule is load-bearing because the underlying defect is unfixed in VS Code through 1.118. Tracking issue: [microsoft/vscode#295620](https://github.com/microsoft/vscode/issues/295620) ("Copilot with Claude models fails to handle backticks with gh") — open, milestone *On Deck*, no scheduled fix. Adjacent terminal-tool work shipped in 1.118 ([PR #307960](https://github.com/microsoft/vscode/pull/307960) heredoc handling) does not address backtick interpretation in double-quoted arguments. Re-evaluate this rule when #295620 closes; until then, the temp-file pattern is mandatory.
