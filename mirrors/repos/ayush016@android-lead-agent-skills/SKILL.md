---
name: android
description: |
  Senior-level Android engineering expertise for Jetpack Compose, Material 3, shared element
  transitions, navigation, performance, security, background work, notifications, adaptive
  layouts, Coil image loading, WorkManager, FCM, Baseline Profiles, R8 optimization,
  accessibility, coroutines and Flow, and extraordinary UI quality.

  Load this skill for ANY Android or Kotlin task — building a screen, animating a transition,
  designing a data layer, scaffolding a multi-module project, optimising startup, adding
  biometric auth, writing WorkManager jobs, wiring FCM, handling foldables, writing
  Roborazzi screenshot tests, debugging on device with ADB or MCP. If it touches Android,
  this skill covers it.

  Non-negotiable aesthetic bar: every screen produced must look like it belongs in a
  design award showcase. Default grey scaffolds, missing animations, hardcoded colors,
  and spinners as sole loading states are bugs, not style choices.

  Trigger on: Kotlin, Jetpack Compose, ViewModel, Hilt, Room, Retrofit, Coroutines, Flow,
  Navigation, WorkManager, FCM, Coil, Roborazzi, Macrobenchmark, Baseline Profiles, R8,
  WindowSizeClass, foldables, shared element transitions, animation, ADB, MCP.

compatibility:
  tools: [android_mcp, bash_tool, create_file, str_replace, view]
  compose_bom: "2024.09.00+"
  min_sdk: 21
  target_sdk: 35
---

# Android Development Skill

Production-grade Android engineering expertise from data layer to pixel, from startup milliseconds to biometric auth, from phone portrait to foldable landscape. UI quality, performance, security, and accessibility are first-class concerns equal to functional correctness.

---

## ⚡ Quick Decision Guide

| Task | Reference |
|------|-----------|
| Color theming, 29 roles, token hierarchy, gradients | [`theming-and-color.md`](references/theming-and-color.md) |
| Building a new screen | [`compose-ui-system.md`](references/compose-ui-system.md) |
| Navigation with shared element transitions | [`shared-element-transitions.md`](references/shared-element-transitions.md) |
| Type-safe navigation, deep links, multi-module | [`navigation.md`](references/navigation.md) |
| Animation / motion (non-shared-element) | [`motion-and-animation.md`](references/motion-and-animation.md) |
| Adaptive layouts, large screens, foldables | [`adaptive-layouts.md`](references/adaptive-layouts.md) |
| Coroutines, Flow, dispatchers, cancellation | [`coroutines-and-flow.md`](references/coroutines-and-flow.md) |
| Room, Retrofit, offline-first data layer | [`data-layer.md`](references/data-layer.md) |
| ViewModel, state, DI, architecture | [`architecture.md`](references/architecture.md) |
| Baseline Profiles, R8, recomposition perf | [`performance.md`](references/performance.md) |
| Encryption, biometrics, cert pinning | [`security.md`](references/security.md) |
| WorkManager, Foreground Services, Alarms | [`background-work.md`](references/background-work.md) |
| Coil3, SubcomposeAsyncImage, caching | [`image-loading.md`](references/image-loading.md) |
| FCM, notification channels, deep links | [`notifications.md`](references/notifications.md) |
| TalkBack, semantics, focus, contrast | [`accessibility.md`](references/accessibility.md) |
| Unit, screenshot, Roborazzi tests | [`testing.md`](references/testing.md) |
| Convention plugins, version catalog, modules | [`build-and-modules.md`](references/build-and-modules.md) |
| ADB / Android MCP debugging | [`android-mcp.md`](references/android-mcp.md) |
| Pre-ship quality review | [`assets/ui-excellence-checklist.md`](assets/ui-excellence-checklist.md) |

---

## Core Engineering Principles

**1. Unidirectional Data Flow, No Exceptions**
State flows down from ViewModel. Events flow up via lambdas or actions. No composable reads from a database. No ViewModel imports Compose. The boundary is sharp and testable.

**2. Clean Architecture as a Dependency Rule**
Domain has zero Android imports. Data is invisible to UI. Features depend on core, never each other. Violations create debt that compounds faster than feature velocity.

