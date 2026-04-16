---
name: agent-browser
description: Browser automation CLI for AI agents. Use when the user needs to interact with websites, including navigating pages, filling forms, clicking buttons, taking screenshots, extracting data, testing web apps, or automating any browser task. Triggers include requests to "open a website", "fill out a form", "click a button", "take a screenshot", "scrape data from a page", "test this web app", "login to a site", "automate browser actions", or any task requiring programmatic web interaction.
---

# Browser Automation with agent-browser

**IMPORTANT — You MUST use the `agent-browser` CLI for all browser automation tasks. Do NOT use puppeteer, playwright, or any other library. The `agent-browser` CLI is the only supported tool.**

## Step 0: Ensure agent-browser Is Installed

Before running any command, check if `agent-browser` is available. If not, install it and ensure a browser is ready:

```bash
if ! command -v agent-browser >/dev/null 2>&1; then
  npm install --global agent-browser
fi

# Ensure Chrome/Chromium is detected. On CI (GitHub Actions), Chrome is typically pre-installed.
# If agent-browser cannot find a browser, download a bundled one:
agent-browser open about:blank && agent-browser close || agent-browser install
```

## Core Workflow

Every browser automation follows this pattern — **open → snapshot → interact → re-snapshot**:

```bash
agent-browser open https://example.com/form
agent-browser snapshot -i
# Output: @e1 [input type="email"], @e2 [input type="password"], @e3 [button] "Submit"

agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser snapshot -i   # MUST re-snapshot after navigation/DOM changes
```

**Critical rule:** Refs (`@e1`, `@e2`) are invalidated when the page changes. Always re-snapshot after clicks that navigate, form submissions, or dynamic content loading.

## Essential Commands

```bash
# Navigation
agent-browser open <url>                  # Open page
agent-browser close                       # Close browser (always close when done!)

# Snapshot (get element refs)
agent-browser snapshot -i                 # Interactive elements with @refs

# Interaction (use @refs from snapshot)
agent-browser click @e1                   # Click element
agent-browser fill @e2 "text"             # Clear field and type
agent-browser type @e2 "text"             # Type without clearing
agent-browser select @e1 "option"         # Select dropdown
agent-browser check @e1                   # Toggle checkbox
agent-browser press Enter                 # Press key

# Wait
agent-browser wait --load networkidle     # Wait for network idle
agent-browser wait @e1                    # Wait for element
agent-browser wait --url "**/dashboard"   # Wait for URL pattern
agent-browser wait --text "Welcome"       # Wait for text to appear

# Capture
agent-browser screenshot output.png       # Screenshot
agent-browser screenshot --full           # Full page screenshot
agent-browser screenshot --annotate       # Screenshot with numbered element labels

# Get information
agent-browser get text @e1                # Get element text
agent-browser get url                     # Get current URL
agent-browser get title                   # Get page title

# Viewport
agent-browser set viewport 1920 1080      # Set viewport size
```

## Command Chaining

Chain commands with `&&` when you don't need intermediate output:

```bash
agent-browser open https://example.com && agent-browser wait --load networkidle && agent-browser screenshot page.png
```

Run separately when you need to parse output (e.g., snapshot → read refs → interact).

## Common Patterns

### Form Submission

```bash
agent-browser open https://example.com/signup
agent-browser snapshot -i
agent-browser fill @e1 "Jane Doe"
agent-browser fill @e2 "jane@example.com"
agent-browser select @e3 "California"
agent-browser click @e5
agent-browser wait --load networkidle
```

### Authentication (State Persistence)

```bash
# Login and save state
agent-browser open https://app.example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "$USERNAME"
agent-browser fill @e2 "$PASSWORD"
agent-browser click @e3
agent-browser wait --url "**/dashboard"
agent-browser state save auth.json

# Reuse in future sessions
agent-browser state load auth.json
agent-browser open https://app.example.com/dashboard
```

### Data Extraction

```bash
agent-browser open https://example.com/products
agent-browser snapshot -i
agent-browser get text @e5
```

### JavaScript Evaluation

```bash
agent-browser eval 'document.title'

# Complex JS: use --stdin to avoid shell quoting issues
agent-browser eval --stdin <<'EVALEOF'
JSON.stringify(Array.from(document.querySelectorAll("a")).map(a => a.href))
EVALEOF
```

## Security (Important)

Always apply these safeguards, especially in CI/automated environments:

```bash
# 1. Content Boundaries — prevent web page content from being interpreted as LLM instructions
export AGENT_BROWSER_CONTENT_BOUNDARIES=1

# 2. Domain Allowlist — restrict navigation to trusted domains only
export AGENT_BROWSER_ALLOWED_DOMAINS="example.com,*.example.com"

# 3. Output Limits — prevent large pages from flooding the context window
export AGENT_BROWSER_MAX_OUTPUT=50000

# 4. Action Policy — restrict which actions the agent can perform
export AGENT_BROWSER_ACTION_POLICY=./policy.json
# Example policy.json: { "default": "deny", "allow": ["navigate", "snapshot", "click", "scroll", "wait", "get"] }
```

**State files and auth tokens**: State files (`.json`) may contain session tokens in plaintext. Always add them to `.gitignore` and delete when no longer needed. Use `AGENT_BROWSER_ENCRYPTION_KEY` for encryption at rest.

## Deep-Dive References

For advanced usage, consult the reference docs in this skill directory:

| Reference | When to Use |
|-----------|-------------|
| [references/commands.md](references/commands.md) | Full command reference with all options |
| [references/snapshot-refs.md](references/snapshot-refs.md) | Ref lifecycle, invalidation rules |
| [references/session-management.md](references/session-management.md) | Parallel sessions, state persistence |
| [references/authentication.md](references/authentication.md) | OAuth, 2FA, cookie-based auth |
| [references/video-recording.md](references/video-recording.md) | Recording workflows for debugging |
| [references/profiling.md](references/profiling.md) | Chrome DevTools profiling |
| [references/proxy-support.md](references/proxy-support.md) | Proxy configuration, geo-testing |

## Ready-to-Use Templates

```bash
sh templates/form-automation.sh https://example.com/form
sh templates/authenticated-session.sh https://app.example.com/login
sh templates/capture-workflow.sh https://example.com ./output
```
