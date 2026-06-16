---
name: qa-testing
description: Verify your work by actually operating the app or website you changed, instead of assuming it works. Strongly recommended whenever you build, modify, or debug a web app, website, or desktop GUI app. Drive real browsers with the agent-browser CLI and native desktop apps with the cua-driver CLI. These are installed on demand through the host's normal command-approval flow.
---

# QA testing - verify by actually driving it

After you build or change an app or website, do not assume it works. Drive it
and check.

## 1. Network is required - check it first

Installing these tools and loading pages need outbound network, which sandboxes
can block. Check before anything else:

```bash
curl -fsI https://github.com >/dev/null 2>&1 && echo "network ok" || echo "network blocked"
```

If it prints `network blocked`, stop and tell the user:

> I need network access to install and run the testing tools. Run `/permissions`
> and choose an access level that allows network, then ask me again.

## 2. Web apps and websites - agent-browser

On macOS/Linux, prefer the prebuilt binary directly:

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
agent-browser install
agent-browser skills get core
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

Then use the tool's maintained guide: `agent-browser open <url>`, take a
snapshot, act on the element refs, and snapshot again.

## 3. Native desktop apps - cua-driver

macOS/Linux:

```bash
command -v cua-driver >/dev/null || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/trycua/cua/main/libs/cua-driver/scripts/install.sh)"
cua-driver list-tools
```

Windows PowerShell:

```powershell
if (-not (Get-Command cua-driver -ErrorAction SilentlyContinue)) {
  irm https://raw.githubusercontent.com/trycua/cua/main/libs/cua-driver/scripts/install.ps1 | iex
  $env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')
}
cua-driver list-tools
```

For native apps, verify a real state change after the action. A click command
that reports success is not enough by itself. Capture an initial state, act,
then capture a post-action state and compare visible text, counters, status
labels, selected state, input values, or screenshot evidence.

## Windows PowerShell command hygiene

Many Windows hosts still run Windows PowerShell 5.1, where `&&` is not a valid
statement separator. Use separate commands, semicolons, or explicit
`if ($LASTEXITCODE -eq 0) { ... }` checks instead. Quote tool arguments that
begin with `@`, especially agent-browser refs.

## Principles

- Check network first.
- Use `command -v` before installing.
- Prefer direct binaries on macOS/Linux when available.
- Defer to each tool's own docs: `agent-browser skills get core` and
  `cua-driver list-tools`.
- Snapshot, act, and re-snapshot to confirm each step landed.
- Confirm before consequential actions such as purchases, messages, form
  submissions, or deletions.
