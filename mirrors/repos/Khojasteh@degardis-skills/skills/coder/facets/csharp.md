---
title: C#
category: Language
guides:
- dotnet-xml-documentation
x-claim-provenance:
- claim: The default C# language version follows the target framework (for example .NET 6 to C# 10 and .NET 9 to C# 13), a version newer than the target framework's default is unsupported, and LangVersion latest follows the installed compiler and can differ between machines.
  source: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/configure-language-version
  scope: .NET 5 and later; page dated 2026-01-16.
- claim: Nullable reference types are entirely a compile-time feature that leaves runtime behavior unchanged, and default structs and new arrays can hold null in non-nullable references without a warning.
  source: https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/null-safety/nullable-reference-types
- claim: An exception from a Task-returning async method is stored in the task and rethrown when awaited, while callers cannot catch exceptions from async void methods, which are meant for event handlers.
  source: https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-return-types
- claim: A ValueTask may be awaited or converted with AsTask only once, and reading its result before completion or consuming it more than once is undefined.
  source: https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.valuetask-1
- claim: LINQ queries that return sequences execute when enumerated, re-execute on each enumeration against the source's current contents, and ToList, ToArray, or scalar operators such as Count execute them immediately.
  source: https://learn.microsoft.com/en-us/dotnet/csharp/linq/get-started/introduction-to-linq-queries
---

C# code compiles under a language version that defaults from the target framework — moving a project from .NET 6 to .NET 9 moves it from C# 10 to C# 13 — and a version newer than the target framework's default is unsupported. `LangVersion` set to `latest` follows whichever compiler is installed, so the same source can build differently on different machines. The nullable context, analyzer rules, and conditional symbols decide the remaining diagnostics.

Nullable reference types are a compile-time feature only. Annotations and warnings change nothing at runtime, so nothing stops `null` from arriving through code compiled without the nullable context, reflection, or deserialization, and a `default` struct or a newly allocated array holds `null` in non-nullable references without a warning. Runtime validation at a boundary is therefore a separate contract from the annotations.

An exception thrown in a `Task`-returning async method is stored in the task and rethrown when it is awaited, while a caller cannot catch an exception from an `async void` method, which is why `async void` belongs to event handlers. A `ValueTask` may be awaited, or converted with `AsTask`, only once, and reading its result before completion or consuming it twice is undefined. A LINQ query that returns a sequence runs when it is enumerated and again on every enumeration, against the source's contents at that moment, while `ToList`, `ToArray`, or an aggregate such as `Count` runs it once.

Equality and hashing, numeric semantics, cancellation, disposal, exception behavior, culture, and serialization at the boundary are also behavioral contracts. Overload and generic inference, value versus reference behavior, records, closures, checked arithmetic, pattern matching, exception filters, async streams, iterator state, the synchronization context, and synchronous versus asynchronous disposal all shape what code actually does. Public metadata, overloads, generic constraints, attributes, reflection, source generation, trimming or ahead-of-time compilation, P/Invoke, COM, and cross-language consumption are part of the emitted contract.

Shape and names are also consumed indirectly, by:

- serializers and persisted payloads
- reflection names, dependency injection, and options binding
- generated code, trimming annotations, and native entry points
- dynamic dispatch, multi-target branches, and downstream assemblies

Behavioral evidence distinguishes synchronous throws from task faults and cancellation from failure, and covers disposal on every exit, repeated enumeration, equality and hash behavior, numeric edges, culture, and serialized compatibility. Where source does not reveal metadata shape, built-assembly and consumer-facing API evidence settles it, and reflection, source generation, trimming, interop, and each supported target are separate runtime surfaces. Performance evidence comes from release builds after the runtime's configured warmup, and an optimization must preserve allocation ownership, continuation timing, public metadata, serialization, and compatibility across supported consumers.
