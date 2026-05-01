# CLAUDE.md

This repository ships `dev-browser`: a Rust CLI plus a Node.js daemon for browser automation with a QuickJS sandbox. Use this file as the repo-specific guide when making code changes.

## Tooling

- Use Node.js tooling for `daemon/` and Cargo for `cli/`. Do not use Bun.
- The daemon package uses `pnpm`.
- The repo root contains packaging glue (`bin/`, `scripts/`, `README.md`), but most runtime behavior lives in `cli/` and `daemon/`.

## Validation

Run these before finishing changes that touch runtime code:

```bash
cd daemon && npx tsc --noEmit
cd daemon && pnpm vitest run
cd cli && cargo build
```

If you change daemon runtime code that is embedded into the Rust binary, rebuild the bundles first:

```bash
cd daemon && pnpm bundle
cd daemon && pnpm bundle:sandbox-client
```

`cli/src/daemon.rs` embeds `daemon/dist/daemon.bundle.mjs` and `daemon/dist/sandbox-client.js` via `include_str!`, so `cargo build` only sees the latest daemon changes after those bundles are regenerated.
