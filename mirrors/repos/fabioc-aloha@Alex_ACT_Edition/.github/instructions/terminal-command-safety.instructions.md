---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Prevent terminal command failures from shell metacharacter interpretation, output capture issues, and hanging commands"
application: "When running terminal commands, especially those with special characters or long output"
applyTo: "**"
currency: 2026-05-19
lastReviewed: 2026-05-19
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

**Temp file location matters**: place temp files **outside the working tree** (`$env:TEMP\<slug>.txt` on Windows, `/tmp/<slug>.txt` on Unix) OR add the pattern to `.gitignore` before staging. Otherwise `git add -A` will stage and commit the message file itself. S360 hit this twice in 2026-05 (commits `26631b4` then caught mid-flight on the next leak via Tenet X self-review).

Preferred PowerShell template for multi-line commit messages:

```pwsh
$m = Join-Path $env:TEMP "<slug>.txt"
Set-Content -Path $m -Value $msg -NoNewline
git commit -F $m
Remove-Item $m
```

Filesystem isolation prevents the leak by construction.

## Output Capture Failures

Terminal output can be silently lost or truncated.

1. Redirect to file, then read: `cmd 2>&1 | Out-File $env:TEMP\out.txt`
2. Pipe pagers through `Out-String`
3. Sentinel: `; echo "EXIT_CODE:$LASTEXITCODE"`
4. Limit volume: `Select-Object -First`, `-Tail`, `Format-Table`
5. Avoid alt-buffer programs (`less`, `vim`, `man`) — use non-interactive equivalents
6. If empty: retry with `get_terminal_output`, then redirect to file, then check stderr

## Terminal Hanging

1. `mode=async` for commands >15s (servers, builds, test suites). VS Code 1.121+ also auto-promotes sync→background after a configurable idle-silence period via `run_in_terminal`; this rule remains correct as agent intent and is required on older builds.
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

## VS Code 1.118 Agentic Execution Sub-Tool

The agentic execution sub-tool in 1.118 pre-filters terminal output before the agent sees it. This reduces noise (build warnings, progress bars, ANSI escapes) but means some output may be silently trimmed from the agent's view. The redirect-to-file fallback from "Output Capture Failures" above remains critical when full unfiltered output matters (e.g., parsing exact error messages, capturing full test results, or diagnosing encoding issues).

## VS Code 1.120 + 1.121 Terminal Output Compression (Preview)

Setting: `chat.tools.compressOutput.enabled`. When enabled, VS Code post-processes long terminal output before sending it to the model — collapses large diff hunks, drops lockfile/snapshot diffs, reduces `ls -l` to entry names, strips `npm install` progress bars / deprecation warnings / audit summaries. A short banner is prepended naming the filters that fired so the model can disable compression if it needs raw text.

1.121 (May 13) expanded coverage beyond `git diff` / `ls -l` / `npm install` to test runners (`pytest`, `jest`, `cargo test`), build tools (`tsc`, `cargo build`, `make`), linters, Docker, and package managers.

1.121 (May 13) also auto-disposes background terminals created by the chat agent once their command finishes — manual `kill_terminal` no longer required for one-shot async commands.

The "Output Capture Failures" file-redirect fallback remains valid when full unfiltered output matters and compression strips data the agent needs to inspect.

## Falsifier — Backtick Hazard

The Backtick Hazard rule is load-bearing because the underlying defect is unfixed in VS Code through 1.121. Tracking issue: [microsoft/vscode#295620](https://github.com/microsoft/vscode/issues/295620) ("Copilot with Claude models fails to handle backticks with gh") — open, milestone *On Deck*, no scheduled fix. Adjacent terminal-tool work shipped in 1.118 ([PR #307960](https://github.com/microsoft/vscode/pull/307960) heredoc handling) and 1.120/1.121 (output compression, idle-silence auto-promotion) does not address backtick interpretation in double-quoted arguments. Re-evaluate this rule when #295620 closes; until then, the temp-file pattern is mandatory.
