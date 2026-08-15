---
name: design-harden
description: "Hardens shipped UI by adding missing error boundaries, content-shaped skeletons, empty-state CTAs, overflow/i18n/offline handling, and keyboard/ARIA coverage while matching the repo's existing patterns. Use for production-ready edge states on screens that already work. Never a visual-language or token-system build; not for drawing new pages from a blank canvas."
version: 1.0.1
---

# Design Harden

Autonomous UI hardening agent. Scan every component in the codebase, find every missing edge case handler, and add it. Do not ask questions. Infer appropriate error, loading, and empty state patterns from the existing codebase and fill every gap.

**Operating mode:** Do NOT ask the user questions. Scan the code, find every missing state, implement it.

## When to Use

- A UI is functional but not production-ready — missing error boundaries, loading skeletons, empty states, or offline handling.
- User says: "harden the UI", "add error states", "handle edge cases", "add loading states", "make this bulletproof", "prepare for production".
- Components fetch data but show blank screens during load or on failure.
- Forms lack validation feedback or submit without loading indicators.
- Text overflows containers, layouts break with long content, or i18n is not ready.
- Accessibility gaps: missing keyboard support, ARIA labels, focus management, or touch targets.

## Prerequisites

- A working codebase with a build system (package.json, pubspec.yaml, build.gradle, or equivalent).
- The project must build successfully before hardening begins.
- Identify the UI framework, state management, and data-fetching layer before making changes.

## Procedure

### Inputs

`$ARGUMENTS` (optional). If provided, focus on specific components, pages, or hardening categories (e.g., "error handling only", "dashboard page", "loading states"). If not provided, perform a full hardening pass.

---

### Phase 1: Codebase Reconnaissance

#### 1.1 Identify Stack and Patterns

1. Read `package.json`, `pubspec.yaml`, `build.gradle`, or equivalent.
2. Identify UI framework: React, Vue, Svelte, Angular, Flutter, SwiftUI, Jetpack Compose.
3. Identify state management: Redux, Zustand, Riverpod, Provider, Bloc, TCA, MVI.
4. Identify data fetching: React Query, SWR, Apollo, Dio, Retrofit, URLSession, custom.
5. Identify existing error handling patterns: error boundaries, try/catch wrappers, Result types.

#### 1.2 Catalog All Interactive Components

List every component that:
- Fetches data from an API or database.
- Accepts user input (forms, text fields, selectors).
- Displays dynamic content (lists, grids, tables, charts).
- Navigates between screens or pages.
- Performs mutations (create, update, delete).

For each component, note which states it currently handles: loading, error, empty, success, partial.

#### 1.3 Identify Gaps

- Flag components that have data fetching but no loading state.
- Flag components that have data fetching but no error state.
- Flag components that display lists but no empty state.
- Flag forms with no validation or error feedback.
- Flag mutations with no loading indicator or optimistic update.
- Rank gaps by user impact (how likely is a user to encounter this state?).

---

### Phase 2: Error Handling

#### 2.1 Error Boundaries (React)

1. Verify every route/page is wrapped in an error boundary.
2. If no error boundaries exist, add a root-level error boundary and per-feature boundaries:

```tsx
// Granular error boundary with recovery
<ErrorBoundary
  fallback={({ error, resetErrorBoundary }) => (
    <ErrorFallback
      message="Something went wrong loading this section."
      onRetry={resetErrorBoundary}
    />
  )}
>
  <FeatureComponent />
</ErrorBoundary>
```

3. Error fallbacks must include: a human-readable message, a retry button, and optionally a "report issue" link.
4. **HARD RULE:** NEVER show raw error messages, stack traces, or internal details to the user.

#### 2.2 Async Error Handling

1. Every async operation (fetch, mutation, file read) must be wrapped in try/catch.
2. Error handling must be specific — catch different error types and show appropriate messages:
   - Network error: "Unable to connect. Check your internet connection and try again."
   - 404: "This content is no longer available."
   - 403: "You don't have permission to view this."
   - 429: "Too many requests. Please wait a moment and try again."
   - 500: "Something went wrong on our end. Please try again later."
   - Timeout: "The request took too long. Please try again."
