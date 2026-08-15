---
name: mobile-web-game-polish
description: "Hardens browser games on phones: safe-area HUD, 48px touch targets, viewport lock, PWA standalone, tap-to-unlock audio, visibility pause, and battery-aware frame caps. Use for canvas or SVG games that break under Safari chrome. Not a desktop marketing-page layout pass; skip native Unity or Godot exports."
version: 1.0.1
---

## Overview
Mobile web games require extra optimization to feel like native apps. Game builders must address browser navigation bars, elastic scrolling, touch latency, and battery drain to deliver an optimal player experience.

## When to Use
Use this skill for interface design, UX review, accessibility, responsive layouts, design systems, mobile/web UI, component behavior, interaction states, visual hierarchy, usability improvements, and frontend implementation guidance. Trigger keywords: mobile web game, touch controls, responsive canvas, SVG scaling, orientation handling, safe areas, PWA install, audio unlock, performance budgets, mobile testing, battery-friendly rendering.

## Prerequisites
- Collect the target users, primary task, platform, viewport range, existing design system, accessibility requirements, brand constraints, data density, interaction states, and success metric.
- Ask for screenshots or reference URLs when visual fidelity matters.
- Collect iOS safe-area and Android gesture-bar constraints before implementing touch ergonomics.

## Procedure

1. **Viewport Management & Safe Area Insets**
   - Set the viewport meta tag to block default responsive scaling and define fixed limits.
   ```html
   <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
   ```
   - Account for screen notches by leveraging CSS env variables:
   ```css
   .hud-panel {
     padding-top: env(safe-area-inset-top, 16px);
     padding-left: env(safe-area-inset-left, 16px);
     padding-right: env(safe-area-inset-right, 16px);
   }
   ```

2. **Viewport Locking Utility**
   - Apply javascript overrides that intercept default gestures (like pinch-to-zoom or elastic momentum bounce-backs).
   ```javascript
   export function initializeViewportLock(canvasElement) {
     document.addEventListener('touchmove', (event) => {
       if (event.scale !== 1) {
         event.preventDefault();
       }
     }, { passive: false });

     canvasElement.addEventListener('contextmenu', (event) => {
       event.preventDefault();
     });

     let lastTouchTime = 0;
     document.addEventListener('touchend', (event) => {
       const currentTime = new Date().getTime();
       const tapInterval = currentTime - lastTouchTime;
       if (tapInterval < 300 && tapInterval > 0) {
         event.preventDefault();
       }
       lastTouchTime = currentTime;
     }, { passive: false });
   }
   ```

3. **High-Performance Mobile Game Loop & Battery Optimization**
   - Pause rendering computations and suspend audio engines immediately when the game tab loses focus using the Visibility API.
   - Cap render frequencies on low-performance devices (e.g., rendering physics at 60Hz but updating graphics at 30Hz when thermal limits are crossed).
   - Implement a Page Visibility State Controller:
   ```javascript
   export class MobileGameVisibilityManager {
     constructor(gameLoopController, audioManagerInstance) {
       this.gameLoop = gameLoopController;
       this.audioManager = audioManagerInstance;
       this.isPaused = false;
       this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
     }
     init() {
       document.addEventListener('visibilitychange', this.handleVisibilityChange);
     }
     destroy() {
       document.removeEventListener('visibilitychange', this.handleVisibilityChange);
     }
     handleVisibilityChange() {
       if (document.hidden) {
         this.pauseGame();
       } else {
         this.resumeGame();
       }
     }
     pauseGame() {
       this.isPaused = true;
       this.gameLoop.pause();
       if (this.audioManager && this.audioManager.ctx && this.audioManager.ctx.state === 'running') {
         this.audioManager.ctx.suspend();
       }
     }
     resumeGame() {
       this.isPaused = false;
       this.gameLoop.resume();
       if (this.audioManager && this.audioManager.ctx && this.audioManager.ctx.state === 'suspended') {
         this.audioManager.ctx.resume();
       }
     }
   }
   ```

