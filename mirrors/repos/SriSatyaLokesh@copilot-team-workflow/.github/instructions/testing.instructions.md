---
applyTo: "**/*.test.ts,**/*.spec.ts,tests/**,__tests__/**"
---
# Testing Standards

## Test Types & Locations
- **Unit tests**: Co-located with source (`src/foo/bar.test.ts`)
- **Integration tests**: `tests/integration/[resource].test.ts`
- **E2E tests**: `tests/e2e/[flow].spec.ts` (Playwright)

## Test Structure
- Use `describe` blocks to group related scenarios
- Use `it` or `test` with a descriptive name: `'returns 404 when user not found'`
- Follow AAA pattern: Arrange → Act → Assert
- One assertion concern per test (multiple `expect` calls are okay if testing one thing)

## Mocking Strategy
- Mock all external services (DB, Redis, email, etc.) in unit tests
- No real network calls in unit or integration tests
- Use `vi.mock()` for module mocking (Vitest)
- Mock at the boundary: mock the repository in service tests, not the DB itself

## Coverage Requirements
- Business logic (services): 80% minimum
- Utility functions: 90% minimum
- Route handlers: happy path + common error paths

## Test Data
- Use factory functions for creating test data, not hard-coded objects
- Keep test data in `tests/fixtures/` or `tests/factories/`
- Use realistic-looking data (not "foo", "bar", "test123")

## Assertions
- Prefer specific assertions: `.toBe(404)` over `.toBeTruthy()`
- For objects: use `.toMatchObject()` for partial matching
- For arrays: check length AND content, not just length

## Running Tests
```bash
npm test                    # Run all tests
npm test -- --watch        # Watch mode
npm test -- src/services   # Run specific directory
npm run test:e2e            # Run Playwright tests
npm run test:coverage       # Generate coverage report
```
