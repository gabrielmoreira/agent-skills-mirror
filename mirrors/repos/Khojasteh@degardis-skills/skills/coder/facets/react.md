---
title: React
category: Framework and library
x-claim-provenance:
- claim: React 19 removed propTypes and defaultProps for function components, legacy context, string refs, module pattern factories, React.createFactory, ReactDOM.render, ReactDOM.hydrate, unmountComponentAtNode, and ReactDOM.findDOMNode.
  source: https://react.dev/blog/2024/04/25/react-19-upgrade-guide
- claim: React ties state to a component's position in the render tree; rendering the same component at the same position preserves its state, while rendering a different component there or giving the component a different key resets it.
  source: https://react.dev/learn/preserving-and-resetting-state
- claim: In development, Strict Mode re-renders components an extra time, re-runs Effects and ref callbacks an extra time, and checks for deprecated APIs; these checks do not affect the production build.
  source: https://react.dev/reference/react/StrictMode
- claim: hydrateRoot expects the rendered content to be identical to the server-rendered content, and mismatches are bugs; common causes include typeof window checks and browser-only APIs in rendering logic and different data on server and client, and in the worst case event handlers attach to the wrong elements.
  source: https://react.dev/reference/react-dom/client/hydrateRoot
---

The configured React version, renderer, build mode, routing and state libraries, server/client boundary, and hydration model decide which APIs apply. React 19, for example, removed `ReactDOM.render`, `ReactDOM.hydrate`, string refs, legacy context, `findDOMNode`, and `propTypes` and `defaultProps` on function components, so code relying on them runs only on earlier versions.

State ownership, render purity, identity and keys, controlled input behavior, context scope, effect purpose and cleanup, suspense and error behavior, accessibility, and cancellation of asynchronous work are behavioral contracts. React keeps a component's state at its position in the tree: the same component at the same position keeps its state, while a different component there or a different `key` resets it, so a key derived from an unstable value moves or discards state and user input. Under Strict Mode, development builds render components and run effects and ref callbacks an extra time to expose impure rendering and missing cleanup, which production builds never do, so a doubled effect in development points at cleanup rather than at production behavior. Server-rendered markup has to match the client's first render exactly; a `typeof window` check, a browser-only API, or data that differs between server and client during rendering produces a hydration mismatch that can, at worst, attach event handlers to the wrong elements.

While React coexists with another framework, shared state, URL routing, DOM ownership, and event bridges each need a single owner; component islands, custom elements, and wrappers are explicit integration boundaries.

Behavior runs through render triggers, state updates, props, context, refs, closures, hook dependencies, effects and cleanup, subscriptions, event ordering, suspense, errors, transitions, server/client imports, hydration, and updates after unmount. Components are also referenced indirectly, through:

- dynamic imports, component registries, and route conventions
- test selectors and generated identifiers
- external stores and raw HTML
- code that relies on reference identity

Characteristic failure modes are duplicated derived state, stale closures, unstable keys, effects that merely copy state, missing cleanup, lost user input, hydration mismatch, and memoization whose identity is itself observed.

Rendered behavior and user interaction are stronger evidence than component internals, and they depend on controlling async updates, timers, network requests, context, routing, external stores, and cleanup. Behavioral evidence covers server and client boundaries, hydration, focus and accessibility, controlled inputs, errors and loading, cancellation, subscriptions, and unmount behavior. Performance evidence comes from production builds and covers commit frequency and render scope, browser long tasks, hydration, and payload size, and an optimization must preserve render purity, event order, identity, and cleanup.
