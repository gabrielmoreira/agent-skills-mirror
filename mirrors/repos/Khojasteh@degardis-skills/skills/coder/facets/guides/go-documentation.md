---
title: Go documentation contracts
applicability:
- When package or declaration documentation, or a documentation example, is among what the work produces or assesses
x-claim-provenance:
- claim: Doc comments are complete sentences that begin with the declared name, a package comment begins with Package followed by the package name and belongs in only one file of a multi-file package, doc links such as [Name] and [pkg.Name] were added in Go 1.19, and a paragraph beginning with Deprecated marks a deprecation notice.
  source: https://go.dev/doc/comment
- claim: Example functions named Example, ExampleF, ExampleT, and ExampleT_M attach to the package, a function, a type, or a method, a concluding Output comment is compared with standard output when tests run, and an example without an output comment is compiled but not executed.
  source: https://pkg.go.dev/testing
---

Go declaration comments conventionally form complete sentences beginning with the declared name. A package has one package comment beginning with `Package name`, with `doc.go` serving as a conventional home when the package overview warrants its own file. Heading, list, code-block, and link behavior follows the configured Go documentation tool rather than arbitrary Markdown semantics.

Caller-visible Go contracts can include goroutine ownership, channel closure, concurrency safety, and sentinel or wrapped error behavior even when signatures do not express them directly. Supported documentation links such as `[Reader]` and `[io.Reader]` refer to identifiers, while a `Deprecated:` paragraph carries the package ecosystem's deprecation signal and replacement guidance.

Executable `Example` functions attach to declarations through Go's naming conventions. An `Output:` block makes output part of the checked example contract rather than merely illustrative text, and an example without one is compiled but not run. When the owning task requires executable or rendered documentation evidence, the adopted test command and `go doc` or the project's configured documentation path are the relevant evidence surfaces.
