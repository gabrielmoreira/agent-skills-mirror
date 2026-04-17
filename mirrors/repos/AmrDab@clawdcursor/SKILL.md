---
name: clawdcursor
version: 0.8.0
description: >
  OS-level desktop automation. 42 tools that control any application on Windows, macOS,
  or Linux by way of mouse, keyboard, screen reading, windows, and a browser CDP bridge.
  Model-agnostic (any AI that can call functions over REST or MCP — Claude, GPT, Gemini,
  Llama, Mistral, Ollama, or plain HTTP) and OS-agnostic (one PlatformAdapter per OS).
  Use this skill WHENEVER the user asks you to do something that would normally require
  sitting at their computer: clicking buttons, filling forms, reading what is on screen,
  opening an app, sending an email through a GUI, driving a web page that has no public
  API, copying text between apps, taking a screenshot, or any phrase like "control my
  desktop", "drive this GUI", "do this in the browser for me", "automate this workflow",
  "read what is on my screen", "click the Send button", "fill out this form".
  Also use it when an earlier attempt to complete a task via API, CLI, or file edit has
  failed and the only remaining surface is a GUI. Prefer APIs and CLIs when they exist —
  clawdcursor is the last-mile tool for when a human would normally reach for the mouse.
homepage: https://clawdcursor.com
source: https://github.com/AmrDab/clawdcursor
privacy: >
  All processing runs locally. Server binds to 127.0.0.1 only — not network-accessible.
  No telemetry, no analytics. Screenshots stay in memory. In agent mode (start),
  screenshots/text are sent only to the user's configured AI provider.
metadata:
  openclaw:
    requires: {}
    install:
      - npm install -g clawdcursor
      - clawdcursor consent --accept
      - clawdcursor serve
    skill_dir: ~/.openclaw/workspace/skills/clawdcursor
---

**If a human can do it on a screen, you can too.** No API? No integration? No problem.

## When to reach for this skill

Pick clawdcursor when the task requires eyes and hands on a real desktop. Concretely:

- The user names an app, a window, or "my screen" — Outlook, Figma, Zoom, a PDF they
  have open, a legacy enterprise tool with no REST endpoint.
- The task is "click / type / read / open / focus / drag" on something visible.
- A web task needs to work without a Playwright script — you can drive the live
  browser the user already has open through the CDP bridge.
- A previous approach (API, CLI, file edit, direct HTTP) has already failed and the
  only remaining surface is a GUI.
- The user mentions a workflow a person would normally do by hand: "export this
  report from Excel", "send this email through the GUI", "transfer the text from
  Notes to Slack".

## When NOT to use this skill

Always check these first — they're cheaper, faster, and more reliable:

1. Is there a native API? (Gmail API, GitHub API, Slack API, Stripe API) → use the API.
2. Is there a CLI? (`git`, `gh`, `aws`, `npm`, `curl`, `sqlite3`) → use the CLI.
3. Can you edit the file directly on disk? → do that.
4. Is there a browser automation layer already wired up (Playwright, Puppeteer)
   for this exact site? → use that.

If and only if none of those apply, use clawdcursor. It's the last mile.

---

## V2 vs legacy pipeline

As of v0.8.0 there are two pipelines. Same 42 tools, same MCP interface — only the
internal decision-maker differs.

| Pipeline | How to invoke | When it's the right choice |
|----------|---------------|----------------------------|
| **V2** (vision-first) | `clawdcursor start --v2` | Any task where being sure the action actually happened matters — sending email, deleting a file, submitting a form. The GroundTruthVerifier stops false positives. |
| **Legacy** (text-first cascade) | `clawdcursor start` | Fast, cheap reads/clicks on well-behaved apps where accessibility trees and OCR are reliable. Also the default for backwards compatibility. |

The legacy pipeline has not been removed. Existing integrations keep working.

### V2 architecture at a glance

```
Router           → regex shortcuts for trivial tasks ("open Safari"). Zero LLM, <1s.
VisionAgent      → one loop: screenshot → tool call → new screenshot → repeat.
                   16 tools, 6-rule system prompt, model-agnostic.
GroundTruthVerifier → 6 independent signals decide whether "done" is really done:
                     pixel diff, window change, focus change, OCR delta,
                     task-type assertions, anti-patterns (error dialogs, send-failed).
                     Cannot be fooled by an LLM self-reporting success.
```

### Legacy architecture

