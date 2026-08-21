---
name: browser-automation
description: "Writes Playwright (preferred) or Puppeteer browser tests and scripts: user-facing locators, auto-wait, storageState auth, traces on failure. Use when the user mentions Playwright, Puppeteer, E2E, page.getByRole, locators, or headless Chromium tests. Not for Java Playwright POM (playwright-java), owned CDP Chrome research sessions (chrome-browser-automation), or Hermes SPA scrape-when-fetch-fails (web-scraping-browser). Never CAPTCHA-bypass or anti-bot evasion."
version: 1.0.1
risk: unknown
source: vibeship-spawner-skills (Apache 2.0)
date_added: 2026-02-27
---

# Browser Automation

Browser automation powers web testing, scraping, and AI agent interactions. The difference between a flaky script and a reliable system comes down to understanding selectors, waiting strategies, and anti-detection patterns.

This skill covers Playwright (recommended) and Puppeteer, with patterns for testing, scraping, and agentic browser control. Key insight: Playwright won the framework war. Unless you need Puppeteer's stealth ecosystem or are Chrome-only, Playwright is the better choice in 2025.

Critical distinction: Testing automation (predictable apps you control) vs scraping/agent automation (unpredictable sites that fight back). Different problems, different solutions.

## When to Use

- User mentions or implies: playwright, puppeteer, browser automation, headless, web scraping, e2e test, end-to-end, selenium, chromium, browser test, page.click, locator
- You need cross-browser E2E testing with reliable auto-waiting
- You need to scrape sites that may have anti-bot protection
- You are building AI agent tools that control a browser
- You need to mock network responses or capture API traffic during tests

## Prerequisites

### Windows Host (Primary)

This skill assumes a Windows host with PowerShell as the primary shell. All CLI commands are PowerShell unless noted.

### Install Playwright (Recommended)

```powershell
npm init -y
npm install -D @playwright/test
npx playwright install
```

### Install Puppeteer (Alternative)

```powershell
npm install puppeteer puppeteer-core
npm install puppeteer-extra puppeteer-extra-plugin-stealth
```

### Verify Installation

```powershell
npx playwright --version
npx playwright install --dry-run
```

### Project Structure

```
project/
├── tests/
│   ├── example.spec.ts
│   └── auth.setup.ts
├── playwright.config.ts
├── package.json
└── playwright/.auth/
    └── user.json
```

## Procedure

### 1. Choose Your Framework

| Framework | When to Use | Notes |
|-----------|-------------|-------|
| Playwright | Default choice | Cross-browser, auto-waiting, best DX. 96% success rate, 4.5s avg execution, Microsoft-backed |
| Puppeteer | Chrome-only, need stealth plugins, existing codebase | 75% success rate at scale, but best stealth ecosystem |
| Selenium | Legacy systems, specific language bindings | Slower, more verbose, but widest browser support |

### 2. Use User-Facing Locators (Always)

Locator priority order:

1. `getByRole` — Best: matches accessibility tree
2. `getByText` — Good: matches visible content
3. `getByLabel` — Good: matches form labels
4. `getByTestId` — Fallback: explicit test contracts
5. CSS/XPath — Last resort: fragile, avoid

```typescript
// GOOD - user-facing
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('link', { name: 'Sign up' }).click();
await page.getByText('Welcome back').isVisible();
await page.getByLabel('Email address').fill('user@example.com');
await page.getByTestId('submit-button').click();

// BAD - fragile, do not use
await page.locator('.btn-primary.submit-form').click();
await page.locator('#header > div > button:nth-child(2)').click();
await page.locator('//div[@class="form"]/button[1]').click();
await page.locator('[data-v-12345]').click();
```

### 3. Filtering and Chaining Locators

```typescript
// Filter by containing text
await page.getByRole('listitem')
  .filter({ hasText: 'Product A' })
  .getByRole('button', { name: 'Add to cart' })
  .click();

// Filter by NOT containing
await page.getByRole('listitem')
  .filter({ hasNotText: 'Sold out' })
  .first()
  .click();

// Chain locators
const row = page.getByRole('row', { name: 'John Doe' });
await row.getByRole('button', { name: 'Edit' }).click();
```

### 4. Let Auto-Wait Handle Timing (Never Manual Waits)

Playwright waits automatically for: element attached to DOM, visible, stable (not animating), receiving events, and enabled.

