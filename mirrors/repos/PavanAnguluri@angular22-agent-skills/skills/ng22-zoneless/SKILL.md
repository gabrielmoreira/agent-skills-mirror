---
name: ng22-zoneless
description: Enforces Angular 22 zoneless best practices for change detection, async handling, and event-driven UI updates.
---

# Angular 22 Zoneless Discipline

Write code that works cleanly without relying on Zone.js for automatic change detection. Make async boundaries, state updates, and UI refresh triggers explicit.

## Core Rules

1. Prefer signal-driven state and explicit state writes over implicit mutation patterns.
2. Use Angular APIs and browser primitives that work predictably without Zone.js patching.
3. Mark asynchronous work clearly and update state in the callback or promise continuation that owns the result.
4. Keep event handlers small so change sources remain obvious.
5. Audit third-party libraries for Zone.js assumptions before adopting zoneless mode.
6. Prefer `OnPush`-compatible components and explicit notifications for anything that mutates outside signals.

## Why Zoneless

- Less overhead from global patching.
- Better debugging because the app changes only when you tell Angular it changed.
- Cleaner compatibility with modern browser APIs.
- More predictable server rendering and test behavior.

## Example

```typescript
import { Component, signal } from '@angular/core';

@Component({
  standalone: true,
  selector: 'app-notification-count',
  template: `<button type="button">Notifications: {{ count() }}</button>`,
})
export class NotificationCountComponent {
  count = signal(0);

  increment(): void {
    this.count.update((value) => value + 1);
  }
}
```

## Compatibility Rules

- Use signals, computed values, and explicit event handlers to drive the UI.
- Use `ChangeDetectorRef.markForCheck()` or signal updates when non-signal state must refresh the view.
- Avoid `NgZone.onStable`, `NgZone.onUnstable`, and similar stability hooks for application flow.
- `NgZone.run()` and `NgZone.runOutsideAngular()` can remain when a library needs them.
- Keep `afterNextRender()` and `afterEveryRender()` in mind when you need render-aware follow-up work.

## SSR and Async Work

For SSR, make Angular aware of pending async tasks when serialization must wait. Use `PendingTasks` or `pendingUntilEvent()` when work needs to keep the app unstable until it finishes.

```typescript
import { inject, signal } from '@angular/core';
import { PendingTasks } from '@angular/core';

const pendingTasks = inject(PendingTasks);
const data = signal<string | null>(null);

pendingTasks.run(async () => {
  data.set(await fetch('/api/profile').then((response) => response.text()));
});
```

## Testing and Debugging

- In TestBed, use zoneless mode when you want test behavior to mirror production.
- Prefer `whenStable()` over manual `detectChanges()` when the test is verifying async-driven updates.
- Use debug-mode checks to catch updates that happen without a notification.

## Anti-Patterns

- Do not rely on implicit zone patching to refresh the UI.
- Do not keep old `NgZone` stability hooks in application code.
- Do not assume a third-party component is zoneless-safe without testing it.

## Review Checklist

- State changes are explicit.
- Async work has a clear notification path.
- Tests cover the zoneless behavior, not the Zone.js fallback.
- SSR tasks are registered when serialization must wait.