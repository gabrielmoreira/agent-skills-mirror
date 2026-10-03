---
title: KDoc contracts
applicability:
- When KDoc comments are among what the work produces or assesses
x-claim-provenance:
- claim: Dokka is the documentation engine for KDoc, KDoc uses Markdown for inline markup and square brackets for links to elements, @constructor documents the primary constructor, @property documents a property including one declared in the primary constructor, @receiver documents an extension receiver, @throws documents an exception, and @sample embeds a named function's body as an example.
  source: https://kotlinlang.org/docs/kotlin-doc.html
---

The configured Dokka version determines the Markdown and tag forms available to KDoc. Declaration links use Kotlin forms such as `[Symbol]` rather than Javadoc HTML. Kotlin types already own nullability, while prose can carry behavior the type system does not express, including coroutine cancellation and cleanup, dispatcher assumptions, or whether a `Flow` is hot or cold.

`@constructor` and class-level `@property` cover primary-constructor declarations that have no separate comment site, and `@receiver` describes an extension receiver's contract. Java-visible behavior can differ when `@JvmName`, `@JvmStatic`, `@JvmOverloads`, `@Throws`, or platform types reshape the surface seen by JVM callers.

Distinct failures remain distinct `@throws` entries when their conditions differ, including differences between call-time failure and failure during suspension or flow collection. Where the configured tool supports it, `@sample` can link documentation to a compiled sample function so the example has an executable source rather than existing only as copied prose.