4. **Touch Controls, Thumb Zones, & Affordances**
   - Place primary interaction nodes (jump, shoot, confirm) along the lower outer edges of the display. Keep secondary or structural utility nodes (pause, settings) in the top corners.
   - Interactive buttons must maintain a minimum physical click area of `48px` by `48px`.
   - Implement explicit tap states instead of relying on CSS `:hover` states.

5. **Progressive Web App (PWA) & Offline Installs**
   - Provide a `manifest.json` specifying `display: standalone` and `orientation: landscape` or `portrait`.
   - Implement a Service Worker using Cache-First pipelines to serve static audio, mesh, and sprite bundles instantly.

6. **UI/UX 2026 Workflow**
   - Start from the user task and information architecture, not decoration.
   - Map key states: empty, loading, success, error, disabled, permission-limited, offline, and responsive variants.
   - Apply accessibility requirements early: keyboard flow, focus visibility, labels, contrast, reduced motion, touch targets, text resizing, and semantic structure.
   - Use design-system primitives where available; otherwise define tokens for spacing, color, type, elevation, radius, and motion.
   - Design responsive layouts with stable dimensions and no text overlap across desktop and mobile.
   - Validate with realistic content, long labels, error text, and touch/keyboard interaction.

## Pitfalls
- **Pinch-to-Zoom Default:** Allowing default browser double-tap or pinch actions, causing the entire layout to zoom in during fast-tapping sessions.
- **Dynamic CSS VH Calculations:** Relying on `height: 100vh` for layout bounds. As the mobile browser address bar shifts on scroll, the `vh` unit changes size, triggering periodic reflows. Use `window.innerHeight` or dynamic CSS `100dvh` units instead.
- **Mouse Event Bindings:** Using `click` events instead of `pointerdown` or `touchstart`. Standard `click` events add a default `300ms` tap delay on mobile viewports.
- **iOS Safari Dynamic Address Bar:** When scrolling triggers, iOS Safari expands or collapses its bottom toolbar. This changes the canvas size and can warp aspect ratios if the update loops do not trigger resize audits.
- **Audio De-synchronization:** If the frame rate drops significantly, audio triggers can drift from their visual event timing. Track sync offsets relative to real system clock time, not frames elapsed.
- **Battery Saver Frame Cap:** Many mobile operating systems force WebGL rendering to lock at 30fps when Low Power Mode is enabled. Plan for this lower performance tier.
- **Autoplay Media Limitations:** Mobile browsers will block audio execution if a play event occurs before a click, touch, or tap. Programmatically defer audio playback until a landing page button is pressed.
- **Tab Crash Limits:** Safari on iOS crashes pages that exceed memory usage thresholds (~300MB overall tab memory). Always optimize texture sizes to 512x512 or 1024x1024, and verify actual RAM footprints on physical devices.
- **WebGL Draw Buffers:** Ensure your canvas width and height parameters match the device pixel ratio (`window.devicePixelRatio`) to keep graphics looking crisp on Retina screens.

## Verification
- **Quality Checklist:**
  - User can complete the core task quickly and repeatedly.
  - UI supports keyboard, screen readers, visible focus, and sufficient contrast.
  - Mobile and desktop layouts do not overlap or rely on fragile viewport-scaled text.
  - Controls use familiar affordances and expose state clearly.
  - Motion is purposeful and respects reduced-motion preferences.
  - Visual direction is intentional and consistent with the product domain.
- **Output Format:** Return a design or implementation plan with: user goal, layout structure, component list, states, accessibility checks, responsive behavior, copy notes, and verification steps. For code tasks, include exact files/components and testing guidance.
- **Failure Handling:** If requirements conflict, prioritize usability, accessibility, and product fit over novelty. If a requested visual pattern harms readability or accessibility, explain the tradeoff and offer a better variant. Verify current platform guidance when building for Apple, Android, or a specific design system.

## Related skills
- `responsive-web-design`
- `pwa-offline-caching`
