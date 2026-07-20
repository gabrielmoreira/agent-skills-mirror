# Frontend Test Implementation (React/TypeScript)

## Project Toolchain Resolution

Before writing a test, inspect the package scripts, runner configuration, setup files, existing neighboring tests, DOM/browser environment, and network handlers. Preserve the repository's runner, imports, mock API, setup lifecycle, file naming, and test location.

- Use React Testing Library when it is the project's component-test renderer; prefer `userEvent` over `fireEvent` for user interactions
- Use the repository's existing network mocking layer for API behavior. When MSW is configured, extend its handlers instead of introducing runner-level fetch mocks
- When Vitest is configured, use its existing import convention and `vi` APIs. When Jest or another runner is configured, use that runner's established equivalents
- When multiple approaches coexist, follow the dominant convention in the changed feature area. If no representative convention exists and adding or replacing tooling is outside the approved work, stop and report the missing test-environment decision

### Vitest Mapping (only when Vitest is configured)

- Test imports: `import { describe, it, expect, beforeEach, vi } from 'vitest'`, unless globals are enabled by the existing config
- Mock creation: use `vi.fn()` and `vi.mock()` following the project's setup and reset conventions

### Jest or Other Runner Mapping

Keep the runner's existing imports or globals, mock factory, module-mocking mechanism, fake-timer behavior, and setup/teardown conventions. Translate the behavior expressed by a skeleton; do not copy Vitest-specific APIs into a different runner.

## Basic Testing Policy

### Quality Requirements
- **Coverage**: prioritize meaningful assertions on critical paths and high-reuse components; treat coverage as a signal for gaps, not a target. Any threshold is the project's CI config
- **Independence**: Each test can run independently without depending on other tests
- **Reproducibility**: Tests are environment-independent and always return the same results
- **Readability**: Test code maintains the same quality as production code

### Where to concentrate test rigor
Test foundational, high-reuse units the hardest — shared components, custom hooks, and utils reused across many features carry the widest blast radius. Higher-composition surfaces (organisms, pages) lean on integration/E2E coverage instead. Any numeric threshold is the project's CI config.

### Test Types and Scope
1. **Unit Tests (React Testing Library)**
   - Verify behavior of individual components or functions
   - Mock all external dependencies
   - Most numerous, implemented with fine granularity
   - Focus on user-observable behavior

2. **Integration Tests (React Testing Library + the project network layer)**
   - Verify coordination between multiple components
   - Mock APIs with the repository's configured network layer (MSW when present)
   - No actual DB connections (backend manages DB)
   - Verify major functional flows

## Red-Green-Refactor Process (Test-First Development)

**Recommended Principle**: Start new or changed behavior and reproducible bug fixes with a failing test. For behavior-preserving refactors, establish passing regression evidence before changing code

**Background**:
- Ensure behavior before changes, prevent regression
- Clarify expected behavior before implementation
- Ensure safety during refactoring

**Development Steps**:
- **New/changed behavior or reproducible bug**: Red (write and confirm a failing test) → Green (minimal implementation) → Refactor
- **Behavior-preserving refactor**: Baseline (confirm existing tests pass or add passing characterization tests) → Refactor → Verify the same evidence

**NG Cases (Test-first not required)**:
- Configuration changes that affect neither runtime nor build behavior; otherwise begin with a failing validator or test check
- Documentation-only updates (README, comments, etc.)
- Emergency production incident response; afterward add a regression test when reproducible, otherwise record the reproduction blocker and static, contract, or environment evidence

## Test Design Principles

### Test Case Structure
- Tests consist of three stages: "Arrange," "Act," "Assert"
- Clear naming that shows purpose of each test
- One test case verifies only one behavior

### Test Data Management
- Manage test data in dedicated directories or co-located with tests
- Define test-specific environment variable values
- Always mock sensitive information
- Keep test data minimal, using only data directly related to test case verification purposes

### Mock and Stub Usage Policy

**Recommended: Mock external dependencies in unit tests**
- Merit: Ensures test independence and reproducibility
- Practice: Use the configured network layer for API calls and the configured runner's mock API for external libraries

For network behavior, prefer the repository's network-level mock layer over mocking implementation modules. Use MSW when configured; keep direct module mocks for non-network external I/O or when that is the established project convention.

### Test Failure Response Decision Criteria

