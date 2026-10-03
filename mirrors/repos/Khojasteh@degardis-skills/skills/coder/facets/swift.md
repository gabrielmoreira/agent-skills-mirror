---
title: Swift
category: Language
guides:
- swift-docc
x-claim-provenance:
- claim: Swift 6 includes a new, opt-in language mode that diagnoses potential data races in concurrent code as compiler errors.
  source: https://www.swift.org/blog/announcing-swift-6/
- claim: A continuation must be resumed exactly once on every execution path; CheckedContinuation traps when resumed more than once and logs a warning when destroyed without being resumed, leaving the task suspended, while UnsafeContinuation performs neither check.
  source: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0300-continuation.md
- claim: Task-tree features such as cancellation apply downward to child tasks, child tasks cannot outlast their parent scope and are canceled when the scope exits with a thrown error while they are unawaited, a detached task inherits no priority, task-local values, or actor context, and an unstructured task runs to completion even with no remaining uses of its handle.
  source: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0304-structured-concurrency.md
---

The configured Swift language mode, compiler, package and platform targets, concurrency checking, Objective-C exposure, testing framework, and deployment versions decide which features and APIs apply, and concurrency, ownership, serialization, and platform APIs exist only where the configured versions support them. The language mode is separate from the compiler version: Swift 6 added an opt-in language mode that reports potential data races as compile errors, so one compiler can accept code in one module and reject the same code in a module that adopted the new mode. Availability decisions are clearest when isolated.

Optionality, value versus reference semantics, ARC ownership, errors, task hierarchy and cancellation, actor isolation, sendability, persistence, and source or binary compatibility are behavioral contracts. Ownership runs through copies and copy-on-write mutation, ARC strong, weak, and unowned edges, closure captures, `defer`, collection indices, throwing and async continuations, task-local state, cancellation, actor hops, and main-actor assumptions.

Task lifetime depends on how a task was created. A child task created with `async let` or a task group cannot outlive its scope and is canceled when the scope exits by throwing, and cancellation flows only downward to children. A detached task inherits no priority, task-local values, or actor context and is not canceled with the task that created it, and an unstructured task runs to completion even after its handle is dropped, which is why it needs an explicit owner. A continuation must be resumed exactly once on every path: `CheckedContinuation` traps on a second resume and only logs when it is dropped unresumed, leaving the awaiting task suspended for good, and `UnsafeContinuation` checks neither. Values crossing actor or Objective-C boundaries and platform APIs guarded by configured availability shape lifecycle and ownership as well.

Code is also referenced indirectly, so structural changes can break:

- Objective-C selectors and exposure, dynamic dispatch, and reflection
- serializers, persistence schemas, and generated bindings
- macros, package resources, and storyboards
- notifications, dependency registries, and string-named callbacks

Behavioral evidence covers optionals, value and reference and copy-on-write behavior, ARC cleanup, error timing, task cancellation, actor isolation, continuation resumption, collection-index invalidation, bridging, persistence, and availability fallbacks. The project's configured XCTest or Swift Testing path on affected supported platforms supplies runtime evidence, with clocks, executors where possible, notifications, files, keychain, persistent stores, and UI and application lifecycle boundaries controlled. Performance evidence comes from release builds with the project's configured instruments or measured tests, and an optimization must preserve value semantics, actor isolation, sendability, cancellation, ARC lifetime, and interoperation contracts.