```
L1.5 Deterministic flows → hardcoded sequences. Zero LLM.
L2   Skill Cache         → learned action patterns. Zero LLM.
L2.5 OCR Reasoner        → OS OCR + cheap text LLM. ~90% of tasks.
L2.5b A11y Reasoner      → fallback when OCR unavailable.
L3   Computer Use        → vision model. Last resort.
```

---

## Modes at a glance

| Mode | Command | Brain | Tools available |
|------|---------|-------|----------------|
| `serve` | `clawdcursor serve` | **You** (REST client) | All 42 tools via HTTP |
| `mcp` | `clawdcursor mcp` | **You** (MCP client) | All 42 tools via MCP stdio |
| `start` | `clawdcursor start [--v2]` | Built-in LLM pipeline | All 42 tools + autonomous agent |

In `serve` and `mcp`: **you reason, clawdcursor acts.** There is no built-in LLM.
You call tools, interpret results, decide next steps.

In `start`: clawdcursor reasons and acts. You hand it a plain-English task and poll
for completion.

---

## Connecting

### Option A — REST (`clawdcursor serve`)

```bash
clawdcursor serve        # starts on http://127.0.0.1:3847
```

All POST endpoints require `Authorization: Bearer <token>` (token at `~/.clawdcursor/token`).

```
GET  /tools              → all tool schemas (OpenAI function-calling format)
POST /execute/{name}     → run a tool: {"param": "value"}
GET  /health             → {"status":"ok","version":"0.8.0"}
GET  /docs               → full documentation
```

If the server isn't running, start it yourself — don't ask the user:
```bash
clawdcursor serve
# wait 2 seconds, then verify: GET /health
```

### Option B — MCP (`clawdcursor mcp`)

```json
{
  "mcpServers": {
    "clawdcursor": {
      "command": "clawdcursor",
      "args": ["mcp"]
    }
  }
}
```

Works with Claude Code, Cursor, Windsurf, Zed, or any MCP-compatible client. All 42
tools are exposed identically.

### Option C — Autonomous agent (`clawdcursor start`)

```
POST /task    {"task": "Open Notepad and write Hello"}   → submit task
GET  /status  → "acting" | "idle" | "waiting_confirm"
POST /confirm {"approved": true}                         → approve safety-gated action
POST /abort                                              → stop current task
```

Use the `delegate_to_agent` tool to submit tasks from within MCP/REST sessions.
Requires `clawdcursor start` running on port 3847.

**Polling pattern:**
```
POST /task  {"task": "...", "returnPartial": true}
→ poll GET /status every 2s:
    "acting"           → still running, keep polling
    "waiting_confirm"  → STOP. Ask user → POST /confirm {"approved": true}
    "idle"             → done, check GET /task-logs for result
→ if 60s+ with no progress: POST /abort, retry with simpler phrasing
```

**returnPartial mode** (legacy pipeline only) — `{"returnPartial": true}` tells
clawdcursor to skip the expensive vision stage and return control to you if the
text stage gets stuck:
```json
{"partial": true, "stepsCompleted": [...], "context": "got stuck on dialog"}
```
You finish the task with MCP tools, then `POST /learn` to save what worked.

**POST /learn — adaptive learning (legacy pipeline):**
```json
{
  "processName": "EXCEL",
  "task": "create table with headers",
  "actions": [
    {"action": "key", "description": "Ctrl+Home to go to A1"},
    {"action": "type", "description": "Type header name"},
    {"action": "key", "description": "Tab to next column"}
  ],
  "shortcuts": {"next_cell": "Tab", "next_row": "Enter"},
  "tips": ["Use Tab between columns, Enter between rows"]
}
```
Enriches the app's guide JSON. The legacy OCR Reasoner reads it on subsequent runs —
no vision fallback needed.

---

## The universal loop

Every GUI task follows the same shape regardless of transport or pipeline:

```
1. ORIENT  →  read_screen() or get_windows()            see what's open and focused
2. ACT     →  smart_click() / smart_type() / key_press()    do the thing
3. VERIFY  →  return value → window state → text check → screenshot
4. REPEAT  →  until done
```

The reason this matters: keystrokes go to whatever has focus. If that's your terminal
instead of Excel, your `Ctrl+S` saves your terminal session, not the spreadsheet. So
orient first, focus the right window, then act, then verify before moving on.

### Verification ladder (cheapest → most expensive)

1. **Tool return value** — every tool reports success/failure. Check it first.
2. **Window state** — `get_active_window()`, `get_windows()` — did a dialog appear?
   Did the title change?
