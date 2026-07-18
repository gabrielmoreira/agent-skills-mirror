---
name: system_control
description: Windows desktop control — clipboard, screenshots, media, volume, apps
version: 2.0.0
---

# Skill: System Control

Interact with the Windows desktop: clipboard, screenshots, media playback,
volume, app launch/close, OS-wide process listing. All eight verbs below
are real registered tools — call them directly. The two verbs in the
"Not a tool yet" section route through `shell_exec` with the PowerShell
snippet shown.

Windows-only in v4.1.2. macOS/Linux callers get a structured error
pointing at the issue tracker; route to the user's clarifying-question
path if they need cross-platform coverage.

## Read-only verbs

### clipboard_read
Read the current clipboard contents as text. Empty string for non-text
clipboard data (image, RTF, file list). Privacy-sensitive — the
clipboard often holds passwords, OTPs, or personal text. Only call when
the user has clearly asked.
```json
{ "tool": "clipboard_read", "input": {} }
```

### screenshot
Capture the primary monitor as a PNG. Saves to
`<aidenHome>/screenshots/<timestamp>.png` and returns the absolute path.
Telegram / Discord channel adapters can attach the file directly via
the returned path. Privacy-sensitive — captures everything visible.
```json
{ "tool": "screenshot", "input": {} }
```

### os_process_list
List OS-wide running processes (top by CPU). Use this to answer
"is X running?" or "what's hogging my CPU?". Distinct from `process_list`
which only shows processes Aiden itself spawned via `process_spawn`.
```json
{ "tool": "os_process_list", "input": { "name": "claude" } }
{ "tool": "os_process_list", "input": { "limit": 50 } }
```

## Mutating verbs (approval-gated)

### clipboard_write
Replace the clipboard with new text. Handles multi-line strings safely
(text routed via stdin to PowerShell, no shell-quoting issues).
```json
{ "tool": "clipboard_write", "input": { "text": "Hello, world!" } }
```

### media_sessions
Enumerate every Windows media session registered with the OS (Spotify,
YouTube in browser, VLC, etc.). One entry per app, with which one is
the OS-routed target for global media keys. Use this BEFORE
`media_transport` when controlling a specific app.
```json
{ "tool": "media_sessions", "input": {} }
```

### media_transport
Verified play / pause / skip against a specific GSMTC media session.
Targets by `AppUserModelId` substring (case-insensitive — "spotify"
matches `Spotify.exe`), then by track title as a softer fallback. Omit
`target` to act on the OS-routed current session. Returns OS-level
success/failure — NOT a blind keystroke like `media_key`.
```json
{ "tool": "media_transport", "input": { "action": "pause", "target": "spotify" } }
{ "tool": "media_transport", "input": { "action": "play",  "target": "spotify" } }
{ "tool": "media_transport", "input": { "action": "next",  "target": "youtube" } }
{ "tool": "media_transport", "input": { "action": "toggle" } }
```

### media_key
Blind global media keypress (`VK_MEDIA_PLAY_PAUSE` and friends). Layer-3
fallback for the rare case where neither a semantic API nor GSMTC can
act. Prefer `media_transport` whenever the user names an app — this
tool returns `degraded:true` because Windows doesn't surface the SMTC
routing outcome to user-mode, so we can't verify any app received it.
```json
{ "tool": "media_key", "input": { "action": "play_pause" } }
{ "tool": "media_key", "input": { "action": "next" } }
{ "tool": "media_key", "input": { "action": "previous" } }
{ "tool": "media_key", "input": { "action": "stop" } }
```

### app_input
Focus a Windows application by process name and send a SendKeys
sequence to it. Escape hatch when GSMTC doesn't enumerate the surface
("press space in Chrome to pause this YouTube tab"). Always returns
`degraded:true` — SendKeys cannot verify receipt at the target window.
```json
{ "tool": "app_input", "input": { "app": "chrome", "keys": "{SPACE}" } }
{ "tool": "app_input", "input": { "app": "notepad", "keys": "Hello{ENTER}" } }
{ "tool": "app_input", "input": { "app": "Spotify", "keys": "^{RIGHT}" } }
```

### volume_set
Set Windows master volume to a percentage, or mute / unmute / toggle.
```json
{ "tool": "volume_set", "input": { "action": "set", "percent": 30 } }
{ "tool": "volume_set", "input": { "action": "mute" } }
{ "tool": "volume_set", "input": { "action": "toggle_mute" } }
```

### app_launch
Launch a Windows application by exe name, friendly name (resolved via
App Paths registry), or absolute path. Returns the PID when available.
```json
{ "tool": "app_launch", "input": { "app": "spotify" } }
{ "tool": "app_launch", "input": { "app": "notepad", "args": ["C:\\temp\\note.txt"] } }
{ "tool": "app_launch", "input": { "app": "C:\\Program Files\\App\\app.exe" } }
```

### app_close
Close one or more processes by name (with or without the `.exe`
suffix). Matches all running instances. Set `force: true` to skip the
app's graceful-shutdown prompt.
```json
{ "tool": "app_close", "input": { "app": "notepad" } }
{ "tool": "app_close", "input": { "app": "chrome.exe", "force": true } }
```

## Not a tool yet — route via `shell_exec`

### Focus a window by title
v4.1.2 does not ship a `window_focus` tool — Win32 P/Invoke complexity
isn't worth a dedicated tool when shell_exec covers the same ground.
```powershell
(New-Object -ComObject WScript.Shell).AppActivate('Notepad')
```

### List visible windows
Same reasoning. The MainWindowTitle filter excludes background services.
```powershell
Get-Process | Where-Object { $_.MainWindowTitle } |
  Select-Object Id, ProcessName, MainWindowTitle |
  ConvertTo-Json -Compress
```

Wrap either snippet in `shell_exec` when the user explicitly asks for
window manipulation. Track v4.1.3+ for native tool wrappers if these
turn into common requests.

## Usage Patterns

**Copy file content to clipboard after writing it:**
1. `file_write` → write the content
2. `clipboard_write` → copy the file path or content

**Confirm an app launched:**
1. `app_launch` → returns PID
2. `os_process_list` with the app's name → verify it's still running

**"Is X running?" workflow:**
1. `os_process_list` with `name: "<substring>"` → returns matching processes
2. If `count === 0` → tell the user honestly, suggest `app_launch`

## Media control — strict order

1. If the user names an app ("Spotify", "YouTube", "VLC") — ALWAYS try
   `media_transport({action, target})` first. Verified, OS-confirmed.
2. If `media_transport` returns `NoSession` OR the user didn't name an app
   — fall back to `media_key({action})`. Blind global keystroke, returns
   `degraded:true` because Windows can't tell us if anything received it.
3. If GSMTC doesn't enumerate the surface at all (e.g. a YouTube tab the
   browser hasn't registered with SMTC) — last resort: `app_input({app,
   keys})` to focus the window and send a keystroke directly.

Never call `media_key` and `media_transport` in the same turn — redundant.
First call gives you the answer; second is noise the user has to read.

Honesty contract:
- `media_transport` success is OS-confirmed → trail row is silent (success).
- `media_key` and `app_input` always report `degraded:true` → yellow trail
  row, because neither can verify receipt at the target app.

**Volume change with feedback:**
1. `volume_set` → returns the resulting volume percent in `result`
2. Surface it to the user so they know the change landed.
