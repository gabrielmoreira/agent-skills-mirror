---
name: ng22-routing-lazy
description: Prescribes Angular 22 route design, lazy loading, guards, and route-level composition.
---

# Angular 22 Routing & Lazy Loading

Design routes as the primary composition boundary for large applications. Load feature code lazily and keep route definitions explicit, typed, and small.

## Core Rules

1. Use `loadComponent()` and `loadChildren()` for feature isolation.
2. Keep route guards functional and side-effect free whenever possible.
3. Put route-specific providers on the route record instead of in a global shell.
4. Use route `data` only for stable metadata such as titles, permissions, and display hints.
5. Favor child routes over runtime template branching when the URL represents a true navigation state.
6. Keep route configuration shallow and easy to scan.

## Example

```typescript
import { Routes } from '@angular/router';
import { authGuard } from './auth.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./home/home.component').then((m) => m.HomeComponent),
    title: 'Home',
  },
  {
    path: 'account',
    canActivate: [authGuard],
    providers: [],
    loadChildren: () => import('./account/account.routes').then((m) => m.ACCOUNT_ROUTES),
  },
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.routes').then((m) => m.ADMIN_ROUTES),
    data: { requiresAuth: true, section: 'admin' },
  },
];
```

## Guard and Resolver Guidance

```typescript
import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';

export const authGuard: CanActivateFn = () => {
  const router = inject(Router);
  const isAuthenticated = true;

  return isAuthenticated ? true : router.parseUrl('/login');
};
```

Use resolvers only when the UI cannot render without preloaded data. Prefer skeletons or deferred content when the page can render immediately and hydrate data later.

## Lazy Loading Best Practices

- Prefer route-level lazy loading over bundle-wide eager imports.
- Keep redirects and wildcard routes at the edge of the route tree.
- Use child routes for nested navigation states instead of template branching.
- Put page titles and permission hints in `data`, not business logic.
- Keep guard logic fast so navigation stays responsive.

## Anti-Patterns

- Do not make route files a dumping ground for unrelated app logic.
- Do not read remote data in a guard unless navigation truly depends on it.
- Do not duplicate the same authorization logic in both route data and component code.

## Review Checklist

- Each major feature has a lazy-loaded boundary.
- Guards are small and predictable.
- Route metadata is static and easy to audit.
- Route structure mirrors product navigation.
