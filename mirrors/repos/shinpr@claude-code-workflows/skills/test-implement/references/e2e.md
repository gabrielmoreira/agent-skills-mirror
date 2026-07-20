# E2E Test Implementation

## Browser Harness Resolution

1. Inspect the repository's E2E scripts, configuration, imports, fixtures, support files, and neighboring tests.
2. When a browser harness already exists, preserve its runner, directory layout, locator/query conventions, network interception, fixtures, retries, and reporting. Translate the lane rules below into that harness.
3. When no harness exists and the approved Work Plan includes E2E harness setup, use Playwright as this workflow's default and apply the Playwright-specific patterns in this reference.
4. When no harness exists and setup is not approved, stop and report the missing environment decision instead of adding a dependency implicitly.

## Lane Selection

E2E tests in this workflow split into two lanes:

| Lane | Backend setup | Use these patterns |
|------|---------------|-------------------|
| **fixture-e2e** | Mocked via the harness's route interception or fixture loaders; no live services | Reusable screen/page helpers, accessible locator strategy, assertions, the **Fixture-Based Backend** section below |
| **service-integration-e2e** | Live local stack with real services | All patterns above PLUS the **E2E Environment Prerequisites** section (seed data, auth fixture against real auth flow) |

The skeleton's `@lane:` annotation declares which lane the test belongs to. Choose implementation patterns to match.

## Playwright Mapping (when Playwright is configured or approved)

- **Playwright Test**: `@playwright/test`
- Test imports: `import { test, expect } from '@playwright/test'`

## Playwright Test Structure

### Directory Layout

Preserve the existing harness layout resolved above. Use this layout only when the approved work establishes a new Playwright harness and the repository has no convention:

```
tests/
└── e2e/
    ├── pages/                   # Page objects (shared across lanes)
    │   ├── login.page.ts
    │   └── dashboard.page.ts
    ├── fixtures/                # Test fixtures (auth, seed)
    │   └── auth.fixture.ts
    ├── data/                    # Static fixture data for fixture-e2e
    │   └── *.fixture.json
    ├── *.fixture.e2e.test.ts    # fixture-e2e test files
    └── *.service.e2e.test.ts    # service-integration-e2e test files
```

### Naming Conventions
- Preserve existing harness naming. For an approved new Playwright harness, default to:
  - fixture-e2e files: `{FeatureName}.fixture.e2e.test.ts`
  - service-integration-e2e files: `{FeatureName}.service.e2e.test.ts`
  - Page objects: `{PageName}.page.ts`
  - Fixtures: `{Purpose}.fixture.ts`
  - Static fixture data: `{scenario}.fixture.json`

## Page Object Pattern

Use the repository's existing browser abstraction. When establishing new Playwright tests, introduce a page object when one page/workflow interaction is reused across 3+ tests or a coherent interaction sequence would otherwise be duplicated. Keep direct accessible locators in a small test when an object would only add indirection.

```typescript
import { type Page, type Locator } from '@playwright/test'

export class LoginPage {
  readonly emailInput: Locator
  readonly passwordInput: Locator
  readonly submitButton: Locator

  constructor(private page: Page) {
    this.emailInput = page.getByLabel('Email')
    this.passwordInput = page.getByLabel('Password')
    this.submitButton = page.getByRole('button', { name: 'Sign in' })
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email)
    await this.passwordInput.fill(password)
    await this.submitButton.click()
  }
}
```

## Test Patterns

### Basic Test
```typescript
import { test, expect } from '@playwright/test'

test('user can navigate to dashboard after login', async ({ page }) => {
  // Arrange
  await page.goto('/login')

  // Act
  await page.getByLabel('Email').fill('user@example.com')
  await page.getByLabel('Password').fill('password')
  await page.getByRole('button', { name: 'Sign in' }).click()

  // Assert
  await expect(page).toHaveURL('/dashboard')
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
})
```