```typescript
// CORRECT - auto-wait handles everything
await page.goto('/dashboard');
await page.getByRole('button', { name: 'Submit' }).click();
await expect(page.getByText('Success!')).toBeVisible();

// WRONG - never do this
await page.waitForTimeout(2000);  // NO! Arbitrary wait
await page.waitForSelector('.loading-spinner', { state: 'hidden' });
await page.waitForTimeout(500);   // "Just to be safe" - NO!
```

### 5. When You DO Need Explicit Waits

```typescript
// Wait for specific network request
const responsePromise = page.waitForResponse(
  response => response.url().includes('/api/data')
);
await page.getByRole('button', { name: 'Load' }).click();
const response = await responsePromise;

// Wait for URL change
await Promise.all([
  page.waitForURL('**/dashboard'),
  page.getByRole('button', { name: 'Login' }).click(),
]);

// Wait for download
const downloadPromise = page.waitForEvent('download');
await page.getByText('Export CSV').click();
const download = await downloadPromise;
```

### 6. Ensure Test Isolation

Each test runs in complete isolation with fresh state (cookies, storage, fresh page, clean state).

```typescript
import { test, expect } from '@playwright/test';

test('user can add item to cart', async ({ page }) => {
  await page.goto('/products');
  await page.getByRole('button', { name: 'Add to Cart' }).click();
  await expect(page.getByTestId('cart-count')).toHaveText('1');
});

test('user can remove item from cart', async ({ page }) => {
  // Completely isolated - cart is empty
  await page.goto('/cart');
  await expect(page.getByText('Your cart is empty')).toBeVisible();
});
```

### 7. Shared Authentication Pattern

Save auth state once, reuse across tests:

```typescript
// auth.setup.ts
import { test as setup } from '@playwright/test';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: './playwright/.auth/user.json' });
});
```

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'tests',
      dependencies: ['setup'],
      use: {
        storageState: './playwright/.auth/user.json',
      },
    },
  ],
});
```

### 8. Configure Error Recovery

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    video: 'retain-on-failure',
  },
  retries: 2,
});
```

Try-catch with debug info for scraping:

```typescript
async function scrapeProduct(page: Page, url: string) {
  try {
    await page.goto(url, { timeout: 30000 });
    const title = await page.getByRole('heading', { level: 1 }).textContent();
    const price = await page.getByTestId('price').textContent();
    return { title, price, success: true };
  } catch (error) {
    const screenshot = await page.screenshot({
      path: `errors/${Date.now()}-error.png`,
      fullPage: true
    });
    const html = await page.content();
    await fs.writeFile(`errors/${Date.now()}-page.html`, html);
    console.error({ url, error: error.message, currentUrl: page.url() });
    return { success: false, error: error.message };
  }
}
```

Retry with exponential backoff:

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  baseDelay = 1000
): Promise<T> {
  let lastError: Error;
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (attempt < maxRetries - 1) {
        const delay = baseDelay * Math.pow(2, attempt);
        const jitter = delay * 0.1 * Math.random();
        await new Promise(r => setTimeout(r, delay + jitter));
      }
    }
  }
  throw lastError;
}

// Usage
const result = await withRetry(() => scrapeProduct(page, url), 3, 2000);
```

### 9. Parallel Execution

```typescript
// playwright.config.ts
export default defineConfig({
  fullyParallel: true,
  workers: process.env.CI ? 4 : undefined,
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
});
```

Parallel scraping with browser contexts:

```typescript
const browser = await chromium.launch();
const urls = ['url1', 'url2', 'url3', 'url4', 'url5'];

const results = await Promise.all(
  urls.map(async (url) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    try {
      await page.goto(url);
      const data = await extractData(page);
      return { url, data, success: true };
    } catch (error) {
      return { url, error: error.message, success: false };
    } finally {
      await context.close();
    }
  })
);
await browser.close();
```

Rate-limited parallel processing:

```typescript
import pLimit from 'p-limit';
const limit = pLimit(5);  // Max 5 concurrent

const results = await Promise.all(
  urls.map(url => limit(async () => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await new Promise(r => setTimeout(r, Math.random() * 2000));
    try {
      return await scrapePage(page, url);
    } finally {
      await context.close();
    }
  }))
);
```

### 10. Network Interception

Block unnecessary resources:

```typescript
await page.route('**/*', (route) => {
  const url = route.request().url();
  const resourceType = route.request().resourceType();
  if (['image', 'font', 'media'].includes(resourceType)) {
    return route.abort();
  }
  if (url.includes('google-analytics') || url.includes('facebook.com/tr')) {
    return route.abort();
  }
  return route.continue();
});
```

Mock API responses:

```typescript
await page.route('**/api/products', async (route) => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([
      { id: 1, name: 'Mock Product', price: 99.99 },
    ]),
  });
});
await page.goto('/products');
```

Capture API responses:

```typescript
const apiResponses: any[] = [];
page.on('response', async (response) => {
  if (response.url().includes('/api/')) {
    const data = await response.json().catch(() => null);
    apiResponses.push({ url: response.url(), status: response.status(), data });
  }
});
await page.goto('/dashboard');
```

### 11. Stealth Browser Pattern (Scraping)

Bot detection checks for: `navigator.webdriver` property, Chrome DevTools protocol artifacts, browser fingerprint inconsistencies, behavioral patterns (perfect timing, no mouse movement), headless indicators.

Puppeteer Stealth (best anti-detection):

```typescript
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

