# UI Excellence Checklist — Quality Gate

Run this checklist against every screen before marking it done. Every item is binary: it either passes or it doesn't. "Good enough" is not a pass.

---

## Visual Design

- [ ] All colors come from `MaterialTheme.colorScheme.*` or a named `CompositionLocal` — zero hardcoded hex values outside the primitive token file
- [ ] All typography uses `MaterialTheme.typography.*` — zero hardcoded `fontSize`, `fontWeight`, or `FontFamily` in composables
- [ ] All spacing values are multiples of 4dp, referenced via `AppSpacing.*` tokens — zero hardcoded `Modifier.padding(Xdp)` calls with non-4dp-multiples
- [ ] Surfaces use appropriate elevation tinting — cards are not all flat at the same `tonalElevation`; depth hierarchy is visible
- [ ] The background is not the default system white or grey — a considered surface treatment exists (gradient, tonal background, texture, or intentional `surfaceVariant`)
- [ ] At least one non-flat visual element exists where flat color would be visually weak: gradient, brush fill, layered radial background, or custom canvas drawing
- [ ] The type scale creates a hierarchy that reads at a glance — a senior designer could identify the most important information within 2 seconds

---

## Motion & Transitions

- [ ] Navigation between related content (list → detail, card → expanded) uses shared element transitions (`sharedElement()` or `sharedBounds()`), not instant or slide-only navigation
- [ ] Enter animations use ease-out or spring physics — content arrives with deceleration, not abruptly
- [ ] Exit animations use ease-in — content leaves by accelerating, not by fading uniformly
- [ ] List items that arrive after a navigation or load stagger their entry animations (per-item delay, capped at 300ms total)
- [ ] The primary loading state is a skeleton screen that mirrors the geometry of the `Ready` state — not a centred `CircularProgressIndicator` on a blank background
- [ ] `LinearProgressIndicator` is absent as the sole loading affordance — it may exist as a secondary indicator (e.g., top-of-screen during background refresh), but not as the primary one

---

## Interaction Design

- [ ] Every interactive element has visible, contextually appropriate press feedback — ripple for contained surfaces, scale indication for cards/images, no visible feedback is a deliberate choice that has been made consciously (not an oversight)
- [ ] All touch targets are minimum 48dp × 48dp — icons with `size(24.dp)` that are clickable are wrapped in a 48dp container
- [ ] The primary action (FAB or equivalent) triggers `HapticFeedbackType.LongPress` or `TextHandleMove` on press — haptics coordinate with the visual confirmation
- [ ] Any swipeable or draggable content has a visible affordance (drag handle, peek of content behind, or clear directional indicator) — users don't need to discover the gesture by accident

---

## Edge-to-Edge & Insets

- [ ] The status bar area is styled or content extends behind it — the status bar is never an unclaimed grey band above the UI
- [ ] The navigation bar area is styled or content extends behind it — the nav bar is not a white rectangle at the screen bottom disconnected from the app's palette
- [ ] All scrollable content has `WindowInsets.navigationBars` padding (or `safeDrawingPadding()`) applied correctly — the last list item is not obscured by the system nav bar
- [ ] The keyboard does not cover text input fields — `imePadding()` or `WindowInsets.ime` is applied to the scroll container containing the input

---

## Accessibility

- [ ] Every `AsyncImage` / `Image` has a meaningful `contentDescription`, or is marked `contentDescription = null` with a documented reason (decorative) — no image has a blank or missing description
- [ ] Every custom interactive component (non-standard button, card, toggle) declares its semantic role via `Modifier.semantics { role = Role.Button }` or equivalent
- [ ] Focus traversal order for keyboard and TalkBack navigation is logical — tested by navigating the screen with TalkBack enabled or verified via `uiautomator dump` hierarchy inspection
- [ ] All text-on-background color combinations meet WCAG AA minimum contrast ratio (4.5:1 for body text, 3:1 for large text / UI components) — verified against the design system color palette

---

## Preview Coverage

- [ ] A `@Preview` exists showing the screen/component in **light theme** with realistic content (not placeholder text)
- [ ] A `@Preview` exists showing the screen/component in **dark theme** (`uiMode = Configuration.UI_MODE_NIGHT_YES`)
- [ ] A `@Preview` exists with **large font scale** (`fontScale = 1.5f`) — text doesn't overflow bounds or clip
- [ ] A `@Preview` exists with **RTL layout** (`locale = "ar"`) — layout mirrors correctly and no element is hardcoded to a specific side
