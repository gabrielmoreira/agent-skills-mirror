## Table of Contents

1. [Installation & TypeScript Setup](#installation--typescript-setup)
2. [Core Concepts](#core-concepts)
3. [Tweens](#tweens)
4. [Timelines](#timelines)
5. [Easing](#easing)
6. [Staggers](#staggers)
7. [Control Methods](#control-methods)
8. [Utility Methods](#utility-methods)
9. [Context & Cleanup](#context--cleanup)
10. [Responsive Animations — matchMedia()](#responsive-animations--matchmedia)
11. [Plugins Overview](#plugins-overview)
12. [ScrollTrigger](#scrolltrigger)
13. [ScrollSmoother](#scrollsmoother)
14. [Flip Plugin](#flip-plugin)
15. [SplitText Plugin](#splittext-plugin)
16. [React Integration — useGSAP()](#react-integration--usegsap)
17. [Performance Tips & Best Practices](#performance-tips--best-practices)
18. [Helper Functions](#helper-functions)

---

## Installation & TypeScript Setup

```bash
npm install gsap
```

TypeScript definitions are bundled with the package. If you need to point your compiler to them explicitly:

```json
// tsconfig.json
{
  "compilerOptions": { ... },
  "files": [
    "node_modules/gsap/types/index.d.ts"
  ]
}
```

**Basic import:**

```ts
import { gsap } from "gsap";
```

**Importing plugins:**

```ts
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Flip } from "gsap/Flip";
import { SplitText } from "gsap/SplitText";
import { ScrollSmoother } from "gsap/ScrollSmoother";
import { DrawSVGPlugin } from "gsap/DrawSVGPlugin";

// Register all plugins once, before use
gsap.registerPlugin(ScrollTrigger, Flip, SplitText, ScrollSmoother);
```

**Recommended: single `gsap.ts` barrel file** to avoid duplicate registrations in large projects:

```ts
// gsap.ts
export * from "gsap";
export * from "gsap/ScrollTrigger";
export * from "gsap/Flip";

import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Flip } from "gsap/Flip";

gsap.registerPlugin(ScrollTrigger, Flip);
```

Then in other files:

```ts
import { gsap, ScrollTrigger } from "../gsap";
```

**UMD/dist format** (for older build tools that don't support ES modules):

```ts
import { gsap } from "gsap/dist/gsap";
import { ScrollTrigger } from "gsap/dist/ScrollTrigger";
```

> **Tree shaking:** Always call `gsap.registerPlugin(...)` to prevent build tools from dropping plugins during tree shaking. It's safe to register the same plugin multiple times.

---

## Core Concepts

GSAP has two primary animation primitives:

**Tween** — animates properties on target(s). Created with `gsap.to()`, `gsap.from()`, or `gsap.fromTo()`.

**Timeline** — a container for sequencing multiple tweens and other timelines. Created with `gsap.timeline()`.

Both extend an `Animation` base class and share the same control methods (`play`, `pause`, `reverse`, `seek`, `timeScale`, etc.).

GSAP can animate **any numeric property** of any JavaScript object — not just CSS. DOM elements, canvas contexts, WebGL uniforms, plain objects — anything works.

**Transform shorthand** — GSAP provides shorthand properties that map to CSS transforms:

| GSAP property               | CSS equivalent                   |
| --------------------------- | -------------------------------- |
| `x`, `y`                    | `translateX`, `translateY`       |
| `xPercent`, `yPercent`      | `translateX(%)`, `translateY(%)` |
| `rotation`                  | `rotate` (degrees)               |
| `rotationX`, `rotationY`    | `rotateX`, `rotateY`             |
| `scale`, `scaleX`, `scaleY` | `scale`                          |
| `skewX`, `skewY`            | `skew`                           |

---

## Tweens

```ts
// Animate TO values
gsap.to(".selector", {
  x: 100,
  y: 50,
  rotation: 360,
  backgroundColor: "red", // camelCase CSS
  duration: 1, // seconds (default: 0.5)
  delay: 0.5,
  ease: "power2.inOut",
  stagger: 0.1, // offset start per target
  paused: false,
  overwrite: "auto", // "auto" | true | false
  repeat: 2, // -1 = infinite
  repeatDelay: 1,
  repeatRefresh: true, // re-evaluate dynamic values each repeat
  yoyo: true, // A→B→A ping-pong
  yoyoEase: "power1.in", // separate ease for reverse
  immediateRender: false,
  onStart: () => {},
  onUpdate: () => {},
  onComplete: () => {},
  onRepeat: () => {},
  onReverseComplete: () => {},
});

// Animate FROM values (immediateRender: true by default)
gsap.from(".selector", { x: -200, opacity: 0, duration: 1 });

// Animate from → to (define both explicitly)
gsap.fromTo(
  ".selector",
  { x: -200, opacity: 0 },
  { x: 0, opacity: 1, duration: 1 },
);

// Set immediately (no animation)
gsap.set(".selector", { x: 100, opacity: 0 });
```

**Function-based values** — called once per target, returning the value to use:

```ts
gsap.to(".box", {
  x: (index, target, targets) => index * 100,
  duration: 1,
});
```

**Random values:**

```ts
gsap.to(".box", {
  x: "random(-100, 100)", // random number in range
  x: "random(-100, 100, 5)", // rounded to nearest 5
  x: "random([0, 100, 200])", // random from array
});
```

**Relative values:**

```ts
gsap.to(".box", { x: "+=50", rotation: "-=30" });
```

**Keyframes:**

```ts
gsap.to(".box", {
  keyframes: [
    { x: 100, duration: 1 },
    { y: 50, duration: 0.5 },
    { opacity: 0, duration: 0.5 },
  ],
});
```

**Special properties:**

| Property            | Description                                 |
| ------------------- | ------------------------------------------- |
| `duration`          | Duration in seconds (default `0.5`)         |
| `delay`             | Delay before start (seconds)                |
| `ease`              | Easing function name or function            |
| `stagger`           | Start time offset per target                |
| `repeat`            | Number of repeats (`-1` = infinite)         |
| `repeatDelay`       | Pause between repeats                       |
| `yoyo`              | Ping-pong direction on repeat               |
| `paused`            | Start paused                                |
| `overwrite`         | Kill conflicting tweens: `"auto"` or `true` |
| `immediateRender`   | Render first frame immediately              |
| `onComplete`        | Callback on finish                          |
| `onStart`           | Callback on start                           |
| `onUpdate`          | Callback every tick                         |
| `onRepeat`          | Callback on each repeat                     |
| `onReverseComplete` | Callback when reversed to start             |
| `id`                | Unique string ID for `gsap.getById()`       |
| `data`              | Arbitrary data attached to the tween        |
| `callbackScope`     | `this` scope for callbacks                  |
| `startAt`           | Define starting values for any property     |
| `keyframes`         | Array of tween vars for sequential states   |

---

## Timelines

```ts
const tl = gsap.timeline({
  delay: 0.5,
  paused: false,
  repeat: -1,
  repeatDelay: 1,
  yoyo: true,
  defaults: {
    // all child tweens inherit these
    duration: 1,
    ease: "power2.out",
  },
  onComplete: () => {},
});

// Chain tweens (sequential by default)
tl.to(".a", { x: 100 }).to(".b", { y: 200 }).to(".c", { rotation: 360 });
```

**Position parameter** — controls where each tween is placed in the timeline:

```ts
tl.to(".a", { x: 100 }, 0.5); // absolute 0.5s from start
tl.to(".b", { x: 100 }, "+=0.3"); // 0.3s after previous ends
tl.to(".c", { x: 100 }, "-=0.2"); // overlap 0.2s with previous
tl.to(".d", { x: 100 }, "myLabel"); // at label position
tl.to(".e", { x: 100 }, "myLabel+=0.5"); // 0.5s after label
tl.to(".f", { x: 100 }, "<"); // same start as previous tween
tl.to(".g", { x: 100 }, "<0.2"); // 0.2s after start of previous
tl.to(".h", { x: 100 }, "-=50%"); // overlap half of new tween's duration
```

**Labels:**

```ts
tl.addLabel("intro", 2); // add label at 2s
tl.seek("intro"); // jump playhead to label
```

**Nesting timelines:**

```ts
function buildScene1() {
  const tl = gsap.timeline();
  tl.to(".a", { x: 100 }).to(".b", { y: 50 });
  return tl;
}

const master = gsap.timeline();
master.add(buildScene1()).add(buildScene2(), "-=0.5"); // overlap slightly
```

---

## Easing

```ts
ease: "none"; // linear
ease: "power1.out"; // default
ease: "power1.in";
ease: "power1.inOut";
// power1 through power4, circ, expo, sine — all have .in .out .inOut

ease: "elastic"; // springy
ease: "elastic.out(1, 0.3)"; // amplitude, period
ease: "back"; // overshoots slightly
ease: "back.out(1.7)"; // configurable overshoot
ease: "bounce"; // bouncy landing
ease: "steps(12)"; // stepped/frame-by-frame

// EasePack (import separately)
ease: "rough({ strength: 1, points: 20, randomize: true })";
ease: "slow(0.7, 0.7, false)";
ease: "expoScale(1, 2)";

// Custom (requires CustomEase plugin)
import { CustomEase } from "gsap/CustomEase";
gsap.registerPlugin(CustomEase);
CustomEase.create("myEase", "0.23, 1, 0.32, 1");
ease: "myEase";
```

**Set global defaults:**

```ts
gsap.defaults({ ease: "power2.inOut", duration: 0.8 });
```

---

## Staggers

```ts
// Simple — seconds between each start
gsap.to(".box", { y: 100, stagger: 0.1 });

// Advanced stagger object
gsap.to(".box", {
  y: 100,
  stagger: {
    each: 0.1, // delay between each (preferred over `amount`)
    amount: 1, // total time split across all targets
    from: "center", // "start" | "end" | "center" | "edges" | "random" | index
    grid: "auto", // [rows, cols] or "auto"
    axis: "x", // "x" | "y" — for grid-based staggers
    ease: "power2.inOut",
    repeat: -1, // repeat per sub-tween
    yoyo: true,
  },
});

// Function-based stagger (return total delay from start)
gsap.to(".box", {
  y: 100,
  stagger: (index, target, list) => index * 0.08,
});
```

---

## Control Methods

```ts
const anim = gsap.to(".box", { x: 100, duration: 2, paused: true });

// Playback
anim.play();
anim.pause();
anim.resume(); // respects current direction
anim.reverse();
anim.restart();
anim.timeScale(2); // 2 = double speed, 0.5 = half
anim.seek(1.5); // jump to time (seconds) or label
anim.progress(0.5); // jump to 50%
anim.totalProgress(0.75); // includes repeats

// State
anim.isActive(); // true if currently animating
anim.paused(); // getter
anim.paused(true); // setter
anim.reversed();
anim.duration();
anim.totalDuration(); // includes repeats
anim.time();
anim.totalTime();

// Destruction
anim.kill(); // stop & remove from parent
anim.revert(); // stop & restore to pre-animation state
anim.invalidate(); // flush recorded start/end values

// Promise
await anim.then(() => console.log("done"));

// Callbacks
anim.eventCallback("onComplete", () => {});

// Timeline-specific
tl.add(thing, position);
tl.call(fn, params, position);
tl.getChildren();
tl.clear();
tl.tweenTo("label", { duration: 0.5 });
tl.tweenFromTo("start", "end", { duration: 1 });
```

**Global kill helpers:**

```ts
gsap.killTweensOf(".selector");
gsap.killTweensOf(myElement);
gsap.killTweensOf(myFunction); // kills delayedCalls
```

**quickSetter & quickTo:**

```ts
// quickSetter: fastest way to repeatedly SET a property (no animation)
const setX = gsap.quickSetter("#id", "x", "px");
document.addEventListener("mousemove", (e) => setX(e.clientX));

// quickTo: same but ANIMATES to the new value each call
const xTo = gsap.quickTo("#id", "x", { duration: 0.4, ease: "power3" });
document.addEventListener("mousemove", (e) => xTo(e.pageX));
```

**Global ticker:**

```ts
gsap.ticker.add((time, deltaTime, frame) => {
  // runs every GSAP tick
});
gsap.ticker.remove(myFunction);
gsap.ticker.fps(60); // cap frame rate
```

---

## Utility Methods

Accessible via `gsap.utils.*`. Many return reusable functions when called without a value argument.

```ts
gsap.utils.clamp(0, 100, 150); // → 100
gsap.utils.clamp(0, 100); // → (v) => clamp(v) — reusable fn

gsap.utils.mapRange(-10, 10, 0, 100, 5); // → 75
gsap.utils.normalize(100, 200, 150); // → 0.5 (maps to 0–1)

gsap.utils.interpolate("red", "blue", 0.5); // → "rgba(128,0,128,1)"
gsap.utils.interpolate([0, 100], 0.25); // → 25

gsap.utils.snap(5, 13); // → 15 (nearest increment of 5)
gsap.utils.snap([0, 50, 100], 73); // → 50 (nearest in array)

gsap.utils.random(0, 100); // → random number
gsap.utils.random(0, 100, 5); // → rounded to nearest 5
gsap.utils.random(["a", "b", "c"]); // → random element

gsap.utils.wrap(0, 10, 12); // → 2 (wraps around range)
gsap.utils.wrapYoyo(0, 10, 12); // → 8 (ping-pong)

gsap.utils.pipe(gsap.utils.clamp(0, 100), gsap.utils.snap(5))(108); // → 100

gsap.utils.toArray(".boxes"); // → Array from selector/NodeList
gsap.utils.selector(myEl); // → scoped selector fn: sel(".box")
gsap.utils.shuffle([1, 2, 3, 4]); // in-place shuffle → [3,1,4,2]
gsap.utils.splitColor("red"); // → [255, 0, 0]
gsap.utils.getUnit("30px"); // → "px"
gsap.utils.unitize(gsap.utils.wrap(0, 100))("150px"); // → "50px"
gsap.utils.checkPrefix("transform"); // → vendor-prefixed string
gsap.utils.distribute({ amount: 1, from: "center", ease: "power2" });
```

---

## Context & Cleanup

`gsap.context()` collects all animations/ScrollTriggers created within it so they can all be reverted at once. Essential for component-based frameworks.

```ts
const ctx = gsap.context(() => {
  gsap.to(".box", { x: 100 });
  gsap.timeline().to(".item", { y: 50 });
  ScrollTrigger.create({ ... });
  // all of the above are tracked
}, myContainerElement); // optional scope for selector text

// Later (e.g. on component unmount):
ctx.revert(); // all animations reverted, elements restored

// Add context-safe functions for event handlers
const ctx = gsap.context((self) => {
  self.add("onClick", () => {
    gsap.to(".box", { rotation: 360 }); // tracked!
  });
}, containerRef);

button.addEventListener("click", ctx.onClick);
```

---

## Responsive Animations — matchMedia()

```ts
const mm = gsap.matchMedia();

// Simple breakpoints
mm.add("(min-width: 800px)", () => {
  gsap.to(".box", { x: 500 });
  ScrollTrigger.create({ ... });

  return () => {
    // optional custom cleanup when query stops matching
  };
});

mm.add("(max-width: 799px)", () => {
  gsap.to(".box", { x: 100 });
});

// Conditions syntax (shared setup code)
mm.add(
  {
    isDesktop: "(min-width: 800px)",
    isMobile: "(max-width: 799px)",
    reduceMotion: "(prefers-reduced-motion: reduce)",
  },
  (context) => {
    const { isDesktop, reduceMotion } = context.conditions;

    gsap.to(".box", {
      rotation: isDesktop ? 360 : 180,
      duration: reduceMotion ? 0 : 1.5,
    });
  }
);

// Revert all
mm.revert();
```

---

## Plugins Overview

Register plugins before use: `gsap.registerPlugin(PluginA, PluginB)`.

| Plugin             | Purpose                                                       |
| ------------------ | ------------------------------------------------------------- |
| **ScrollTrigger**  | Scroll-based animation triggers, scrubbing, pinning           |
| **ScrollSmoother** | Native-scroll-based smooth scrolling (requires ScrollTrigger) |
| **SplitText**      | Split text into chars/words/lines for animation               |
| **Flip**           | Seamless layout/DOM-change transitions (FLIP technique)       |
| **Draggable**      | Drag & drop with physics/bounds                               |
| **Inertia**        | Momentum/glide after release (requires Draggable)             |
| **Observer**       | Unified pointer/touch/scroll event observer                   |
| **MotionPath**     | Animate along SVG or custom paths                             |
| **MorphSVG**       | Morph between SVG shapes                                      |
| **DrawSVG**        | Animate SVG stroke drawing                                    |
| **CustomEase**     | Create arbitrary cubic-bezier eases                           |
| **CustomBounce**   | Create custom bounce eases                                    |
| **CustomWiggle**   | Create custom wiggle eases                                    |
| **EasePack**       | Extra eases: `rough`, `slow`, `expoScale`                     |
| **ScrollTo**       | Animate the scroll position of any element                    |
| **TextPlugin**     | Animate text content character by character                   |
| **ScrambleText**   | Scramble/randomize text during animation                      |
| **Physics2D**      | Physics-based 2D motion                                       |
| **PhysicsProps**   | Physics-based property animation                              |
| **GSDevTools**     | Visual timeline debugger (dev only)                           |
| **PixiPlugin**     | Animate PixiJS display objects                                |
| **EaselPlugin**    | Animate EaselJS display objects                               |

---

## ScrollTrigger

```ts
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);
```

**Simple trigger:**

```ts
gsap.to(".box", {
  scrollTrigger: ".box", // shorthand: trigger selector
  x: 500,
});
```

**Full config on a timeline:**

```ts
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: ".container",
    start: "top top", // [trigger edge] [scroller edge]
    end: "+=500", // relative: 500px beyond start
    scrub: 1, // seconds to "catch up" (true = instant)
    pin: true, // pin the trigger element
    markers: true, // dev-only visual markers
    anticipatePin: 1, // counteract fast-scroll flash
    snap: {
      snapTo: "labels", // or number/array/fn
      duration: { min: 0.2, max: 3 },
      ease: "power1.inOut",
    },
    toggleActions: "play pause resume reset",
    // actions: play | pause | resume | reset | restart | complete | reverse | none
    // order: onEnter onLeave onEnterBack onLeaveBack
    toggleClass: "active",
    once: true, // kill after first activation
    horizontal: false,
    invalidateOnRefresh: true,
    fastScrollEnd: true,
    preventOverlaps: true,
    onEnter: (self) => {},
    onLeave: (self) => {},
    onEnterBack: (self) => {},
    onLeaveBack: (self) => {},
    onUpdate: (self) => {},
    onToggle: (self) => {},
    onRefresh: (self) => {},
    onScrubComplete: (self) => {},
  },
});
```

**Standalone ScrollTrigger:**

```ts
ScrollTrigger.create({
  trigger: "#section",
  start: "top center",
  end: "bottom center",
  onToggle: (self) => console.log("active:", self.isActive),
  onUpdate: (self) => console.log("progress:", self.progress),
});
```

**Key static methods:**

```ts
ScrollTrigger.refresh();              // recalculate all positions
ScrollTrigger.getAll();               // array of all instances
ScrollTrigger.getById("id");
ScrollTrigger.killAll();
ScrollTrigger.defaults({ markers: true }); // set defaults

// Batch — coordinate multiple triggers that fire around the same time
ScrollTrigger.batch(".card", {
  onEnter: (elements) => gsap.from(elements, { y: 50, opacity: 0, stagger: 0.1 }),
  start: "top 85%",
});

// Responsive — use matchMedia instead of ScrollTrigger.matchMedia (deprecated)
const mm = gsap.matchMedia();
mm.add("(min-width: 800px)", () => {
  ScrollTrigger.create({ ... });
});
```

**start/end position syntax:**

```
"top top"        → top of trigger meets top of viewport
"center center"  → midpoints meet
"bottom 80%"     → bottom of trigger hits 80% down viewport
"+=300"          → 300px beyond start
"top bottom-=100px" → top of trigger hits 100px above bottom of viewport
```

---

## ScrollSmoother

Requires ScrollTrigger. Adds native-scroll smooth scrolling via CSS transforms.

**Required HTML structure:**

```html
<body>
  <div id="smooth-wrapper">
    <div id="smooth-content">
      <!-- ALL content here -->
    </div>
  </div>
  <!-- position:fixed elements outside the wrapper -->
</body>
```

```ts
import { ScrollSmoother } from "gsap/ScrollSmoother";
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger, ScrollSmoother);

// Create BEFORE any ScrollTriggers
const smoother = ScrollSmoother.create({
  smooth: 1, // seconds to catch up to native scroll
  effects: true, // enable data-speed / data-lag attributes
  smoothTouch: 0.1, // smoothing on touch devices (default: none)
  normalizeScroll: true, // prevent mobile address bar jump
  ignoreMobileResize: true,
});
```

**Parallax & lag via data attributes:**

```html
<div data-speed="0.5">half scroll speed</div>
<div data-speed="2">double scroll speed</div>
<div data-speed="auto">auto-parallax (fill parent)</div>
<div data-lag="0.5">lags 0.5s behind scroll</div>
<div data-speed="clamp(0.5)">clamped — starts at native position</div>
```

**JavaScript effects:**

```ts
smoother.effects(".box", { speed: 0.5, lag: 0.2 });
```

**Useful methods:**

```ts
ScrollSmoother.get(); // get the singleton instance
smoother.scrollTo(".section", true, "top top");
smoother.scrollTop(500);
smoother.paused(true); // halt all scrolling
smoother.smooth(2); // change smooth time on the fly
smoother.getVelocity();
smoother.kill();
```

---

## Flip Plugin

FLIP = **F**irst, **L**ast, **I**nvert, **P**lay. Animate seamlessly between two DOM states, even across layout or DOM changes.

```ts
import { Flip } from "gsap/Flip";
gsap.registerPlugin(Flip);
```

**Three-step pattern:**

```ts
// 1. Capture current state
const state = Flip.getState(".targets");

// Optionally capture extra CSS props
const state = Flip.getState(".targets", { props: "backgroundColor,color" });

// 2. Make any DOM/CSS changes
element.classList.toggle("expanded");
container.appendChild(element);

// 3. Animate from old state to new
Flip.from(state, {
  duration: 0.6,
  ease: "power1.inOut",
  absolute: true, // use position:absolute during flip
  nested: true, // handle parent+child being flipped together
  scale: false, // use width/height (default) vs scaleX/scaleY
  fade: true, // crossfade when swapping elements
  toggleClass: "flipping",
  zIndex: 100,
  onEnter: (elements) => gsap.fromTo(elements, { opacity: 0 }, { opacity: 1 }),
  onLeave: (elements) => gsap.to(elements, { opacity: 0 }),
  onComplete: () => {},
});
```

**Swapping two different elements** — give them matching `data-flip-id` attributes:

```html
<div class="card" data-flip-id="card-1"></div>
<!-- somewhere else in DOM -->
<div class="card-expanded" data-flip-id="card-1"></div>
```

**Other Flip methods:**

```ts
Flip.to(state, vars); // animate TO a saved state (reverse)
Flip.fit(target, destination); // resize/reposition target to match destination
Flip.isFlipping(element); // check if actively flipping
Flip.killFlipsOf(targets);
Flip.makeAbsolute(targets); // position:absolute while keeping visual position
```

---

## SplitText Plugin

```ts
import { SplitText } from "gsap/SplitText";
gsap.registerPlugin(SplitText);
```

**Basic usage:**

```ts
const split = SplitText.create(".headline", {
  type: "lines, words, chars", // what to split into
});

// Returns arrays of newly created elements
split.chars; // Array of character <div>s
split.words; // Array of word <div>s
split.lines; // Array of line <div>s

// Animate them
gsap.from(split.chars, {
  y: 60,
  opacity: 0,
  stagger: 0.03,
  duration: 0.8,
  ease: "back.out",
});

// Revert to original HTML when done
split.revert();
```

**Recommended v3.13+ pattern with autoSplit:**

```ts
SplitText.create(".headline", {
  type: "lines, words",
  mask: "lines", // wraps lines with overflow:clip for reveal effects
  autoSplit: true, // re-splits on font load or resize
  onSplit(self) {
    return gsap.from(self.lines, {
      yPercent: 100,
      opacity: 0,
      stagger: 0.1,
      duration: 0.8,
    }); // returned animation is synced on re-split
  },
});
```

**Key config options:**

| Option             | Description                                                      |
| ------------------ | ---------------------------------------------------------------- |
| `type`             | `"chars"`, `"words"`, `"lines"` (comma-separated)                |
| `mask`             | `"chars"` \| `"words"` \| `"lines"` — adds overflow clip wrapper |
| `autoSplit`        | Re-splits on font load or container resize                       |
| `onSplit`          | Callback on each split; return animation for auto-sync           |
| `linesClass`       | CSS class for line elements (`"line++"` = auto-increment)        |
| `wordsClass`       | CSS class for word elements                                      |
| `charsClass`       | CSS class for char elements                                      |
| `aria`             | `"auto"` (default) \| `"hidden"` \| `"none"`                     |
| `deepSlice`        | Handle nested elements (`<strong>`, `<a>`) spanning lines        |
| `tag`              | Wrapper tag, default `"div"` (use `"span"` for inline)           |
| `reduceWhiteSpace` | Collapse whitespace (default `true`)                             |
| `ignore`           | Selector for elements to skip splitting                          |

> **Accessibility:** By default, SplitText adds `aria-label` to the parent and `aria-hidden` to split children, so screen readers read the whole text correctly.

> **Performance tip:** Only split what you animate. Splitting thousands of nodes is expensive.

> **Custom fonts:** Use `autoSplit: true` or wrap in `document.fonts.ready.then(() => {...})` to avoid layout shift.

---

## React Integration — useGSAP()

```bash
npm install @gsap/react
```

```tsx
import { useRef } from "react";
import { gsap } from "gsap";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(useGSAP); // prevents React version discrepancies

function MyComponent() {
  const container = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      // All animations here are automatically reverted on unmount
      gsap.to(".box", { x: 360, duration: 1 });
    },
    { scope: container }, // scopes selector text to container
  );

  return (
    <div ref={container}>
      <div className="box" />
    </div>
  );
}
```

**Config options:**

```ts
useGSAP(() => { ... }, {
  dependencies: [value],  // re-run when these change (like useEffect deps)
  scope: containerRef,    // scope selector text
  revertOnUpdate: true,   // revert & re-run on every dependency change
});
```

**Event handlers (context-safe):**

Animations created inside event handlers run AFTER `useGSAP()` executes and won't be auto-cleaned up — wrap them in `contextSafe`:

```tsx
// Option 1: destructure contextSafe from return value (for handlers outside the hook)
const { contextSafe } = useGSAP({ scope: container });

const onClick = contextSafe(() => {
  gsap.to(".box", { rotation: 360 }); // safely tracked
});

return <button onClick={onClick} />;
```

```tsx
// Option 2: use 2nd argument inside the hook (for manual event listeners)
useGSAP(
  (context, contextSafe) => {
    gsap.to(".box", { x: 100 }); // safe

    const onHover = contextSafe(() => {
      gsap.to(".box", { scale: 1.2 }); // safe
    });

    boxRef.current.addEventListener("mouseenter", onHover);

    return () => {
      boxRef.current.removeEventListener("mouseenter", onHover);
    };
  },
  { scope: container },
);
```

> **React 18 Strict Mode:** GSAP effects run twice in dev. `useGSAP()` handles the cleanup correctly so animations don't double-fire. Never use plain `useEffect` for GSAP without manual cleanup.

> **SSR / Next.js:** `useGSAP()` is SSR-safe. In App Router, add `"use client"` at the top of the file.

---

## Performance Tips & Best Practices

**Prefer transform properties** — `x`, `y`, `rotation`, `scale` are GPU-composited and far cheaper than animating `top`, `left`, `width`, etc.

**Use `will-change` sparingly** — only on elements actively animating; too many defeats the purpose.

**overwrite: "auto"** — prevents conflicting tweens fighting each other without killing unrelated animations.

**Register plugins once at app root** — not inside components.

**Kill or revert animations on cleanup** — use `gsap.context()` or `useGSAP()` to avoid memory leaks.

**Use `gsap.quickSetter` for high-frequency updates** (mousemove, scroll) instead of repeated `gsap.set()` calls.

**Use `gsap.quickTo` for high-frequency animated updates** (pointer following, real-time sliders).

**Avoid animating `display` or `visibility` directly** — use `autoAlpha` (animates both `opacity` and `visibility` together).

**`autoAlpha`** — GSAP shorthand: `opacity: 0` + `visibility: hidden` when 0, `visibility: visible` when > 0.

**`clearProps`** — remove inline styles after animation:

```ts
gsap.set(".box", { clearProps: "transform" }); // remove transforms
gsap.set(".box", { clearProps: "all" }); // remove all inline styles
```

**Set defaults globally or per-timeline:**

```ts
gsap.defaults({ ease: "power2.out", duration: 0.6 });

const tl = gsap.timeline({ defaults: { ease: "back.out", duration: 0.4 } });
```

**Register effects for reuse:**

```ts
gsap.registerEffect({
  name: "fadeIn",
  effect: (targets, config) =>
    gsap.from(targets, { opacity: 0, y: 30, duration: config.duration }),
  defaults: { duration: 0.8 },
  extendTimeline: true, // tl.fadeIn(".box") works!
});

gsap.effects.fadeIn(".hero");
tl.fadeIn(".cards", { duration: 0.5 });
```

**Modifiers plugin** — dynamically transform values each frame (useful for infinite loops, clamping, etc.):

```ts
gsap.to(".box", {
  x: 1000,
  modifiers: {
    x: gsap.utils.unitize((x) => parseFloat(x) % 500), // wrap at 500px
  },
});
```

---

## Helper Functions

The GSAP team maintains an official collection of community helper functions at `gsap.com/docs/v3/HelperFunctions`. Notable ones:

| Helper                   | Purpose                                           |
| ------------------------ | ------------------------------------------------- |
| `seamlessLoop()`         | Infinite seamless carousel/ticker loop            |
| `stopOverscroll()`       | Prevent overscroll on iOS Safari                  |
| `lottieScrollTrigger()`  | Tie a Lottie animation to scroll position         |
| `blendEases()`           | Blend two eases at start/end of animation         |
| `distributeByPosition()` | Stagger irregular grid elements by position       |
| `scrubCanvasFrames()`    | Scrub through canvas image sequences on scroll    |
| `anchorProgress()`       | Progress values for SVG path anchor points        |
| `weightedRandom()`       | Biased random values using an ease curve          |
| `callAfterResize()`      | Debounced resize handler                          |
| `getScrollLookup()`      | Get element scroll position (ScrollTrigger-aware) |

---

## Quick Reference

```ts
// One-liner fade-in on scroll
gsap.from(".card", {
  scrollTrigger: { trigger: ".card", start: "top 85%" },
  opacity: 0,
  y: 40,
  duration: 0.8,
  stagger: 0.1,
});

// Text reveal with SplitText
SplitText.create("h1", {
  type: "lines",
  mask: "lines",
  autoSplit: true,
  onSplit: (self) => gsap.from(self.lines, { yPercent: 100, stagger: 0.1 }),
});

// Pinned scroll section
gsap.timeline({
  scrollTrigger: {
    trigger: ".panel",
    pin: true,
    start: "top top",
    end: "+=600",
    scrub: 1,
  },
}).to(".inner", { x: 400 }).to(".inner", { opacity: 0 });

// FLIP layout change
const state = Flip.getState(".item");
container.classList.toggle("grid-layout");
Flip.from(state, { duration: 0.6, ease: "power1.inOut", stagger:
Flip.from(state, { duration: 0.6, ease: "power1.inOut", stagger: 0.05 });
// Smooth scroll setup
ScrollSmoother.create({ smooth: 1, effects: true });
// Responsive animations
const mm = gsap.matchMedia();
mm.add("(min-width: 800px)", () => {
  gsap.to(".box", { x: 500 });
});
mm.add("(prefers-reduced-motion: reduce)", () => {
  gsap.globalTimeline.timeScale(0); // kill all motion
});
```
