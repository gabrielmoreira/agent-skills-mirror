---
title: Vue
category: Framework and library
x-claim-provenance:
- claim: Vue 2 reached end of life on December 31, 2023, and afterward remains available in existing distribution channels but receives no updates, including security and browser compatibility fixes.
  source: https://v2.vuejs.org/lts/
- claim: Destructuring a primitive property of a reactive() object into a local variable, or passing it into a function, loses the reactivity connection; DOM updates after a reactive state change are buffered until the next tick rather than applied synchronously, and nextTick() waits for them.
  source: https://vuejs.org/guide/essentials/reactivity-fundamentals.html
- claim: In server-side rendering, application modules are initialized once and reused across requests, so singleton state declared at module root scope leaks between requests, and a new application instance, including stores, is created for each request.
  source: https://vuejs.org/guide/scaling-up/ssr.html
---

The configured Vue version, Options or Composition conventions, build and template mode, router and store, SSR or hydration setup, and plugin set decide which APIs apply. Vue 2 reached end of life at the end of 2023 and receives no further updates, security fixes included, so a defect found in Vue 2 itself stays unfixed upstream.

Prop and emit contracts, reactive state ownership, computed values versus side-effecting watchers, provider scope, lifecycle, routing, server and request state, accessibility, and cleanup are behavioral contracts. Reactivity is easy to lose silently: destructuring a primitive property out of a `reactive()` object, or passing it to a function, hands over a plain value that no longer tracks the source. DOM updates are batched until the next tick rather than applied as state changes, so code that reads the DOM right after a mutation sees the old state unless it waits for `nextTick()`. On the server, modules are initialized once and shared by every request, so state created at module scope rather than per request leaks one user's data into another's response.

While Vue coexists with another framework, shared state, DOM, and URL routing each need a single owner; mounted containers, custom elements, store bridges, and plugin globals are explicit integration boundaries.

Behavior runs through refs and reactive objects, destructuring, computed dependencies, watchers and cleanup, props, emits, slots, provide/inject, plugins, routing, stores, lifecycle, async work, SSR, and hydration. Behavior is also referenced indirectly, through:

- templates, component names, and directives
- route names, store keys, and dynamic imports
- plugin registration, test selectors, and generated declarations
- raw HTML and state created outside a server request

Characteristic failure modes are lost reactivity, watcher loops, mutated props, unstable keys, shared SSR state, hydration mismatch, unsafe HTML, and work or subscriptions that survive unmount.

Async evidence depends on Vue's update boundary, and rendered behavior and interaction are stronger evidence than component internals when timers, network, router, stores, plugins, and cleanup are controlled. Behavioral evidence covers prop validation, emits, slots, model binding, conditional and keyed rendering, computed and watcher updates, async components, SSR and hydration, accessibility, and unmount. Performance evidence comes from production builds and real component updates, and an optimization must preserve reactivity, identity, server/client parity, accessibility, and cleanup.
