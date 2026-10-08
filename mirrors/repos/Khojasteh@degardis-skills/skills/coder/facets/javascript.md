---
title: JavaScript
category: Language
description: Code written in JavaScript, or in TypeScript, which runs as JavaScript once its types are erased.
guides:
- javascript-typescript-documentation
x-claim-provenance:
- claim: JSON.stringify omits object properties whose values are undefined, functions, or symbols, serializes those values as null inside arrays, serializes non-finite numbers as null, calls a value's toJSON method, and throws a TypeError for a BigInt or a cyclic structure.
  source: https://tc39.es/ecma262/multipage/structured-data.html
  scope: ECMAScript specification draft (SerializeJSONProperty, SerializeJSONObject, SerializeJSONArray), read 2026-09.
- claim: Array.prototype.sort without a comparator sorts undefined values to the end and compares other values by converting them with ToString and comparing the strings.
  source: https://tc39.es/ecma262/multipage/indexed-collections.html
  scope: ECMAScript specification draft (CompareArrayElements), read 2026-09.
- claim: HTML schedules promise jobs in the microtask queue and performs a microtask checkpoint when the JavaScript execution context stack becomes empty after running a script or callback.
  source: https://html.spec.whatwg.org/multipage/webappapis.html
  scope: WHATWG HTML Living Standard, read 2026-09.
---

The actual host, ECMAScript target, module format and resolution mode, transpilation or bundling path, package client and lockfile, supported runtimes, and strictness decide which syntax and APIs apply, and language and host APIs exist only where the configured runtime or transformation path supports them. Dependency versions and transitive ownership live in the adopted package client's resolved graph.

Missing versus `undefined` versus `null`, coercion, equality, object identity, property descriptors, iteration, promise rejection, cancellation, serialization, and event-loop timing at each boundary are behavioral contracts, and the language's defaults decide several of them silently. `JSON.stringify` drops object properties whose value is `undefined`, a function, or a symbol, writes `null` for those values in arrays and for non-finite numbers, and throws on a `BigInt` or a cycle, so a round trip through JSON erases the difference between a missing property and an `undefined` one. `Array.prototype.sort` without a comparator compares values as strings, so `[10, 9, 1]` sorts to `[1, 10, 9]`.

In browsers and other HTML hosts, promise reactions are microtasks, and the microtask queue is drained as soon as the JavaScript stack empties after a script or callback, so a promise continuation runs before the next timer or event task. Control flow, lifecycle, and ownership run through synchronous execution, microtasks, host task queues, timers, events, promise chains, thenables, async iterators, abort signals, cleanup, and callbacks that outlive their owner.

Behavior is also referenced indirectly, through:

- dynamic property access, proxies, getters and setters, and prototype mutation
- symbols, JSON or structured cloning, and dynamic imports
- loader hooks, bundler aliases, and side-effect declarations
- globals and host-provided objects

The resolved module and package graph, conditional exports, CommonJS/ES module interoperation, duplicate package instances, tree-shaking assumptions, and code that depends on browser, worker, server, or embedded-host behavior are observable state.

Behavioral evidence covers coercion and missing values, event ordering, rejection and cancellation, iterator closure, serialization, dynamic lookup, and cleanup in the actual supported hosts. Runtime evidence depends on the configured loader, transformer, bundler, package graph, and test environment, and a different module mode or DOM or runtime shim does not establish the shipped path. Performance evidence comes from emitted production code with host-appropriate profilers and bundle evidence, and an optimization must preserve observable scheduling, module side effects, runtime validation, and package resolution.
