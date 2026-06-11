---
name: qa-testing
description: Verify your work by actually operating the app or website you changed, instead of assuming it works. Strongly recommended whenever you build, modify, or debug a web app, website, or desktop GUI app. Drive real browsers with the agent-browser CLI (navigate, click, fill, snapshot, screenshot) and native desktop apps with the cua-driver CLI (snapshot the accessibility tree, click/type by element). These aren't bundled - you install them on demand, gated by the host's normal command-approval.
---

# QA testing - verify by actually driving it

After you build or change an app or website, **don't assume it works - drive it
and check.**

## 1. Network is required - check it first

Installing these tools and (for web) loading pages need outbound network, which
sandboxes block by default. Check before anything else:

```bash
curl -fsI https://github.com >/dev/null 2>&1 && echo "network ok" || echo "network blocked"
```

If it prints **network blocked**, stop and tell the user - don't attempt offline
workarounds:

> I need network access to install and run the testing tools. Run **/permissions**
> and choose an access level that allows network (Full Access), then ask me again.

## 2. Web apps / websites -> agent-browser

On macOS/Linux, prefer the prebuilt binary directly with `curl` - no Node, no
Homebrew, no version manager:

```bash
if ! command -v agent-browser >/dev/null; then
  os=$(uname -s | tr '[:upper:]' '[:lower:]'); m=$(uname -m)
  case "$os/$m" in
    darwin/arm64)              asset=agent-browser-darwin-arm64 ;;
    darwin/x86_64)             asset=agent-browser-darwin-x64 ;;
    linux/aarch64|linux/arm64) asset=agent-browser-linux-arm64 ;;
    linux/x86_64)              asset=agent-browser-linux-x64 ;;
  esac
  mkdir -p ~/.local/bin
  curl -fL "https://github.com/vercel-labs/agent-browser/releases/latest/download/$asset" -o ~/.local/bin/agent-browser
  chmod +x ~/.local/bin/agent-browser
fi
agent-browser install            # one-time: downloads a Chrome build
agent-browser skills get core    # the real usage guide (maintained by the tool)
```

On Windows, use the package installer because it downloads the matching native
binary:

```powershell
if (-not (Get-Command agent-browser -ErrorAction SilentlyContinue)) {
  npm install -g agent-browser
  $env:Path = "$env:APPDATA\npm;$env:Path"
}
agent-browser install
agent-browser skills get core
```

If `agent-browser` is installed but Windows PowerShell still says it is not
recognized, refresh PATH for the current shell and retry:

```powershell
$env:Path = "$env:APPDATA\npm;$env:Path"
Get-Command agent-browser
```

When running `agent-browser` from Windows PowerShell, quote snapshot refs such
as `'@e4'`. Unquoted `@e4` is PowerShell syntax, not a literal argument:

```powershell
agent-browser snapshot -i
agent-browser click '@e4'
agent-browser fill '@e3' 'search text'
```

(Convenience alternatives on supported platforms: `brew install agent-browser`,
`cargo install agent-browser`, or `npx agent-browser ...`.) Then:
`agent-browser open <url>` -> `snapshot -i` -> act on the `@eN` refs ->
re-snapshot.

If the browser must be visible for a demo or manual inspection, use headed mode:
`agent-browser --headed open <url>` or set `AGENT_BROWSER_HEADED=1`.

## 3. Native desktop apps -> cua-driver (Cua AI)

macOS/Linux:

```bash
command -v cua-driver >/dev/null || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/trycua/cua/main/libs/cua-driver/scripts/install.sh)"
cua-driver list-tools            # the real tool reference (maintained by the tool)
```

Windows PowerShell:

```powershell
if (-not (Get-Command cua-driver -ErrorAction SilentlyContinue)) {
  irm https://raw.githubusercontent.com/trycua/cua/main/libs/cua-driver/scripts/install.ps1 | iex
  $env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')
}
cua-driver list-tools
```

On Windows PowerShell 5.1, if `install.ps1` fails to parse, use PowerShell 7
(`pwsh`) if available, or use the manual zip fallback from the Cua Driver
installation docs:

```powershell
$version = "0.2.9"
$arch = if ([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture -eq 'Arm64') { 'arm64' } else { 'x86_64' }
$url = "https://github.com/trycua/cua/releases/download/cua-driver-rs-v$version/cua-driver-rs-$version-windows-$arch-binary.zip"
iwr $url -OutFile $env:TEMP\cua.zip -UseBasicParsing
$dest = "$env:LOCALAPPDATA\Programs\Cua\cua-driver\bin"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Expand-Archive -Force -Path $env:TEMP\cua.zip -DestinationPath $dest
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if (@($userPath -split ';') -notcontains $dest) {
  [Environment]::SetEnvironmentVariable('Path', "$dest;$userPath", 'User')
}
$env:Path = "$dest;$env:Path"
```

