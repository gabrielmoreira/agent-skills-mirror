# Fuzz harnesses

libFuzzer targets for the parsers an untrusted request reaches. CI builds and
runs all of them on every push and pull request — see the `fuzz` job in
[`.github/workflows/ci.yml`](../../.github/workflows/ci.yml), which is just a
wrapper around [`.github/scripts/fuzz-smoke.sh`](../../.github/scripts/fuzz-smoke.sh).

## Running them

```sh
rustup toolchain install nightly
cargo install cargo-fuzz --locked

# exactly what CI does: build every target, replay every seed, explore for 20s each
bash .github/scripts/fuzz-smoke.sh

# a real campaign
FUZZ_SECONDS=3600 bash .github/scripts/fuzz-smoke.sh

# one target, interactively
cd engine && cargo +nightly fuzz run query_string
```

Crashing inputs land in `fuzz/artifacts/<target>/`; re-run one with
`cargo +nightly fuzz run <target> fuzz/artifacts/<target>/<file>`.

## seeds/ vs corpus/

`fuzz/seeds/<target>/` is tracked; every file is named after what it covers and
is a regression case. `fuzz/corpus/<target>/` is the working corpus and is
**gitignored** — `cargo fuzz run` writes every input it finds interesting there,
and a few hundred opaque blobs per run is how a seed corpus stops being
reviewable. `fuzz-smoke.sh` copies the seeds in before each run.

To promote a discovered input (a crash, or a case that reached something new),
copy it into `seeds/<target>/` under a descriptive name.
`seeds/date_math/regression-207-overflow-hours` is the first one: it is the
input libFuzzer minimised the `TimeDelta::hours out of bounds` panic down to.

## The targets

| target | entry point | why it is untrusted |
|---|---|---|
| `query_dsl` | `xerj_query::parse_request`, `rewrite` | the whole `_search` body: nesting depth, clause count, sort and `_source` specs |
| `query_string` | `xerj_query::parse_query` on `query_string` / `simple_query_string` | the hand-written Lucene grammar, also reachable via `?q=` — ES's CVE-2023-31419 was a stack overflow here |
| `date_math` | `xerj_query::dates` | `"gte": "now-1d/d"` and `"format": "…"` are caller-supplied; both compile through hand-written tokenisers |
| `sql` | `xerj_engine::sql::parse_sql` | `/_sql` takes a statement from the wire; ES's CVE-2024-43709 was an OOM from a crafted SQL query |
| `painless` | `xerj_engine::painless::{check_script_limits, eval_painless}` | attacker-supplied *code* inside a query body, plus the depth/op/deadline budgets that are supposed to bound it |
| `index_name_date_math` | `xerj_api::es_compat::resolve_date_math_index`, then `xerj_engine::index::resolve_date_math` | `<logs-{now/d}>` arrives in a request URI — a second date-math implementation with its own brace scanner |
| `agg_script` | `xerj_engine::aggs::run_aggs` with a fuzzed script in `scripted_metric`, `bucket_script`, `bucket_selector` | two *more* Painless-subset tokenisers, distinct from `xerj_engine::painless` and reached only through an aggregation body |

The `es_compat` entry point above is named first for a reason. The first version
of `index_name_date_math` fuzzed `xerj_engine::index::resolve_date_math` alone —
which has no production callers — so it passed while the resolver that runs on
the wire still aborted on `<logs-{2026-01-01||+9999999999999d}>`. **Fuzz the
function the request reaches**, and check that it is that function: `grep` for
callers before you write the harness.

This list is the coverage. It is not every parser in the engine, and the
security docs must name these rather than claim the parser surface generally —
that overstatement is what [#207](https://github.com/xerj-org/xerj/issues/207)
was filed about.

## Adding a target

1. Write `fuzz_targets/<name>.rs` and add the matching `[[bin]]` to `Cargo.toml`.
2. Seed `seeds/<name>/` with real, *valid* inputs. A target with no seeds
   starts from the empty input and reaches almost nothing in a bounded run.
3. Nothing else — `fuzz-smoke.sh` discovers targets with `cargo fuzz list`, so
   CI picks it up automatically, and
   `xerj-engine/tests/security_tooling_claims.rs` fails if the harness or its
   seeds are missing.

## Conventions

- Harnesses cap their input length. The engine's own caps are larger; the
  smaller bound here keeps the fuzzer's budget on grammar states instead of on
  the length check that rejects everything past it.
- Prefer the uncached entry point when a memoising wrapper exists. Driving
  unique keys through a bounded cache measures its eviction policy, not the
  parser.
- Harnesses must stay deterministic and free of I/O: no files, no sockets, no
  clocks that change the control flow.