3. **Text check** — `read_screen()` or `smart_read()` — is the expected text visible?
4. **Screenshot** — `desktop_screenshot()` — only when text methods fail.
5. **Negative check** — look for error dialogs, wrong window, unchanged screen.

**Always verify** after: sends, saves, deletes, form submissions.
**Skip verification** for: mid-sequence keystrokes, scrolling.

The V2 pipeline's GroundTruthVerifier handles this automatically when you use `start --v2`.

---

## Tool decision trees

### Perception — always start here

```
read_screen()          → FIRST. Accessibility tree: buttons, inputs, text, with coords.
                          Fast, structured, works on native apps.
ocr_read_screen()      → When a11y tree is empty (canvas UIs, image-based apps).
smart_read()           → Combines OCR + a11y. Good first call when unsure.
desktop_screenshot()   → LAST RESORT. Only when you need pixel-level visual detail.
desktop_screenshot_region(x,y,w,h) → Zoomed crop when you need detail in one area.
```

### Clicking

```
smart_click("Save")              → FIRST. Finds by label/text via OCR + a11y.
                                   Pass processId to target the right window.
invoke_element(name="Save")      → When you already know the automation ID.
cdp_click(text="Submit")         → Browser elements. Requires cdp_connect() first.
mouse_click(x, y)                → LAST RESORT. Raw coords from a screenshot.
```

### Typing

```
smart_type("Email", "user@x.com") → FIRST. Finds field by label, focuses, types.
cdp_type(label="Email", text="…") → Browser inputs. Requires cdp_connect() first.
type_text("hello")                → Clipboard paste into whatever is focused.
                                    Use after manually focusing with smart_click.
```

### Browser / CDP

```
1. navigate_browser(url)     → opens URL, auto-enables CDP
2. cdp_connect()             → connect to browser DevTools Protocol
3. cdp_page_context()        → list interactive elements on page
4. cdp_read_text()           → extract DOM text (empty on canvas apps → use OCR)
5. cdp_click(text="…")       → click by visible text
6. cdp_type(label, text)     → fill input by label
7. cdp_evaluate(script)      → run JavaScript in page context
8. cdp_scroll(direction, px) → scroll page via DOM (not mouse wheel)
9. cdp_list_tabs()           → list all open tabs
10. cdp_switch_tab(target)   → switch to a specific tab
```

If CDP isn't available, fall back to keyboard:
```
key_press("ctrl+1")          → tab 1   (cmd+1 on macOS — the PlatformAdapter translates)
key_press("ctrl+tab")        → next tab
key_press("ctrl+shift+tab")  → previous tab
```

### Window management

```
get_windows()                         → list all open windows with PIDs
get_active_window()                   → what's in the foreground now
focus_window(processName="Discord")   → bring to front
minimize_window(processName="calc")   → minimize a window — cross-platform single call
                                         also accepts: processId, title
```

**Rule:** Always `focus_window()` before `key_press()` or `type_text()`. Keystrokes
go to whatever has focus — if that's your terminal, not the target app.

### Canvas apps (Google Docs, Figma, Notion)

DOM has no readable text. Pattern:
```
ocr_read_screen()          → read content (DOM extraction fails)
mouse_click(x, y)          → click into the canvas area
type_text("your text")     → clipboard paste works even on canvas
```

---

## Quick patterns

**Open app and type:**
```
open_app("notepad") → wait(2) → smart_read() → type_text("Hello") → smart_read()
```

**Read a webpage:**
```
navigate_browser(url) → wait(3) → cdp_connect() → cdp_read_text()
```

**Fill a web form:**
```
cdp_connect() → cdp_type("Email", "x@x.com") → cdp_type("Password", "…") → cdp_click("Submit")
```

**Cross-app copy/paste:**
```
focus_window("Chrome") → key_press("ctrl+a") → key_press("ctrl+c")
→ read_clipboard() → focus_window("Notepad") → type_text(clipboard)
```

**Send email via Outlook:**
```
open_app("outlook") → wait(2) → smart_click("New Email")
→ smart_type("To", "recipient@x.com")
→ smart_type("Subject", "Subject line")
→ smart_type("Message body", "Body text")
→ smart_click("Send")
→ verify: read_screen() — is the sent-folder visible or did a "Cannot send" dialog appear?
```

