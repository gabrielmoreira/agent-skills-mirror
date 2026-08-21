---
name: gsap-frameworks
description: "Integrates GSAP into Vue 3, Nuxt 4, Svelte, and SvelteKit via onMounted/onMount, gsap.context scoped selectors, and ctx.revert() cleanup. Use when writing or reviewing GSAP in those non-React frameworks, including ScrollTrigger plugin registration. Not for React useGSAP/@gsap/react (gsap-web-animations) or GSAP tween/timeline recipes without a component lifecycle."
version: 1.0.1
---

# GSAP with Vue, Svelte, and Other Frameworks

Production guide for integrating GSAP into Vue 3, Nuxt 4, Svelte, and other lifecycle-based component frameworks. Covers scoped selectors via `gsap.context()`, cleanup on unmount, plugin registration, and ScrollTrigger refresh patterns.

> **For React specifically**, use the **gsap-react** skill (useGSAP hook, gsap.context()). This skill targets non-React frameworks.

## When to Use

Apply this skill when:

- Writing or reviewing GSAP code in **Vue 3** (Composition API or `<script setup>`) or **Nuxt 4**.
- Writing or reviewing GSAP code in **Svelte** or **SvelteKit**.
- The user asks about GSAP with Vue, Svelte, Nuxt, `onMounted`, `onMount`, `onDestroy`, or component lifecycle animation.
- Scoping GSAP selectors to a component root to avoid cross-component leakage.
- Setting up GSAP plugin registration (ScrollTrigger, SplitText, etc.) in a framework context.
- Cleaning up tweens and ScrollTriggers on component unmount/destroy.

**Related skills:**

- **gsap-core** — tweens, basic properties, easing.
- **gsap-timeline** — timeline construction and sequencing.
- **gsap-scrolltrigger** — scroll-driven animation, pinning, scrubbing.
- **gsap-react** — React-specific patterns (useGSAP, contextSafe).

## Prerequisites

- GSAP installed in the project: `npm install gsap` (or `pnpm add gsap`, `yarn add gsap`).
- For Vue: Vue 3.x with Composition API available.
- For Nuxt: Nuxt 4.x project with `composables/` directory support.
- For Svelte: Svelte 4.x or 5.x (lifecycle APIs differ slightly; see Svelte section).
- For ScrollTrigger or other plugins: import from `gsap/<PluginName>` and register once at app level.

**Windows host note (PowerShell):** All CLI commands below assume PowerShell as the default shell. On macOS/Linux, commands are equivalent unless noted.

## Procedure

### Core Principles (All Frameworks)

1. **Create** tweens and ScrollTriggers **after** the component's DOM is available (e.g., `onMounted`, `onMount`).
2. **Kill or revert** them in the **unmount** (or equivalent) cleanup so nothing runs on detached nodes and there are no leaks.
3. **Scope selectors** to the component root so `.box` and similar only match elements inside that component, not the rest of the page.

### Vue 3 (Composition API)

1. Import `onMounted`, `onUnmounted`, and `ref` from Vue.
2. Import `gsap` and any plugins (e.g., `ScrollTrigger`).
3. Register plugins once at app level (e.g., in `main.js`), not inside every component.
4. In `onMounted`, create a `gsap.context()` with the container ref as scope.
5. In `onUnmounted`, call `ctx.revert()`.

```javascript
import { onMounted, onUnmounted, ref } from "vue";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger); // once per app, e.g. in main.js

export default {
  setup() {
    const container = ref(null);
    let ctx;

    onMounted(() => {
      if (!container.value) return;
      ctx = gsap.context(() => {
        gsap.to(".box", { x: 100, duration: 0.6 });
        gsap.from(".item", { autoAlpha: 0, y: 20, stagger: 0.1 });
      }, container.value);
    });

    onUnmounted(() => {
      ctx?.revert();
    });

    return { container };
  },
};
```

**Key points:**

- `gsap.context(callback, scope)` — pass `container.value` as the second argument so selectors like `.item` are scoped to that root.
- All animations and ScrollTriggers created inside the callback are tracked and reverted when `ctx.revert()` is called.
- Always call `ctx.revert()` in `onUnmounted` so tweens and ScrollTriggers are killed and inline styles reverted.

### Vue 3 (`<script setup>`)

Same pattern with `<script setup>` syntax:

```vue
<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

const container = ref(null);
let ctx;

onMounted(() => {
  if (!container.value) return;
  ctx = gsap.context(() => {
    gsap.to(".box", { x: 100 });
    gsap.from(".item", { autoAlpha: 0, stagger: 0.1 });
  }, container.value);
});

onUnmounted(() => {
  ctx?.revert();
});
</script>

<template>
  <div ref="container">
    <div class="box">Box</div>
    <div class="item">Item</div>
  </div>
</template>
```

### Nuxt 4

1. Create a reusable composable at `composables/useGSAP.ts` to register GSAP plugins and provide lazy-loading for infrequently used plugins.
2. Access `gsap`, `ScrollTrigger`, and `lazyLoadPlugin` in components via `useGSAP()`.
3. Use `gsap.context(scope)` and `onUnmounted` `ctx.revert()` in components, same as Vue 3.

