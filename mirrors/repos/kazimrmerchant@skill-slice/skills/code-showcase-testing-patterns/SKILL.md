---
name: code-showcase-testing-patterns
description: "Applies Jest and Testing Library patterns for React and React Native: getMockX factories, jest.mock GraphQL hooks, renderWithTheme providers, and red-green-refactor TDD. Trigger when writing unit tests, test factories, or module mocks. Do not use for Playwright or Cypress E2E, GitHub Actions workflow YAML, or shipping production features without a failing test first."
version: 1.0.1
risk: unknown
source: https://github.com/ChrisWiles/claude-code-showcase/tree/main/.claude/skills/testing-patterns
source_repo: ChrisWiles/claude-code-showcase
source_type: community
date_added: 2026-07-01
license: MIT
license_source: https://github.com/ChrisWiles/claude-code-showcase/blob/main/LICENSE
---

# Testing Patterns and Utilities

## Overview

This skill provides a comprehensive set of Jest testing patterns for React and React Native projects, including factory functions for test data, module and GraphQL hook mocking strategies, custom render utilities, and a structured TDD workflow. It is framework-agnostic in principle but uses `@testing-library/react-native` and Jest as the concrete toolchain.

## When to Use

Use this skill when any of the following apply:

- You are writing or refactoring unit tests with Jest.
- You need to create test factories for component props or domain data.
- You are mocking modules, GraphQL hooks, or external dependencies.
- You are following the TDD red-green-refactor cycle and need a structured workflow.
- You need a custom render function to wrap components with required providers (e.g., ThemeProvider).
- You are organizing test suites with `describe` blocks and need a consistent structure.

Trigger keywords: `jest`, `unit test`, `test factory`, `mock`, `TDD`, `red-green-refactor`, `testing-library`, `renderWithTheme`, `getMockUser`, `factory function`.

## Prerequisites

- Node.js and a package manager (`npm` or `yarn`) installed on your system.
- Jest and `@testing-library/react-native` (or `@testing-library/react` for web projects) installed in the project.
- TypeScript configured if using type-safe factories (recommended but not required).
- Windows host is primary; commands below use PowerShell syntax. On macOS/Linux, adapt path separators and line-continuation characters as needed.

## Procedure

### 1. Follow the TDD Red-Green-Refactor Cycle

1. **Red** — Write a failing test that describes the desired behavior. Run it and confirm it fails for the right reason.
2. **Green** — Implement the minimal production code to make the test pass.
3. **Refactor** — Clean up the implementation while keeping the test green. Never refactor without a passing test.

Core rules:

- Never write production code without a failing test.
- Test behavior, not implementation. Focus on public APIs and business requirements.
- Avoid testing implementation details (private methods, internal state).
- Use descriptive test names that describe observable behavior.

### 2. Create a Custom Render Function

Wrap components with required providers so every test gets consistent context.

```typescript
// src/utils/testUtils.tsx
import { render } from '@testing-library/react-native';
import { ThemeProvider } from './theme';

export const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider>{ui}</ThemeProvider>
  );
};
```

Usage in a test:

```typescript
import { renderWithTheme } from 'utils/testUtils';
import { screen } from '@testing-library/react-native';

it('should render component', () => {
  renderWithTheme(<MyComponent />);
  expect(screen.getByText('Hello')).toBeTruthy();
});
```

### 3. Create Factory Functions for Test Data

Factories provide sensible defaults and allow per-test overrides, keeping tests DRY and consistent.

**Component Props Factory:**

```typescript
import { ComponentProps } from 'react';

const getMockMyComponentProps = (
  overrides?: Partial<ComponentProps<typeof MyComponent>>
) => {
  return {
    title: 'Default Title',
    count: 0,
    onPress: jest.fn(),
    isLoading: false,
    ...overrides,
  };
};

// Usage in tests
it('should render with custom title', () => {
  const props = getMockMyComponentProps({ title: 'Custom Title' });
  renderWithTheme(<MyComponent {...props} />);
  expect(screen.getByText('Custom Title')).toBeTruthy();
});
```

**Data Factory:**

```typescript
interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
}

const getMockUser = (overrides?: Partial<User>): User => {
  return {
    id: '123',
    name: 'John Doe',
    email: 'john@example.com',
    role: 'user',
    ...overrides,
  };
};

// Usage
it('should display admin badge for admin users', () => {
  const user = getMockUser({ role: 'admin' });
  renderWithTheme(<UserCard user={user} />);
  expect(screen.getByText('Admin')).toBeTruthy();
});
```

### 4. Mock Modules and GraphQL Hooks

**Mock an entire module:**

```typescript
// Mock entire module
jest.mock('utils/analytics');

// Mock with factory function
jest.mock('utils/analytics', () => ({
  Analytics: {
    logEvent: jest.fn(),
  },
}));

// Access mock in test
const mockLogEvent = jest.requireMock('utils/analytics').Analytics.logEvent;
```

**Mock a generated GraphQL hook:**

```typescript
jest.mock('./GetItems.generated', () => ({
  useGetItemsQuery: jest.fn(),
}));

const mockUseGetItemsQuery = jest.requireMock(
  './GetItems.generated'
).useGetItemsQuery as jest.Mock;

// In test
mockUseGetItemsQuery.mockReturnValue({
  data: { items: [] },
  loading: false,
  error: undefined,
});
```

### 5. Structure Test Suites with Describe Blocks

Organize tests by rendering, user interactions, and edge cases:

```typescript
describe('ComponentName', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render component with default props', () => {});
    it('should render loading state when loading', () => {});
  });

  describe('User interactions', () => {
    it('should call onPress when button is clicked', async () => {});
  });

  describe('Edge cases', () => {
    it('should handle empty data gracefully', () => {});
  });
});
```

