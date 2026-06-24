---
name: ng22-reactivity
description: Enforces Angular 22 fine-grained reactivity using Signals, Signal inputs, and Model primitives.
---

# Angular 22 Signals & Reactivity Discipline

You are an expert Angular 22 architect. Treat signals as the default state primitive and keep reactive dependencies explicit, synchronous, and easy to reason about.

## Core Rules

1. Use `signal()` for writable local state and expose readonly views with `asReadonly()` when consumers should not mutate the state.
2. Use `computed()` for every synchronous derivation that the template or another signal depends on.
3. Declare component inputs with `input()` or `input.required()` instead of `@Input()`.
4. Use `model()` for two-way state that must sync between parent and child.
5. Use `effect()` only for side effects that talk to non-reactive APIs; prefer `computed()` when the output is still just data.
6. Read signals before `await` boundaries. Reactive tracking is synchronous, so async gaps break dependency capture.

## Signal Shapes

### Writable state

```typescript
import { signal } from '@angular/core';

const count = signal(0);

count.set(1);
count.update((value) => value + 1);
```

### Readonly exposure

```typescript
import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class CounterState {
  private readonly _count = signal(0);
  readonly count = this._count.asReadonly();

  increment(): void {
    this._count.update((value) => value + 1);
  }
}
```

### Dynamic derivation

```typescript
import { computed, signal } from '@angular/core';

const showCount = signal(false);
const count = signal(0);

const message = computed(() => {
  if (showCount()) {
    return `The count is ${count()}`;
  }

  return 'Nothing to see here.';
});
```

## Component Example

```typescript
import { Component, computed, input, model, signal } from '@angular/core';

@Component({
  standalone: true,
  selector: 'app-user-profile',
  template: `
    <section>
      <h3>{{ fullName() }}</h3>
      <p>{{ badgeText() }}</p>
      <input [value]="role()" (input)="role.set($any($event.target).value)" />
      <button type="button" (click)="isExpanded.update((value) => !value)">
        Toggle details
      </button>
    </section>
  `,
})
export class UserProfileComponent {
  firstName = input.required<string>();
  lastName = input.required<string>();
  role = model<string>('Developer');
  isExpanded = signal(false);

  fullName = computed(() => `${this.firstName()} ${this.lastName()}`);
  badgeText = computed(() => (this.isExpanded() ? 'Expanded' : 'Collapsed'));
}
```

## Effects and Interop

Use `effect()` when the code needs to update a non-reactive API such as storage, title, analytics, or a logging service. Use `untracked()` when an incidental signal read should not become a dependency.

```typescript
import { effect, untracked } from '@angular/core';

effect(() => {
  const user = currentUser();

  untracked(() => loggingService.log(`User changed: ${user}`));
});
```

Only use `toSignal()` or `toObservable()` from `@angular/core/rxjs-interop` when bridging asynchronous streams such as HTTP pipelines, WebSocket feeds, or form value streams.

## Anti-Patterns

- Do not store derived data in writable state if it can be expressed as `computed()`.
- Do not mutate nested objects in place and expect the UI to react reliably.
- Do not use signals as a dumping ground for unrelated state.
- Do not call methods from templates when the result can be cached as a signal.

## Review Checklist

- Every input is signal-based.
- Every derived value is a computed signal.
- Side effects are isolated and intentional.
- The template reads data, it does not calculate it.