The first GUI action can require OS permissions or an interactive desktop
session. Run `cua-driver serve` so element state persists across calls. Defer to
cua-driver's own installed skill for the full workflow.

For native apps, verify a real state change after the action. A click command
that reports "posted", "clicked", or "UIA Invoke" is not enough by itself.
Capture an initial state, act, then capture a post-action state and compare exact
visible text, counters, status labels, selected state, input values, or
screenshot evidence. If `Score: 0`, `Total Clicks: 0`, `Status: Waiting`, or an
equivalent unchanged value remains after the action, the action did not count as
verified even if the driver returned success.

Do not write a passing native QA report that only says coordinate clicks were
posted or UIA Invoke succeeded. A report with "clicks posted but
counter/label/state was not confirmed" is a failure. Keep testing until a
post-action screenshot, accessibility tree, window text, counter, status label,
selected state, or other visible artifact proves the UI changed. If the tool
cannot prove state change on that app, mark the native QA as failed and explain
the exact blocker.

Keep native QA output readable in recorded demos. Do not print full
`cua-driver` JSON responses when they include screenshot/base64 fields. For
state checks, parse the JSON and print only the useful fields, for example
`tree_markdown`, window ids, status labels, counters, and short pass/fail
summaries. If Cua shows a visual cursor or overlay, disable it or move it out of
the app/browser area before taking final screenshots or recording proof.

## Windows PowerShell command hygiene

Many Windows hosts still run Windows PowerShell 5.1, where `&&` is not a valid
statement separator. Use separate commands, semicolons, or explicit
`if ($LASTEXITCODE -eq 0) { ... }` checks instead. Quote tool arguments that
begin with `@`, especially agent-browser refs.

## Windows visible demo recordings

When the QA proof is a screen recording, treat the visible desktop as part of
the test surface:

- Pin the exact executable under test. Do not record against a PATH default if
  the app has launcher/router binaries or sibling binaries. Log the resolved
  launcher and any required sibling executables before recording.
- Put a plain white backdrop behind the terminal and app/browser windows so
  wallpaper and desktop icons do not show through gaps.
- Run helper daemons and long-lived tool servers without visible console
  windows. On Windows, native desktop tools such as `cua-driver serve` are
  inherently daemon-style; that is fine, but the helper console should be
  hidden or launched with no-window process creation.
- Do not open extra terminals or VM helper shells during an active recording.
  Read logs, screenshots, and trace files from disk instead, or pause/stop the
  recording first.
- For headed browser demos, use a fresh browser profile, suppress session
  restore/startup prompts as much as possible, and verify the active visible tab
  is the app before final proof. Browser automation may operate on the right tab
  even when Chrome visibly focuses a restore/banner tab, so inspect screenshots.
- Demonstrate the real user path. If the proof is about typing a command and
  selecting a menu item, type the command visibly, use arrow keys, and press
  Enter. Do not open the target popup by calling internal app functions.
- If foreground `SendInput`/Unicode typing does not reach a visible Windows
  console TUI, use a short-lived helper process that calls `AttachConsole` and
  `WriteConsoleInput` against the actual console client process
  (`interpreter`, `interpreter-root-tui`, `powershell`, etc.). Do not call
  `FreeConsole`/`AttachConsole` inside the long-running recorder process; it
  can detach or corrupt that process's own console host.
- Capture proof frames after each important step: prompt typed, app opened,
  action before/after, slash command typed, picker open, arrow-key selection,
  Enter accepted, and post-switch/follow-up response.

## Principles

- **Network first.** Check it; if blocked, tell the user to open `/permissions`.
- **`command -v` before installing**; don't reinstall if present.
- **Avoid Node when a direct binary works** - on macOS/Linux use the direct
  binary download (or brew/cargo). On Windows, `npm install -g agent-browser` is
  the supported native-binary installer.
- **Defer to each tool's own docs** (`agent-browser skills get core`,
  `cua-driver list-tools`) - they're the source of truth, current with the
  installed version.
- **Snapshot -> act -> re-snapshot** to confirm each step landed; if nothing
  changed, it failed - say so, don't claim success.
- **Confirm before consequential actions** (purchases, messages, form
  submissions, deletions) - get explicit user intent for that step.