3. Implement retry logic with exponential backoff for transient errors:

```typescript
async function fetchWithRetry<T>(fn: () => Promise<T>, maxRetries = 3): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try { return await fn(); }
    catch (e) {
      if (i === maxRetries - 1 || !isTransient(e)) throw e;
      await sleep(Math.pow(2, i) * 1000);
    }
  }
  throw new Error('unreachable');
}
```

#### 2.3 Graceful Degradation

- If a non-critical section fails, the rest of the page must still render.
- Sidebar widgets, recommendation sections, and analytics should degrade silently.
- Critical sections (main content, navigation) should show an error with retry.
- **HARD RULE:** Never let one failed API call take down the entire page.

#### 2.4 Flutter Error Handling

- Wrap async calls in try/catch with proper error state management.
- Use `ErrorWidget.builder` for custom error widgets in debug and release mode.
- Implement `runZonedGuarded` for catching uncaught async errors.
- Use `Result` or `Either` types for typed error handling in repositories.

#### 2.5 Form Validation

1. Every form field must have validation rules that run on blur and on submit.
2. Show inline error messages below the field (not alerts/toasts).
3. Error messages must be specific: "Email must include @" not "Invalid input."
4. Disable submit button while form has errors or submission is in progress.
5. **HARD RULE:** Preserve form state on error — never clear the form after a failed submission.

---

### Phase 3: Loading States

#### 3.1 Skeleton Screens (Not Spinners)

1. Replace generic spinners with skeleton screens that mirror the content layout:

```tsx
// Bad: generic spinner
{isLoading && <Spinner />}

// Good: content-shaped skeleton
{isLoading && (
  <div className="card-skeleton">
    <div className="skeleton-image" />
    <div className="skeleton-line w-3/4" />
    <div className="skeleton-line w-1/2" />
  </div>
)}
```

2. Skeleton styles should use a shimmer animation:

```css
.skeleton {
  background: linear-gradient(
    90deg,
    oklch(0.92 0 0) 25%,
    oklch(0.96 0 0) 50%,
    oklch(0.92 0 0) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
  from { background-position: 200% 0; }
  to { background-position: -200% 0; }
}
```

#### 3.2 Suspense Boundaries (React)

- Wrap lazy-loaded components in Suspense with appropriate fallbacks.
- Nest Suspense boundaries: page-level loading for route changes, section-level for deferred content.
- Use `startTransition` for non-urgent updates to avoid unnecessary loading states.

#### 3.3 Loading Indicators for Mutations

Every button that triggers a mutation must show a loading state:
- Disable the button.
- Replace text with a spinner or "Saving..." text.
- Prevent double-submission.
- For long-running operations (file upload, batch processing), show a progress indicator.

#### 3.4 Optimistic Updates

For mutations where the outcome is predictable (toggle, like, delete), update UI immediately:

```typescript
// Optimistic: update cache immediately, revert on error
const previousData = queryClient.getQueryData(key);
queryClient.setQueryData(key, optimisticData);
try {
  await mutation(data);
} catch {
  queryClient.setQueryData(key, previousData);
  showToast("Failed to save. Please try again.");
}
```

Show a subtle sync indicator for optimistic updates (small icon, not a toast).

#### 3.5 Flutter Loading States

- Use `Shimmer` package or custom `AnimatedContainer` for skeleton screens.
- Implement loading state in state management (Riverpod AsyncValue, Bloc states).
- **HARD RULE:** Never use bare `CircularProgressIndicator()` — always wrap in a meaningful layout.
- For lists, show 3–5 skeleton items matching the list item shape.

---

### Phase 4: Empty States

#### 4.1 Empty State Design

1. Every list, grid, table, or collection must handle the empty case.
2. Empty states must include:
   - An illustration or icon (not just text).
   - A descriptive message explaining why it is empty.
   - A primary action CTA (create first item, adjust filters, etc.).

```tsx
<EmptyState
  icon={<SearchIcon />}
  title="No results found"
  description="Try adjusting your filters or search terms."
  action={<Button onClick={clearFilters}>Clear filters</Button>}
/>
```

#### 4.2 Contextual Empty States

