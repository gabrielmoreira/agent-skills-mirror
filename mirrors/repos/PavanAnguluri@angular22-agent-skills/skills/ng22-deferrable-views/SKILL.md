---
name: ng22-deferrable-views
description: Automates chunk splitting and deferred lazy-loading setup for heavy viewport components.
---

# Angular 22 Deferrable Views Layout Guideline

Wrap heavy UI sections, dashboards, or complex components in `@defer` blocks to reduce initial bundle work and keep first paint responsive.

## Core Rules

1. Defer expensive UI that is not required for initial interaction.
2. Use `on viewport` for below-the-fold content by default.
3. Use `on interaction` or `on hover` for drawers, menus, dialogs, and infrequently used tools.
4. Always provide a `@placeholder` and usually a `minimum` duration to avoid flicker.
5. Provide `@loading` and `@error` states when the deferred content has visible loading or failure states.
6. Combine deferral with route splitting when the content is an entire feature page.

## Standard Execution

```html
@defer (on viewport; prefetch on idle) {
  <app-heavy-analytics-chart [data]="metrics()" />
} @placeholder (minimum 500ms) {
  <div class="skeleton-loader">Preparing data layout blocks...</div>
} @loading {
  <app-spinner />
} @error {
  <div class="alert-box">Failed to load asset bundle. Try again later.</div>
}
```

## Trigger Guide

```html
@defer (on interaction) {
  <app-settings-drawer />
} @placeholder {
  <button type="button">Open settings</button>
}
```

```html
@defer (on hover; prefetch on idle) {
  <app-insight-popover />
} @placeholder {
  <span>Hover for details</span>
}
```

## Practical Rules

- Use `@defer` for charts, data grids, WYSIWYG editors, and other heavy widgets.
- Avoid deferring content that must be immediately available for primary navigation.
- Keep placeholders structurally close to the final layout so dimensions stay stable.
- Use `prefetch on idle` when you want the browser to prepare the chunk before the user reaches it.
- Be cautious with server rendering and hydration; ensure the placeholder and deferred content transition cleanly.

## Anti-Patterns

- Do not defer critical page chrome or the first interactive control.
- Do not omit a placeholder for heavy content that would otherwise cause layout shift.
- Do not nest unrelated business logic inside the deferred block.

## Review Checklist

- The deferred content is truly non-essential at first paint.
- The trigger matches the user’s expected interaction model.
- Placeholder, loading, and error states are intentional.
- The layout remains stable while the chunk loads.