### With Page Objects
```typescript
import { test, expect } from '@playwright/test'
import { LoginPage } from './pages/login.page'
import { DashboardPage } from './pages/dashboard.page'

test('user completes purchase flow', async ({ page }) => {
  const loginPage = new LoginPage(page)
  const dashboardPage = new DashboardPage(page)

  await page.goto('/login')
  await loginPage.login('user@example.com', 'password')
  await expect(dashboardPage.heading).toBeVisible()
})
```

### Auth Fixture
```typescript
import { test as base } from '@playwright/test'

export const test = base.extend<{ authenticatedPage: Page }>({
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login')
    await page.getByLabel('Email').fill('user@example.com')
    await page.getByLabel('Password').fill('password')
    await page.getByRole('button', { name: 'Sign in' }).click()
    await page.waitForURL('/dashboard')
    await use(page)
  },
})
```

## Fixture-Based Backend (fixture-e2e)

fixture-e2e tests run a real browser against deterministic fixtures — no live backend, no DB, no external services. Use one of these patterns to fake the network:

### Pattern A: Browser-harness route interception (`page.route()` in Playwright)

```typescript
test('Dismiss-then-Undo restores card', async ({ page }) => {
  // Arrange: intercept all backend calls with deterministic responses
  await page.route('**/api/cards', async (route) => {
    await route.fulfill({ json: cardsFixture })
  })
  await page.route('**/api/cards/*/dismiss', async (route) => {
    await route.fulfill({ status: 204 })
  })

  await page.goto('/cards')
  await page.getByRole('button', { name: 'Dismiss' }).first().click()
  await page.getByRole('button', { name: 'Undo' }).click()

  await expect(page.getByText(cardsFixture[0].title)).toBeVisible()
})
```

### Pattern B: Fixture loader injection

```typescript
// data/cards-with-dismiss.fixture.json — committed alongside the test
// Loaded via a route helper or app-level test mode
```

**Principles for fixture-e2e**:
- Backend is faked, not running. No `npm run start:backend` required to execute these tests
- Fixtures are versioned in the repo (`tests/e2e/data/`) so tests are deterministic across machines
- Auth, when needed, is faked too (set a test cookie via `page.context().addCookies()` or use a fixture-mode bypass)
- These tests run in CI without provisioning external infrastructure

## E2E Environment Prerequisites (service-integration-e2e)

service-integration-e2e tests require a running application with real data state. Unlike fixture-e2e, environment setup is part of test implementation scope.

### Seed Data Strategy

Prepare test data via API calls or database seeding:

```typescript
// fixtures/seed.fixture.ts
import { test as base } from '@playwright/test'

export const test = base.extend<{ seededData: SeedResult }>({
  seededData: async ({ request }, use) => {
    // Arrange: Create test data via API before test
    // Example: adjust to the project's actual seeding mechanism
    const result = await request.post('/api/test/seed', {
      data: { scenario: 'e2e-user-with-subscription' }
    })
    const seedData = await result.json()

    await use(seedData)

    // Cleanup: Remove test data after test
    await request.delete(`/api/test/seed/${seedData.id}`)
  },
})
```

**Principles**:
- Use the application's existing deterministic seeding mechanism if present (for example a fixture loader, CLI, API, or database seeder); create a new seed interface only when the approved design requires it
- Seed data setup belongs to test fixtures, not to a separate manual step
- Each test must be self-contained: create its own data, clean up after
- Keep seeding within the repository's supported test boundary; do not bypass production invariants unless the test environment explicitly defines that mechanism

### Authentication Fixture

Implement auth fixtures that match the application's actual login flow:

```typescript
// fixtures/auth.fixture.ts
export const test = base.extend<{ playerPage: Page }>({
  playerPage: async ({ page, request }, use) => {
    // Use the application's existing auth endpoint — not admin backdoors
    // Example: adjust the URL and payload to match the project's actual login flow
    await request.post('/api/login', {
      data: { loginId: E2E_LOGIN_ID, password: E2E_PASSWORD }
    })
    // Transfer session to browser context
    await page.goto('/')
    await use(page)
  },
})
```

