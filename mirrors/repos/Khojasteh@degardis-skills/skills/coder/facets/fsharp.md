---
title: F#
category: Language
guides:
- dotnet-xml-documentation
x-claim-provenance:
- claim: An F# async expression defines a computation that runs only when started by a triggering function such as Async.StartImmediate, Async.RunSynchronously, or Async.StartAsTask.
  source: https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/async-expressions
- claim: An F# task expression starts immediately, does not implicitly pass a cancellation token or perform cancellation checks, and does not support tail calls, unlike async expressions; backgroundTask ignores the current SynchronizationContext.
  source: https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/task-expressions
- claim: An F# signature file determines which elements of its implementation file are accessible outside it, elements it omits are private, it precedes its implementation file in a project, and its parameter names replace the implementation's.
  source: https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/signature-files
---

F# has two asynchronous models with different semantics. An `async { }` expression only defines a computation: nothing runs until a triggering function such as `Async.StartImmediate`, `Async.RunSynchronously`, or `Async.StartAsTask` starts it, the cancellation token flows through implicitly, and a recursive `return!` is a tail call. A `task { }` expression creates a .NET task that starts immediately, gets no implicit cancellation token or cancellation checks, and does not support tail calls, so a recursive task loop builds an unbounded chain of tasks. `backgroundTask { }` ignores the current synchronization context. Code that mixes the two models, or moves from one to the other, changes when work starts, how it is canceled, and whether deep recursion is safe.

A signature file (`.fsi`) decides what its implementation file exposes: anything it omits is private, it precedes the implementation file in the project, and its parameter names replace the implementation's. The public shape that other .NET languages see can therefore differ from the implementation source, as can compiled names, curried members, tuples, unions, records, options, attributes, reflection, serialization, trimming, and C# consumption, all of which are part of the emitted contract. The effective language version, target frameworks, warning policy, nullable and interop settings, and conditional symbols decide which features apply.

Types carry domain invariants, so representation, equality, comparison, units, mutation, exception versus result behavior, cancellation, and resource ownership are behavioral contracts. Semantics also run through partial application, type inference, generic constraints, pattern-match completeness, option and null boundaries, structural equality and comparison, sequence laziness, closures, computation-expression control flow, task interoperation, the synchronization context, agents or mailboxes, parallel evaluation, disposal expressions, and callbacks whose lifetime crosses the originating scope.

Code is also reached indirectly through:

- active patterns and statically resolved parameters
- generated or erased type providers
- reflection names, serializers, and compiled-name attributes
- extension members, native interop, and downstream C# or other .NET callers

Behavioral evidence covers pattern branches, equality and comparison, lazy and repeated enumeration, async failure timing, cancellation, disposal, null interop, and serialization round trips. Where source syntax hides the emitted public shape, built-assembly and representative-consumer evidence settles it, and reflection, trimming, interop, and each supported target are separate runtime surfaces. Performance evidence comes from release builds after configured warmup, and an optimization must preserve tail-call behavior where it is relied upon, allocation and closure semantics, emitted API compatibility, and concurrency ownership.
