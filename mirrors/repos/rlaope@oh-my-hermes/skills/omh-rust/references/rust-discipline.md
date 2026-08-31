# Rust Change Discipline

Load this when preparing a Rust change. The escalation check in `references/ub-escalation.md` runs first and is not optional; this reference covers the ordinary-Rust half of the contract.

OMH runs no toolchain. Every command below is one the executor runs and reports.

## 1. Ownership shape

The borrow checker is not an obstacle to route around; it is the design surfacing early. Before code, name:

- **Who owns each value**, and for how long.
- **Which borrows cross a boundary** -- a function return, a struct field, an `await` point, a thread spawn. Borrows that cross an `await` are the usual reason a future is not `Send`.
- **Every deliberate clone**, with the reason. A clone is a legitimate decision when the alternative is a lifetime that infects a public API; it is a surrender when it exists because an error message would not go away.
- **Every interior-mutability wrapper.** `Rc<RefCell<_>>` and `Arc<Mutex<_>>` move a compile-time check to runtime. That trade is sometimes right and is always a decision to write down, because the failure mode changes from a build error to a panic or a deadlock.

Escalation ladder when the checker refuses: restructure ownership, then narrow the borrow's scope, then split the type, then clone deliberately, then interior mutability. `unsafe` is not on this ladder -- reaching for it moves the change into the UB escalation.

## 2. Errors and the API surface

- Name the error type and where conversion happens. Library crates define their own error enum; binaries may collapse to a single boxed error at the top. Mixing the two conventions inside one crate is the thing to avoid.
- Every surviving `unwrap`, `expect`, or `panic!` is listed with its justification. "The invariant is guaranteed by the constructor" is a justification. Silence is not.
- Panicking in a library is an API decision. Say whether the function's contract allows it.
- Make illegal states unrepresentable where the type system can: newtypes for distinct semantic primitives, enums over stringly-typed states, exhaustive `match` so a new variant is a build error rather than a silent fallthrough.
- Public API changes name their semver impact before the change, not at release.

## 3. Async and concurrency

- Say which runtime, and whether the change adds a blocking call inside an async context. Blocking inside an async task starves the executor and is invisible until load.
- Any shared mutable state names its synchronization primitive and its lock order. Two locks with no stated order is a deadlock waiting for scheduling.
- Cancellation is part of the contract: state what happens when a future is dropped mid-operation.
- A hand-written lock-free structure is not ordinary Rust. It escalates.

## 4. The gate list

Name the exact commands, in this order, and treat each as its own observed state:

| Gate | What it proves | What it does not prove |
| --- | --- | --- |
| `cargo fmt --check` | formatting | nothing about behavior |
| `cargo clippy -- -D warnings` | lint cleanliness at the crate's configured level | nothing about runtime behavior |
| `cargo test` | the tests that exist pass | nothing about paths without tests |
| `cargo test --release` | behavior under optimization | debug-only assertions no longer run |
| `cargo doc` | doc links resolve, doc tests compile | nothing about API quality |

Add the repository's own gates rather than assuming this list is complete. When the change is escalated, the Miri and sanitizer gates from `references/ub-escalation.md` are appended and are blocking.

## 5. Failure modes

| Symptom | What actually went wrong | Correction |
| --- | --- | --- |
| Clones added until it compiled | Ownership was never designed | Name the owner, then re-derive the borrows |
| `Rc<RefCell<_>>` everywhere | A compile-time problem was moved to runtime | State the decision, or restructure |
| `unwrap` in a library path | A contract was assumed rather than encoded | Encode it in the type or return the error |
| "It compiles" reported as done | Compilation is one gate of five | Report each gate separately |
| `unsafe` used to end a borrow argument | The change silently became a UB-risk change | Escalate; the compiler stopped checking |

## Attribution

Concept lineage only. The idea of a mandatory per-language reference gate that
escalates on `unsafe`/FFI contact, and of a hypothesis-first native debugging
loop, is adapted from the `programming` and `debugging` skills of the
`omo-ai` plugin; the DAP-over-printf preference is adapted from `can1357/oh-my-pi`'s
first-class debug adapter tooling. No upstream text is reproduced -- the
wording, the artifact vocabulary, and the `prepared_not_observed` claim
boundary are OMH's own, and OMH keeps its no-execution boundary: every command
below is something the executor runs, never OMH.
