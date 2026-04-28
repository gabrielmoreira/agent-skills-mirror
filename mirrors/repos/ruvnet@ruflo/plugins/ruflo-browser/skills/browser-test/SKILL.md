---
name: browser-test
description: Automated browser testing with Playwright -- navigate, interact, screenshot, and validate UI
allowed-tools: mcp__claude-flow__browser_open mcp__claude-flow__browser_click mcp__claude-flow__browser_fill mcp__claude-flow__browser_type mcp__claude-flow__browser_press mcp__claude-flow__browser_check mcp__claude-flow__browser_uncheck mcp__claude-flow__browser_select mcp__claude-flow__browser_hover mcp__claude-flow__browser_wait mcp__claude-flow__browser_screenshot mcp__claude-flow__browser_snapshot mcp__claude-flow__browser_get-text mcp__claude-flow__browser_get-title mcp__claude-flow__browser_get-url mcp__claude-flow__browser_get-value mcp__claude-flow__browser_eval mcp__claude-flow__browser_close mcp__claude-flow__browser_session-list Bash
---

# Browser Testing

Automated UI testing using Playwright via the ruflo browser MCP tools.

## When to use

When you need to verify UI functionality, test user flows, or validate that frontend changes work correctly in a real browser.

## Steps

1. **Open page** — call `mcp__claude-flow__browser_open` with the target URL
2. **Interact** — use `browser_click`, `browser_fill`, `browser_type`, `browser_select` for form inputs
3. **Wait** — call `mcp__claude-flow__browser_wait` for elements to appear or network idle
4. **Validate** — call `browser_get-text` / `browser_get-value` to check content
5. **Screenshot** — call `mcp__claude-flow__browser_screenshot` to capture visual state
6. **Snapshot** — call `mcp__claude-flow__browser_snapshot` for accessibility tree
7. **Clean up** — call `mcp__claude-flow__browser_close` when done

## Navigation

- `browser_back` / `browser_forward` for history navigation
- `browser_reload` to refresh the page
- `browser_scroll` to scroll to elements or coordinates

## Tips

- Use `browser_wait` before assertions to handle async rendering
- Take screenshots before and after interactions for visual regression
- Use `browser_eval` for custom JavaScript assertions
