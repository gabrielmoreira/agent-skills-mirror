---
name: gsap-web-animations
description: "Implements coordinated GSAP 3 motion (timelines, ScrollTrigger, Flip, MotionPath, Draggable, SplitText, ScrollSmoother, SSR hydration, prefers-reduced-motion). Use when designing, debugging, or refactoring JS-driven web animation (gsap.to, useGSAP, @gsap/react). Not for one-shot CSS hover or keyframes, Emil Kowalski UI polish (emil-design-eng), or Remotion frame timelines."
version: 1.0.1
---

# Web Animations with GSAP

A practical guide to building animations with GSAP that stay maintainable, performant, and inclusive. The intent is to explain *why* each pattern is preferred so you can adapt it rather than copy it verbatim.

> [!NOTE]
> * For CSS tokens, design variables, and layout-level UI work, see the [frontend-design](../frontend-design/SKILL.md) skill *if it is available in your environment*.
> * For generating characters, logos, illustrations, or other assets to animate, see the [creative-prompt-engineering](../creative-prompt-engineering/SKILL.md) skill *if available*.
> * As of GSAP 3.13 (following the Webflow acquisition, 2024) every plugin — including the previously paid `SplitText`, `MorphSVG`, `DrawSVG`, `ScrollSmoother`, `Inertia`, and `GSDevTools` — is free for all uses. If you previously avoided a plugin on licensing grounds, that constraint is gone.
> * TypeScript users: types ship inside the `gsap` package itself. Do **not** install `@types/gsap` (it would shadow the bundled types with stale community definitions).

---

## When to Use

Reach for this skill when motion is **coordinated** (multiple elements animating together), **scroll-linked** (progress tied to scroll position), or **performance-sensitive** (must hold 60fps on low-end hardware).

**Trigger keywords and signals:**

- The word "GSAP" or any GSAP API call: `gsap.to`, `gsap.fromTo`, `gsap.timeline`, `gsap.set`, `gsap.from`
- `ScrollTrigger`, `useGSAP`, `gsap.context()`, `gsap.matchMedia()`
- Plugin names: `Flip`, `MotionPath`, `MotionPathPlugin`, `Draggable`, `SplitText`, `ScrollSmoother`, `InertiaPlugin`, `GSDevTools`
- Stack mentions of `@gsap/react` or `gsap/dist/*`, `gsap/ScrollTrigger`
- SSR/hydration issues with GSAP in Next.js, Nuxt, Astro, or SvelteKit
- Jank, frame drops, or performance issues during scroll animations
- `prefers-reduced-motion` accessibility requirements

**When NOT to use this skill:**

- Purely declarative one-shot hover/focus transitions — native CSS transitions are simpler and lighter.
- "Fade in once when this enters the viewport" — `IntersectionObserver` + a CSS transition is smaller and needs no JS animation library.
- Pure `@keyframes` animations with no JS state.
- Native CSS `animation-timeline: scroll()` / `view()` if your target browsers support it (Chromium-only at time of writing — verify on caniuse before committing).

---

## Prerequisites

### Installation

```powershell
# Core package (includes TypeScript definitions)
npm install gsap

# React hook (optional, recommended for React 18+)
npm install @gsap/react
```

**Do NOT install `@types/gsap`** — it shadows the bundled types with stale community definitions.

### Plugin registration

GSAP plugins must be registered so tree-shaking bundlers don't drop them. The call is idempotent — registering twice does not break anything — but do it once at module scope (not in every component) to avoid redundant work on each mount and simplify static analysis for the bundler.

```javascript
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);
```

### Tree-shaking

Import each plugin from its own path rather than from the `gsap/all` umbrella:

```javascript
// CORRECT — tree-shakeable
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Flip } from 'gsap/Flip';

// AVOID — pulls everything
import { gsap, ScrollTrigger, Flip } from 'gsap/all';
```

The umbrella import is the universal mistake worth avoiding. Check actual sizes with your bundler analyzer rather than relying on quoted ranges.

### Environment constraints

