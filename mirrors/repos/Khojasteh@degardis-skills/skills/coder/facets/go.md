---
title: Go
category: Language
guides:
- go-documentation
x-claim-provenance:
- claim: Go 1.22 creates new for-loop variables on each iteration instead of once per loop, and the new semantics apply only when the package being compiled is from a module whose go line declares Go 1.22 or later.
  source: https://go.dev/wiki/LoopvarExperiment
- claim: An interface value is nil only if both its type and value are unset; storing a nil pointer of a concrete type in an interface such as an error return produces a non-nil interface value.
  source: https://go.dev/doc/faq#nil_error
- claim: The race detector finds only races that happen at runtime and cannot find races in code paths that are not executed; it requires cgo, and on non-Darwin systems an installed C compiler; it supports a listed set of operating system and architecture pairs; and it typically increases memory use 5-10x and execution time 2-20x.
  source: https://go.dev/doc/articles/race_detector
---

The module's configured Go version, build tags, supported operating systems and architectures, cgo policy, and dependency ownership decide which language and library features apply. The `go` line in `go.mod` selects language semantics: since Go 1.22 each loop iteration gets fresh loop variables, but only in packages from modules whose `go` line declares 1.22 or later, so the same closure over a loop variable captures one shared variable or one per iteration depending on that line.

Goroutine ownership, channel direction and closure, context cancellation, error identity and wrapping, resource lifetime, synchronization, serialization, and compatibility at each boundary are behavioral contracts. A goroutine without an explicit completion and cancellation path has no owner that can stop it. Go interfaces belong at consumer boundaries; one introduced merely to wrap a single concrete implementation adds indirection without a consumer. Control flow and ownership run through every goroutine from creation to termination, every channel closer, select behavior, context propagation, lock order, atomic use, deferred cleanup, and loop-variable or closure capture.

An interface value is nil only when both its dynamic type and its value are unset, so a function that returns a nil `*MyError` through an `error` result returns a non-nil error, and its caller sees a failure that never happened. Other characteristic failure modes involve map iteration assumptions, slice capacity and aliasing, pointer escape, zero values, error comparisons, panic/recover boundaries, finalizers, and partial I/O.

Code is also referenced indirectly, so structural changes can break:

- init functions and blank imports
- generated files, build constraints, and embed directives
- reflection, struct tags, and serializers
- plugin or cgo symbols and module replacements

Behavioral evidence covers cancellation, timeouts, early returns, channel closure, blocked send/receive, concurrent access, typed nils, error wrapping, partial I/O, and cleanup after failure. The configured tests and analyzers speak for the build tags and target combinations they ran under. The race detector reports only races that actually occur during the run, so paths the run did not execute stay unexamined; it needs cgo, exists only on the platforms it supports, and multiplies memory use and run time, which makes a race-enabled build diagnostic evidence rather than performance evidence. Stress or fuzz evidence is what exposes schedule- or input-sensitive contracts. Performance evidence comes from built or benchmarked code under representative parallelism and allocation conditions, and an optimization must preserve goroutine termination, synchronization, error identity, and resource ownership.