**Fix tests**: Wrong expected values, references to non-existent features, dependence on implementation details, implementation only for tests
**Fix implementation**: Valid specifications, business logic, important edge cases
**When in doubt**: Confirm with user

## Test Helper Utilization Rules

### Decision Criteria
| Mock Characteristics | Response Policy |
|---------------------|-----------------|
| **Simple and stable** | Keep local until reuse or a named readability/contract benefit justifies a helper |
| **Complex or frequently changing** | Individual implementation |
| **Duplicated in 3+ places** | Consider consolidation |
| **Test-specific logic** | Individual implementation |

### Test Helper Usage Examples
```typescript
// Builder pattern for test data
const testUser = createTestUser({ name: 'Test User', email: 'test@example.com' })

// Custom render function with providers
function renderWithProviders(ui: React.ReactElement) {
  return render(<TestProvider>{ui}</TestProvider>)
}
```

## Test Implementation Conventions

### Directory Structure (Co-location Principle)

Preserve the repository location discovered in Project Toolchain Resolution. When the approved work establishes a new component-test convention and no representative layout exists, use this co-located default:

```
src/
└── components/
    └── Button/
        ├── Button.tsx
        ├── Button.test.tsx  # Co-located with component
        └── index.ts
```

### Naming Conventions
- Test files: preserve the repository pattern; for an approved new convention, default to `{ComponentName}.test.tsx`
- Integration test files: preserve the repository pattern; for an approved new convention, default to `{FeatureName}.integration.test.tsx`
- Test suites: Names describing target components or features
- Test cases: Names describing expected behavior from user perspective

### Test Code Quality Rules

**Keep all tests always active**
- Fix problematic tests and activate them

**Keep all tests executable**: Fix failing tests or delete tests that no longer apply. Remove any `test.skip()` before commit.

## Test Granularity Principles

### Core Principle: User-Observable Behavior Only
**Test only**: Rendered output, user interactions, accessibility, error states

```typescript
// Test user-observable behavior
expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument()

// NOT implementation details
expect(component.state.count).toBe(0)
```

## Test Quality Criteria

### Literal Expected Values
Use hardcoded literal values by default so the implementation cannot calculate its own oracle. A property, approved snapshot, or fixture-derived expectation may replace a literal only when it is independently derived and makes the intended behavior more explicit.
```typescript
expect(formatPrice(1000)).toBe('¥1,000')
expect(calculateTax(100)).toBe(10)
expect(user.role).toBe('admin')
```

### Result-Based Verification
Verify final results and outcomes.
```typescript
expect(mockOnSubmit).toHaveBeenCalledWith({ name: 'test' })
expect(result).toEqual({ id: '1', status: 'success' })
expect(screen.getByText('Submitted')).toBeInTheDocument()
```

### Meaningful Assertions
Every test must include at least one `expect()` that validates observable behavior.

### Appropriate Mock Scope (Vitest example)
Mock only direct external I/O dependencies. Internal utilities should use real implementations.
With another runner, apply the same boundary using its established module-mocking API.
```typescript
vi.mock('./api/userApi')  // External API - mock
vi.mock('./lib/database') // External I/O - mock
// Internal utils like validators/formatters - use real implementations
```

## Mock Type Safety Enforcement

### MSW Setup (only when MSW is configured)
```typescript
import { http, HttpResponse } from 'msw'

const handlers = [
  http.get('/api/users/:id', () => {
    return HttpResponse.json({ id: '1', name: 'John' } satisfies User)
  })
]
```

### Component Mock Type Safety (Vitest example)
```typescript
type TestProps = Pick<ButtonProps, 'label' | 'onClick'>
const mockProps: TestProps = { label: 'Click', onClick: vi.fn() }
```

## Continuity Test Scope

Limited to verifying existing feature impact when adding new features. Long-term operations and performance testing are infrastructure responsibilities, not test scope.

## Basic React Testing Library Example (Vitest)

Use this mapping only when Vitest is the configured runner. With another runner, preserve the same user-observable assertions while using that runner's imports and mock API.

```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'

describe('Button', () => {
  it('should call onClick when clicked', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()
    render(<Button label="Click me" onClick={onClick} />)
    await user.click(screen.getByRole('button', { name: 'Click me' }))
    expect(onClick).toHaveBeenCalledOnce()
  })
})
```
