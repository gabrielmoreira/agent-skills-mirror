---
name: ng22-testing
description: Establishes Angular 22 testing habits for components, services, routing, and user interactions.
---

# Angular 22 Testing Discipline

Write tests that verify user-visible behavior, route behavior, and service contracts. Keep test intent clear and avoid over-mocking the framework itself.

## Core Rules

1. Prefer behavior assertions over implementation details.
2. Test components through their public inputs, outputs, and rendered DOM.
3. Keep service tests focused on deterministic business logic and adapter behavior.
4. Use route tests for navigation, redirects, and guard outcomes.
5. Mock only external boundaries such as network, storage, or time.
6. Match the test style to the risk: unit, integration, or browser-mode testing.

## Angular Testing Setup

Angular CLI projects now default to Vitest and `jsdom` for unit tests. Use the default toolchain unless a project has a clear reason to customize it.

## Component Test Pattern

```typescript
import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';

@Component({
  standalone: true,
  selector: 'app-counter',
  template: `<button type="button" (click)="increment()">Count: {{ count }}</button>`,
})
class CounterComponent {
  count = 3;

  increment(): void {
    this.count += 1;
  }
}

describe('CounterComponent', () => {
  it('renders and updates the current count', () => {
    const fixture = TestBed.createComponent(CounterComponent);
    fixture.detectChanges();

    fixture.nativeElement.querySelector('button').click();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Count: 4');
  });
});
```

## Service and Route Testing

```typescript
import { describe, expect, it } from 'vitest';

describe('price service', () => {
  it('applies discounts consistently', () => {
    const applyDiscount = (price: number, percent: number) => price - price * percent;

    expect(applyDiscount(100, 0.15)).toBe(85);
  });
});
```

## Testing Depth

- Use component tests for DOM, events, and rendering state.
- Use service tests for pure calculations and adapter behavior.
- Use route tests for redirects, guards, and navigation state.
- Use harnesses for complex Angular Material or CDK interactions when they reduce brittleness.
- Use browser mode only when a test depends on real browser behavior or visual fidelity.

## Tooling Notes

- New Angular projects use Vitest and `jsdom` by default.
- Use `providersFile` or `setupFiles` for shared test infrastructure instead of repeating it in every spec.
- Keep test configuration close to the Angular build target so the behavior is obvious.

## Example: Async Behavior

```typescript
import { fakeAsync, tick } from '@angular/core/testing';

it('completes delayed work', fakeAsync(() => {
  let completed = false;

  setTimeout(() => {
    completed = true;
  }, 1000);

  tick(1000);

  expect(completed).toBe(true);
}));
```

## Coverage and CI

- Collect coverage for the code paths that matter, not as a vanity metric.
- Keep CI runs deterministic and single-shot.
- Prefer setup files and providers files for shared test configuration instead of repeated boilerplate.

## Anti-Patterns

- Do not assert private fields when the rendered output already proves the behavior.
- Do not overuse snapshots for interactive UI.
- Do not keep brittle test data inline when a tiny factory would read better.

## Review Checklist

- The test fails for the right reason when behavior changes.
- The test body reads like a user scenario.
- Mocks only touch real external boundaries.
- Coverage gaps are intentional, not accidental.
