---
name: motion
description: "Implements React UI animation with Motion (motion/react, formerly Framer Motion): layout, AnimatePresence exits, layoutId, gestures, useScroll, and reduced-motion. Use when animating React components, shared-element transitions, or scroll-linked effects. Not for Remotion frame timelines (remotion-video), GSAP/Lottie/Rive authoring, or Three.js scenes."
version: 1.0.1
---

# Motion (formerly Framer Motion) Animation for React

## Overview

Motion is the production-ready animation library for React (formerly Framer Motion). It provides a declarative API where animations are defined as props rather than imperative code. Use it for fluid animations, layout transitions, scroll-linked effects, gesture interactions, shared layout animations, and exit animations.

**Package:** `motion` — import from `"motion/react"` (not `"framer-motion"`).

**Official docs:** https://motion.dev/docs/react

## When to Use

Use this skill when the user asks for any of the following:

- **Mount/entrance animations** — fade-in, slide-in, scale-in on component mount
- **Exit animations** — elements animating out before unmount (requires `AnimatePresence`)
- **Layout animations** — automatic size/position transitions when layout changes
- **Shared layout animations** — elements that visually travel between components (tab indicators, expanding cards)
- **Scroll-linked effects** — parallax, scroll-triggered reveals, progress bars
- **Gesture interactions** — `whileHover`, `whileTap`, `whileDrag`, `whileFocus`
- **Staggered children** — sequenced list or grid entrance animations
- **Motion accessibility** — respecting `prefers-reduced-motion`, designing reduced-motion variants
- **Motion system design** — duration/easing tokens, spring tuning, interruption rules

**Trigger keywords:** motion, framer-motion, animation, animate, whileInView, AnimatePresence, layoutId, useScroll, useTransform, stagger, reduced-motion, parallax, spring, transition, exit animation, layout animation.

## Prerequisites

1. **Node.js** installed and a React project (Next.js, Vite, CRA, or similar).
2. **Install the package:**

```bash
npm install motion
```

3. **Verify installation on Windows (PowerShell):**

```powershell
npm ls motion
```

Expected output shows `motion@x.x.x` with no `UNMET DEPENDENCY` errors.

4. **Import path** is always `"motion/react"`:

```tsx
import { motion, AnimatePresence, useScroll, useTransform } from "motion/react";
```

> **Do not** import from `"framer-motion"` in new projects. The package was renamed to `motion`. Legacy `"framer-motion"` imports still work for backward compatibility but are not recommended for new code.

## Procedure

### 1. Basic Mount Animation

Animate a component from an `initial` state to an `animate` target on mount.

```tsx
import { motion } from "motion/react";

function FadeIn({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}
```

- `initial` — starting state before first render.
- `animate` — target state; Motion animates to this on mount and whenever it changes.
- `transition` — timing config: `duration` + `ease`, or `type: "spring"` with `stiffness`/`damping`.

### 2. Hover and Tap Gestures

```tsx
function InteractiveCard({ title }: { title: string }) {
  return (
    <motion.div
      className="card"
      whileHover={{ scale: 1.05, boxShadow: "0 10px 30px rgba(0,0,0,0.12)" }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      <h3>{title}</h3>
    </motion.div>
  );
}
```

- `whileHover` — state when pointer is over the element.
- `whileTap` — state when pointer is pressed.
- `whileFocus` — state when element receives focus (useful for accessibility-visible focus animation).
- `whileDrag` — state during drag (requires `drag` prop).

### 3. Exit Animations with AnimatePresence

Wrap conditionally rendered or list children in `AnimatePresence` to animate them out before unmount.

```tsx
function NotificationList({ notifications }: { notifications: Notification[] }) {
  return (
    <AnimatePresence>
      {notifications.map((n) => (
        <motion.div
          key={n.id}
          initial={{ opacity: 0, x: 100 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -100, height: 0 }}
          transition={{ type: "spring", damping: 25 }}
        >
          {n.message}
        </motion.div>
      ))}
    </AnimatePresence>
  );
}
```

**HARD RULES for AnimatePresence:**
- Every direct child **must** have a unique `key` prop.
- `AnimatePresence` only animates its **direct children** — do not wrap an extra layer between `AnimatePresence` and the `motion` components.
- The `exit` prop is required on each child for exit animation to fire.
- `mode="wait"` makes exit complete before enter starts; default mode fires both simultaneously.

### 4. Layout Animations

Add the `layout` prop to any `motion` element to automatically animate size and position changes.

```tsx
function ExpandableCard({ isExpanded, onClick, children }: Props) {
  return (
    <motion.div
      layout
      onClick={onClick}
      style={{
        width: isExpanded ? 400 : 200,
        height: isExpanded ? 300 : 100,
      }}
      transition={{ layout: { type: "spring", stiffness: 200 } }}
    >
      <motion.h3 layout="position">Title</motion.h3>
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
```