puppeteer.use(StealthPlugin());

const browser = await puppeteer.launch({
  headless: 'new',
  args: [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-blink-features=AutomationControlled',
  ],
});

const page = await browser.newPage();
await page.setViewport({ width: 1920, height: 1080 });
await page.setUserAgent(
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
);
await page.goto('https://target-site.com', { waitUntil: 'networkidle0' });
```

Playwright Stealth:

```typescript
import { chromium } from 'playwright-extra';
import stealth from 'puppeteer-extra-plugin-stealth';

chromium.use(stealth());

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  userAgent: 'Mozilla/5.0 ...',
  locale: 'en-US',
  timezoneId: 'America/New_York',
});
```

Human-like behavior:

```typescript
const randomDelay = (min: number, max: number) =>
  new Promise(r => setTimeout(r, Math.random() * (max - min) + min));

await page.goto(url);
await randomDelay(500, 1500);

const button = await page.$('button.submit');
const box = await button.boundingBox();
await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 10 });
await randomDelay(100, 300);
await button.click();

await page.evaluate(() => {
  window.scrollBy({ top: 300 + Math.random() * 200, behavior: 'smooth' });
});
```

### 12. Handle iframes and Popups

New window/tab:

```typescript
const pagePromise = context.waitForEvent('page');
await page.getByRole('link', { name: 'Open in new tab' }).click();
const newPage = await pagePromise;
await newPage.waitForLoadState();
await expect(newPage.getByRole('heading')).toBeVisible();
await newPage.close();
```

Popup windows:

```typescript
const popupPromise = page.waitForEvent('popup');
await page.getByRole('button', { name: 'Open popup' }).click();
const popup = await popupPromise;
await popup.waitForLoadState();
```

iframes:

```typescript
// By frame name
const frame = page.frame('payment-iframe');
await frame.getByRole('textbox', { name: 'Card number' }).fill('4242...');

// By selector
const frameLocator = page.frameLocator('iframe#payment');
await frameLocator.getByRole('textbox', { name: 'Card number' }).fill('4242...');

// Nested iframes
const outer = page.frameLocator('iframe#outer');
const inner = outer.frameLocator('iframe#inner');
await inner.getByRole('button').click();

// Wait for iframe to load
await page.waitForSelector('iframe#payment');
const frame = page.frameLocator('iframe#payment');
await frame.getByText('Secure Payment').waitFor();
```

### 13. Set Consistent Viewport for Headless

Headless browsers have no display, which affects some CSS (visibility calculations), viewport sizing, and font rendering. Some animations behave differently. Popup windows may not work.

```typescript
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
```

Or in config:

```typescript
export default defineConfig({
  use: { viewport: { width: 1280, height: 720 } },
});
```

### 14. Run and Debug

```powershell
# Run all tests
npx playwright test

# Run headed for debugging
npx playwright test --headed

# Slow down to watch
npx playwright test --headed --slowmo 100

# Show trace viewer for CI failures
npx playwright show-trace trace.zip

