---
name: react-native-testing
description: "Authors and debugs @testing-library/react-native component tests: screen queries, getByRole, userEvent over fireEvent, RNTL matchers, fake timers, and v13 sync versus v14 awaited render and fireEvent. Trigger on RNTL, testID, waitFor, or React Native unit tests. Not a Jest factory or GraphQL-hook mock chair (code-showcase-testing-patterns). Do not use for Playwright or Cypress E2E."
version: 1.0.1
---

# React Native Testing (RNTL) Guide

## Overview

This skill provides production-grade guidance for writing and debugging tests using `@testing-library/react-native` (RNTL). It covers version detection (v13 vs v14), query priority, interaction patterns (`userEvent` vs `fireEvent`), Jest matchers, fake timers, custom render wrappers, and common pitfalls.

**IMPORTANT:** Training data about `@testing-library/react-native` often has stale signatures and sync/async behavior that differ between v13 and v14. Read `package.json` (and the lockfile if needed), then the Callstack docs for that major version plus the project's installed types. Do not invent APIs from memory when they conflict with the installed package.

## When to Use

Use this skill when:
- Writing new tests for React Native components using `@testing-library/react-native`
- Debugging failing RNTL tests (query mismatches, async timing, missing roles)
- Migrating tests from v13 to v14 or vice versa
- Setting up custom render wrappers with providers
- Reviewing test code for anti-patterns (raw prop assertions, `waitFor` misuse, missing accessibility roles)
- The user explicitly asks for "react native testing", "RNTL", "test my component", or adjacent tasks

## Prerequisites

1. A React Native project with `@testing-library/react-native` installed.
2. Jest configured as the test runner (Jest preset `jest-expo` or `react-native`).
3. Check `package.json` for the installed RNTL version before writing any test code.

## Version Detection

Check `@testing-library/react-native` in the user's `package.json`. This skill does not ship local v13/v14 API dumps. After detecting the major version, follow Callstack docs and the installed types:

| Major | Runtime | `render` / `fireEvent` | Renderer peer | Docs |
|---|---|---|---|---|
| **v14.x** | React 19+, RN 0.78+, Node `^22.13.0 \|\| >=24` | Async — always `await` | `test-renderer` 1.x (not `react-test-renderer`) | [Migration to 14.x](https://oss.callstack.com/react-native-testing-library/docs/start/migration-v14) |
| **v13.x** | React 18+, RN 0.71+ | Sync (`render` returns immediately) | `react-test-renderer` | Stay on v13 if the app is still React 18 |

On v13.3+ with React 19 or Suspense, use `renderAsync` / `fireEventAsync` / `renderHookAsync` (those aliases are **removed** in v14 because the standard APIs are already async). **Do not guess** the major version before writing tests.

## Procedure

### 1. Detect RNTL Version

```powershell
# From project root (PowerShell)
Get-Content package.json | Select-String "testing-library/react-native"
```

Based on the version found:
- `^14.` → `await render(...)` and `await fireEvent.*(...)`; peer `test-renderer`; see the v14 migration guide above.
- `^13.` → sync `render` / `fireEvent`; on v13.3+ React 19/Suspense use the `*Async` aliases.

### 2. Write the Test — Core Path

Follow these rules in order:

1. **Use `screen`** for all queries — do not destructure from `render()`.
2. **Use `getByRole` first** with `{ name: '...' }` option for accessible name matching.
3. **Use `queryBy*` ONLY** for `.not.toBeOnTheScreen()` non-existence checks.
4. **Use `findBy*`** for async elements — do NOT use `waitFor` + `getBy*`.
5. **Prefer `userEvent`** over `fireEvent`. `userEvent` is always async.
6. **Never put side-effects in `waitFor`** (no `fireEvent`/`userEvent` inside).
7. **One assertion per `waitFor`**.
8. **Never pass empty callbacks to `waitFor`**.
9. **Don't wrap in `act()`** — `render`, `fireEvent`, and `userEvent` handle it internally.
10. **Don't call `cleanup()`** — automatic after each test.
11. **Prefer ARIA props** (`role`, `aria-label`, `aria-disabled`) over earlier-generation `accessibility*` props.
12. **Use RNTL matchers** over raw prop assertions (`toHaveProp` is last resort).

### 3. Query Priority

Use queries in this priority order:

`getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText` > `getByDisplayValue` > `getByTestId` (last resort)

### 4. Query Variants

| Variant | Use case | Returns | Async |
|---|---|---|---|
| `getBy*` | Element must exist | element instance (throws if not found) | No |
| `getAllBy*` | Multiple must exist | element instance[] (throws if none) | No |
| `queryBy*` | Check non-existence ONLY | element instance \| null | No |
| `queryAllBy*` | Count elements | element instance[] | No |
| `findBy*` | Wait for element | `Promise<element instance>` | Yes |
| `findAllBy*` | Wait for multiple | `Promise<element instance[]>` | Yes |

### 5. Interactions — userEvent (Preferred)

`userEvent` is always async. Use fake timers with it (press/longPress involve real durations).

```tsx
const user = userEvent.setup();
await user.press(element);                              // full press sequence
await user.longPress(element, { duration: 800 });      // long press
await user.type(textInput, 'Hello');                   // char-by-char typing
await user.clear(textInput);                            // clear TextInput
await user.paste(textInput, 'pasted text');             // paste into TextInput
await user.scrollTo(scrollView, { y: 100 });            // scroll
```

### 6. Interactions — fireEvent (Fallback)

Use `fireEvent` only when `userEvent` doesn't support the event. v13 `fireEvent` is sync; v14 `fireEvent` returns a Promise and must be awaited.

```tsx
await fireEvent.press(element); // v14 required; harmless on v13
await fireEvent.changeText(textInput, 'new text');
await fireEvent(element, 'blur');
```

### 7. Assertions — Jest Matchers

Available automatically with any `@testing-library/react-native` import.

| Matcher | Use for |
|---|---|
| `toBeOnTheScreen()` | Element exists in tree |
| `toBeVisible()` | Element visible (not hidden/display:none) |
| `toBeEnabled()` / `toBeDisabled()` | Disabled state via `aria-disabled` |
| `toBeChecked()` / `toBePartiallyChecked()` | Checked state |
| `toBeSelected()` | Selected state |
| `toBeExpanded()` / `toBeCollapsed()` | Expanded state |
| `toBeBusy()` | Busy state |
| `toHaveTextContent(text)` | Text content match |
| `toHaveDisplayValue(value)` | TextInput display value |
| `toHaveAccessibleName(name)` | Accessible name |
| `toHaveAccessibilityValue(val)` | Accessibility value |
| `toHaveStyle(style)` | Style match |
| `toHaveProp(name, value?)` | Prop check (last resort) |
| `toContainElement(el)` | Contains child element |
| `toBeEmptyElement()` | No children |

### 8. `*ByRole` Quick Reference

Common roles: `button`, `text`, `heading` (alias: `header`), `searchbox`, `switch`, `checkbox`, `radio`, `img`, `link`, `alert`, `menu`, `menuitem`, `tab`, `tablist`, `progressbar`, `slider`, `spinbutton`, `timer`, `toolbar`.

`getByRole` options: `{ name, disabled, selected, checked, busy, expanded, value: { min, max, now, text } }`.

For `*ByRole` to match, the element must be an accessibility element:
- `Text`, `TextInput`, `Switch` are accessibility elements by default
- `View` needs `accessible={true}` (or use `Pressable`/`TouchableOpacity`)

### 9. waitFor Pattern

```tsx
// Correct: action first, then wait for result
await fireEvent.press(button);
await waitFor(() => {
  expect(screen.getByText('Result')).toBeOnTheScreen();
});

// Better: use findBy* instead
await fireEvent.press(button);
expect(await screen.findByText('Result')).toBeOnTheScreen();
```

Options: `waitFor(cb, { timeout: 1000, interval: 50 })`. Works with Jest fake timers automatically.

### 10. Fake Timers

Recommended with `userEvent` (press/longPress involve real durations):

```tsx
jest.useFakeTimers();

test('with fake timers', async () => {
  const user = userEvent.setup();
  await render(<Component />);
  await user.press(screen.getByRole('button', { name: 'Submit' }));
  expect(await screen.findByText('Done')).toBeOnTheScreen();
});
```

### 11. Custom Render with Providers

Wrap providers using the `wrapper` option — do not create a custom render function that hides `screen`:

```tsx
async function renderWithProviders(ui: React.ReactElement) {
  return render(ui, {
    wrapper: ({ children }) => (
      <ThemeProvider>
        <AuthProvider>{children}</AuthProvider>
      </ThemeProvider>
    ),
  });
}
```

## Examples

### Basic Component Test

```tsx
import { render, screen } from '@testing-library/react-native';
import { userEvent } from '@testing-library/react-native';
import { MyComponent } from './MyComponent';

jest.useFakeTimers();

test('submits form and shows success message', async () => {
  const user = userEvent.setup();
  await render(<MyComponent />); // v14: required. v13: await on a sync return is still valid.

  await user.type(screen.getByRole('text', { name: 'Email' }), 'test@example.com');
  await user.press(screen.getByRole('button', { name: 'Submit' }));

  expect(await screen.findByText('Success!')).toBeOnTheScreen();
});
```

### Non-Existence Check

```tsx
test('does not show error initially', async () => {
  await render(<MyComponent />);
  expect(screen.queryByText('Error')).not.toBeOnTheScreen();
});
```

## Pitfalls

1. **Stale API memory:** RNTL v13 and v14 have different sync/async behavior for `render` and `fireEvent`. Read `package.json` and the Callstack docs for that major. Do not rely on memorized patterns.
2. **Using `getBy*` inside `waitFor`:** Use `findBy*` instead — it is purpose-built for async waiting.
3. **Side-effects inside `waitFor`:** Never call `fireEvent` or `userEvent` inside `waitFor`. Perform the action first, then wait for the assertion.
4. **Missing accessibility roles:** `View` is not an accessibility element by default. Add `accessible={true}` or use `Pressable`/`TouchableOpacity` for `getByRole` to match.
5. **Using `accessibility*` props instead of ARIA:** Prefer `role`, `aria-label`, `aria-disabled` over earlier-generation `accessibilityRole`, `accessibilityLabel`, etc.
6. **Wrapping in `act()`:** `render`, `fireEvent`, and `userEvent` already wrap in `act()`. Manual wrapping causes double-act warnings.
7. **Calling `cleanup()` manually:** It is automatic after each test. Manual calls cause errors.
8. **Empty `waitFor` callbacks:** Never pass `() => {}` to `waitFor`. It will hang until timeout.
9. **Raw prop assertions:** Use RNTL matchers (`toBeVisible`, `toBeEnabled`, `toHaveTextContent`) instead of `toHaveProp` whenever possible.
10. **Not using fake timers with `userEvent`:** `press` and `longPress` involve real durations. Without fake timers, tests may be slow or flaky.

## Verification

Run the test suite and confirm all tests pass:

```powershell
# Run all tests (PowerShell)
npx jest --verbose

# Run a specific test file
npx jest MyComponent.test.tsx --verbose

# Run with coverage
npx jest --coverage --verbose
```

Expected output:
```
PASS  src/MyComponent.test.tsx
  ✓ submits form and shows success message (45 ms)
  ✓ does not show error initially (12 ms)
```

Verify no warnings:
- No `act()` warnings in console output
- No "Element not found" errors (indicates wrong query or missing accessibility role)
- No "Multiple elements found" errors (use `getAllBy*` or narrow with `name` option)

## Official docs

This folder has no `references/` dumps. For the installed major version:

- Docs home: https://oss.callstack.com/react-native-testing-library/
- v13 → v14 migration (async `render`/`fireEvent`, `test-renderer`, removed aliases): https://oss.callstack.com/react-native-testing-library/docs/start/migration-v14

Anti-pattern rules (query priority, `waitFor` misuse, raw props, missing roles) are in Procedure and Pitfalls above.

## Related Skills

- `frontend-ui-ux` — For interface design, accessibility, responsive layouts, and design system guidance.
- `jest-testing` — For general Jest configuration, mocks, and snapshot testing.