- `layout` — animates any layout change (size + position).
- `layout="position"` — animates only position, not size; prevents text reflow during animation.
- `layoutId="sharedId"` — same `layoutId` on two elements in different components creates a shared animation between them (tab indicators, expanding image galleries).

**Shared layout example:**

```tsx
function TabLayout({ activeTab }: { activeTab: string }) {
  return (
    <div className="tabs">
      {tabs.map((tab) => (
        <button key={tab.id} onClick={() => setActive(tab.id)}>
          {tab.label}
          {activeTab === tab.id && (
            <motion.div
              layoutId="activeTab"
              className="underline"
              transition={{ type: "spring", stiffness: 500, damping: 30 }}
            />
          )}
        </button>
      ))}
    </div>
  );
}
```

### 5. Scroll Animations

**Scroll-triggered entrance with `whileInView`:**

```tsx
function ScrollReveal({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.6 }}
    >
      {children}
    </motion.div>
  );
}
```

- `viewport={{ once: true }}` — animate only the first time it enters viewport.
- `margin` — offset the viewport detection boundary (e.g., `"-100px"` triggers 100px before fully visible).

**Scroll-linked parallax with `useScroll` + `useTransform`:**

```tsx
import { motion, useScroll, useTransform } from "motion/react";

function ParallaxHero() {
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 500], [0, -150]);
  const opacity = useTransform(scrollY, [0, 300], [1, 0]);

  return (
    <motion.div style={{ y, opacity }} className="hero">
      <h1>Welcome</h1>
    </motion.div>
  );
}
```

- `useScroll()` returns a `MotionValue` tracking scroll position.
- `useTransform(input, inputRange, outputRange)` maps the scroll value to an output range.
- Pass `MotionValue`s to the `style` prop — do **not** pass them to `animate` or `initial`.

### 6. Staggered Children

Use `variants` with `staggerChildren` to sequence child animations.

```tsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

function StaggeredList({ items }: { items: { id: string; name: string }[] }) {
  return (
    <motion.ul variants={container} initial="hidden" animate="show">
      {items.map((i) => (
        <motion.li key={i.id} variants={item}>
          {i.name}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

- Parent defines `staggerChildren` in its `transition`.
- Children inherit the parent's `initial`/`animate` variant labels automatically — do **not** set `initial`/`animate` on children if you want them to inherit.
- Each child must have `variants` matching the same label names (`hidden`, `show`).

### 7. Motion Accessibility (Reduced Motion)

**HARD RULE:** Always respect `prefers-reduced-motion`. Motion does not automatically disable animations.

```tsx
import { motion, useReducedMotion } from "motion/react";

function AccessibleFadeIn({ children }: { children: React.ReactNode }) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: shouldReduceMotion ? 0.01 : 0.5 }}
    >
      {children}
    </motion.div>
  );
}
```

- `useReducedMotion()` returns `true` when the user has reduced motion enabled at the OS/browser level.
- Design reduced-motion variants: disable movement (`y`, `x`, `scale`), keep opacity changes instant or very short.
- Never block task completion behind an animation.

### 8. Motion System Design

When building a motion system for a product:

1. **Start from purpose:** feedback, continuity, hierarchy, causality, spatial orientation, progress, or delight.
2. **Define motion tokens:** duration, easing, delay, distance, spring behavior, reduced-motion behavior, and interruption rules.
3. **Map states:** idle, hover, focus, active, pressed, loading, success, error, disabled, drag, drop, enter, exit, and route change.
4. **Choose technology by job:**
   - CSS transitions/animations — simple state changes, hover/focus
   - Motion — React layout/component animation, shared layout, scroll-linked
   - GSAP — complex timeline orchestration, ScrollTrigger
   - Lottie/Rive — authored vector animations from design tools
   - Three.js/WebGL — spatial 3D scenes
5. **Validate accessibility and performance before polish.**

## Examples

### Spring vs Tween

```tsx
// Spring — natural, physics-based
transition={{ type: "spring", stiffness: 300, damping: 20 }}

// Tween — precise duration control
transition={{ duration: 0.5, ease: "easeOut" }}

// Easing presets: "easeOut", "easeInOut", "circIn", "backOut", "anticipate"
```

### Keyframe Animations

```tsx
<motion.div
  animate={{
    scale: [1, 1.2, 1],
    rotate: [0, 180, 360],
  }}
  transition={{ duration: 2, repeat: Infinity, repeatType: "loop" }}
/>
```

### Drag with Constraints

```tsx
<motion.div
  drag
  dragConstraints={{ left: 0, right: 300, top: 0, bottom: 300 }}
  dragElastic={0.2}
  whileDrag={{ scale: 1.1 }}
  onDragEnd={(e, info) => console.log(info.point.x, info.point.y)}