**Principles**:
- Use the application's real authentication contract in an isolated test or local environment; fixtures should exercise the same endpoints and session behavior as real users unless the fixture-e2e lane intentionally supplies a documented auth double
- Never run E2E fixtures against the production environment or production credentials
- Store test credentials in environment variables only (`E2E_*` prefixed)
- If the auth flow requires specific user records, seed them in the fixture

### Environment Checklist (service-integration-e2e only)

Before service-integration-e2e tests can pass, verify:
- [ ] Application is running and accessible at `baseURL`
- [ ] Database has required seed data (test users, subscriptions, content)
- [ ] Authentication flow works with test credentials
- [ ] Environment variables are set (`E2E_*` prefixed)
- [ ] External services are either available or stubbed

When the work plan includes dedicated environment setup tasks, follow those tasks. When a required prerequisite is missing from both the repository and approved plan, stop and report the exact missing environment decision instead of expanding scope implicitly. Move verification to fixture-e2e only when the same proof obligation can be established without the real service; record that lane change in the task/work-plan evidence.

## Locator Strategy

Prefer accessible locators in this order:
1. `page.getByRole()` — best for accessibility
2. `page.getByLabel()` — form elements
3. `page.getByText()` — visible text
4. `page.getByTestId()` — last resort

```typescript
await page.getByRole('button', { name: 'Submit' }).click()
```

## Assertions

```typescript
// Visibility
await expect(page.getByText('Success')).toBeVisible()
await expect(page.getByText('Error')).not.toBeVisible()

// Navigation
await expect(page).toHaveURL('/dashboard')
await expect(page).toHaveTitle('Dashboard')

// Element state
await expect(page.getByRole('button')).toBeEnabled()
await expect(page.getByRole('button')).toBeDisabled()

// Content
await expect(page.getByRole('heading')).toHaveText('Welcome')
```

## Viewport Testing

When UI Spec defines responsive behavior:

```typescript
test.describe('responsive navigation', () => {
  test('shows hamburger menu on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')
    await expect(page.getByRole('button', { name: 'Menu' })).toBeVisible()
    await expect(page.getByRole('navigation')).not.toBeVisible()
  })

  test('shows full navigation on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 })
    await page.goto('/')
    await expect(page.getByRole('navigation')).toBeVisible()
  })
})
```

## Test Isolation

- Each test starts from a clean browser context
- No shared state between tests
- Use `beforeEach` for common setup (auth, navigation)
- Prefer `page.goto()` over in-test navigation for setup steps

## Skeleton Comment Format

E2E test skeletons follow the same annotation format as integration tests (adapt comment syntax to the project's language). The `@lane` annotation routes the test to the correct implementation patterns.

### fixture-e2e example
```typescript
// AC: [Original acceptance criteria text]
// Behavior: [User action] → [System response] → [Observable result in browser]
// @category: fixture-e2e
// @lane: fixture-e2e
// @dependency: full-ui (mocked backend)
// @complexity: medium
// ROI: [score]
test('AC1: [Description]', async ({ page }) => {
  // Arrange: load fixture data, intercept network
  // Act: user interaction
  // Assert: observable browser state
})
```

### service-integration-e2e example
```typescript
// AC: [Original acceptance criteria text]
// Behavior: [User action] → [System response across services] → [Observable cross-service result]
// @category: service-integration-e2e
// @lane: service-integration-e2e
// @dependency: full-system
// @complexity: high
// ROI: [score]
test('AC1: [Description]', async ({ page, request }) => {
  // Arrange: seed real data, real auth
  // Act: user interaction
  // Assert: observable result + cross-service evidence (DB row, downstream event)
})
```
