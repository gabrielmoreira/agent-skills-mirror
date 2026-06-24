---
name: ng22-ssr-hydration
description: Enforces Angular 22 SSR, hydration safety, event replay readiness, and browser-only boundary discipline.
---

# Angular 22 SSR and Hydration Discipline

Treat SSR and hydration as first-class runtime constraints. Prevent browser-only assumptions from leaking into server execution paths.

## Core Rules

1. Never access `window`, `document`, or browser globals in code that can run during SSR without guards.
2. Keep browser-only behavior inside explicit hydration-safe lifecycle boundaries.
3. Use Angular image and hydration configuration such as `IMAGE_CONFIG` where runtime behavior requires explicit injection.
4. Keep event replay and incremental hydration compatibility by avoiding side effects before hydration completes.
5. Isolate third-party browser scripts behind guarded entry points.

## SSR-Safe Guard Pattern

```typescript
import { Component, Inject, PLATFORM_ID, computed, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Component({
  standalone: true,
  selector: 'app-runtime-banner',
  template: `
    @if (isBrowser()) {
      <p>Interactive runtime enabled.</p>
    } @else {
      <p>Server-rendered shell.</p>
    }
  `,
})
export class RuntimeBannerComponent {
  private readonly browser = signal(false);

  constructor(@Inject(PLATFORM_ID) platformId: object) {
    this.browser.set(isPlatformBrowser(platformId));
  }

  isBrowser = computed(() => this.browser());
}
```

## Hydration Hook Discipline

- Execute browser-only script wiring in hydration-aware lifecycle hooks.
- Delay DOM-dependent integrations until client-side hydration has established control.
- Keep script bootstrapping idempotent so replayed events and incremental hydration do not duplicate effects.

## IMAGE_CONFIG Injection Pattern

```typescript
import { IMAGE_CONFIG, ImageConfig } from '@angular/common';
import { ApplicationConfig } from '@angular/core';

const imageConfig: ImageConfig = {
  placeholderResolution: 40,
};

export const appConfig: ApplicationConfig = {
  providers: [
    {
      provide: IMAGE_CONFIG,
      useValue: imageConfig,
    },
  ],
};
```

## Browser-Only Boundary Pattern

- Wrap browser integrations with platform guards.
- Use lazy dynamic imports for browser-only libraries where appropriate.
- Keep server render path side-effect free and deterministic.

## Anti-Patterns

- Direct `window`/`document` reads in constructors or top-level module scope.
- Registering DOM event listeners during SSR code paths.
- Unscoped third-party script initialization that runs in both server and client contexts.
- Hydration-unsafe code that mutates DOM before Angular hydration completes.

## Review Checklist

- All browser APIs are guarded.
- Hydration lifecycle boundaries are explicit.
- Image behavior uses configuration injection when needed.
- SSR path remains deterministic and side-effect free.
