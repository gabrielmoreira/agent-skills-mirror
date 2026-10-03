---
title: Node.js
category: Runtime and platform
x-claim-provenance:
- claim: The default --unhandled-rejections mode is throw, which emits unhandledRejection and, if no such hook is set, raises the unhandled rejection as an uncaught exception.
  source: https://nodejs.org/api/cli.html
- claim: Every time the next-tick queue is drained the microtask queue is drained immediately after, so in CommonJS modules process.nextTick() callbacks run before queueMicrotask() callbacks, while in ES modules, which are processed as part of the microtask queue, queueMicrotask() callbacks run before process.nextTick() ones.
  source: https://nodejs.org/api/process.html
- claim: A .js file is loaded as an ES module when its nearest parent package.json has a top-level "type" field of "module"; introducing an "exports" field to an existing package prevents consumers from using any entry point it does not define, including package.json, which is likely a breaking change.
  source: https://nodejs.org/api/packages.html
- claim: When a readable stream piped with pipe() emits an error, the writable destination is not closed automatically, and each stream must be closed to prevent memory leaks.
  source: https://nodejs.org/api/stream.html
---

The configured Node versions, module and resolution mode, package manager and lockfile, package exports and imports, supported operating systems, worker and process model, and deployment environment define the Node environment. Node, package-manager, loader, permission, test-runner, and stream APIs exist only in the configured versions that support them, and dependencies change through the declaration that owns the resolved version.

CommonJS or ES module boundaries follow from the package contract rather than local preference. A `.js` file is an ES module when the nearest `package.json` declares `"type": "module"`, so moving a file across a package boundary can change its module system, and adding an `exports` map to an existing package hides every entry point it does not list, `package.json` included, which breaks consumers that import other paths.

Ownership of processes, workers, timers, streams, sockets, files, abort signals, caches, environment, and shutdown is a behavioral contract. Scheduling depends on the module format: in CommonJS, `process.nextTick` callbacks run before promise and `queueMicrotask` callbacks, while in an ES module the microtasks run first, because module evaluation already happens inside the microtask queue. By default an unhandled promise rejection is raised as an uncaught exception, which terminates the process unless something handles it. Control flow runs through next-tick and microtask queues, event-loop phases, timers, promise rejection, async-resource context, callbacks, worker messages, child-process events, signals, and handles that keep the process alive.

Lifecycle and ownership run through stream consumption, backpressure, errors, close, end, and finish ordering, pipeline teardown, partial writes, abort behavior, encodings, buffer ownership, and web-stream interoperation. `readable.pipe()` does not close the destination when the source errors, which leaves both streams for the surrounding code to close. The following are observable state as well:

- conditional exports, resolution conditions, and loader hooks
- symlinks, native add-ons, and package graph duplication
- caches, environment variables, and filesystem and path assumptions
- startup files and shutdown handlers

Runtime evidence depends on the configured Node, package-manager, and loader path on affected supported operating systems, and packages exporting both module formats have two consumer surfaces. Behavioral evidence distinguishes event ordering, unhandled rejections, stream backpressure and premature close, aborts, signals, worker and process shutdown, filesystem edges, cache invalidation, and absence of leaked handles. Performance evidence comes from production-equivalent processes with Node's configured profiling and diagnostic facilities, and an optimization must preserve event-loop responsiveness, stream semantics, package resolution, cleanup, and exit status.