# Generate report
npx playwright show-report
```

## Pitfalls

### CRITICAL: Using waitForTimeout Instead of Proper Waits

**Symptoms:** Tests pass locally, fail in CI. Pass 9 times, fail on the 10th. "Element not found" errors that seem random. Tests take 30+ seconds when they should take 3.

**Why:** `waitForTimeout` is a fixed delay. If the page loads in 500ms, you wait 2000ms anyway. If the page takes 2100ms (CI is slower), you fail. There is no correct value — it's always either too short or too long.

**Fix:** Remove ALL `waitForTimeout` calls. Use auto-wait, `waitForResponse`, `waitForURL`, or assertions instead. NEVER use `setTimeout` or `waitForTimeout` in production code.

### HIGH: CSS Selectors Tied to Styling Classes

**Symptoms:** Tests break after CSS refactoring. Selectors like `.btn-primary` stop working. Frontend redesign breaks all tests without changing behavior.

**Why:** CSS class names are implementation details for styling, not semantic meaning. When designers change from `.btn-primary` to `.button--primary`, tests break even though behavior is identical.

**Fix:** Use user-facing locators (`getByRole`, `getByText`, `getByLabel`, `getByTestId`). If you must use CSS, use `data-testid`.

### HIGH: navigator.webdriver Exposes Automation

**Symptoms:** Immediate 403 errors. CAPTCHA challenges. Empty pages. "Access Denied" messages. Works for 1 request, then gets blocked.

**Why:** By default, headless browsers set `navigator.webdriver = true`. This is the first thing bot detection checks.

**Fix:** Use stealth plugins (`puppeteer-extra-plugin-stealth` or `playwright-extra` with stealth). Manual partial fix: override `navigator.webdriver` via `evaluateOnNewDocument`. This is cat-and-mouse — detection evolves. For serious scraping, consider managed solutions like Browserbase.

### HIGH: Tests Share State and Affect Each Other

**Symptoms:** Tests pass individually but fail when run together. Order matters — test B fails if test A runs first. Random failures that "fix themselves" on rerun.

**Why:** Shared browser context means shared cookies, localStorage, and session state.

**Fix:** Each test must be fully isolated with fresh context. For shared auth, save `storageState` to file and reuse via config. Never modify global state in tests.

### HIGH: Getting Blocked by Rate Limiting

**Symptoms:** Works for first 50 pages, then 429 errors. Suddenly all requests fail. IP gets blocked. CAPTCHA starts appearing after successful requests.

**Why:** Sites monitor request patterns. 100 requests per second from one IP is obviously automated.

**Fix:** Add random delays (1-3 seconds) between requests. Use rotating proxies. Limit concurrent requests with `pLimit`. Rotate user agents.

### MEDIUM: New Windows/Popups Not Handled

**Symptoms:** Click button, nothing happens. Test hangs. "Window not found" errors. Actions succeed but verification fails because you're on wrong page.

**Why:** `target="_blank"` links open new windows. Your page reference still points to the original page.

**Fix:** Wait for popup BEFORE triggering it using `context.waitForEvent('page')` or `page.waitForEvent('popup')`.

### MEDIUM: Can't Interact with Elements in iframes

**Symptoms:** Element clearly visible but "not found". Selector works in DevTools but not in Playwright. Parent page selectors work, iframe content doesn't.

**Why:** iframes are separate documents. `page.locator` only searches the main frame.

**Fix:** Use `page.frame()` or `page.frameLocator()` to explicitly access iframe content.

## Verification

### Check Playwright is installed and browsers are ready

```powershell
npx playwright --version
npx playwright install --dry-run
```

### Run a smoke test

```powershell
npx playwright test --headed --project=chromium
```

Expected: tests execute, browser window visible, report generated.

### Verify no waitForTimeout in codebase

```powershell
Select-String -Path .\tests\*.ts -Pattern "waitForTimeout"
```

Expected: no matches. If matches found, remove them.

### Verify no CSS class selectors in tests

```powershell
Select-String -Path .\tests\*.ts -Pattern "\.locator\(['\"']\."
```

Expected: no matches or only `data-testid` based selectors.

### Verify test isolation

```powershell
npx playwright test --workers=1
npx playwright test --workers=4
```

Expected: same pass/fail results regardless of worker count.

### Verify trace and screenshots on failure

```powershell
npx playwright test --trace=on
npx playwright show-trace test-results\*\trace.zip
```

Expected: trace viewer opens showing screenshots, DOM snapshots, and network logs.

### Verify stealth setup (scraping only)

```powershell
node -e "const p = require('puppeteer-extra'); const s = require('puppeteer-extra-plugin-stealth'); p.use(s()); console.log('stealth loaded');"
```

Expected: prints `stealth loaded` without errors.

## Related Skills

Works well with: `agent-tool-builder`, `workflow-automation`, `computer-use-agents`, `test-architect`

### Delegation Triggers

- User needs full desktop control beyond browser → `computer-use-agents`
- User needs API testing alongside browser tests → `backend`
- User needs testing strategy → `test-architect`
- User needs visual regression testing → `ui-design`
- User needs browser automation in workflows → `workflow-automation`
- User building browser tools for agents → `agent-tool-builder`

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- API testing → use `backend` skill. Load testing → use `performance-thinker`. Accessibility testing → use `accessibility-specialist`. Visual regression testing → use `ui-design`.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
