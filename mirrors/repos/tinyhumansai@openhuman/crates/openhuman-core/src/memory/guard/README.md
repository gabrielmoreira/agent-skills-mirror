# guard

The taint/scope/budget policy gate over every memory-provider call. The
rustdoc cites `docs/specs/plan-memory.md` §3.4, `docs/specs/kernel.md` §3.4
and `docs/specs/memory-guard-allowlist.md`; those files were removed from the
tree in `0017c58d86`, so the citations are historical and the code comments
are what remains of the argument. `MemoryGuard` implements
`MemoryProvider` over the bound driver, so it is the only handle product code
should hold — a caller writes the same code against the guard as against the
raw driver, and there is no second, unguarded shape to reach for instead.

## Public surface

- `pub struct MemoryGuard` (`provider.rs`) — the decorator. Its `as_*`
  overrides (one per optional family, twenty-three today) hand back guarded
  family handles instead of the inner driver's; see `families.rs` for why
  that has to be an owned field per family rather than a value built on
  demand.
- `pub struct GuardPolicy` (`policy.rs`) — the resolved policy bundle the
  guard and all family decorators share: `enforce_read` / `enforce_write`
  (the `SecurityPolicy` tier check), `ambient_scope` (source-scope query
  predicate), `stamp_taint`, `redact_outbound`, `check_egress`. Binding facts
  (driver id, `DriverClass`, hook budgets, trust state) are cached at bind
  time; the `SecurityPolicy` itself is re-read live on every call so an
  autonomy change takes effect immediately.
- Family decorators (`families.rs` + `families/` — `types.rs`,
  `ingest_and_tree.rs`, `retrieval_and_profile.rs`, `graph_and_bookkeeping.rs`,
  `typed_ingest_and_answer.rs`) — one
  `decorator!`-generated struct per optional capability family (`GuardedTree`,
  `GuardedProfile`, `GuardedGraph`, … — 23 of the contract's 26 families),
  each present exactly when the bound driver advertises that family. (The
  "ten decorators" / "thirteen families" figures still in `families.rs`,
  `policy.rs` and `test_support.rs` predate the contract growing.)
- `mandatory.rs` — the three families every driver has (`MemoryCore`,
  `MemoryRecall`, `MemoryPortability`), where steps 3, 4 and 6 land for the
  always-present surface.
- `budget.rs` — pure char-budget truncation, step 6.
- `audit.rs` — the tracing span and audit event, step 7.
- `in_memory.rs` — `#[doc(hidden)]` in-memory `MemoryProvider` fake for tests
  that need a genuine round trip. Not `#[cfg(test)]`: integration tests link
  it too.
- `test_support*.rs` — a recording fake that proves a call was made without
  storing data.

## The seven enforcement steps

| # | Step | Where |
| - | ---- | ----- |
| 1 | `SecurityPolicy` tier | `GuardPolicy::enforce_read` / `enforce_write` |
| 1b | path rules | no-op — no contract method carries a path |
| 2 | source scope as a query predicate | `GuardPolicy::ambient_scope`, applied in `GuardedTree::query_source` (not recall — the bound driver refuses a scoped recall) |
| 3 | taint stamping | `GuardPolicy::stamp_taint` (raises, never overrides) |
| 4 | redaction | `GuardPolicy::redact_outbound` — a no-op for embedded drivers |
| 5 | egress + trust | `GuardPolicy::check_egress` |
| 6 | char budgets | `budget.rs`, driven by `MemoryHooksConfig` |
| 7 | audit + tracing | `audit.rs` |

See `mod.rs` for the full argument behind each departure from a naive reading
of the milestone brief, and its "Honesty clause" section for what the guard
still does not cover: the engine's own `ProfileStore` reads and writes, which
sit beneath the module contract (the guarded `MemoryProfile` family exists;
the allowlist test tracks what has not moved onto it).

## Calls into

- `crate::memory::api::provider::MemoryProvider` (the `tinymemory-api`
  contract) — what the guard decorates.
- `crate::security::SecurityPolicy` — the tier check in step 1.
- `crate::memory::source_scope` — the ambient per-turn source allowlist read
  in step 2.
- `crate::config::schema::MemoryHooksConfig` — the budgets read in step 6.

## Called by

- `crate::memory::ops::guard::active_memory_guard` — how a memory RPC
  handler reaches the guarded driver (the unguarded
  `helpers::active_memory_client` it used to sit beside is gone, #5560).
- `CoreContext::memory` (`crate::core::runtime::context`) — resolves
  `memory_binding()` and returns its `.guard()`; this is additive next to
  `CoreContext::memory_binding()`, which still hands out the bare driver for
  callers (like the health probe) that must not run through the tier check.
- `crate::memory::binding` — constructs the `MemoryGuard` at bind time
  (`MemoryGuard::new`).

## Tests

- `budget_tests.rs`, `families_tests.rs`, `policy_tests.rs`,
  `provider_tests.rs` — unit coverage per file above.
- `../bypass_allowlist_tests.rs` — the ratchet lint: a needle list
  (`binding::for_workspace(`, `.memory_binding(`, `.unguarded_provider(`,
  `.profile_store(`, …) scanned over production files, with an `ALLOWED`
  list carrying a reason per entry (the CLI and `CoreContext` bind sites, the
  `ops::provider` health probe, the guard's own forwarding). It fails if the
  set grows or an entry goes stale.