Distinguish between different empty reasons:
- **First use:** "Welcome! Create your first project to get started." (encouraging, with CTA)
- **No results:** "No items match your filters." (with clear filters action)
- **Deleted all:** "All items have been archived." (with undo or view archive action)
- **Permission:** "You don't have access to this content." (with request access action)

#### 4.3 Partial Empty States

- Tables with no data but existing columns should show an empty row message, not a blank table.
- Charts with no data should show axes with a "No data for this period" message.
- Dashboards should show draft cards, not collapsed sections.

#### 4.4 Flutter Empty States

- Create a reusable `EmptyStateWidget` with icon, title, description, and optional action.
- Use `AnimatedSwitcher` to transition between loading, content, and empty states smoothly.
- Verify `ListView.builder` with `itemCount: 0` shows an empty state, not a blank screen.

---

### Phase 5: Text Overflow and Content Resilience

#### 5.1 Text Overflow Handling

Every text element that displays dynamic content must handle overflow:

```css
/* Single line truncation */
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Multi-line clamp */
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

- Headings in cards and list items should truncate, not wrap infinitely.
- User-generated content must have max-width constraints.

#### 5.2 Long Content Stress Test

Mentally test every text field with:
- A single character ("A").
- A very long string with no spaces ("Aaaaaaaaaaaaaaaaaa...").
- A very long string with spaces (full paragraph).
- Unicode characters, emoji, RTL text.
- HTML entities (should be escaped, not rendered).

Fix any layout that breaks under these conditions.

#### 5.3 Word Break Handling

For user-generated content areas, add word-break handling:

```css
.user-content {
  overflow-wrap: break-word;
  word-break: break-word;
  hyphens: auto;
}
```

URLs and file paths should break with `word-break: break-all` in constrained containers.

#### 5.4 Number and Date Formatting

- Large numbers should use locale-aware formatting (1,234,567 not 1234567).
- Dates should use relative time for recent ("2 hours ago") and formatted for older.
- Currency should always show the correct number of decimal places.
- Verify number formatting does not break layout (e.g., "$1,234,567.89" in a narrow column).

#### 5.5 Flutter Text Resilience

- Use `maxLines` and `overflow: TextOverflow.ellipsis` on all dynamic text.
- Verify `Text` widgets inside `Row` are wrapped in `Expanded` or `Flexible` to prevent overflow.
- Use `FittedBox` sparingly for headings that must fit a constrained width.

---

### Phase 6: I18N Readiness

#### 6.1 String Externalization

1. Scan for hardcoded user-facing strings in component files.
2. Flag strings that should be in a localization file (l10n, i18n, intl, arb).
3. **HARD RULE:** Do NOT move all strings — flag them and create a task list for future extraction.
4. Ensure string templates use parameterized interpolation, not concatenation:

```typescript
// Bad: "Welcome " + userName + "!"
// Good: t("welcome", { name: userName })
```

#### 6.2 RTL Support Readiness

Check for directional CSS properties that should use logical properties:

```css
/* Physical (breaks RTL) */
margin-left: 16px;
padding-right: 8px;
text-align: left;