**Autonomous complex task (requires `clawdcursor start`):**
```
delegate_to_agent("Open Gmail, find latest email from Stripe, forward to billing@x.com")
→ poll GET /status every 2s
→ if waiting_confirm: ask user → POST /confirm {"approved": true}
→ if idle: task done
```

---

## Full tool reference (42 tools)

Speed: ⚡ Free/instant · 🔵 Cheap · 🟡 Moderate · 🔴 Vision (expensive)

### Perception (6)
| Tool | What it does | When |
|------|-------------|------|
| `read_screen` | A11y tree — buttons, inputs, text, coords | ⚡ Default first read |
| `smart_read` | OCR + a11y combined | 🔵 When unsure which to use |
| `ocr_read_screen` | Raw OCR text with bounding boxes | 🔵 Canvas UIs, empty a11y trees |
| `desktop_screenshot` | Full screen image (1280px wide) | ⚡ Last resort visual check |
| `desktop_screenshot_region` | Zoomed crop of specific area | ⚡ Fine-grained visual detail |
| `get_screen_size` | Screen dimensions and DPI | ⚡ Coordinate calculations |

### Mouse (7)
| Tool | What it does | When |
|------|-------------|------|
| `smart_click` | Find element by text/label, click | 🔵 First choice for clicking |
| `mouse_click` | Left click at (x, y) | ⚡ Last resort |
| `mouse_double_click` | Double click at (x, y) | ⚡ Open files, select words |
| `mouse_right_click` | Right click at (x, y) | ⚡ Context menus |
| `mouse_hover` | Move cursor without clicking | ⚡ Hover menus |
| `mouse_scroll` | Scroll at position (physical mouse wheel) | ⚡ Scroll content |
| `mouse_drag` | Drag from start to end — accepts `startX/startY/endX/endY` or `x1/y1/x2/y2` | ⚡ Resize, select ranges |

### Keyboard (5)
| Tool | What it does | When |
|------|-------------|------|
| `smart_type` | Find input by label, focus it, type | 🔵 First choice for form fields |
| `type_text` | Clipboard paste into focused element | ⚡ After manually focusing |
| `key_press` | Send key combo (`ctrl+s`, `Return`, `alt+tab`) — PlatformAdapter maps `ctrl` → `cmd` on macOS | ⚡ After focus_window |
| `shortcuts_list` | List keyboard shortcuts for current app | ⚡ Before reaching for mouse |
| `shortcuts_execute` | Run a named shortcut (fuzzy match) | ⚡ Save, copy, paste, undo |

### Window management (5)
| Tool | What it does | When |
|------|-------------|------|
| `get_windows` | List all open windows with PIDs and bounds | ⚡ Situational awareness |
| `get_active_window` | Current foreground window | ⚡ Check current focus |
| `get_focused_element` | Element with keyboard focus | ⚡ Debug wrong-field typing |
| `focus_window` | Bring window to front | ⚡ Always before key_press |
| `minimize_window` | Minimize by processName, processId, or title | ⚡ Clear focus stealers |

### UI elements (2)
| Tool | What it does | When |
|------|-------------|------|
| `find_element` | Search UI tree by name or type | ⚡ Find automation IDs |
| `invoke_element` | Invoke element by automation ID or name | ⚡ When ID known from read_screen |

### Clipboard (2)
| Tool | What it does | When |
|------|-------------|------|
| `read_clipboard` | Read clipboard text | ⚡ After copy operations |
| `write_clipboard` | Write text to clipboard | ⚡ Before paste operations |

### Browser / CDP (11)
| Tool | What it does | When |
|------|-------------|------|
| `cdp_connect` | Connect to browser DevTools Protocol | ⚡ First step for any browser task |
| `cdp_page_context` | List interactive elements on page | ⚡ After connect |
| `cdp_read_text` | Extract DOM text | ⚡ Read page content |
| `cdp_click` | Click by CSS selector or visible text | ⚡ Browser clicks |
| `cdp_type` | Type into input by label or selector | ⚡ Browser form filling |
| `cdp_select_option` | Select dropdown option | ⚡ Select elements |
| `cdp_evaluate` | Run JavaScript in page context | ⚡ Custom queries |
| `cdp_scroll` | Scroll page via DOM (`direction`, `amount` px) | ⚡ DOM-level scroll |
| `cdp_wait_for_selector` | Wait for element to appear | ⚡ After navigation/AJAX |
| `cdp_list_tabs` | List all browser tabs | ⚡ When on wrong tab |
| `cdp_switch_tab` | Switch to a tab by title or index | ⚡ After cdp_list_tabs |

