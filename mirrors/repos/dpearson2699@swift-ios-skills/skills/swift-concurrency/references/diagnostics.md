# Concurrency Diagnostics

Common Swift concurrency compiler warnings and errors with their fixes.

## Diagnostic → Fix Reference

| Diagnostic | Cause | Fix |
| --- | --- | --- |
| `Sending 'x' risks causing data races` | Passing a non-Sendable value across isolation boundaries | Make the type `Sendable`, use `sending` parameter, or restructure to avoid the crossing |
| `Capture of 'x' with non-sendable type in a @Sendable closure` | Closure captures non-Sendable value | Make type Sendable, copy the value, or use an actor |
| `Non-sendable type 'X' returned by implicitly asynchronous call` | Returning non-Sendable from cross-isolation call | Make return type Sendable or keep work on same isolation |
| `Main actor-isolated property 'x' can not be mutated from a nonisolated context` | Accessing @MainActor state from non-main context | Add `@MainActor` to caller, use `await MainActor.run { }`, or restructure |
| `Call to main actor-isolated function in a synchronous nonisolated context` | Calling @MainActor function without await | Add `await`, annotate caller `@MainActor`, or use `.task { }` in SwiftUI |
| `Actor-isolated property 'x' can not be referenced from a nonisolated context` | Accessing actor state without await | Add `await` or move code into the actor |
| `Type 'X' does not conform to protocol 'Sendable'` | Stored properties aren't all Sendable | Make properties Sendable, use `@unchecked Sendable` with a lock, or redesign |
| `Passing closure as a 'sending' parameter risks causing data races` | Closure captures values that could race | Ensure captures are Sendable or don't escape the isolation domain |
| `Task-isolated value of type 'X' passed as a strongly transferred parameter` | Moving a value out of a task unsafely | Copy the value or use `sending` return |
| `Global variable 'x' is not concurrency-safe` | Mutable global without isolation | Add `@MainActor`, make it `nonisolated(unsafe)` (with justification), or use actor |

## Swift 6.2 Approachable Concurrency Changes

With `UpcomingFeature.InferSendableFromCaptures` (Swift 6.2):
- Closures infer Sendable from their captures (fewer explicit annotations needed)
- `nonisolated(nonsending)` is the new default for async functions (SE-0461)
- `@concurrent` marks functions that intentionally run off-actor

## Strict Concurrency Adoption Strategy

1. **Start with `StrictConcurrency: targeted`** in build settings — warns on `Sendable` issues without full enforcement
2. **Fix warnings bottom-up** — start with leaf types (models, DTOs), then services, then UI
3. **Move to `StrictConcurrency: complete`** once warnings are resolved
4. **Use `@preconcurrency import`** temporarily for third-party modules that haven't adopted Sendable — document removal plan

## Runtime Diagnostics

Enable the Thread Sanitizer (`-sanitize=thread`) to catch data races at runtime that the compiler can't statically prove.

Xcode: Edit Scheme → Run → Diagnostics → Thread Sanitizer.

Common TSan findings in concurrent code:
- Simultaneous reads and writes to `Dictionary` or `Array` without actor protection
- Delegate callbacks arriving on unexpected queues
- Completion handlers racing with synchronous property access
