---
name: webapp-testing
description: "Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browse..."
risk: unknown
source: community
date_added: "2026-02-27"
---

# Web Application Testing

To test local web applications, write native Python Playwright scripts.

**Helper Scripts Available**:
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)

**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be very large and thus pollute your context window. They exist to be called directly as black-box scripts rather than ingested into your context window.

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Example: Using with_server.py

To start a server, run `--help` first, then use the helper:

**Single server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Multiple servers (e.g., backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

To create an automation script, include only Playwright logic (servers are managed automatically):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors** from inspection results

3. **Execute actions** using discovered selectors

## Common Pitfall

❌ **Don't** inspect the DOM before waiting for `networkidle` on dynamic apps
✅ **Do** wait for `page.wait_for_load_state('networkidle')` before inspection

## Best Practices

- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of the scripts available in `scripts/` can help. These scripts handle common, complex workflows reliably without cluttering the context window. Use `--help` to see usage, then invoke directly. 
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`

## Reference Files

- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation

## When to Use
This skill is applicable to execute the workflow or actions described in the overview.

## When to Use This Skill

Use this skill when you need to:
- Test frontend functionality in a real browser
- Verify UI behavior and interactions
- Debug web application issues
- Capture screenshots for documentation or debugging
- Inspect browser console logs
- Validate form submissions and user flows
- Check responsive design across viewports

## Prerequisites

- Node.js installed on the system
- A locally running web application (or accessible URL)
- Playwright will be installed automatically if not present

## Core Capabilities

### 1. Browser Automation
- Navigate to URLs
- Click buttons and links
- Fill form fields
- Select dropdowns
- Handle dialogs and alerts

### 2. Verification
- Assert element presence
- Verify text content
- Check element visibility
- Validate URLs
- Test responsive behavior

### 3. Debugging
- Capture screenshots
- View console logs
- Inspect network requests
- Debug failed tests

## Usage Examples

### Example 1: Basic Navigation Test
```javascript
// Navigate to a page and verify title
await page.goto('http://localhost:3000');
const title = await page.title();
console.log('Page title:', title);
```

### Example 2: Form Interaction
```javascript
// Fill out and submit a form
await page.fill('#username', 'testuser');
await page.fill('#password', 'password123');
await page.click('button[type="submit"]');
await page.waitForURL('**/dashboard');
```

### Example 3: Screenshot Capture
```javascript
// Capture a screenshot for debugging
await page.screenshot({ path: 'debug.png', fullPage: true });
```

## Guidelines

1. **Always verify the app is running** - Check that the local server is accessible before running tests
2. **Use explicit waits** - Wait for elements or navigation to complete before interacting
3. **Capture screenshots on failure** - Take screenshots to help debug issues
4. **Clean up resources** - Always close the browser when done
5. **Handle timeouts gracefully** - Set reasonable timeouts for slow operations
6. **Test incrementally** - Start with simple interactions before complex flows
7. **Use selectors wisely** - Prefer data-testid or role-based selectors over CSS classes

## Common Patterns

### Pattern: Wait for Element
```javascript
await page.waitForSelector('#element-id', { state: 'visible' });
```

### Pattern: Check if Element Exists
```javascript
const exists = await page.locator('#element-id').count() > 0;
```

### Pattern: Get Console Logs
```javascript
page.on('console', msg => console.log('Browser log:', msg.text()));
```

### Pattern: Handle Errors
```javascript
try {
  await page.click('#button');
} catch (error) {
  await page.screenshot({ path: 'error.png' });
  throw error;
}
```

## Limitations

- Requires Node.js environment
- Cannot test native mobile apps (use React Native Testing Library instead)
- May have issues with complex authentication flows
- Some modern frameworks may require specific configuration

## Setup

```bash
npm init playwright@latest
```

## Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';

test('homepage has title', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await expect(page).toHaveTitle(/My App/);
});

test('can navigate to about page', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.click('text=About');
  await expect(page).toHaveURL(/.*about/);
});
```

## Common Actions

### Navigation
```typescript
await page.goto('http://localhost:3000');
await page.goBack();
await page.reload();
```

### Clicking
```typescript
await page.click('button');
await page.click('text=Submit');
await page.click('#submit-btn');
await page.click('[data-testid="submit"]');
```

### Form Input
```typescript
await page.fill('input[name="email"]', 'test@example.com');
await page.fill('#password', 'secret123');
await page.selectOption('select#country', 'USA');
await page.check('input[type="checkbox"]');
```

### Waiting
```typescript
await page.waitForSelector('.loaded');
await page.waitForURL('**/dashboard');
await page.waitForResponse('**/api/data');
await page.waitForTimeout(1000); // Avoid if possible
```

## Assertions

```typescript
await expect(page.locator('h1')).toHaveText('Welcome');
await expect(page.locator('.items')).toHaveCount(5);
await expect(page.locator('button')).toBeEnabled();
await expect(page.locator('.modal')).toBeVisible();
await expect(page.locator('input')).toHaveValue('test');
```

## Screenshots

```typescript
// Full page
await page.screenshot({ path: 'screenshot.png', fullPage: true });

// Element only
await page.locator('.chart').screenshot({ path: 'chart.png' });
```

## Console Logs

```typescript
page.on('console', msg => console.log(msg.text()));
page.on('pageerror', err => console.error(err.message));
```

## Network Interception

```typescript
await page.route('**/api/data', route => {
  route.fulfill({
    status: 200,
    body: JSON.stringify({ items: [] })
  });
});
```

## Running Tests

```bash
# Run all tests
npx playwright test

# Run specific file
npx playwright test tests/login.spec.ts

# Run in headed mode
npx playwright test --headed

# Run with UI
npx playwright test --ui
```