### Orchestration (4)
| Tool | What it does | When |
|------|-------------|------|
| `open_app` | Launch application by name | ⚡ First step for desktop tasks |
| `navigate_browser` | Open URL (auto-enables CDP) | ⚡ First step for browser tasks |
| `wait` | Pause N seconds | ⚡ After opening apps, let UI render |
| `delegate_to_agent` | Send task to built-in autonomous agent | 🟡 Complex multi-step (requires `clawdcursor start`) |

---

## Provider setup (agent mode only)

| Provider | Setup | Cost |
|----------|-------|------|
| **Ollama** (local) | `ollama pull qwen2.5:7b && ollama serve` | $0 — offline, nothing leaves the machine |
| **Any cloud** | Set env var: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `MOONSHOT_API_KEY`, etc. | Varies |
| **OpenClaw users** | Auto-detected from `~/.openclaw/agents/main/auth-profiles.json` | No extra setup |

Run `clawdcursor doctor` to auto-detect and validate providers.

---

## Security

- **Network isolation:** Binds to `127.0.0.1` only. Verify: `netstat -an | grep 3847` —
  should show `127.0.0.1:3847`, never `0.0.0.0:3847`.
- **Ollama:** 100% offline. Screenshots stay in RAM, never leave the machine.
- **Cloud providers:** Screenshots/text sent only to your configured provider. No
  telemetry, no analytics, no third-party logging.
- **Token auth:** All mutating POST endpoints require `Authorization: Bearer <token>`.
  Token at `~/.clawdcursor/token`.
- **Safety tiers:** Auto / Preview / Confirm. Agents must **never self-approve Confirm
  actions**.

---

## Coordinate system

All mouse tools use **image-space coordinates** from a 1280px-wide viewport — matching
screenshots from `desktop_screenshot`. DPI scaling is handled by the PlatformAdapter.
Do not pre-scale coordinates.

---

## Safety

| Tier | Actions | Behavior |
|------|---------|----------|
| 🟢 Auto | Navigation, reading, opening apps | Runs immediately |
| 🟡 Preview | Typing, form filling | Logged |
| 🔴 Confirm | Send, delete, purchase | Pauses — **always ask user first** |

- **Never self-approve Confirm actions.**
- `Alt+F4` and `Ctrl+Alt+Delete` are blocked.
- Server binds to `127.0.0.1` only.
- First run requires explicit user consent for desktop control.

---

## Error recovery

| Problem | Fix |
|---------|-----|
| Port 3847 not responding | `clawdcursor serve` — wait 2s — `GET /health` |
| 401 Unauthorized | Token changed — read `~/.clawdcursor/token` and use fresh value |
| CDP not available | Chrome must be open. `navigate_browser(url)` auto-enables it. |
| CDP on wrong tab | `cdp_list_tabs()` → `cdp_switch_tab(target)` |
| `focus_window` fails | `get_windows()` to confirm title/processName, then retry |
| `smart_click` can't find element | `read_screen()` for coords → `mouse_click(x, y)` |
| `key_press` goes to wrong window | You skipped `focus_window` — always focus first |
| `cdp_read_text` returns empty | Canvas app — use `ocr_read_screen()` instead |
| Same action fails 3+ times | Try a completely different approach |
| V2 agent reports done but nothing changed | Trust the verifier — check `verifier_signals` in the result; if pixel_diff and ocr_delta both zero, the action didn't land |

---

## Platform support

| Platform | A11y | OCR | CDP |
|----------|------|-----|-----|
| Windows (x64/ARM64) | PowerShell + .NET UIA | Windows.Media.Ocr | Chrome/Edge |
| macOS (Intel/Apple Silicon) | JXA + System Events | Apple Vision | Chrome/Edge |
| Linux (x64/ARM64) | AT-SPI | Tesseract | Chrome/Edge |

- **macOS:** Grant Accessibility + Screen Recording in System Settings → Privacy.
  Run `clawdcursor grant` to walk through the dialogs.
- **Linux:** `sudo apt install tesseract-ocr` for OCR support.

### OS-agnostic by design

Platform-specific code lives in `src/v2/platform/{macos,windows,linux}.ts`, behind a
single `PlatformAdapter` interface. Business logic — the agent, the verifier, the
router — never reads `process.platform`. Adding a new OS is one file. Writing a tool
that works everywhere is the default, not an afterthought.
