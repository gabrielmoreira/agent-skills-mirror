---
title: Blazor
category: Framework and library
x-claim-provenance:
- claim: Blazor render modes are Static Server, Interactive Server, Interactive WebAssembly, and Interactive Auto, which uses Blazor Server initially and client-side rendering on later visits after the bundle downloads, decides once per component without switching while it is on the page, and requires components built from a separate client project.
  source: https://learn.microsoft.com/en-us/aspnet/core/blazor/components/render-modes
  scope: ASP.NET Core 8.0 and later.
- claim: Prerendering is enabled by default for interactive components, so components render twice; state not persisted during prerendering is lost and recreated and can cause UI flicker; OnAfterRender is not called during prerendering; client-only services fail to resolve during prerendering.
  source: https://learn.microsoft.com/en-us/aspnet/core/blazor/components/prerender
  scope: ASP.NET Core 8.0 and later.
- claim: A Blazor WebAssembly app's code is served to clients and cannot be protected from inspection and tampering, so sensitive data must not be placed in it, and client-side authorization checks can be bypassed.
  source: https://learn.microsoft.com/en-us/aspnet/core/blazor/security/webassembly/
---

In .NET 8 and later, where a Blazor component runs is decided by its render mode. Static server rendering produces HTML with no interactivity, Interactive Server runs the component on the server over a circuit, Interactive WebAssembly runs it in the browser, and Interactive Auto starts on the server and uses WebAssembly on later visits once the bundle has downloaded, deciding once per component rather than switching while it is on the page. The render mode therefore fixes what a component can inject, what must be serializable, and what a network interruption means, and Auto components have to be built from the client project that hosts WebAssembly.

Interactive components are prerendered by default, so they render twice: once statically on the server and again when they become interactive. State created during prerendering is lost unless it is persisted, which repeats the work and can make the UI flicker; `OnAfterRender` runs only in the interactive render; and a component from the client project fails at run time during prerendering if it injects a service registered only on the client.

Code that runs on WebAssembly is served to the browser and can be inspected and modified, so secrets, connection strings, and private logic do not belong in a WebAssembly assembly, and authorization checks there can be bypassed; authorization holds only in the server's own endpoints. When render modes or frameworks coexist, component islands, route splits, JavaScript bridges, persistent component state, and reconnection behavior are the boundaries that need explicit limits.

Parameter and cascading-state ownership, event flow, form validation, the authorization boundary, DI scope, navigation, cancellation, and disposal are behavioral contracts, and behavior runs through lifecycle methods, parameter changes, cascading values, render triggers, circuits and reconnection, JS interop, serialization, and subscription cleanup. Browser-visible state and failures are distinct from server circuit, HTTP, and application-host failures.

Behavior is also reached indirectly through:

- host-page integration and route declarations
- registered callbacks and JS object references
- scoped services and persisted state
- generated assets and code whose availability differs by render mode

Each supported render mode has its own lifecycle and interop behavior, observable at the narrowest component, host, or browser boundary that preserves it. Behavioral evidence covers parameter updates, event rendering, forms, authorization, DI scope, reconnection, parity between prerendered and interactive output, JS argument and result serialization, cancellation, navigation, and disposal. Performance evidence comes from published builds under the correct hosting model, and an optimization must not regress startup payload, circuit round trips, render scope, or interop frequency, and must preserve state, authorization, and cleanup.
