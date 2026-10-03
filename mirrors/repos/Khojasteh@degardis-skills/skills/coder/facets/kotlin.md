---
title: Kotlin
category: Language
guides:
- kdoc
x-claim-provenance:
- claim: Java types are platform types in Kotlin, with null checks relaxed so their safety guarantees are the same as in Java; a platform value may be used or assigned as non-null, and a null then fails at run time, including through an assertion the compiler emits on assignment to a non-null type or when passing it to a non-null parameter.
  source: https://kotlinlang.org/docs/java-interop.html
- claim: Coroutine cancellation is cooperative, so coroutines react to cancellation only when they suspend or check for it explicitly, and catching CancellationException can break cancellation propagation unless it is rethrown.
  source: https://kotlinlang.org/docs/coroutines-cancellation.html
- claim: The block of a cold flow builder does not run until a collector collects it, and each new collector starts a new, independent execution; hot flows such as SharedFlow and StateFlow emit independently of collectors and share the same stream of values with all collectors.
  source: https://kotlinlang.org/docs/coroutines-flow.html
- claim: For a data class, the compiler uses only the properties declared in the primary constructor for the generated toString, equals, hashCode, copy, and component functions, so properties declared in the class body are excluded.
  source: https://kotlinlang.org/docs/data-classes.html
---

The configured Kotlin version, language and API levels, compiler plugins, target platforms, coroutine and serialization versions, opt-ins, and Java interoperation constraints decide which features apply.

Nullability across platform types, value and data-class equality, coroutine scope ownership, dispatcher and cancellation behavior, flow semantics, resource lifetime, serialization, and source or binary compatibility are behavioral contracts. A value from Java has a platform type whose null checks are relaxed to Java's level: the compiler accepts it where a non-null value is expected, and a null then fails only at run time, so Kotlin's null safety starts where such values are checked. A data class's generated `equals`, `hashCode`, `toString`, `copy`, and component functions use only the properties in its primary constructor, so moving a property into or out of the constructor changes equality. Semantics run through smart casts, platform types, variance, delegation, extension dispatch, operator resolution, destructuring, initialization order, non-local returns, inline lambdas, and Java overload or property mapping.

Structured concurrency holds only while each coroutine is tied to an owner. Cancellation is cooperative: a coroutine reacts only at a suspension point or an explicit check, so a loop with neither keeps running after its scope is canceled, and a broad `catch` that swallows `CancellationException` stops cancellation from propagating through the hierarchy. A cold flow runs its builder anew for every collector, while a hot `SharedFlow` or `StateFlow` emits whether or not anyone collects and shares one stream among its collectors. Lifecycle and ownership run through coroutine parents and children, supervisor boundaries, dispatchers, context elements, cancellation and cleanup, hot versus cold flows, sharing start and stop policy, buffering, and exception propagation.

Generated methods, default arguments, inline or reified code, suspend signatures, annotations, and multiplatform expect/actual declarations are emitted or cross-platform contracts. Code is also referenced indirectly, so structural changes can break:

- compiler-plugin output, serializers, and generated bindings
- reflection names and annotations
- Java callers and native or JS exports
- platform source sets, expect/actual pairs, and dynamic registrations

Behavioral evidence covers nulls crossing platform boundaries, equality and generated members, default and named arguments, coroutine failure and cancellation timing, flow collection and replay, dispatcher changes, and resource cleanup. Build and runtime evidence spans each affected configured target and representative foreign-language consumer, and emitted signatures or generated serializers are evidence where source syntax hides compatibility. Dispatchers, virtual time, scopes, and collectors decide coroutine timing under test, and a change must preserve structured concurrency, cancellation, memory visibility, serialization shape, and platform-specific behavior unless altering them is part of its requested outcome. A performance result is specific to the stated target and runtime and to the project's target-specific benchmark harness with its configured warmup. Boxing, collection or sequence pipelines, coroutine dispatch, flow buffering, allocation, and interoperation are cost candidates only where profiles locate cost, and JVM conclusions do not transfer to Native, JavaScript, or Wasm targets.