/>
```

## Pitfalls

1. **Missing `key` on `AnimatePresence` children** — exit animations silently fail. Every direct child must have a stable, unique `key`.

2. **Importing from `"framer-motion"` in new projects** — use `"motion/react"` instead. The package was renamed. Legacy imports work but are deprecated for new code.

3. **Passing `MotionValue` to `animate` or `initial`** — `MotionValue`s (from `useScroll`, `useTransform`) go in the `style` prop, not `animate`/`initial`. Mixing them causes errors or no animation.

4. **Animating layout-triggering properties** — avoid animating `width`, `height`, `margin`, `padding`, `top`, `left` directly when possible. Prefer `transform` (`x`, `y`, `scale`) and `opacity` which are GPU-accelerated and do not cause layout thrashing. Use the `layout` prop for size changes instead of manual width/height animation.

5. **Forgetting `prefers-reduced-motion`** — Motion does not auto-disable animations. You must check `useReducedMotion()` and provide reduced-motion variants. This is a WCAG 2.2 requirement (2.3.3 Animation from Interactions).

6. **`layout` prop causing unexpected animations** — adding `layout` to a container will animate **any** layout change, including those caused by content loading or font swap. Use `layout="position"` if you only want position changes animated.

7. **`staggerChildren` not working** — children must have `variants` with matching label names and must **not** set their own `initial`/`animate` props (they inherit from parent).

8. **`whileInView` not triggering** — check `viewport` margin settings. If the element is below the fold and `once: true` is set, it will only animate when scrolled into view. Ensure the element is not `display: none` or zero-height.

9. **Animating too many SVG paths or large blurs** — these are expensive. Profile with Chrome DevTools Performance tab before shipping. Pause offscreen animations.

10. **Exit animation not firing on route changes** — `AnimatePresence` must wrap the route-level content, and each route component needs a stable `key` that changes on navigation. In Next.js App Router, this requires careful placement since layout components do not unmount on navigation by default.

11. **`AnimatePresence` with multiple children and no `mode`** — by default, enter and exit animations run simultaneously, which can cause overlap. Use `mode="wait"` if you need exit to complete before enter starts.

12. **Performance on low-power devices** — test with real content, long labels, mobile, desktop, zoom, and low-power devices. Pause offscreen and background animations.

## Verification

### Installation Check

```powershell
npm ls motion
```

Expected: `motion@x.x.x` listed with no errors.

### Import Path Check

Verify your imports use the correct path:

```powershell
Select-String -Path "src\**\*.tsx" -Pattern "from [`"']framer-motion[`"']" -Recurse
```

If any results appear, migrate them to `"motion/react"`.

### Reduced Motion Check

Verify `useReducedMotion` is used in components with movement animations:

```powershell
Select-String -Path "src\**\*.tsx" -Pattern "useReducedMotion" -Recurse
```

Any component using `y`, `x`, `scale`, `rotate` in `initial`/`animate`/`whileHover` should appear in results or have a documented reduced-motion fallback.

### AnimatePresence Key Check

Verify every `AnimatePresence` child has a `key`:

```powershell
Select-String -Path "src\**\*.tsx" -Pattern "AnimatePresence" -Recurse
```

Manually inspect each match to confirm direct children have unique `key` props.

### Runtime Verification

1. **Mount animation:** Load the page — element should animate from `initial` to `animate` state on first render.
2. **Exit animation:** Remove an item from the list — it should animate out (not instantly disappear).
3. **Layout animation:** Toggle a size/position change on a `layout` element — it should smoothly transition.
4. **Scroll animation:** Scroll the page — `whileInView` elements should animate when entering viewport; `useScroll` elements should move with scroll.
5. **Reduced motion:** Enable reduced motion in OS settings (Windows: Settings → Accessibility → Visual effects → Animation effects → Off) — animations should be instant or minimal.
6. **Performance:** Open Chrome DevTools → Performance tab → Record interaction → confirm no long tasks (>50ms) or layout thrashing during animation.

## Related Skills

- **css-animations** — for simple state transitions that do not need React lifecycle integration
- **gsap** — for complex timeline orchestration and ScrollTrigger
- **accessibility** — for WCAG 2.2 compliance, focus management, and reduced-motion requirements
- **design-system** — for motion token definitions and design system integration

## Current References

- Motion for React docs: https://motion.dev/docs/react
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/intro
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines
- Material accessibility guidance: https://m2.material.io/design/usability/accessibility.html
- MDN Web Animations API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API
- MDN CSS scroll-driven animations: https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations
- MDN View Transition API: https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API
- GSAP docs: https://gsap.com/docs/v3/
- GSAP ScrollTrigger docs: https://gsap.com/docs/v3/Plugins/ScrollTrigger/
- React Native animation docs: https://reactnative.dev/docs/next/animations
- LottieFiles dotLottie web docs: https://developers.lottiefiles.com/docs/dotlottie-player/dotlottie-web/
- Rive runtimes docs: https://rive.app/docs/runtimes/getting-started
- Three.js AnimationMixer docs: https://threejs.org/docs/pages/AnimationMixer.html
- React Three Fiber docs: https://r3f.docs.pmnd.rs/
- Remotion docs: https://www.remotion.dev/docs/
- Motion Canvas docs: https://motioncanvas.io/docs/