- **SSR frameworks** (Next.js, Nuxt, Astro, SvelteKit): GSAP touches `window` and the DOM. Importing and running GSAP code at module top level during server render will throw. See [Procedure §SSR](#ssr--hydration-nextjs-nuxt-astro-sveltekit) below.
- **Test environments** (Jest, Vitest, jsdom): jsdom does not implement `requestAnimationFrame` reliably, `matchMedia`, `IntersectionObserver`, or layout. See [Pitfalls §Testing](#test-environments-jest-vitest-jsdom) below.

---

## Procedure

### 1. Timeline Construction & Sequencing

#### When a timeline beats individual tweens

A single `gsap.to(...)` is fine for a one-off effect. Once two or more animations need to coordinate — overlap, share defaults, be paused/reversed/seeked together, or be tied to a single scroll position — `gsap.timeline()` is the better tool. The timeline owns one playhead, supports relative offsets (`'-=0.4'`, `'<'`, `'>'`, labels), inherits defaults, and exposes `.pause()`, `.reverse()`, `.timeScale()`, and `.kill()` on the whole group.

#### Core timeline example

The hero entrance below leads with the header, overlaps the paragraph against the tail of the header, and starts the button and image on the same tick so the elements resolve into one composed image rather than four sequential motions.

```javascript
import { gsap } from 'gsap';

export function initializeHeroAnimation(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const header = container.querySelector('.hero-header');
  const paragraph = container.querySelector('.hero-paragraph');
  const button = container.querySelector('.hero-button');
  const image = container.querySelector('.hero-image');

  // `defaults` removes repetition: every child tween inherits these
  // unless it overrides them locally, so you can retune the whole
  // sequence by editing one object.
  const tl = gsap.timeline({
    defaults: { duration: 0.8, ease: 'power2.out' }
  });

  tl.fromTo(header,
      { opacity: 0, y: 50 },
      { opacity: 1, y: 0 }
    )
    .fromTo(paragraph,
      { opacity: 0, y: 30 },
      { opacity: 1, y: 0 },
      '-=0.4' // Start 0.4s before the previous tween ends. Overlapping
              // tweens during the tail of the prior motion tend to read
              // as one continuous beat; the exact overlap is a feel
              // decision — start around a quarter of the prior duration
              // and adjust by eye.
    )
    .fromTo(button,
      { opacity: 0, scale: 0.8 },
      { opacity: 1, scale: 1 },
      '-=0.3'
    )
    .fromTo(image,
      { opacity: 0, x: 50 },
      { opacity: 1, x: 0 },
      '<' // Start at the same time as the previous tween (the button).
          // Use this when two elements should resolve on the same beat.
    );

  return tl;
}
```

#### Timeline tips

1. **Add labels when relative offsets stop reading clearly.** If reordering an earlier tween would silently shift later offsets, switch to `tl.addLabel('reveal')` and place subsequent tweens at the label. Labels are order-independent and self-documenting.
2. **Use `stagger` instead of a `forEach` loop of tweens.** It runs through GSAP's single ticker, supports `{ each, from: 'center' | 'end' | index, grid: [rows, cols] }`, and stays in lockstep with the parent timeline's playhead.
3. **Pick eases for the action, not the aesthetic.**
   - `power2.out` — decelerates; conventionally read as arriving/settling.
   - `power2.in` — accelerates; read as leaving.
   - `back.out` — overshoots and settles.
   - `none` (linear) — usually right for scroll-scrubbed motion because the user's scroll already provides the curve.

---

### 2. Scroll-Linked Animations (ScrollTrigger)

#### When ScrollTrigger is the right tool

`IntersectionObserver` tells you *whether* an element is visible. `ScrollTrigger` tells you *how far through* a scroll range you are, lets you pin an element while progressing a timeline, batches DOM reads/writes to avoid layout thrash, and integrates with timelines so the same code can drive both "play on enter" and "scrub with scroll position."

#### Scroll-scrubbed, pinned section

The workhorse pattern for narrative sections: the user scrolls, the section stays in place, and the timeline progresses in lockstep with the scroll position.

```javascript
export function setupScrollTimeline(sectionId) {
  const section = document.getElementById(sectionId);
  if (!section) return;

  const cards = section.querySelectorAll('.scroll-card');
  const title = section.querySelector('.scroll-title');

  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: section,
      start: 'top top',     // Activate when the section's top reaches
                            // the viewport's top.
      end: '+=1000',        // The trigger range spans 1000px of scroll
                            // beyond `start`.
      scrub: 0.5,           // Number, not boolean: a smoothing duration
                            // in seconds. With `scrub: true` the playhead
                            // snaps exactly to the latest scroll sample,
                            // which can read as twitchy on trackpads.
                            // A numeric value (~0.3–0.8s) eases the
                            // playhead toward the target position over
                            // that window; it's not a flat delay, it's
                            // a catch-up duration, so the animation
                            // still feels coupled to scroll while small
                            // jitter is damped out.
      pin: true,            // Hold the section visually fixed during the
                            // active range (see pinning notes below).
      anticipatePin: 1,     // Promote the element to its own compositor
                            // layer one tick before the pin engages, so
                            // the first pinned frame doesn't stutter
                            // while the browser builds the layer.
                            // Trade-off: each promoted layer costs GPU
                            // memory. `0` (default) is fine if you don't
                            // see a first-frame jump; raise to `1`
                            // (sometimes `2`) only if you do.
      invalidateOnRefresh: true, // On refresh (font load, resize, viewport
                                 // change), re-read `fromTo` starting
                                 // values rather than reusing stale ones.
      // markers: true,     // Dev-only: draws start/end indicators in
                            // the page so you can verify trigger
                            // positions.
    }
  });

  tl.to(title, { opacity: 0.2, scale: 0.9 })
    .fromTo(cards,
      { opacity: 0, y: 100 },
      { opacity: 1, y: 0, stagger: 0.15 }
    );

  return tl;
}
```

#### `toggleActions` for non-scrubbed reveals

When a section should *play* (not scrub) on entry and reverse on exit, `toggleActions` defines behavior at each of the four edges: `onEnter onLeave onEnterBack onLeaveBack`.

```javascript
gsap.from('.feature', {
  scrollTrigger: {
    trigger: '.feature',
    start: 'top 80%',
    // Play forward on first enter; reverse when scrolling back above.
    // Pause looping/expensive animations when the section leaves the
    // viewport so they don't burn CPU offscreen.
    toggleActions: 'play pause resume pause'
  },
  y: 60,
  opacity: 0,
  duration: 0.6
});
```

#### Pinning, refresh, and responsiveness

1. **What pinning actually does.** During the active range, ScrollTrigger fixes the element's position and inserts a same-sized spacer into the DOM so surrounding layout does not collapse. Content above and below stays where it should; anything that depended on the element being in normal flow during the pin window (e.g., sticky siblings, container queries on the parent) may behave unexpectedly.

2. **When to set `pinSpacing: false`.** Only when the spacer itself causes a layout bug — for example, pinning *inside* a fixed-height parent where the spacer pushes other children out of bounds, or pinning an element whose space was already reserved by an explicit `min-height` on its container. In normal page flow, leaving the spacer in is what keeps subsequent content from jumping.

3. **iOS Safari quirks.** Mobile Safari's URL bar resizes the viewport on scroll, which fires layout changes mid-pin and can cause the pinned element to jump. `ScrollTrigger.normalizeScroll(true)` (GSAP 3.10+) routes scroll through GSAP's own pipeline and smooths most of these artifacts. Trade-offs: it intercepts native scroll events, which can break momentum scrolling on some trackpads, conflicts with elements that have their own custom scroll handling, and stacks awkwardly with `ScrollSmoother` (use one or the other, not both). Try it scoped to mobile via `gsap.matchMedia()` before turning it on globally.

4. **Mobile keyboard.** Soft-keyboard appearance resizes the visual viewport on mobile, same family of bug as the iOS URL bar but triggered by focusing form inputs. If a scroll-linked section contains forms, expect to re-measure on focus/blur or accept some jitter.

5. **Refresh after layout changes.** If web fonts load late, images reflow, you toggle responsive states, or the user switches themes (line-heights can shift with font-weights), trigger positions calculated at first paint will be wrong. Call `ScrollTrigger.refresh()` after the change settles. Pass `true` (`ScrollTrigger.refresh(true)`) to force a full recalculation even if GSAP would otherwise skip it — useful after font swaps when nothing in the DOM changed but measurements did.

6. **bfcache restores (back/forward navigation).** Safari and Firefox restore pages from the back/forward cache without re-running scripts, so ScrollTrigger keeps measurements from the previous visit even though scroll position and viewport may differ. Hook `pageshow` and refresh when the event was a bfcache restore:
   ```javascript
   window.addEventListener('pageshow', (e) => {
     if (e.persisted) ScrollTrigger.refresh();
   });
   ```

7. **Custom scroll containers.** Every example above assumes the document scrolls. If the scrollable element is a child container (modal, drawer, sidebar), pass `scroller: '.my-container'` to every trigger that lives inside it. For pinning inside a custom scroller, `pinType: 'transform'` is more reliable than `'fixed'` (the default for body-scroll), since `position: fixed` is anchored to the viewport, not to the scroll container.

8. **Use `gsap.matchMedia()` for breakpoints**, not manual resize listeners that destroy and recreate triggers. `matchMedia` registers per-breakpoint setups and runs the returned cleanup when the query stops matching:
   ```javascript
   const mm = gsap.matchMedia();
   mm.add('(min-width: 768px)', () => {
     gsap.to('.hero', { scrollTrigger: { /* ... */ }, x: 200 });
     return () => { /* per-breakpoint cleanup, if any */ };
   });
   ```

---

### SSR & hydration (Next.js, Nuxt, Astro, SvelteKit)

GSAP touches `window` and the DOM, so importing and *running* GSAP code at module top level during server render will throw. Two reliable patterns:

1. **Run GSAP only after mount.** `useEffect` (React), `onMounted` (Vue/Nuxt), `onMount` (Svelte). The component renders server-side without animation; client hydration then attaches the timeline.

2. **Treat plugins that touch globals as client-only.** `ScrollTrigger`, `ScrollSmoother`, and `Draggable` interact with `window` and scroll listeners.
   - **Next.js App Router (13+):** mark the animation component with `'use client'`. Server Components cannot import `gsap` *at all* — the import is evaluated at build/SSR time and `window` is undefined. Pages Router doesn't need the directive (everything is a client component).
   - **Astro:** mount inside a `client:load` (or `client:visible`) island.
   - **Nuxt:** wrap in `<ClientOnly>` or guard with `import.meta.client` (or the legacy `process.client`).
   - **SvelteKit:** run inside `onMount` (or guard with `browser` from `$app/environment`).

3. **React Suspense / streaming SSR.** If a child component lives behind a suspended boundary, it may not exist in the DOM when a parent's `useGSAP` first runs. Either set up animations *inside* the suspended child (so its own mount fires the effect) or pass the relevant element refs/dependencies to `useGSAP`'s dependency array so the setup re-runs after the boundary resolves.

A common bug is *hydration mismatch*: if GSAP sets inline styles before the framework hydrates, the client's expected DOM will not match the server-rendered HTML. Always make the first GSAP call *after* the mount hook fires.

---

### 3. Performance & Lifecycle

#### What actually costs frame budget

The browser's render pipeline is roughly *style → layout → paint → composite*. Changing `width`, `height`, `top`, `left`, `margin`, or `padding` forces relayout of the page, which is the expensive part. Changing `transform` and `opacity` skips to composite because both are handled on the GPU layer. This is why most GSAP examples animate `x`, `y`, `scale`, `rotation`, and `opacity` rather than positional properties — it is a frame-time budget concern, not a stylistic convention.

The gap is most visible on low-end hardware; Chrome DevTools' CPU throttling is the standard proxy when you don't have a physical low-end device on hand. Chrome's own docs label `4×` as "low-end mobile" — use it as a reasonable midpoint and step up to `6×` for an explicitly stricter target.

#### Performance guidelines

1. **Animate `transform` and `opacity` whenever possible.** If you genuinely need a size change, use `scale` with a corrected `transform-origin`, or use the `Flip` plugin, which snapshots layout before and after a DOM/class change and animates the diff with transforms only.

2. **Apply `will-change` just before animation; remove it after.** `will-change: transform, opacity` asks the browser to pre-promote the element to its own compositor layer, eliminating the first-frame promotion stutter. Each promoted layer costs memory, and over-promoting many elements can *slow* rendering down. For continuous loops (e.g., a marquee), set it in CSS. For one-shot tweens, either set `gsap.set(el, { willChange: 'transform' })` just before and clear it in the tween's `onComplete`, or rely on GSAP's default `force3D: 'auto'` behaviour.

3. **What `force3D` actually controls.** It decides whether GSAP appends a 3D hint (e.g. `translateZ(0)`) to the `transform` it writes, which is what triggers layer promotion.
   - `'auto'` (default) — promotes for the duration of the tween and releases afterward. The right default in almost every case.
   - `true` — keeps the element promoted permanently. Use only for elements you'll animate again immediately; the layer stays in GPU memory.
   - `false` — disables the hint entirely. Rare — useful when you need to avoid layer promotion because it's interacting badly with `backdrop-filter` or text rendering.

4. **Tree-shake your imports.** Import each plugin from its own path (`import { ScrollTrigger } from 'gsap/ScrollTrigger'`) rather than from the `gsap/all` umbrella.

5. **Kill timelines and triggers on unmount.** GSAP's global ticker holds references to tween targets. If the DOM node is removed but the timeline is not killed, you get memory leaks and console errors from tweening orphaned elements.

6. **Prefer scoped cleanup primitives** (`gsap.context()` or, in React, the `useGSAP` hook from `@gsap/react`) over manually tracking refs to every timeline and ScrollTrigger.

#### React: `useGSAP` (current recommended pattern)

The `@gsap/react` package's `useGSAP` hook wraps `gsap.context()` and handles cleanup on unmount automatically. It is the pattern GSAP currently recommends for React 18+. The hook collects every animation, timeline, and ScrollTrigger created inside its callback *via the GSAP API* and reverts them on unmount or dependency change.

```tsx
import React, { useRef } from 'react';
import { gsap } from 'gsap';
import { useGSAP } from '@gsap/react';

export const AnimatedCard: React.FC = () => {
  const rootRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    // Selectors here are scoped to rootRef.current.
    // useGSAP collects every tween/timeline/ScrollTrigger created in
    // this callback and reverts them on unmount or dependency change.
    gsap.timeline({ repeat: -1, yoyo: true })
      .to('.floating-element', { y: -20, duration: 1 })
      .to('.floating-element', { y: 0, duration: 1 });
  }, { scope: rootRef });

  return <div ref={rootRef}><div className="floating-element" /></div>;
};
```

#### Non-React cleanup with `gsap.context()`

For Vue, Svelte, or vanilla JS, use `gsap.context()` to scope selectors and batch cleanup:

```javascript
import { gsap } from 'gsap';

let ctx;

function setupAnimations() {
  ctx = gsap.context(() => {
    gsap.to('.box', { x: 100, duration: 1 });
    gsap.timeline().to('.box', { y: 50 });
  });
}

function cleanupAnimations() {
  ctx.revert(); // Reverts all animations created inside the context
}
```

#### React Strict Mode and HMR

- **React Strict Mode** double-invokes effects in development. `useGSAP` (and the `useEffect` + `gsap.context()` pattern) handle this correctly because `ctx.revert()` undoes the first run before the second begins, so animations don't double up. If you instead use a hand-rolled `useEffect` that doesn't revert or kill on cleanup, you'll see "my entrance animation plays twice and the second copy starts mid-flight in dev only" — the fix is to put the work in a context (or use `useGSAP`), not to disable Strict Mode.

- **Hot Module Replacement.** During dev, HMR re-runs modules without unmounting components, which can leave orphan `ScrollTrigger` instances from the previous module version. `gsap.context()` / `useGSAP` clean these up on the next render. As a belt-and-suspenders option for ScrollTrigger-heavy modules, add a dispose hook:
  ```javascript
  if (import.meta.hot) {
    import.meta.hot.dispose(() => {
      ScrollTrigger.getAll().forEach(t => t.kill());
    });
  }
  ```

---

### 4. Accessibility & `prefers-reduced-motion`

#### Why it matters

Vestibular disorders, migraines, and motion sensitivity can make parallax, scrubbed transitions, and large translations physically uncomfortable. The `prefers-reduced-motion: reduce` media query is the standard signal users send when they want less motion. WCAG 2.1 Success Criterion 2.3.3 (Animation from Interactions, Level AAA) specifically calls out respecting this preference for non-essential motion triggered by interaction.

Reduced motion does not mean *no* feedback — users still need to perceive that something changed. The right transformation is usually: keep the opacity change, drop the translation/scale, shorten the duration to something perceptible but not lingering (a couple hundred milliseconds is a defensible starting point — choose by feel, not by rule), and switch to a linear or gentle ease.

#### Page-wide pattern with `gsap.matchMedia()`

`gsap.matchMedia()` registers motion-rich and motion-reduced variants once and swaps between them if the user toggles their OS setting mid-session, so individual call sites do not each need to re-check the media query.

```javascript
import { gsap } from 'gsap';

const mm = gsap.matchMedia();

mm.add({
  reducedMotion: '(prefers-reduced-motion: reduce)',
  fullMotion: '(prefers-reduced-motion: no-preference)'
}, (context) => {
  // Read explicitly with === true so a missing/undefined condition
  // (rare, e.g. during a media-query transition) falls through to the
  // full-motion branch deliberately, not by accident.
  const reduced = context.conditions.reducedMotion === true;

  gsap.fromTo('.reveal',
    { opacity: 0, y: reduced ? 0 : 40 },
    {
      opacity: 1,
      y: 0,
      duration: reduced ? 0.2 : 0.8,
      ease: reduced ? 'none' : 'power2.out',
      stagger: reduced ? 0 : 0.1
    }
  );

  // Returned cleanup runs when the matched conditions stop applying.
  return () => { /* per-variant cleanup */ };
});
```

#### Ad-hoc check for a single tween

When a `matchMedia` registry is overkill (one-off interaction, a third-party component you don't own), an inline check is fine:

```javascript
const prefersReduced =
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;
gsap.fromTo(el,
  { opacity: 0, x: prefersReduced ? 0 : -100 },
  { opacity: 1, x: 0, duration: prefersReduced ? 0.2 : 0.8 }
);
```

#### Other accessibility considerations

- **WCAG 2.2.2 (Pause, Stop, Hide)** applies to *moving, blinking, or auto-updating* content that (a) starts automatically, (b) lasts longer than five seconds, **and** (c) is presented in parallel with other content. When all three conditions are met, provide a way to pause, stop, or hide it. A decorative loop that meets (a) but not (b) or (c) is out of scope.
- **WCAG 2.3.1 (Three Flashes)** — avoid content that flashes more than three times per second, to protect photosensitive users.
- **Continuous motion adjacent to body text** (a looping marquee or parallax background sharing a reading flow with paragraphs of copy) measurably degrades reading comprehension for some users. Pause such loops when offscreen via `toggleActions: 'play pause resume pause'`, and prefer animations that resolve to a stable state over those that loop indefinitely near long-form text.

---

### 5. Plugins

All of the following are free as of GSAP 3.13. The lifecycle, cleanup, performance, and reduced-motion guidance above applies to every one of them.

#### ScrollSmoother

Adds inertia/easing to native scrolling on the body. Use sparingly: it overrides default browser scrolling and can confuse users on trackpads who expect native feel. Provide an opt-out (or disable entirely) under `prefers-reduced-motion`. **Do not combine with `ScrollTrigger.normalizeScroll(true)` — pick one.**

#### Flip

Records a "before" snapshot of element positions, lets you mutate the DOM (reorder, change classes, swap parents), then animates from the recorded state to the new layout using transforms only. Canonical solution for shared-element transitions, list reorders, and expand/collapse where layout actually changes.

```javascript
import { gsap } from 'gsap';
import { Flip } from 'gsap/Flip';

gsap.registerPlugin(Flip);

// 1. Snapshot the before state
const state = Flip.getState('.card');

// 2. Mutate the DOM (reorder, change classes, etc.)
document.querySelector('.card').classList.add('expanded');

// 3. Animate from the old state to the new
Flip.from(state, { duration: 0.5, ease: 'power2.out' });
```

#### MotionPathPlugin

Animates elements along an SVG path or set of bezier points. Use when motion semantically follows a curve (a falling leaf, an arc into a target) rather than a straight line.

```javascript
import { gsap } from 'gsap';
import { MotionPathPlugin } from 'gsap/MotionPathPlugin';

gsap.registerPlugin(MotionPathPlugin);

gsap.to('.dot', {
  motionPath: {
    path: '#myPath', // SVG path element selector
    align: '#myPath',
    alignOrigin: [0.5, 0.5]
  },
  duration: 3,
  ease: 'none'
});
```

#### Draggable

Pointer/touch dragging with optional inertia (via `InertiaPlugin`), bounds, snapping, and edge resistance. Substantially less code than hand-rolling pointer events.

```javascript
import { gsap } from 'gsap';
import { Draggable } from 'gsap/Draggable';

gsap.registerPlugin(Draggable);

Draggable.create('.box', {
  type: 'x,y',
  bounds: '.container',
  inertia: true, // requires InertiaPlugin
  snap: { x: [0, 100, 200], y: [0, 50, 100] }
});
```

#### SplitText

Splits text nodes into per-character, per-word, or per-line wrappers so each can be tweened independently.

- **Accessibility:** set `aria-label` on the parent to the original string so screen readers announce the whole word/sentence rather than one letter at a time.
- **Dynamic content / font swaps:** line-wrapping depends on the font, so a `SplitText` instance made before a webfont loads will fragment differently afterward. Call `split.revert()` then re-split on `document.fonts.ready`, and re-split (plus `ScrollTrigger.refresh()`) when the underlying text changes.

```javascript
import { gsap } from 'gsap';
import { SplitText } from 'gsap/SplitText';

gsap.registerPlugin(SplitText);

const split = new SplitText('.headline', { type: 'chars, words, lines' });
gsap.from(split.chars, {
  opacity: 0,
  y: 20,
  stagger: 0.02,
  duration: 0.4,
  ease: 'power2.out'
});
```

#### ScrollTrigger

Covered in detail in [§2 above](#2-scroll-linked-animations-scrolltrigger).

---

## Pitfalls

### Hydration mismatch

If GSAP sets inline styles before the framework hydrates, the client's expected DOM will not match the server-rendered HTML. **Always make the first GSAP call after the mount hook fires** (`useEffect`, `onMounted`, `onMount`).

### Server Components importing GSAP

Next.js App Router Server Components cannot import `gsap` *at all* — the import is evaluated at build/SSR time and `window` is undefined. Mark animation components with `'use client'`.

### Test environments (Jest, Vitest, jsdom)

jsdom does not implement `requestAnimationFrame` reliably, `matchMedia`, `IntersectionObserver`, or layout, so plugins like `ScrollTrigger` will either throw or silently no-op in unit tests. Two practical paths:

1. **Mock the plugin** in tests that don't care about animation:
   ```javascript
   jest.mock('gsap/ScrollTrigger', () => ({
     ScrollTrigger: {
       create: jest.fn(),
       refresh: jest.fn(),
       getAll: () => []
     }
   }));
   ```

2. **Run animation-touching code in a real-browser test runner** (Playwright, Cypress, WebdriverIO) where layout and scrolling actually work.

### Memory leaks from un-killed timelines

GSAP's global ticker holds references to tween targets. If the DOM node is removed but the timeline is not killed, you get memory leaks and console errors from tweening orphaned elements. Always use `gsap.context()` / `useGSAP` for scoped cleanup, or manually call `.kill()` on timelines and `ScrollTrigger.getAll().forEach(t => t.kill())` on unmount.

### Stale ScrollTrigger measurements

Trigger positions calculated at first paint will be wrong after:
- Web fonts loading late
- Images reflowing
- Responsive state toggles
- Theme switches (line-heights can shift with font-weights)

Call `ScrollTrigger.refresh()` after the change settles. Pass `true` to force a full recalculation.

### bfcache restore issues

Safari and Firefox restore pages from the back/forward cache without re-running scripts. Hook `pageshow` and refresh:
```javascript
window.addEventListener('pageshow', (e) => {
  if (e.persisted) ScrollTrigger.refresh();
});
```

### iOS Safari URL bar jitter

Mobile Safari's URL bar resizes the viewport on scroll, causing pinned elements to jump. Try `ScrollTrigger.normalizeScroll(true)` scoped to mobile via `gsap.matchMedia()`. **Do not combine with `ScrollSmoother` — use one or the other.**

### SplitText before font load

Line-wrapping depends on the font. A `SplitText` instance made before a webfont loads will fragment differently afterward. Call `split.revert()` then re-split on `document.fonts.ready`.

### ScrollSmoother + normalizeScroll conflict

Do not combine `ScrollSmoother` with `ScrollTrigger.normalizeScroll(true)`. They both intercept scroll events and stack awkwardly. Pick one.

### Animating layout properties instead of transforms

Animating `width`, `height`, `top`, `left`, `margin`, or `padding` forces relayout — the expensive part of the render pipeline. Animate `x`, `y`, `scale`, `rotation`, and `opacity` instead, which skip to composite on the GPU.

### Over-promoting layers with `will-change`

Each promoted layer costs GPU memory, and over-promoting many elements can *slow* rendering down. Set `will-change` just before animation and remove it after. For one-shot tweens, rely on GSAP's default `force3D: 'auto'` which promotes for the duration of the tween and releases afterward.

### Installing `@types/gsap`

Do **not** install `@types/gsap`. Types ship inside the `gsap` package itself. The community `@types/gsap` package shadows the bundled types with stale definitions.

### Umbrella imports

Avoid `import { ... } from 'gsap/all'`. It pulls every plugin and prevents tree-shaking. Import each plugin from its own path.

---

## Verification

### Confirm animations are running

1. **Check GSAP is loaded and registered:**
   ```javascript
   // In browser console
   console.log('GSAP version:', gsap.version);
   console.log('Registered plugins:', gsap.ticker.lagSmoothing);
   ```

2. **Enable ScrollTrigger markers (dev only):**
   ```javascript
   scrollTrigger: {
     markers: true, // Draws start/end indicators on the page
   }
   ```
   Verify start/end lines align with your intended trigger positions.

3. **Check active ScrollTrigger instances:**
   ```javascript
   // In browser console
   ScrollTrigger.getAll().forEach(t => console.log(t.trigger, t.start, t.end));
   ```

### Confirm jank in DevTools

Open DevTools → Performance, record a few seconds of the offending animation, and read the timeline:

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Long purple **Layout** or green **Paint** bars | Layout-triggering property being animated | Convert to `transform`/`opacity` |
| Long yellow **Scripting** bars synchronous with scroll | Too much work in `scrollTrigger.onUpdate` | Debounce, hoist allocations, or precompute |
| Dropped frames with idle main thread | Compositor-side bottleneck (too many layers, large images, heavy `filter`/`box-shadow`) | Reduce layer count or simplify visual filters |

Fix the underlying cause rather than masking it with `will-change`.

### Verify reduced-motion behavior

1. Open Chrome DevTools → Rendering tab (three-dot menu → More tools → Rendering).
2. Toggle **Emulate CSS media feature `prefers-reduced-motion`** to `reduce`.
3. Confirm animations switch to the reduced variant (shorter duration, no translation/scale, linear ease).
4. Toggle back to `no-preference` and confirm full-motion variant resumes.

### Verify cleanup on unmount

1. In React DevTools, mount and unmount the animated component.
2. Check the console for errors about tweening orphaned elements.
3. Verify `ScrollTrigger.getAll()` returns no instances from the unmounted component:
   ```javascript
   // After unmount
   console.log('Remaining triggers:', ScrollTrigger.getAll().length);
   ```

### Verify SSR doesn't throw

1. Run the production build:
   ```powershell
   npm run build
   ```
2. Check for `window is not defined` or `document is not defined` errors during the build/SSR phase.
3. Confirm the page renders without animation server-side, then animations attach after client hydration.

### Verify tree-shaking

1. Run the bundler analyzer:
   ```powershell
   # Next.js
   npx @next/bundle-analyzer

   # Vite
   npx vite-bundle-visualizer
   ```
2. Confirm `gsap` core and only the plugins you imported appear in the bundle.
3. If `gsap/all` appears, switch to per-plugin imports.

---

## Quick Reference Index

- **Timelines, offsets, labels, eases** — [Procedure §1](#1-timeline-construction--sequencing)
- **ScrollTrigger basics, scrub vs. toggleActions** — [Procedure §2](#2-scroll-linked-animations-scrolltrigger)
- **Pinning, pinSpacing, iOS jitter, mobile keyboard, theme/font refresh, bfcache, custom scroll containers, matchMedia breakpoints** — [Procedure §2 Pinning](#pinning-refresh-and-responsiveness)
- **SSR / hydration / Server Components / Suspense** — [Procedure SSR](#ssr--hydration-nextjs-nuxt-astro-sveltekit)
- **Test environments (Jest/Vitest/jsdom)** — [Pitfalls §Testing](#test-environments-jest-vitest-jsdom)
- **What costs frame budget, transform vs layout properties, will-change, force3D, tree-shaking** — [Procedure §3](#3-performance--lifecycle)
- **useGSAP, non-GSAP cleanup, Strict Mode, HMR** — [Procedure §3 React](#react-usegsap-current-recommended-pattern)
- **Diagnosing jank in DevTools** — [Verification §Confirm jank](#confirm-jank-in-devtools)
- **prefers-reduced-motion patterns** — [Procedure §4](#4-accessibility--prefers-reduced-motion)
- **Plugins (ScrollSmoother, Flip, MotionPath, Draggable, SplitText)** — [Procedure §5](#5-plugins)