/* Logical (RTL-safe) */
margin-inline-start: 16px;
padding-inline-end: 8px;
text-align: start;
```

- Flag all physical direction properties for future RTL conversion.
- Verify icons with directional meaning (arrows, chevrons) can be mirrored.

#### 6.3 Pluralization and Gender

- Check for naive pluralization ("1 items", "item(s)").
- Verify date/time formatting uses Intl API or equivalent.
- Check number formatting uses locale-aware separators.

#### 6.4 Text Expansion

- Verify layouts can handle text expansion (German is ~30% longer than English).
- Buttons with text should not have fixed widths.
- Navigation labels should accommodate longer translations.

---

### Phase 7: Offline and Connectivity

#### 7.1 Offline Detection

- Verify the app detects connectivity changes.
- Web: `navigator.onLine` + `online`/`offline` events.
- Mobile: platform connectivity APIs (connectivity_plus for Flutter).
- Show a non-intrusive banner when offline, not a blocking modal.

#### 7.2 Offline-First Patterns

If the app uses any local caching (service worker, Hive, SQLite, AsyncStorage):
- Verify cached data is shown when offline instead of an error.
- Show a "Last updated X ago" indicator when serving stale data.
- Queue mutations for sync when connectivity returns.

If no caching exists, flag it as an improvement opportunity.

#### 7.3 Low Bandwidth Handling

- Verify images have `loading="lazy"` (web) or equivalent lazy loading.
- Check for unnecessary auto-playing videos or large asset downloads.
- Verify API calls are not duplicated (no fetching the same data twice on page load).

#### 7.4 Service Worker (Web)

- If a service worker exists, verify it caches critical assets (HTML, CSS, JS, fonts).
- Verify stale-while-revalidate strategy for API responses.
- If no service worker exists and the app would benefit from offline support, flag it.

---

### Phase 8: Accessibility Hardening

#### 8.1 Interactive Element Hardening

- Every interactive element must be keyboard accessible.
- Custom interactive elements must have appropriate ARIA roles.
- Modals must trap focus and return focus on close.
- Dropdown menus must support arrow key navigation.

#### 8.2 Screen Reader Hardening

- Images must have meaningful alt text (not "image" or "photo").
- Icon-only buttons must have `aria-label`.
- Dynamic content updates must use `aria-live` regions.
- Form errors must be associated with fields via `aria-describedby`.

#### 8.3 Motion Sensitivity

- Verify `prefers-reduced-motion` is respected for all animations.
- Auto-playing carousels must have pause controls.
- Parallax effects must have reduced-motion alternatives.

#### 8.4 Touch Target Sizing

- All interactive elements must be at least 44x44px (48x48px preferred).
- Spacing between touch targets must be at least 8px.
- Small interactive elements (close buttons, checkboxes) must have expanded hit areas:

```css
.small-button::before {
  content: '';
  position: absolute;
  inset: -8px;
}
```

---

### Phase 9: Apply Hardening

#### 9.1 Execution Strategy

Prioritize fixes by user impact:
1. Missing error handling on data fetching (crashes in production).
2. Missing loading states (confusing blank screens).
3. Text overflow issues (broken layouts).
4. Missing empty states (confusing blank sections).
5. Accessibility gaps (exclusion of users).
6. i18n and offline (future readiness).

For each fix, follow existing patterns in the codebase. Do not introduce new libraries or paradigms. If the codebase has no existing pattern for a state (e.g., no error handling anywhere), create a minimal, reusable pattern and apply it consistently.

#### 9.2 Create Reusable Utilities

When adding multiple instances of the same pattern, create a shared utility:
- `ErrorFallback` component for error states.
- `Skeleton` component for loading states.
- `EmptyState` component for empty states.
- `withRetry` or `fetchWithRetry` utility for retry logic.

Then use these utilities across all instances.

---

### Phase 10: Self-Healing Validation

#### 10.1 Build Verification

1. Run the project build command.
2. If build fails, revert the last change and re-run.
3. Run linter and fix any new warnings.

#### 10.2 Type Safety Check

- If TypeScript/Dart/Kotlin, verify no new type errors were introduced.
- Verify error types are properly typed (not `catch(e: any)`).
- Verify loading/error state types are exhaustive in switch/match statements.

#### 10.3 Test Verification

- Run existing tests. Fix any that break due to hardening changes.
- If tests exist for components that were modified, verify they still pass.
- **HARD RULE:** Do not remove or weaken existing test assertions.

#### 10.4 State Coverage Check

For every component modified, verify it now handles: loading, error, empty, and success states. List any components that still have gaps (with justification for why they were skipped).

---

### Phase 11: Telemetry and Report

#### 11.1 Hardening Summary

Output a summary table:

```
## Hardening Summary

