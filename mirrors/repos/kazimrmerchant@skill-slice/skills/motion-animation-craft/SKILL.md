---
name: motion-animation-craft
description: "Chooses the lightest web motion engine (CSS, WAAPI, GSAP, Framer Motion, canvas/WebGL) for UI transitions, scroll scenes, and game-like micro-feedback. Use when setting duration/easing tokens, GPU-only transform/opacity, or prefers-reduced-motion fallbacks. Not for Remotion compositions or Emil Kowalski popover/drawer/toast recipes."
version: 1.0.1
---

## Overview
This skill provides a comprehensive motion design and animation engineering workflow for UI transitions, microinteractions, canvas motion, scroll animation, and game-like feedback. It ensures animations are implemented using the lightest possible engineering layer while preserving performance and accessibility.

## When to Use
Use this skill when you need to:
- Add or review UI animations, transitions, or microinteractions.
- Implement motion using CSS, Web Animations API (WAAPI), GSAP, Framer Motion, Three.js, or canvas.
- Design motion systems, animation specs, and spatial orientation.
- Ensure animations respect accessibility (a11y) constraints like `prefers-reduced-motion`.
- Optimize animation performance to maintain 60fps/120fps.

## Prerequisites
- Windows host is primary (PowerShell). Ensure Node.js and package managers (npm/yarn/pnpm) are available in your PowerShell environment.
- Re-check official/current docs before relying on provider-specific APIs, policy, pricing, security behavior, or platform rules.
- Collect target users, primary task, platform, viewport range, existing design system, accessibility requirements, brand constraints, data density, interaction states, and success metric. Ask for screenshots or reference URLs when visual fidelity matters.

## Procedure

### 1. Architectural Motion Layer Selection
Choose the lightest possible engineering layer that satisfies the design intent:
- **CSS Transitions/Keyframes:** Best for static state-to-state properties (hover, active, focus). Runs on the browser's compositor thread.
- **Web Animations API (WAAPI):** Best for programmatic control of simple sequences without external libraries.
- **Framer Motion:** Best for React environments. Simplifies layout transition tracking and handles entry/exit DOM manipulation cleanly.
- **GSAP (GreenSock):** Best for complex timelines, morphing SVG vector lines, or scroll-driven scenes.
- **Canvas / WebGL (Three.js):** Reserved for rendering large point-clouds, physical particle fields, custom shaders, and interactive 3D models.

### 2. Easing and Timing Mechanics
Animations should feel natural, reflecting physical laws of inertia:
- **Standard Timing Windows:**
  - Micro-interactions (toggles, button feedback): **100ms - 150ms**
  - Segment expansions, dropdown triggers: **200ms - 300ms**
  - Full-screen route adjustments, modal slide-ins: **300ms - 400ms**
- **Easing Profiles:**
  - **Ease-Out (Deceleration):** Fast entrance, slow settlement. Best for elements entering the viewport.
  - **Ease-In (Acceleration):** Slow start, fast exit. Best for elements exiting active layouts.
  - **Elastic / Bounce Ease:** Reserved for interfaces mimicking rubber-band limits. Never apply to structural page components.

### 3. Performance Optimization and Reflow Mitigation
To keep animations running at a smooth 60fps/120fps:
- **GPU Accelerated Properties:** Only animate `transform` (translation, scaling, rotation) and `opacity`. The browser delegates these directly to the GPU compositor thread.
- **Avoid Layout-Thrashing Properties:** Do not animate `width`, `height`, `margin`, `top`, or `left`. These force reflow and repaint, causing jank.
- **Will-Change Strategy:** For complex vector paths or large elements, apply `will-change: transform, opacity` in CSS to pre-allocate GPU memory buffers. Remove this class when animations finish to release resources.

### 4. Motion Engineering Engine Matrix

| Feature | CSS Transitions | WAAPI | GSAP | Framer Motion | Three.js |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Runtime Overhead** | None | Low (Browser Native) | Medium (~25KB bundle) | High (~35-50KB React lib) | Extreme (>150KB WebGL wrapper) |
| **Complex Timelines** | Hard (CSS Keyframe chains) | Medium | Exceptional (Timeline nesting) | Medium (Sequential triggers) | Custom (Loop-driven updates) |
| **React Integration** | Style hooks | Class refs | Refs + `useGSAP` | Native components | Native via Fiber wrapper |
| **Hardware Accelerated**| Yes (Compositor only) | Yes (Compositor only) | JS main-thread driven | JS main-thread driven | Yes (Direct WebGL pipeline) |
| **SVG Sub-path Morphing**| No | No | Outstanding | Medium | N/A |

### 5. Implementation Workflow
1. Start from purpose: feedback, continuity, hierarchy, causality, spatial orientation, progress, or delight.
2. Define motion tokens: duration, easing, delay, distance, spring behavior, reduced-motion behavior, and interruption rules.
3. Map states: idle, hover, focus, active, pressed, loading, success, error, disabled, drag, drop, enter, exit, and route change.
4. Choose technology by job: CSS for simple states, Motion for React layout/component animation, GSAP for orchestration, Lottie/Rive for authored vector animation, Three.js/WebGL for spatial scenes.
5. Validate accessibility and performance before polish.

### 6. Code Examples

