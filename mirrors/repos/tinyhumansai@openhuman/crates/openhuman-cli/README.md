# openhuman-cli

The `openhuman-core` binary, the developer/benchmark bins, and every root
`tests/*.rs` / `examples/*.rs` target.

```
openhuman-core (library)  ──►  openhuman-embed  ──►  openhuman-tinyhumans
                                                              ▲
                                                       openhuman-cli
```

The core library carries no backend client. The binary that must talk to the
hosted TinyHumans backend therefore cannot live inside the core package: it
lives here, and `src/main.rs` installs the `openhuman-tinyhumans` transport
before dispatching into `openhuman_core::run_core_from_args`. The integration
suites that boot the core in-process do the same through
`tests/support/tinyhumans_boot.rs`.

## Targets

| Target | Path | Required features |
| --- | --- | --- |
| `openhuman-core` | `src/main.rs` | none |
| `test-mcp-stub` | `src/bin/test_mcp_stub.rs` | none |
| `openhuman-fleet` | `src/bin/fleet.rs` | `http-server`, `bin-tools` |
| `rss-bench` | `src/bin/rss_bench.rs` | `rss-bench` |
| `library-profile` | `src/bin/library_profile/main.rs` | `rss-bench` (+ `rss-bench-dhat`) |
| `[[test]]` × 44 | `../../tests/<name>.rs` | some carry `required-features` (see the manifest) |
| `[[example]]` × 4 | `../../examples/<name>.rs` | — |

`tests/raw_coverage/*.rs` are globbed by the shared root `build.rs` into the
single `raw_coverage_all` target and need no entry. `pnpm rust:layout` keeps
the tables exhaustive and refuses any target table in the core manifest.

## Features

Every core gate is forwarded 1:1 (`<gate> = ["openhuman-core/<gate>", …]`), so
the product lanes' `--features "$(scripts/ci/product-features.sh)"` resolve
here unchanged. Crate-local gates: `bin-tools` (clap for `openhuman-fleet`),
`rss-bench-dhat` (dhat heap profiling for `library-profile`),
`crash-reporting` (Sentry init in `main.rs` + the `observability_smoke`
target).

## Common commands

```bash
cargo build --manifest-path Cargo.toml -p openhuman-cli --bin openhuman-core
cargo test  --manifest-path Cargo.toml -p openhuman-cli --test json_rpc_e2e --features "$(bash scripts/ci/product-features.sh)"
pnpm test:rust     # scripts/test-rust-with-mock.sh — the canonical runner
```
