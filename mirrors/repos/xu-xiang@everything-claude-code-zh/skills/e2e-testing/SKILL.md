---
name: e2e-testing
description: Playwright E2E 测试模式、页面对象模型 (Page Object Model)、配置、CI/CD 集成、产物管理以及不稳定测试 (Flaky Test) 策略。
origin: ECC
---

# E2E 测试模式 (E2E Testing Patterns)

用于构建稳定、快速且易于维护的 E2E 测试套件的全面 Playwright 模式。

## 测试文件组织 (Test File Organization)

```
tests/
├── e2e/
│   ├── auth/
│   │   ├── login.spec.ts
│   │   ├── logout.spec.ts
│   │   └── register.spec.ts
│   ├── features/
│   │   ├── browse.spec.ts
│   │   ├── search.spec.ts
│   │   └── create.spec.ts
│   └── api/
│       └── endpoints.spec.ts
├── fixtures/
│   ├── auth.ts
│   └── data.ts
└── playwright.config.ts
```

## 页面对象模型 (Page Object Model - POM)

```typescript
import { Page, Locator } from '@playwright/test'

export class ItemsPage {
  readonly page: Page
  readonly searchInput: Locator
  readonly itemCards: Locator
  readonly createButton: Locator

  constructor(page: Page) {
    this.page = page
    this.searchInput = page.locator('[data-testid="search-input"]')
    this.itemCards = page.locator('[data-testid="item-card"]')
    this.createButton = page.locator('[data-testid="create-btn"]')
  }

  async goto() {
    await this.page.goto('/items')
    await this.page.waitForLoadState('networkidle')
  }

  async search(query: string) {
    await this.searchInput.fill(query)
    await this.page.waitForResponse(resp => resp.url().includes('/api/search'))
    await this.page.waitForLoadState('networkidle')
  }

  async getItemCount() {
    return await this.itemCards.count()
  }
}
```

## 测试结构 (Test Structure)

```typescript
import { test, expect } from '@playwright/test'
import { ItemsPage } from '../../pages/ItemsPage'

test.describe('项目搜索 (Item Search)', () => {
  let itemsPage: ItemsPage

  test.beforeEach(async ({ page }) => {
    itemsPage = new ItemsPage(page)
    await itemsPage.goto()
  })

  test('应该能通过关键字搜索', async ({ page }) => {
    await itemsPage.search('test')

    const count = await itemsPage.getItemCount()
    expect(count).toBeGreaterThan(0)

    await expect(itemsPage.itemCards.first()).toContainText(/test/i)
    await page.screenshot({ path: 'artifacts/search-results.png' })
  })

  test('应该能处理无结果的情况', async ({ page }) => {
    await itemsPage.search('xyznonexistent123')

    await expect(page.locator('[data-testid="no-results"]')).toBeVisible()
    expect(await itemsPage.getItemCount()).toBe(0)
  })
})
```

## Playwright 配置 (Playwright Configuration)

```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['junit', { outputFile: 'playwright-results.xml' }],
    ['json', { outputFile: 'playwright-results.json' }]
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
})
```

## 不稳定测试模式 (Flaky Test Patterns)

### 隔离 (Quarantine)

```typescript
test('flaky: complex search', async ({ page }) => {
  test.fixme(true, 'Flaky - Issue #123')
  // 测试代码...
})

test('conditional skip', async ({ page }) => {
  test.skip(process.env.CI, '在 CI 中不稳定 - Issue #123')
  // 测试代码...
})
```

### 识别不稳定 (Identify Flakiness)

```bash
npx playwright test tests/search.spec.ts --repeat-each=10
npx playwright test tests/search.spec.ts --retries=3
```

### 常见原因与修复 (Common Causes & Fixes)

**竞态条件 (Race conditions):**
```typescript
// 错误做法：假设元素已就绪
await page.click('[data-testid="button"]')

// 正确做法：使用自动等待的定位器 (locator)
await page.locator('[data-testid="button"]').click()
```