**Performance-Optimized Web Animations API (WAAPI) Transition:**
```javascript
class PerformanceAnimationEngine {
  constructor() {
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    this.prefersReducedMotion = query.matches;
    query.addEventListener("change", (e) => {
      this.prefersReducedMotion = e.matches;
    });
  }

  animateElement(element, keyframes, options) {
    if (!element) return null;

    if (this.prefersReducedMotion) {
      const finalStyles = keyframes[keyframes.length - 1];
      Object.keys(finalStyles).forEach((prop) => {
        element.style[prop] = finalStyles[prop];
      });
      return { finished: Promise.resolve(), cancel: () => {} };
    }

    const defaultOptions = {
      duration: 250,
      easing: "cubic-bezier(0.16, 1, 0.3, 1)",
      fill: "both"
    };

    const combinedOptions = { ...defaultOptions, ...options };
    const animation = element.animate(keyframes, combinedOptions);

    animation.finished
      .then(() => {
        const finalFrame = keyframes[keyframes.length - 1];
        Object.keys(finalFrame).forEach((prop) => {
          element.style[prop] = finalFrame[prop];
        });
        animation.cancel();
      })
      .catch((e) => {
        console.warn("Animation cleanup interrupted:", e);
      });

    return animation;
  }
}
```

**Declarative Framer Motion Transition with Layout Matching (React):**
```tsx
import * as React from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";

interface TaskItem {
  id: string;
  label: string;
}

export function TaskList({ items }: { items: TaskItem[] }) {
  const shouldReduceMotion = useReducedMotion();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: shouldReduceMotion ? 0 : 0.05 }
    }
  };

  const itemVariants = {
    hidden: { 
      opacity: 0, 
      y: shouldReduceMotion ? 0 : 15 
    },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { type: "spring", stiffness: 300, damping: 30 }
    },
    exit: { 
      opacity: 0, 
      scale: shouldReduceMotion ? 1 : 0.95,
      transition: { duration: 0.15 } 
    }
  };

  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-2 p-4 bg-background border rounded-lg"
    >
      <AnimatePresence mode="popLayout">
        {items.map((item) => (
          <motion.li
            key={item.id}
            layout={!shouldReduceMotion}
            variants={itemVariants}
            exit="exit"
            className="p-3 bg-card text-card-foreground border rounded shadow-sm flex items-center justify-between"
          >
            <span>{item.label}</span>
          </motion.li>
        ))}
      </AnimatePresence>
    </motion.ul>
  );
}
```

## Pitfalls

### Anti-Patterns in UI Motion
- **Non-Accelerated Geometry Morphing:** Animating dialog card expansions using `width` and `height` instead of `transform: scale()`. This forces layout recalculation on every frame.
- **Unbounded Loop Execution:** Leaving `requestAnimationFrame` loops or React intervals running indefinitely after components unmount. This causes CPU leaks and battery drain.
- **Blocking Pointer Targets:** Leaving interactive elements active during exit animations. Disable clicking immediately (`pointer-events: none`) to prevent double-click actions.

### Gotchas and Edge Cases
- **Flexbox Layout Scaling Shunting:** Using `transform: scale()` on flex child elements can scale background colors while leaving border coordinates unchanged. Use explicit parent wrappers to isolate scaling.
- **Z-Index Layer Clipping during Rotations:** 3D perspective transforms (`rotateY`) can clip behind container boundaries. Ensure parent containers have `transform-style: preserve-3d` and `backface-visibility: hidden`.
- **Keyboard Navigation Synchronization:** Animating components off-screen using `opacity: 0` while keeping them in the DOM allows screen readers and keyboard users to focus hidden elements. Set `visibility: hidden` or `display: none` once exit animations complete.

### Accessibility (a11y) Constraints
- Flash animations and high-velocity transitions can trigger seizures in users with photosensitive epilepsy. Avoid high-frequency flickering.
- Use the CSS variable `transition: var(--transition-speed, 200ms)` coupled with a global theme class to globally disable animations for testing or reduced motion.
- A user's preference for reduced motion does not mean a worse experience. Keep layout transformations functional by swapping sliding transitions for simple, rapid opacity crossfades.

## Verification

### Quality Checklist
- [ ] User can complete the core task quickly and repeatedly.
- [ ] UI supports keyboard, screen readers, visible focus, and sufficient contrast.
- [ ] Mobile and desktop layouts do not overlap or rely on fragile viewport-scaled text.
- [ ] Controls use familiar affordances and expose state clearly.
- [ ] Motion is purposeful and respects reduced-motion preferences.
- [ ] Visual direction is intentional and consistent with the product domain.
- [ ] Motion never blocks task completion.
- [ ] Animation is interruptible, reversible, and does not cause layout shift.
- [ ] Durations are short enough for repeated work and long enough to be legible.

### Failure Handling
If requirements conflict, prioritize usability, accessibility, and product fit over novelty. If a requested visual pattern harms readability or accessibility, explain the tradeoff and offer a better variant. Verify current platform guidance when building for Apple, Android, or a specific design system.

## Related skills
- `ui-ux-design-craft`: For general interface design, UX review, and responsive layouts.
- `frontend-architecture-craft`: For broader frontend implementation guidance and state management.