| Category         | Gaps Found | Fixed | Deferred |
|------------------|------------|-------|----------|
| Error Boundaries |            |       |          |
| Async Errors     |            |       |          |
| Loading States   |            |       |          |
| Empty States     |            |       |          |
| Text Overflow    |            |       |          |
| Form Validation  |            |       |          |
| i18n Readiness   |            |       |          |
| Offline          |            |       |          |
| Accessibility    |            |       |          |
| **Total**        |            |       |          |
```

#### 11.2 State Coverage Matrix

For each major component, show its state coverage:

```
| Component | Loading | Error | Empty | Offline | a11y |
|-----------|---------|-------|-------|---------|------|
| UserList  | [x]     | [x]   | [x]   | [ ]     | [x]  |
| Dashboard | [x]     | [x]   | [x]   | [ ]     | [x]  |
```

#### 11.3 Reusable Utilities Created

List any shared components or utilities created during hardening.

#### 11.4 Deferred Items

List items not addressed with reasons and recommended follow-up actions.

#### 11.5 Self-Evolution Notes

- Which categories had the most gaps? (Focus future hardening here.)
- Were there systematic patterns? (e.g., "No component has error handling" suggests missing conventions.)
- What infrastructure improvements would prevent these gaps? (error boundary wrapper in layout, global error handler, etc.)
- Recommend running `/design-polish` after hardening to ensure new states match the design language.

## Pitfalls

- **Introducing new libraries:** Follow existing codebase patterns. Do not introduce new state management or data-fetching libraries during hardening.
- **Showing raw errors to users:** Never expose stack traces, internal error codes, or implementation details in the UI.
- **Clearing form on error:** A failed submission must preserve all user input. Clearing the form forces the user to re-enter everything.
- **Bare spinners:** A bare `CircularProgressIndicator()` or `<Spinner />` with no layout context is confusing. Always use skeleton screens that mirror content shape.
- **One API failure takes down the page:** Non-critical sections (sidebar, recommendations, analytics) must degrade silently. Only critical sections should show error + retry.
- **Naive pluralization:** "1 items" or "item(s)" is not acceptable. Use ICU MessageFormat or framework equivalent.
- **Physical CSS properties in RTL contexts:** `margin-left`, `padding-right`, `text-align: left` break RTL layouts. Use logical properties (`margin-inline-start`, `padding-inline-end`, `text-align: start`).
- **Fixed-width buttons with translatable text:** German translations are ~30% longer than English. Fixed widths will truncate or overflow.
- **Touch targets below 44x44px:** Fails WCAG 2.5.5 and Apple HIG. Small icons need expanded hit areas via pseudo-elements or padding.
- **Ignoring `prefers-reduced-motion`:** Shimmer animations, carousels, and parallax must respect this media query.
- **Weakening existing tests:** Never remove or relax test assertions to make hardening changes pass. Fix the implementation, not the test.

## Verification

### Build

```powershell
# Web (Node.js)
npm run build

# Flutter
flutter build apk --release

# Verify no new warnings
npm run lint
```

### Type Safety

```powershell
# TypeScript
npx tsc --noEmit

# Dart
dart analyze
```

### Tests

```powershell
# Run existing test suite
npm test

# Flutter
flutter test
```

All existing tests must pass. No test assertions may be removed or weakened.

### State Coverage Audit

For every modified component, manually verify:

| Check | How to verify |
|-------|---------------|
| Loading state | Trigger a slow network (DevTools throttle) and confirm skeleton renders |
| Error state | Force a 500 response (DevTools network override) and confirm error fallback with retry |
| Empty state | Return empty array from API mock and confirm empty state with CTA |
| Offline | Toggle offline in DevTools and confirm stale data or offline banner |
| Text overflow | Inject a 500-character string with no spaces and confirm truncation |
| Keyboard nav | Tab through the component and confirm focus visibility and logical order |
| Screen reader | Run VoiceOver/NVDA and confirm aria-live announcements for state changes |

### Accessibility

```powershell
# Run axe-core if available
npx @axe-core/cli http://localhost:3000
```

Verify zero critical and serious violations. Verify `prefers-reduced-motion` disables shimmer and auto-playing carousels.

## Related Skills

- **design-polish:** Run after hardening to ensure new states (error, loading, empty) match the design language and visual system.
- **design-system:** Use when establishing or consuming design tokens for spacing, color, type, elevation, radius, and motion.

## References

- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/intro
- W3C WAI resources: https://www.w3.org/WAI/
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines
- Material accessibility guidance: https://m2.material.io/design/usability/accessibility.html