**3. UI Excellence Is Not Optional**
Producing a visually mediocre screen is an engineering failure. Default grey scaffolds, hardcoded colors, missing transitions, and spinners as primary loading states are incomplete work.

**4. Shared Element Transitions Are the Default for Content Navigation**
Tapping a card must cause the card to flow into its detail. `sharedBounds()` or `sharedElement()` is the default. Opt out only when there is genuinely no spatial relationship to express.

**5. Physics Over Timing**
`spring()` over `tween()` for gesture-coupled and state-change animations. Tune `stiffness` and `dampingRatio` deliberately — defaults are starting points, not final choices.

**6. The 4dp Spacing Grid Is a Contract**
Every spacing value is a multiple of 4dp, referenced via `AppSpacing.*` tokens. Arbitrary values are bugs that accumulate into visual dissonance.

**7. Fakes Over Mocks**
Test ViewModels against in-memory fake implementations. Fakes exercise real contracts, survive refactors. Mocks couple tests to implementation details and silently pass when production code breaks.

**8. Performance Is a Feature**
Baseline Profiles are committed for every app shipped. Recomposition counts are checked with Layout Inspector before any UI work is done. Cold start is tracked in CI via Macrobenchmark.

**9. Security from Day One**
Encrypted storage for all sensitive data. Certificate pinning for all network endpoints. No secrets in source code. Input validated at every external boundary. These are not features to add later.

**10. Accessibility Is Not Optional**
Every image has a content description. Every custom component declares its semantic role. Every interactive element has a 48dp touch target. Colour contrast meets WCAG AA. TalkBack is tested before any screen is shipped.

---

## ★ THE EXTRAORDINARY UI MANDATE ★

Android users have seen a million apps. The ones they remember have something alive about them — a transition that makes content feel like a physical object moving through space, surfaces that catch light at different elevations, a loading state so well crafted it does not feel like waiting.

**The Bar.** Every screen passes three tests before it ships:

1. **The scroll-stop test.** Would a designer pause on this if scrolling past it? Not because it is garish — because something is considered. A hierarchy that breathes. A transition that reveals spatial relationship. A surface treatment that says "we care."

2. **The feel test.** Does it respond to touch like a physical object? Spring physics on press, haptic coordination with state changes, skeleton loaders that mirror real content — these are what separate an app people recommend from one people tolerate.

3. **The motion test.** Do transitions communicate where content came from? Shared elements communicate spatial memory. Instant cuts communicate nothing. Slide transitions say you moved sideways. Shared elements say: this is that thing, grown.

**In code, this means:**
- Shared element transitions for every navigation between related content — always
- `spring()` physics tuned for each context; no unexamined defaults
- Color exclusively from Material 3 roles; `Brush` gradients where flat color is visually weak
- A display typeface for headlines paired with a humanist sans for body
- Skeleton screens mirroring the exact geometry of real content — no centred spinners
- Edge-to-edge always; status bar and nav bar are part of the design
- `Canvas` for anything standard components cannot achieve
- Haptic feedback coordinated with meaningful state transitions

**Anti-patterns to refuse:** Default grey scaffold backgrounds. Hardcoded hex colors in composables. Instant navigation between related content. `LinearProgressIndicator` as the sole loading state. Cards with identical elevation everywhere. Spacing not on the 4dp grid.

---

## Shared Element Transitions — Overview

`SharedTransitionLayout` coordinates geometry between composable trees during navigation. `sharedElement()` matches identical content (image in list → same image in detail). `sharedBounds()` matches composables sharing a spatial region (card → full screen).

Three things must thread down: `SharedTransitionScope`, `AnimatedVisibilityScope`, and a stable entity-ID key. Missing any one silently breaks the transition.

Full guide, four complete Kotlin patterns, pitfalls: [`references/shared-element-transitions.md`](references/shared-element-transitions.md)

---

## Android MCP Integration

MCP = eyes on device. Code = hands in codebase. Build → install → screenshot → compare → refine. Catches what Roborazzi misses: real inset behaviour, animation timing, system bar styling, density quirks.

Full capability table, workflows, log filtering, hierarchy inspection: [`references/android-mcp.md`](references/android-mcp.md)

---

