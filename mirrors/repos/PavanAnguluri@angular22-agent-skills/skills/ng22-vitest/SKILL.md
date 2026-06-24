---
name: ng22-vitest
description: Guides Angular 22 teams to use Vitest for fast, deterministic unit and component testing.
---

# Angular 22 Vitest Testing

Use Vitest for fast feedback loops, deterministic assertions, and lightweight component and service tests. Keep test setup minimal and focus on observable behavior.

## Core Rules

1. Prefer Vitest for unit tests that do not need a full browser runtime.
2. Keep test files colocated with the code they verify when that improves discoverability.
3. Mock only external boundaries such as HTTP, storage, timers, and browser globals.
4. Use `describe`, `it`, `expect`, `vi`, and lifecycle hooks consistently.
5. Favor stable assertions over snapshot-heavy workflows unless snapshots are truly valuable.
6. Use `vitest run` for one-shot CI execution and the watch runner for local iteration.

## Example

```typescript
import { afterEach, describe, expect, it, vi } from 'vitest';

describe('formatPrice', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('formats currency deterministically', () => {
    const formatter = vi.fn((value: number) => `USD ${value.toFixed(2)}`);

    expect(formatter(12.5)).toBe('USD 12.50');
    expect(formatter).toHaveBeenCalledWith(12.5);
  });
});
```

## Async and Timers

```typescript
import { describe, expect, it, vi } from 'vitest';

describe('delayed work', () => {
  it('uses fake timers predictably', async () => {
    vi.useFakeTimers();

    const result = new Promise<string>((resolve) => {
      setTimeout(() => resolve('ready'), 1000);
    });

    await vi.advanceTimersByTimeAsync(1000);
    await expect(result).resolves.toBe('ready');

    vi.useRealTimers();
  });
});
```

## Configuration Guidance

- Vitest reads `vite.config.*` by default, so reuse existing Vite configuration when possible.
- Use a dedicated `vitest.config.*` when test-specific settings need to stay separate.
- Keep setup files small and predictable.
- Use browser mode only when a test depends on real browser APIs or visual behavior.

## Testing Style

- Prefer explicit arrange, act, assert structure.
- Keep assertions close to the behavior that matters.
- Use `vi.mock()` sparingly and reset mocks between tests.
- Use snapshots only when the output is stable and structural change matters.
- Use `test.each` or `describe.each` when coverage varies only by input data.

## Best Practices

- Reset spies and mocks between tests to avoid shared state.
- Keep async tests explicit by awaiting the observable result.
- Prefer fake timers for predictable time-based logic.
- Use component tests only for rendered behavior that matters to users.

## Review Checklist

- The test name says what changes if the assertion fails.
- The setup is minimal and local.
- The test runner choice matches the test's risk and scope.
- Mocks do not hide important integration behavior.