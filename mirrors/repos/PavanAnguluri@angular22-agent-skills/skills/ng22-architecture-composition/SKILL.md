---
name: ng22-architecture-composition
description: Guides Angular 22 architecture toward standalone composition, narrow services, and feature boundaries.
---

# Angular 22 Architecture & Composition

Prefer small, explicit feature slices over large shared abstractions. Keep components focused on orchestration and move domain rules into services or pure functions.

## Core Rules

1. Use standalone components, directives, and pipes by default.
2. Prefer `inject()` over constructor injection when the dependency is used directly in the class body.
3. Keep state ownership local to the nearest feature boundary; lift state only when a second consumer actually needs it.
4. Split large screens into container and presentational components before extracting shared utilities.
5. Avoid `NgModule`-based organization for new code unless a third-party integration requires it.
6. Treat route boundaries, feature folders, and service scopes as deliberate design tools.

## Good Structure

```typescript
import { Component, inject } from '@angular/core';

interface UserSummary {
  id: string;
  name: string;
  tier: 'free' | 'pro';
}

class UserSummaryService {
  getSummary(userId: string): UserSummary {
    return { id: userId, name: 'Ada Lovelace', tier: 'pro' };
  }
}

@Component({
  standalone: true,
  selector: 'app-user-summary-card',
  template: `
    <article>
      <h2>{{ user.name }}</h2>
      <p>Plan: {{ user.tier }}</p>
    </article>
  `,
  providers: [UserSummaryService],
})
export class UserSummaryCardComponent {
  private readonly service = inject(UserSummaryService);
  user = this.service.getSummary('user-1');
}
```

## Feature Boundary Pattern

```typescript
import { Injectable, signal } from '@angular/core';

@Injectable()
export class CartFacade {
  private readonly _items = signal<string[]>([]);
  readonly items = this._items.asReadonly();

  add(item: string): void {
    this._items.update((items) => [...items, item]);
  }
}
```

## Architectural Guardrails

- Use services for I/O, persistence, and cross-component state coordination.
- Use pure helper functions for deterministic data shaping.
- Keep templates declarative and keep business rules out of them.
- Co-locate feature-specific routes, tests, and assets with the feature when possible.
- Prefer explicit provider scopes over global singleton behavior when a feature owns the dependency.

## Anti-Patterns

- Do not create shared abstractions before you have two real consumers.
- Do not put view logic, API calls, and state mutation into one component.
- Do not use a global service when a feature-scoped facade is enough.

## Review Checklist

- The feature can be understood from its folder and route boundary.
- Components are thin and declarative.
- Services own rules, data access, or coordination.
- Shared code is actually shared.
