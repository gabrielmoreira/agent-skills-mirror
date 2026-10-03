---
title: Svelte
category: Framework and library
description: Svelte compiler-driven components and reactivity; include SvelteKit only when its routing and server features are configured.
x-claim-provenance:
- claim: "Svelte 5 reactivity uses runes, with $state replacing reactive let declarations, $derived and $effect replacing $: statements, and $props replacing export let; on:click directives become onclick properties and createEventDispatcher is deprecated in favor of callback props; legacy Svelte 4 syntax still works in components not using runes mode."
  source: https://svelte.dev/docs/svelte/v5-migration-guide
- claim: Effects created with $effect run only in the browser, not during server-side rendering, after the component mounts and after state changes, batched after DOM updates; they track reactive values read synchronously, not reads after await or inside setTimeout; and a returned teardown function runs before the effect re-runs and when the component unmounts.
  source: https://svelte.dev/docs/svelte/$effect
- claim: With a key expression, Svelte updates an each block by inserting, moving, and deleting items rather than adding or removing items at the end and updating state in the middle.
  source: https://svelte.dev/docs/svelte/each
- claim: SvelteKit server load functions run only on the server and must return data serializable with devalue, while universal load functions run on the server during the initial render and also in the browser and can return any value.
  source: https://svelte.dev/docs/kit/load
---

The configured Svelte version and reactivity model, compiler, build tooling, component conventions, and whether SvelteKit supplies routing, loading, actions, server boundaries, and deployment define the Svelte environment. In Svelte 5 the reactivity model is a per-component fact: a component in runes mode declares state with `$state`, derived values with `$derived`, side effects with `$effect`, and props with `$props`, and takes event handlers as properties such as `onclick`, while a component without runes keeps Svelte 4's reactive `let`, `$:`, `export let`, and `on:` directives, so the same syntax can be current in one file and legacy in the next.

Prop and binding ownership, derived state, effects, stores, events, actions, context, keyed identity, lifecycle, accessibility, server/client execution, hydration, transitions, errors, and cleanup are behavioral contracts. An `$effect` never runs during server rendering, only in the browser after mount and after state it read changes, and it tracks only values read synchronously, so a value read after an `await` or inside a timer does not re-run it. An unkeyed `{#each}` block updates items in place by position, while a keyed one inserts, moves, and deletes them, which decides where item state and DOM go when a list reorders. In SvelteKit, a `+page.server` load runs only on the server and returns serializable data, while a universal `+page` load also runs in the browser, so code there cannot assume server-only access.

While Svelte coexists with another framework, shared state, DOM, and URL routing each need a single owner; mounted islands, custom elements, store bridges, and adapter-specific server behavior are explicit integration boundaries.

Behavior runs through reactive dependencies, update scheduling, bindings, stores and subscriptions, events, actions, context, keyed blocks, lifecycle and destroy callbacks, SSR, hydration, transitions, form actions, and generated output where source shape is insufficient. Behavior is also referenced indirectly, through:

- routes, load functions, and server-only modules
- store initialization and action registration
- adapter configuration and generated manifests
- raw HTML and code that mutates generated output

Characteristic failure modes are reactive work rerunning on unrelated changes, unkeyed identity, subscriptions that outlive components or requests, browser-only assumptions on the server, and cleanup missing at destroy.

Async evidence depends on the framework's configured update boundary, and behavioral evidence covers rendered behavior, binding, events, stores, actions, context, lifecycle, server rendering, hydration, transitions, and cleanup. The configured compiler and production build are evidence in their own right: build output, adapter behavior, and accessibility diagnostics come from them, and runtime checks do not expose compiler findings. Performance evidence comes from production output and real interactions, and an optimization must preserve reactive semantics, identity, hydration parity, accessibility, and destroy-time cleanup.