```typescript
// composables/useGSAP.ts
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

const PLUGINS = [
  "CSSRulePlugin", "CustomBounce", "CustomEase", "CustomWiggle",
  "Draggable", "DrawSVGPlugin", "EaselPlugin", "EasePack", "Flip",
  "GSDevTools", "InertiaPlugin", "MorphSVGPlugin", "MotionPathHelper",
  "MotionPathPlugin", "Observer", "Physics2DPlugin", "PhysicsPropsPlugin",
  "PixiPlugin", "ScrambleTextPlugin", "ScrollSmoother", "ScrollToPlugin",
  "ScrollTrigger", "SplitText", "TextPlugin",
] as const;

const pluginMap = {
  CustomEase: () => import("gsap/CustomEase"),
  Draggable: () => import("gsap/Draggable"),
  CSSRulePlugin: () => import("gsap/CSSRulePlugin"),
  EaselPlugin: () => import("gsap/EaselPlugin"),
  EasePack: () => import("gsap/EasePack"),
  Flip: () => import("gsap/Flip"),
  MotionPathPlugin: () => import("gsap/MotionPathPlugin"),
  Observer: () => import("gsap/Observer"),
  PixiPlugin: () => import("gsap/PixiPlugin"),
  ScrollToPlugin: () => import("gsap/ScrollToPlugin"),
  ScrollTrigger: () => import("gsap/ScrollTrigger"),
  TextPlugin: () => import("gsap/TextPlugin"),
  DrawSVGPlugin: () => import("gsap/DrawSVGPlugin"),
  Physics2DPlugin: () => import("gsap/Physics2DPlugin"),
  PhysicsPropsPlugin: () => import("gsap/PhysicsPropsPlugin"),
  ScrambleTextPlugin: () => import("gsap/ScrambleTextPlugin"),
  CustomBounce: () => import("gsap/CustomBounce"),
  CustomWiggle: () => import("gsap/CustomWiggle"),
  GSDevTools: () => import("gsap/GSDevTools"),
  InertiaPlugin: () => import("gsap/InertiaPlugin"),
  MorphSVGPlugin: () => import("gsap/MorphSVGPlugin"),
  MotionPathHelper: () => import("gsap/MotionPathHelper"),
  ScrollSmoother: () => import("gsap/ScrollSmoother"),
  SplitText: () => import("gsap/SplitText"),
} as const;

type PluginMap = typeof pluginMap;
type Plugins = keyof PluginMap;
type PluginModule<K extends Plugins> = Awaited<ReturnType<PluginMap[K]>>;
type PluginExport<K extends Plugins> = PluginModule<K>[K & keyof PluginModule<K>];

export default function () {
  gsap.registerPlugin(ScrollTrigger);

  async function lazyLoadPlugin<K extends Plugins>(plugin: K): Promise<PluginExport<K>> {
    const loader = pluginMap[plugin];
    const m = await loader();
    const p = (m as any)[plugin];
    gsap.registerPlugin(p);
    return p;
  }

  return { gsap, ScrollTrigger, lazyLoadPlugin };
}
```

Access in components:

```javascript
const { gsap, ScrollTrigger, lazyLoadPlugin } = useGSAP();
```

- `useGSAP()` provides typed access to the gsap instance and lazy-load method.
- Lazy-load any plugin (SplitText, MorphSVG, etc.) that is not widely used to reduce initial bundle size.
- Use `gsap.context(scope)` and `onUnmounted` `ctx.revert()` in components, same as Vue 3.

### Svelte

1. Import `onMount` from Svelte.
2. Import `gsap` and any plugins.
3. Use `bind:this={container}` to get a reference to the root element.
4. In `onMount`, create a `gsap.context()` with the container as scope.
5. Return a cleanup function from `onMount` that calls `ctx.revert()`.

```svelte
<script>
  import { onMount } from "svelte";
  import { gsap } from "gsap";
  import { ScrollTrigger } from "gsap/ScrollTrigger";

  let container;

  onMount(() => {
    if (!container) return;
    const ctx = gsap.context(() => {
      gsap.to(".box", { x: 100 });
      gsap.from(".item", { autoAlpha: 0, stagger: 0.1 });
    }, container);
    return () => ctx.revert();
  });
</script>

<div bind:this={container}>
  <div class="box">Box</div>
  <div class="item">Item</div>
</div>
```

- `bind:this={container}` — get a reference to the root element to pass to `gsap.context(scope)`.
- `return () => ctx.revert()` — Svelte's `onMount` can return a cleanup function; `ctx.revert()` runs when the component is destroyed.
- **Svelte 5 note:** Svelte 5 uses a different lifecycle API (runes); the same principle applies: create in mounted and revert in destroyed.

### Scoping Selectors

Always pass the **scope** (container element or ref) as the second argument to `gsap.context(callback, scope)`:

