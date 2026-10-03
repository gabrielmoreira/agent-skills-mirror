---
title: Rust
category: Language
guides:
- rustdoc
x-claim-provenance:
- claim: Integer overflow panics at run time in debug builds, which include overflow checks, and performs two's complement wrapping in release builds, which do not; relying on the wrapping is considered an error, and the wrapping_*, checked_*, overflowing_*, and saturating_* methods handle overflow explicitly.
  source: https://doc.rust-lang.org/book/ch03-02-data-types.html
- claim: When a dependency is used by several packages, Cargo builds it with the union of all features enabled on it, so features should be additive; resolver version 2 avoids this unification for platform-specific dependencies of targets not being built, for build-dependencies and proc-macros, and for dev-dependencies not needed by the target being built.
  source: https://doc.rust-lang.org/cargo/reference/features.html
- claim: Resolver version 2 is the default for edition 2021 and resolver version 3 for edition 2024; the resolver is a workspace-wide setting taken from the top-level package, and a virtual workspace sets it in its [workspace] table.
  source: https://doc.rust-lang.org/cargo/reference/resolver.html
  scope: Cargo reference, read 2026-09.
- claim: Cargo's feature resolver applies the same options for resolver versions 2 and 3, decoupling build-dependency and proc-macro features from normal dependencies, decoupling dev-dependency features unless dev units are built, and ignoring features of inactive targets.
  source: https://github.com/rust-lang/cargo/blob/07b80494920f3824e2515e536b76ff282e23993e/src/resolver/features.rs#L198-L224
  scope: Cargo source at commit 07b80494, committed 2026-09-25.
- claim: In Rust 2024, temporaries created while evaluating the tail expression of a block, function, or closure body are dropped before the block's local variables, whereas in Rust 2021 they were dropped after them.
  source: https://doc.rust-lang.org/edition-guide/rust-2024/temporary-tail-expr-scope.html
---

The configured edition, minimum supported Rust version, target triples, feature sets, dependency lock, profiles, panic strategy, FFI boundaries, and unsafe policy decide which language and library features apply, and compiler, standard-library, target, and dependency features exist only where the configured toolchains and features support them. Several of these change behavior without changing source. Integer overflow panics in a debug build and wraps silently in a default release build, which is why the explicit `wrapping_*`, `checked_*`, `overflowing_*`, and `saturating_*` methods exist. The edition moves drop timing: in Rust 2024 the temporaries in a block's tail expression are dropped before the block's locals rather than after, which can shorten a borrow or lock guard. Cargo builds each dependency once with the union of every feature its dependents enable, so enabling a feature in one crate changes that dependency for all of them. Resolver versions 2 and 3 narrow that union in the same way: they do not enable features of a target-specific dependency for a target not being built, and they keep features enabled by build-dependencies, by proc-macros, and by dev-dependencies not needed by the target being built apart from those of the same package used as a normal dependency. The resolver is one setting for the whole workspace, taken from the top-level package or from a virtual workspace's `[workspace]` table rather than from each member's edition; a top-level package on the 2021 edition defaults to resolver version 2, and one on the 2024 edition to resolver version 3.

Ownership and borrowing, drop order, pinning, error and panic behavior, integer semantics, thread safety, atomics and memory ordering, serialization, and source or ABI compatibility are behavioral contracts. Ownership runs through moves, borrows, reborrows, interior mutability, lifetimes hidden by elision, temporary lifetime, destructor order, partial initialization, unwinding, and callbacks or futures that retain captures. Unsafe-code boundaries are clearest when unsafe scope is minimal and each invariant is stated at the boundary that relies on it. Every unsafe operation carries validity, alignment, provenance, aliasing, initialization, layout, unwind, thread-safety, and ownership assumptions, and those assumptions travel through raw pointers, unions, transmute, FFI, allocators, and `repr` attributes.

Code is also referenced indirectly, so structural changes can break:

- macros, generated code, and build scripts
- conditional compilation and feature unification
- trait objects, auto traits, and pin projections
- serializers, exported symbols, and dynamically loaded names

Behavioral evidence covers move and drop paths, errors and panics, cancellation by future drop, pinning, integer edges, feature combinations, thread handoff, atomics, serialization, and FFI ownership. Build evidence spans the supported toolchain, target, profile, and feature matrix established by the project, and interpreter, sanitizer, model, fuzz, or concurrency evidence is additional only where the project configures and supports it. Performance evidence comes from release profiles with observable work, and an optimization must preserve unsafe invariants, memory ordering, drop behavior, panic strategy, ABI layout, and `Send`/`Sync` assumptions.
