---
name: browser-scrape
description: Extract structured data from web pages using browser automation and DOM queries
allowed-tools: mcp__claude-flow__browser_open mcp__claude-flow__browser_get-text mcp__claude-flow__browser_get-value mcp__claude-flow__browser_eval mcp__claude-flow__browser_snapshot mcp__claude-flow__browser_screenshot mcp__claude-flow__browser_scroll mcp__claude-flow__browser_wait mcp__claude-flow__browser_click mcp__claude-flow__browser_close mcp__claude-flow__browser_session-list Bash
---

# Browser Scraping

Extract structured data from web pages using browser automation.

## When to use

When you need to gather information from web pages that require JavaScript rendering, authentication, or dynamic content loading.

## Steps

1. **Open page** — call `mcp__claude-flow__browser_open` with the target URL
2. **Wait for content** — call `mcp__claude-flow__browser_wait` for dynamic content to load
3. **Get accessibility tree** — call `mcp__claude-flow__browser_snapshot` for structured page content
4. **Extract text** — call `mcp__claude-flow__browser_get-text` with CSS selectors
5. **Run queries** — call `mcp__claude-flow__browser_eval` with JavaScript to extract structured data
6. **Paginate** — use `browser_click` on next/load-more buttons, then repeat extraction
7. **Close** — call `mcp__claude-flow__browser_close` when done

## Best practices

- Prefer `browser_snapshot` (accessibility tree) over raw HTML for structured extraction
- Use `browser_eval` with `document.querySelectorAll` for bulk extraction
- Add `browser_wait` between page loads to avoid timing issues
- Respect robots.txt and rate limits