**网络时机 (Network timing):**
```typescript
// 错误做法：任意设置超时
await page.waitForTimeout(5000)

// 正确做法：等待特定条件
await page.waitForResponse(resp => resp.url().includes('/api/data'))
```

**动画时机 (Animation timing):**
```typescript
// 错误做法：在动画进行时点击
await page.click('[data-testid="menu-item"]')

// 正确做法：等待元素稳定
await page.locator('[data-testid="menu-item"]').waitFor({ state: 'visible' })
await page.waitForLoadState('networkidle')
await page.locator('[data-testid="menu-item"]').click()
```

## 产物管理 (Artifact Management)

### 截图 (Screenshots)

```typescript
await page.screenshot({ path: 'artifacts/after-login.png' })
await page.screenshot({ path: 'artifacts/full-page.png', fullPage: true })
await page.locator('[data-testid="chart"]').screenshot({ path: 'artifacts/chart.png' })
```

### 追踪 (Traces)

```typescript
await browser.startTracing(page, {
  path: 'artifacts/trace.json',
  screenshots: true,
  snapshots: true,
})
// ... 执行测试操作 ...
await browser.stopTracing()
```

### 视频 (Video)

```typescript
// 在 playwright.config.ts 中配置
use: {
  video: 'retain-on-failure',
  videosPath: 'artifacts/videos/'
}
```

## CI/CD 集成 (CI/CD Integration)

```yaml
# .github/workflows/e2e.yml
name: E2E Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test
        env:
          BASE_URL: ${{ vars.STAGING_URL }}
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

## 测试报告模板 (Test Report Template)

```markdown
# E2E 测试报告 (E2E Test Report)

**日期 (Date):** YYYY-MM-DD HH:MM
**耗时 (Duration):** Xm Ys
**状态 (Status):** 通过 (PASSING) / 失败 (FAILING)

## 摘要 (Summary)
- 总计: X | 通过: Y (Z%) | 失败: A | 不稳定 (Flaky): B | 跳过: C

## 失败的测试 (Failed Tests)

### test-name
**文件 (File):** `tests/e2e/feature.spec.ts:45`
**错误 (Error):** 期望元素可见
**截图 (Screenshot):** artifacts/failed.png
**建议修复 (Recommended Fix):** [描述内容]

## 产物 (Artifacts)
- HTML 报告: playwright-report/index.html
- 截图: artifacts/*.png
- 视频: artifacts/videos/*.webm
- 追踪 (Traces): artifacts/*.zip
```

## 钱包 / Web3 测试 (Wallet / Web3 Testing)

```typescript
test('wallet connection', async ({ page, context }) => {
  // 模拟钱包提供者 (Mock wallet provider)
  await context.addInitScript(() => {
    window.ethereum = {
      isMetaMask: true,
      request: async ({ method }) => {
        if (method === 'eth_requestAccounts')
          return ['0x1234567890123456789012345678901234567890']
        if (method === 'eth_chainId') return '0x1'
      }
    }
  })

  await page.goto('/')
  await page.locator('[data-testid="connect-wallet"]').click()
  await expect(page.locator('[data-testid="wallet-address"]')).toContainText('0x1234')
})
```

## 金融 / 关键流程测试 (Financial / Critical Flow Testing)

```typescript
test('trade execution', async ({ page }) => {
  // 在生产环境跳过 —— 涉及真金白银
  test.skip(process.env.NODE_ENV === 'production', '生产环境跳过')

  await page.goto('/markets/test-market')
  await page.locator('[data-testid="position-yes"]').click()
  await page.locator('[data-testid="trade-amount"]').fill('1.0')

  // 验证预览 (Verify preview)
  const preview = page.locator('[data-testid="trade-preview"]')
  await expect(preview).toContainText('1.0')

  // 确认并等待区块链处理
  await page.locator('[data-testid="confirm-trade"]').click()
  await page.waitForResponse(
    resp => resp.url().includes('/api/trade') && resp.status() === 200,
    { timeout: 30000 }
  )

  await expect(page.locator('[data-testid="trade-success"]')).toBeVisible()
})
