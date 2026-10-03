---
title: Java
category: Language
guides:
- javadoc
x-claim-provenance:
- claim: javac --release compiles for the specified Java SE release against that release's combined Java SE and JDK API; when --source or --target is used instead, the platform classes must be set separately, with the boot class path options for JDK 8 and earlier or --system for JDK 9 and later.
  source: https://docs.oracle.com/en/java/javase/21/docs/specs/man/javac.html
  scope: JDK 21 javac documentation.
- claim: A comparator is consistent with equals when compare(e1, e2) == 0 has the same boolean value as e1.equals(e2); a sorted set or sorted map using a comparator inconsistent with equals violates the general Set or Map contract, for example a TreeSet keeps two elements that are equal but compare as different.
  source: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Comparator.html
- claim: Stream intermediate operations are lazy and traversal of the source does not begin until the terminal operation executes; after the terminal operation the pipeline is consumed and cannot be used again.
  source: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/package-summary.html
---

The configured source or release level, JDK, target runtimes, compiler flags, nullness or analyzer rules, and conditional build variants decide which language and library features apply, and APIs exist only on the configured runtimes that support them. How the release level is set matters: `javac --release N` compiles against the API of release N, while `-source` and `-target` alone still compile against the running JDK's classes unless the build also supplies that release's platform classes, so code can compile cleanly and then fail on the target runtime with a missing method.

Nullability, equality and hashing, ordering, numeric and locale behavior, exception and resource ownership, generics, serialization, concurrency and memory visibility, and source or binary compatibility are behavioral contracts, and the library enforces some of them only by misbehaving. A comparator whose zero result disagrees with `equals` makes a `TreeSet` or `TreeMap` break the `Set` or `Map` contract, keeping two elements that are equal or merging two that are not. A stream runs nothing until its terminal operation and cannot be traversed again afterward. Semantics run through overload resolution, boxing and unboxing, generic erasure and bridges, covariance, collection mutability, stream laziness, comparator consistency, try-with-resources suppression, and exception translation.

Lifecycle and ownership run through threads, executors, futures, interruption, locks, volatile and atomic accesses, publication, happens-before edges, thread-local state, and callbacks that outlive owners. Public signatures, erased generic shape, records or sealed hierarchies, annotations, reflection, service loading, serialization, JNI, and cross-language callers are compatibility boundaries. Code is also referenced indirectly, so structural changes can break:

- annotations and processors and generated sources
- reflection, method handles, and serializers
- service descriptors and dependency injection
- native declarations, module exports and opens, and dynamically loaded names

Behavioral evidence covers equality, hash, and order contracts, locale and encoding, numeric edges, resource failure and suppression, stream reuse or laziness, interruption, publication, races, and serialized compatibility. Build and runtime evidence comes from the configured JDK and supported target runtimes, and bytecode and representative consumer compilation are evidence where erasure, bridges, modules, reflection, or binary compatibility matter. Performance evidence comes from warmed production-equivalent code with configured profilers or harnesses, and an optimization must preserve memory visibility, allocation ownership, public binary surface, and exception behavior.