- `gsap.context(() => { gsap.to(".box", ...) }, containerRef)` — `.box` is only searched inside `containerRef`.
- Running `gsap.to(".box", ...)` without a context scope in a component can affect other instances or the rest of the page.

### ScrollTrigger Cleanup and Refresh

- ScrollTrigger instances are created when you use the `scrollTrigger` config on a tween/timeline or `ScrollTrigger.create()`.
- They are **included** in `gsap.context()` and reverted when you call `ctx.revert()`.
- Create ScrollTriggers inside the same `gsap.context()` callback you use for tweens.
- Call `ScrollTrigger.refresh()` after layout changes (e.g., after data loads) that affect trigger positions.
  - In Vue: use `nextTick` after DOM updates.
  - In Svelte: use `tick` after DOM updates.
  - After async content load: call `ScrollTrigger.refresh()` once content is rendered.

### When to Create vs Kill

| Lifecycle | Action |
|---|---|
| **Mounted** | Create tweens and ScrollTriggers inside `gsap.context(scope)`. |
| **Unmount / Destroy** | Call `ctx.revert()` so all animations and ScrollTriggers in that context are killed and inline styles reverted. |

Do not create GSAP animations in the component's setup or in a synchronous top-level script that runs before the root element exists. Wait for `onMounted` / `onMount` (or equivalent) so the container ref is in the DOM.

## Pitfalls

- **Creating tweens before mount:** Do not create tweens or ScrollTriggers before the component is mounted (e.g., in `setup` without `onMounted`); the DOM nodes may not exist yet.
- **Ungscoped selectors:** Do not use selector strings without a scope. Always pass the container to `gsap.context()` as the second argument so selectors don't match elements outside the component.
- **Skipping cleanup:** Always call `ctx.revert()` in `onUnmounted` / `onMount`'s return so animations and ScrollTriggers are killed when the component is destroyed. Leaked tweens on detached nodes cause performance degradation and visual bugs.
- **Registering plugins per render:** Do not register plugins inside a component body that runs every render. It doesn't break anything but is wasteful. Register once at app level (e.g., `main.js` or a Nuxt plugin/composable).
- **Forgetting ScrollTrigger.refresh():** After layout changes, image loads, font loads, or async data rendering, trigger positions may be stale. Call `ScrollTrigger.refresh()` after the DOM updates.
- **Animating pinned trigger elements in ways that invalidate measurements:** Avoid animating layout properties (width, height, top, left) on pinned elements; this can cause ScrollTrigger measurement errors.
- **Not respecting prefers-reduced-motion:** Provide simpler transitions, instant states, or user-controlled playback for users with reduced-motion preference.

## Verification

1. **Check that animations are scoped:** Open browser DevTools Console and verify no GSAP inline styles appear on elements outside the component root after mount.
2. **Check cleanup on unmount:** Navigate away from the component (or conditionally destroy it), then run in Console:
   ```javascript
   ScrollTrigger.getAll().length
   ```
   The count should not include stale triggers from the unmounted component.
3. **Check for leaked tweens:** After unmount, verify no console errors about tweening detached or null nodes.
4. **Check ScrollTrigger positions:** After layout changes or data loads, run:
   ```javascript
   ScrollTrigger.refresh()
   ```
   and verify trigger start/end positions update correctly.
5. **Check reduced-motion:** In DevTools, emulate `prefers-reduced-motion: reduce` (Rendering tab in Chrome DevTools) and verify animations degrade gracefully.
6. **Type check (Nuxt/TS):** Run `npx vue-tsc --noEmit` in PowerShell to verify the `useGSAP` composable types resolve correctly.
7. **Build check:** Run `npm run build` (or `pnpm build`) and confirm no GSAP-related import or tree-shaking errors.

## Examples

### Runnable Projects

- See `examples/vue/` for a runnable Vite + Vue 3 project demonstrating these patterns.
- See `examples/nuxt/` for a runnable Nuxt 4 project with plugin registration, lazy loading, and SSR-safe patterns.

> **When to load reference files:** If the user needs a full project scaffold, read the files under `examples/vue/` or `examples/nuxt/` to provide copy-pasteable project structure. For plugin-specific API details, refer the user to the **gsap-scrolltrigger** or **gsap-core** skills.

## Related Skills

- **gsap-core** — tweens, properties, easing fundamentals.
- **gsap-timeline** — timeline construction, sequencing, labels.
- **gsap-scrolltrigger** — scroll-driven animation, pinning, scrubbing, refresh patterns.
- **gsap-react** — React-specific patterns (useGSAP hook, contextSafe, cleanup).

## References

- GSAP docs: https://gsap.com/docs/v3/
- GSAP ScrollTrigger docs: https://gsap.com/docs/v3/Plugins/ScrollTrigger/
- GSAP context() docs: https://gsap.com/docs/v3/GSAP/gsap.context()
- Vue 3 Composition API: https://vuejs.org/api/composition-api-lifecycle.html
- Nuxt 4 composables: https://nuxt.com/docs/guide/directory-structure/composables
- Svelte onMount: https://svelte.dev/docs/svelte/onMount
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- MDN prefers-reduced-motion: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
