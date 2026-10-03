---
title: Swift DocC contracts
applicability:
- When symbol documentation or DocC content is among what the work produces or assesses
x-claim-provenance:
- claim: Swift typed throws lets a function declare a concrete thrown error type with throws(E), and untyped throws is equivalent to throws(any Error).
  source: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0413-typed-throws.md
  scope: SE-0413, status Implemented (Swift 6.0).
---

Swift symbol documentation uses `///` comments with a summary and discussion, while the configured DocC version determines the supported parameter, return, throws, and callout forms and how they render as structured content. Plain `throws` is equivalent to `throws(any Error)` and names no concrete error type, so caller-recognizable error cases can require prose when those distinctions matter to use. Typed `throws(E)`, available from Swift 6.0, names the thrown type, while prose still explains which of its cases a caller can meet and when.

Swift-specific contracts can include value-versus-reference effects, mutation, actor isolation, `@MainActor` obligations, `Sendable` expectations, cancellation, and partial effects when declarations and attributes do not communicate the full consumer-visible behavior. `@available` remains the declaration-level owner of supported platforms and versions rather than duplicated prose.

DocC symbol and article links are meaningful only when the configured tool resolves them. Tutorials, articles, and overview material have a natural home in the target's `.docc` catalog rather than inside an expanded symbol comment. When the owning task requires link or rendered-documentation verification, the project's DocC build is the relevant evidence surface.