### 6. Use Correct Query Patterns

```typescript
// Element must exist — throws if not found
expect(screen.getByText('Hello')).toBeTruthy();

// Element should not exist — returns null, does not throw
expect(screen.queryByText('Goodbye')).toBeNull();

// Element appears asynchronously — retries until timeout
await waitFor(() => {
  expect(screen.findByText('Loaded')).toBeTruthy();
});
```

### 7. Simulate User Interactions

```typescript
import { fireEvent, screen } from '@testing-library/react-native';

it('should submit form on button click', async () => {
  const onSubmit = jest.fn();
  renderWithTheme(<LoginForm onSubmit={onSubmit} />);

  fireEvent.changeText(screen.getByLabelText('Email'), 'user@example.com');
  fireEvent.changeText(screen.getByLabelText('Password'), 'password123');
  fireEvent.press(screen.getByTestId('login-button'));

  await waitFor(() => {
    expect(onSubmit).toHaveBeenCalled();
  });
});
```

### 8. Run Tests

On Windows (PowerShell):

```powershell
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run a specific file
npm test ComponentName.test.tsx
```

## Examples

### Complete Test File Using All Patterns

```typescript
import { renderWithTheme } from 'utils/testUtils';
import { fireEvent, screen, waitFor } from '@testing-library/react-native';
import { UserCard } from './UserCard';
import { getMockUser } from './__mocks__/userFactory';

jest.mock('./GetUser.generated', () => ({
  useGetUserQuery: jest.fn(),
}));

const mockUseGetUserQuery = jest.requireMock('./GetUser.generated').useGetUserQuery as jest.Mock;

describe('UserCard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render user name', () => {
      mockUseGetUserQuery.mockReturnValue({
        data: { user: getMockUser({ name: 'Alice' }) },
        loading: false,
        error: undefined,
      });
      renderWithTheme(<UserCard userId="123" />);
      expect(screen.getByText('Alice')).toBeTruthy();
    });

    it('should render loading state', () => {
      mockUseGetUserQuery.mockReturnValue({ data: undefined, loading: true, error: undefined });
      renderWithTheme(<UserCard userId="123" />);
      expect(screen.getByTestId('loading-spinner')).toBeTruthy();
    });
  });

  describe('Edge cases', () => {
    it('should handle empty data gracefully', () => {
      mockUseGetUserQuery.mockReturnValue({ data: null, loading: false, error: undefined });
      renderWithTheme(<UserCard userId="123" />);
      expect(screen.queryByText('Alice')).toBeNull();
    });
  });
});
```

## Pitfalls

1. **Testing mock behavior instead of real behavior.** Asserting that a mock was called is sometimes necessary, but the primary assertion should verify observable output (rendered text, state changes, etc.).

   ```typescript
   // Bad — only checks the mock
   expect(mockFetchData).toHaveBeenCalled();

   // Good — checks actual behavior
   expect(screen.getByText('John Doe')).toBeTruthy();
   ```

2. **Not using factories.** Inline test data leads to duplication and inconsistency (e.g., a `role` field silently missing in one test). Always use `getMockX(overrides)` factories.

3. **Using `getBy*` for elements that may not exist.** `getByText` throws if the element is not found. Use `queryByText` when asserting absence, and `findByText` (with `await`) for async elements.

4. **Forgetting `jest.clearAllMocks()` in `beforeEach`.** Mock call counts and return values leak between tests, causing flaky or false-positive results.

5. **Testing implementation details.** Testing private methods or internal component state makes tests brittle. Refactoring production code then breaks tests even though behavior is unchanged.

6. **Over-mocking.** Mocking too many modules can make tests pass while the real integration is broken. Mock only external boundaries (network, storage, analytics, generated code).

7. **Skipping the "Red" phase.** If a test passes before you write the implementation, it is either redundant or not testing the right thing. Always confirm the test fails first.

## Verification

Confirm your test setup and patterns are working correctly:

1. **Verify Jest is installed and configured:**

   ```powershell
   npx jest --version
   ```

   Expected output: a version number (e.g., `29.x.x`).

2. **Run the full test suite and confirm it passes:**

   ```powershell
   npm test
   ```

   Expected: all suites pass with `0 failures`.

3. **Run a single test file to isolate failures:**

   ```powershell
   npm test ComponentName.test.tsx
   ```

4. **Verify coverage is collected:**

   ```powershell
   npm run test:coverage
   ```

   Expected: a coverage table is printed showing file, statement, branch, and function percentages.

5. **Verify a factory produces correct defaults and overrides:**

   ```typescript
   const user = getMockUser({ role: 'admin' });
   expect(user.id).toBe('123');       // default preserved
   expect(user.role).toBe('admin');   // override applied
   ```

6. **Verify mocks are cleared between tests:**

   ```typescript
   beforeEach(() => {
     jest.clearAllMocks();
   });

   it('call count starts at zero', () => {
     const fn = jest.fn();
     // In the next test, fn.mock.calls should be empty
   });
   ```

## Related Skills

- **react-ui-patterns** — Test all UI states: loading, error, empty, and success. Pair with this skill to ensure every visual state has coverage.
- **systematic-debugging** — Write a test that reproduces a bug before fixing it. This skill provides the factory and mocking patterns to construct the failing scenario.

## Limitations

- Use this skill only when the task clearly matches its upstream source and local project context.
- Verify commands, generated code, dependencies, credentials, and external service behavior before applying changes.
- Do not treat examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
- Examples assume `@testing-library/react-native`; for web projects using `@testing-library/react`, replace `fireEvent.press` with `fireEvent.click` and `changeText` with `change` as appropriate.
