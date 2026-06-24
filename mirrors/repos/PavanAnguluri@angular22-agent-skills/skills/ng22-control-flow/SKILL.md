---
name: ng22-control-flow
description: Instructs the agent to exclusively write templates using modern native block control flow.
---

# Angular 22 Control Flow & Template Directives

You must reject legacy template structural directives such as `*ngIf`, `*ngFor`, and `*ngSwitch`. Use the native block syntax because it is compiler-optimized, more expressive, and easier to read.

## Core Rules

1. Use `@if` for most conditional rendering.
2. Use `@for` for repeated collections and always supply a meaningful `track` expression.
3. Use `@empty` when a collection can reasonably be empty.
4. Use `@switch` for union-like states where exhaustiveness matters.
5. Prefer template aliases with `as` when the condition or expression is reused inside the block.

## Conditionals with `@if`

```html
@if (user.profile.settings.startDate; as startDate) {
  <p>Joined on {{ startDate | date }}</p>
} @else if (user.isPending()) {
  <p>Verifying access status...</p>
} @else {
  <app-login-form />
}
```

Use `@if` aliases for long expressions that would otherwise be repeated in the block.

## Iteration with `@for`

The `track` clause is mandatory for performance and correctness. Use a stable identifier like `id` or `uuid`. Use `$index` only for static primitive lists.

```html
@for (item of items(); track item.id; let index = $index, first = $first) {
  <div class="list-item">
    <span>#{{ index + 1 }}</span>
    <span>{{ item.name }}</span>
    @if (first) {
      <strong>Featured</strong>
    }
  </div>
} @empty {
  <p>No inventory found in this region.</p>
}
```

## Exhaustive branching with `@switch`

Use `@switch` when the UI state is a small discrete union and you want compile-time coverage of all cases.

```html
@switch (status()) {
  @case ('loading') {
    <p>Loading...</p>
  }
  @case ('success') {
    <app-results />
  }
  @case ('error') {
    <app-error-panel />
  }
  @default {
    <p>Unknown state.</p>
  }
}
```

## Anti-Patterns

- Do not mix old structural directives with new control flow in the same template.
- Do not use `@for` without `track` unless the data is a static primitive list.
- Do not hide complex branching in helper methods if a block expression reads clearly.
- Do not use `@switch` when `@if` is more readable.

## Review Checklist

- No `*ngIf`, `*ngFor`, or `*ngSwitch` remains.
- Every loop has a useful `track` clause.
- Every empty collection case is handled where needed.
- The template reads like the rendering logic, not like a workaround.
