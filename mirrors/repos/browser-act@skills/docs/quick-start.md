# Quick Start

Two paths to your first result in 60 seconds.

## Path A: Content Extraction (Advanced WebFetch Replacement)

Things WebFetch / curl can't fetch — JS-rendered pages, anti-bot blocks, geo-restricted content — handled in one command:

```bash
browser-act stealth-extract https://example.com
```

Returns the page in markdown. No browser to manage, no session to name, no cleanup required. Comes with JS rendering and anti-bot bypass, and each call is independent — multiple URLs can run in parallel.

```bash
# HTML output
browser-act stealth-extract https://example.com --content-type html

# Use a proxy for geo-restricted content
browser-act stealth-extract https://example.com --dynamic-proxy JP

# Save to file
browser-act stealth-extract https://example.com --output ./page.md
```

Use it for: protected content, batch data collection, information retrieval. See [Anti-Blocking](anti-blocking.md) for details.

## Path B: Full Browser Automation

For login flows, form filling, and click interactions — use sessions:

```bash
# 1. List available browsers
browser-act browser list

# 2. Open the browser to a target URL (starts a session)
browser-act --session my-task browser open <browser-id> https://example.com

# 3. See what interactive elements exist on the page
browser-act --session my-task state

# 4. Interact by element index
browser-act --session my-task click 4
browser-act --session my-task input 2 "hello@example.com"

# 5. Close when done
browser-act session close my-task
```

## The Core Loop

```
Open → State → Interact → State → ... → Close
```

1. **Open** with `browser open` — starts a session
2. **State** with `state` — see indexed elements
3. **Interact** with `click` / `input` / `select` — by index
4. **State** again to confirm the result
5. Repeat until the task is done
6. **Close** with `session close`

## Reading `state` Output

`state` is the agent's eyes. It returns the URL, title, and an indexed element tree:

```
url=https://example.com/login
title=Login

*[1]<div id=login-form />
  *[2]<input type=email placeholder=Email address />
  *[3]<input type=password placeholder=Password />
  *[4]<button id=submit />
    Sign In
  *[5]<a />
    Forgot password?
```

Each `[N]` is an interactive element. Operate it directly by index:

```bash
browser-act --session login input 2 "user@example.com"
browser-act --session login input 3 "password123"
browser-act --session login click 4
```

After the page changes, old indices are invalid — call `state` again for fresh ones.

## Command Chaining

Chain consecutive operations that don't depend on intermediate output with `&&`, in a single call:

```bash
browser-act --session s1 input 2 "user" && \
browser-act --session s1 input 3 "pass" && \
browser-act --session s1 click 4
```

When you need to read intermediate output (e.g. check `state` before deciding what to click), run them separately.

## Next Steps

| To learn about | See |
|----------------|------|
| How to choose between the three browser modes | [Browser Modes](browser-modes.md) |
| How to defeat anti-scraping | [Anti-Blocking](anti-blocking.md) |
| How a human takes over when stuck | [Better Headless](headless.md) |
| How to run multiple tasks in parallel | [Concurrency & Isolation](concurrency.md) |
| The full command list | [Commands](commands.md) |
| Letting AI write your scrapers | [Skill Forge](skill-forge.md) |
