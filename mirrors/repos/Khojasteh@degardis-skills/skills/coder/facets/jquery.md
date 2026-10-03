---
title: jQuery
category: Framework and library
x-claim-provenance:
- claim: From jQuery 3.0, Deferred .then() callbacks are always called asynchronously, where previously a callback added to an already settled Deferred ran synchronously, and exceptions thrown in .then() callbacks become rejections; .done(), .fail(), and .pipe() keep the old behavior, which is not Promises/A+ compliant and lets thrown errors bubble out; the development build of jQuery Migrate warns when deprecated or removed features are used and can serve short term when older incompatible code must run.
  source: https://jquery.com/upgrade-guide/3.0/
- claim: .remove() removes all bound events and jQuery data associated with the removed elements, while .detach() removes elements without removing their data and events.
  source: https://api.jquery.com/remove/
- claim: Directly bound event handlers are bound only to the currently selected elements, which must exist when .on() is called, while delegated handlers can process events from descendant elements added to the document later.
  source: https://api.jquery.com/on/
---

The configured jQuery version, compatibility layer, plugins, browser support, and whether another framework also owns the same DOM define the jQuery environment. The version changes asynchronous behavior: since jQuery 3.0, a Deferred's `.then()` callbacks always run asynchronously and exceptions thrown in them become rejections, while `.done()`, `.fail()`, and `.pipe()` keep the older behavior that runs synchronously and lets errors escape, so code moved from one family to the other changes timing and error handling. jQuery Migrate warns when deprecated or removed features are used, which makes its warnings evidence of what a removal would break.

Selector scope, DOM ownership, delegated versus direct event handling, data storage, queue and animation behavior, Ajax defaults, promise semantics, and cleanup are behavioral contracts. A directly bound handler attaches only to the elements that exist when `.on()` runs, while a delegated handler on an ancestor also serves descendants inserted later, so the choice decides whether dynamic content responds. `.remove()` discards the elements' handlers and jQuery data with them and `.detach()` keeps both, while nodes removed by another owner through the native DOM leave that cleanup undone. Behavior runs through chained selection, implicit iteration, delegated handlers, event namespaces, data caches, cloned nodes, insertion and removal, animation queues, deferred callbacks, Ajax converters and global handlers, and plugin initialization.

Behavior is also referenced indirectly, through:

- selector strings and data attributes
- load-time plugins, document-level handlers, and global aliases
- template fragments and dynamically inserted markup
- code that assumes a plugin-mutated DOM shape

Characteristic failure modes are duplicate handlers, stale data, detached nodes, unsafe HTML insertion, event-order differences, and missing cleanup when another owner removes nodes. Replacing jQuery has observable responsibilities in plugin behavior, event namespaces, serialized requests, global Ajax hooks, and DOM mutations, and shared DOM and routing need a single owner during coexistence.

Behavioral evidence covers real DOM behavior for selectors, propagation, delegation, insertion, removal, focus, forms, accessibility, plugin lifecycle, and browser integration. Ajax and deferred completion are timing variables whose behavior is not safely assumed to match native Promise timing, and evidence covers abort, error, global hooks, serialization, and cleanup. Performance evidence comes from the real interaction and DOM size rather than isolated selector calls, and an optimization must preserve event order, plugin contracts, accessibility, and teardown.
