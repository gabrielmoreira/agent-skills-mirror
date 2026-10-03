---
title: Groovy
category: Language
x-claim-provenance:
- claim: Under Groovy truth, non-empty collections, arrays, and maps, non-empty strings, GStrings, and CharSequences, non-zero numbers, and non-null object references are true, and a class can customize its truth with an asBoolean() method.
  source: https://groovy-lang.org/semantics.html
- claim: Code accepted by @TypeChecked remains vulnerable to runtime metaprogramming that changes a called method and can fail at run time, while @CompileStatic resolves method calls at compile time so metaclass changes do not affect them.
  source: https://github.com/apache/groovy/blob/master/src/spec/doc/core-semantics.adoc
- claim: GString and String hash codes differ, so GStrings should be avoided as Map keys, especially when retrieving values with a String; a closure expression ${-> x} is called on each coercion of the GString to String, while ${x} binds its value when the GString is created.
  source: https://groovy-lang.org/syntax.html
- claim: Closure.OWNER_FIRST is the default resolve strategy, calling a property or method on the owner when it exists there and otherwise on the delegate; DELEGATE_FIRST reverses that order.
  source: https://groovy-lang.org/closures.html
---

The configured Groovy and JVM versions, compilation mode, type-checking extensions, dependency graph, and host framework decide which syntax and runtime facilities apply, and features exist only where the configured Groovy/JVM combination supports them.

Whether dynamic dispatch is contractual or static type checking or compilation is required is a per-boundary design distinction, and truthiness, coercion, property lookup, closure delegation, metaprogramming, serialization, and Java-facing signatures follow from it. `@TypeChecked` only checks: code it accepted still dispatches dynamically and fails at run time if metaprogramming changes a method it relied on, while `@CompileStatic` links calls at compile time, so metaclass changes no longer reach them. Global metaclass changes and runtime category effects reach every dynamically dispatched caller and are safe only when tightly owned.

Several semantics differ from Java in ways a Java reader misses. An empty collection, map, or string, a zero number, and `null` are all false, and a class can redefine its truth with `asBoolean()`. A `GString` has a different hash code from the equal `String`, so a map keyed by `GString` misses lookups by `String`, and `${-> x}` re-evaluates on every conversion to `String` while `${x}` captures its value once. A closure resolves names on its owner before its delegate unless its resolve strategy says otherwise, which decides what a DSL block actually calls. Dispatch and semantics run through method and property resolution, `getProperty`/`propertyMissing`/`methodMissing`, closure owner/delegate/resolve strategy, GString conversion timing, coercion, operator dispatch, and default arguments.

Behavior is also referenced indirectly, through:

- AST transforms, annotations, generated methods, and traits
- categories, extension modules, and metaclass mutation
- scripts, binding variables, and DSL entry points
- reflection, serializers, and classloader boundaries

Characteristic failure modes involve Java overload selection, generic erasure, checked exceptions, bean properties, SAM coercion, static-compilation boundaries, and build-phase code that runs before normal tests.

Behavioral evidence covers dynamic and statically compiled paths, truthiness, GString-to-String boundaries, closure delegation, property fallback, overload selection, metaclass isolation, and Java callers. Build evidence comes from the project's configured Groovy, JVM, and build-tool versions and from the relevant classloader and build-phase contexts; a standalone script approximates neither. Global metaclass state leaks between tests unless it is cleaned up, and a change must preserve dynamic lookup, generated members, serialization shape, and Java interoperability unless altering them is part of its requested outcome.
