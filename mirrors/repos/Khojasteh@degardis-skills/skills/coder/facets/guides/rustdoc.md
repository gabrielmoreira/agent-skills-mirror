---
title: Rustdoc contracts
applicability:
- When item or module documentation, or a documentation example, is among what the work produces or assesses
x-claim-provenance:
- claim: Rustdoc uses outer /// comments for the following item and inner //! comments for the enclosing crate or module, the first line before the first blank line serves as the summary, and the conventional Examples, Panics, Errors, and Safety sections document examples, panic conditions, Result error conditions, and unsafe preconditions.
  source: https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html
- claim: Rustdoc treats code blocks as Rust doctests by default, ignore skips a block, no_run compiles it without running it, compile_fail requires compilation to fail, and should_panic requires the compiled code to panic.
  source: https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html
---

Rustdoc uses `///` for an item and `//!` for its containing crate or module. Its item lists draw on the opening summary, intra-doc links connect documented items, and established sections such as `# Examples`, `# Errors`, `# Panics`, and `# Safety` signal specific kinds of caller-facing contract rather than generic headings.

Rust-specific documentation can expose behavior not evident from the signature alone: distinct `Result` error conditions, reachable panic conditions, invariants an `unsafe` caller must uphold, feature-gated behavior, blocking or cancellation behavior, interior mutability, and `Send` or `Sync` implications when these affect consumers. Declaration attributes remain the owner of deprecation and hidden visibility, so an absent or incorrect attribute is a code-surface mismatch rather than a documentation defect.

Fenced Rust code blocks participate in rustdoc's doctest model, while `ignore`, `no_run`, `compile_fail`, and `should_panic` alter how that example is checked. Private or exhaustive checks belong to ordinary tests rather than the public example contract. When the owning task requires generated-documentation or example verification, the adopted rustdoc build and doctest command are the relevant evidence surfaces.
