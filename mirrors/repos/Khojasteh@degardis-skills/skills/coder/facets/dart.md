---
title: Dart
category: Language
x-claim-provenance:
- claim: Dart DevTools exposes CPU and memory profiling for VM-backed targets, while Dart web applications require browser profiling tools.
  source: https://dart.dev/tools/dart-devtools
- claim: Dart has enforced sound null safety since Dart 3, released in May 2023.
  source: https://dart.dev/null-safety
- claim: On native platforms int is a signed 64-bit integer and double a 64-bit IEEE value, while on the web both are a single 64-bit double-precision value with 53 bits of integer precision, x is int is true for a number with a zero fractional part, bitwise operators truncate operands to 32-bit integers, and identical(1.0, 1) is true.
  source: https://dart.dev/resources/language/number-representation
- claim: The Dart web platform does not support isolates, and web apps can use web workers instead; web workers copy data sent between threads, and isolates do the same while also providing APIs that can transfer memory more efficiently.
  source: https://dart.dev/language/concurrency
- claim: A function that returns a Future and throws synchronously lets the error escape a caller's catchError, so functions returning futures should emit their errors in the future; Future.sync completes with an error when its callback throws.
  source: https://dart.dev/libraries/async/futures-error-handling
---

The configured SDK constraint, soundness mode, target runtime, package resolution, lints, and code-generation pipeline decide which language and library features apply. Dart has enforced sound null safety since Dart 3, so the soundness mode varies only for code still on a Dart 2 SDK.

Nullability, value and identity semantics, synchronous versus asynchronous error delivery, future and stream ownership, cancellation protocol, zone behavior, isolate boundaries, serialization, and cleanup are behavioral contracts. Error delivery breaks most quietly: a function that returns a `Future` but throws before producing it raises the error synchronously, past any `catchError` the caller attached, and `Future.sync` exists to turn such a throw into a failed future. Control flow, lifecycle, and ownership run through future completion order, microtask versus event-queue scheduling, unawaited work, zone error handling, stream subscription pause/cancel behavior, and resource cleanup.

Targets differ in more than speed. Native `int` is a signed 64-bit integer, but on the web every number is a JavaScript double, so integers lose precision beyond 2^53, bitwise operators truncate to 32 bits, `1.0 is int` is true, and `identical(1.0, 1)` holds. The web platform has no isolates at all, and data sent between isolates, like data sent between web workers, is copied unless an isolate API transfers it. An isolate earns its cost only at an actual concurrency or isolation boundary, and generated models or serializers stay maintainable only when their checked-in or build-produced ownership is explicit. Characteristic failure modes involve null promotion, late initialization, collection aliasing, equality and hash codes, numeric behavior across targets, and values crossing JavaScript, native, or serialized boundaries.

Code is also referenced indirectly, so structural changes can break:

- dynamic invocation, mirrors, and annotations
- generated `.g.dart` and part files and package configuration
- conditional imports, platform channels, and FFI
- isolate messages and serializer field names

Behavioral evidence distinguishes immediate throws from failed futures, makes event ordering explicit, and covers stream completion and cancellation, zone capture, isolate message shape, nullability edges, and cleanup after failure. Code generation and analysis run through the project's configured commands, and each supported runtime or compiled target is separate evidence where its numeric, I/O, FFI, or scheduling behavior differs. Clocks, queues, randomness, files, sockets, and isolate lifecycle make results nondeterministic, and static analysis alone does not establish runtime validity. A performance result is specific to the measured target and execution mode, including JIT versus AOT and assertion settings, and to the project's benchmark harness. DevTools provides CPU and memory evidence for supported VM-backed targets, while web targets need the target browser's tools, and allocation, isolate-message copying, scheduling, and serialization costs do not transfer between target cost models.