## Feature Build Workflow

1. **Module** — Create with `yourapp.android.library.compose` plugin. [`build-and-modules.md`](references/build-and-modules.md)
2. **Routes** — `@Serializable` data class in `:core:navigation`. [`navigation.md`](references/navigation.md)
3. **UI State** — Sealed interface: `Loading`, `Ready(data)`, `Error(message, canRetry)`. [`architecture.md`](references/architecture.md)
4. **Actions** — Sealed interface for all user interactions.
5. **ViewModel** — `StateFlow` + `SharedFlow(replay=0)` + `SavedStateHandle.toRoute()`. [`architecture.md`](references/architecture.md)
6. **Domain** — UseCase → Repository interface → impl in `:core:data`. [`data-layer.md`](references/data-layer.md)
7. **Composables** — Public screen + private sub-composables; `AppSpacing`, `colorScheme`, `typography` only. [`compose-ui-system.md`](references/compose-ui-system.md)
8. **Shared elements** — `sharedElement()` or `sharedBounds()` with stable ID keys. [`shared-element-transitions.md`](references/shared-element-transitions.md)
9. **Motion** — Stagger entry, spring state changes, enter/exit transitions. [`motion-and-animation.md`](references/motion-and-animation.md)
10. **Skeleton loading** — Mirror `Ready` geometry with `ShimmerBox`. [`compose-ui-system.md`](references/compose-ui-system.md)
11. **Adaptive** — Verify on 600dp+; apply `WindowSizeClass`-aware layout. [`adaptive-layouts.md`](references/adaptive-layouts.md)
12. **Accessibility** — Semantics, content descriptions, focus order, 48dp targets. [`accessibility.md`](references/accessibility.md)
13. **Security** — No secrets; input validated at all external boundaries. [`security.md`](references/security.md)
14. **MCP review** — Screenshot in light/dark/large font/RTL; check insets + transitions. [`android-mcp.md`](references/android-mcp.md)
15. **Tests** — ViewModel unit tests + Roborazzi screenshots. [`testing.md`](references/testing.md)
16. **UI excellence** — Every item in [`assets/ui-excellence-checklist.md`](assets/ui-excellence-checklist.md) must pass.

---

## Common Pitfalls

**1. Hardcoded colors** — `Color.White` in a composable. Fix: all colors via `MaterialTheme.colorScheme.*`.

**2. Missing `modifier` parameter** — Composable cannot be resized by caller. Fix: every public composable takes `modifier: Modifier = Modifier` on its outermost layout.

**3. SharedFlow vs StateFlow for events** — Toast fires again on rotation. Fix: events = `MutableSharedFlow(replay=0)`. State = `MutableStateFlow(initial)`.

**4. Shared element key mismatch** — Navigation works but no transition fires. Fix: build from stable entity ID. Log both sides and compare.

**5. SharedTransitionLayout not wrapping NavHost** — `IllegalStateException: No SharedTransitionScope`. Fix: `SharedTransitionLayout { NavHost { } }` — must contain both source and destination.

**6. Missing renderInSharedTransitionScope** — Back button blinks into existence at transition end. Fix: apply `.renderInSharedTransitionScope(scope).animateEnterExit(...)` to destination-only elements.

**7. Blocking main thread** — ANR or UI freeze. Fix: `withContext(dispatchers.io)` for all I/O; never `runBlocking` on the main dispatcher.

**8. Spinner as only loading state** — `CircularProgressIndicator` centred on a blank background. Fix: `ShimmerBox` composable mirroring `Ready` geometry.

**9. Non-4dp spacing** — Visual rhythm feels slightly off; design review flags it. Fix: `AppSpacing.*` for every spacing value.

**10. collectAsState instead of collectAsStateWithLifecycle** — Flow collects in background. Fix: always `collectAsStateWithLifecycle()` for UI-bound collection.

**11. GlobalScope usage** — Coroutine leaks, ignores cancellation. Fix: `viewModelScope`, `lifecycleScope`, or `rememberCoroutineScope()`. Never `GlobalScope`.

**12. Images loaded at full resolution for thumbnails** — OOM in lists. Fix: `.size(width, height)` in `ImageRequest` matching display dimensions.
