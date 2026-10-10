# examples

Runnable programs that use `openhuman-embed` the way a host product would.
Cargo discovers them, so they run with `cargo run -p openhuman-embed
--example <name>`. Both build their tokio runtime by hand with
`AGENT_WORKER_STACK_BYTES` and `MAX_BLOCKING_THREADS` instead of
`#[tokio::main]`, because a turn overflows tokio's default worker stack. Set
`RUST_LOG=debug` to see the `[embed]` log lines around each turn.

## run_turn

One turn on a `Harness`, read-only, with live progress printed to stderr.
By default it builds an ephemeral workspace, points the agent's `action_dir`
at the current directory, and sends inference to the endpoint you name:

```bash
OPENHUMAN_EXAMPLE_BASE_URL=https://api.openai.com/v1 \
OPENHUMAN_EXAMPLE_API_KEY=sk-... \
OPENHUMAN_EXAMPLE_MODEL=gpt-5 \
  cargo run -p openhuman-embed --example run_turn -- "What can you see in this directory?"
```

`OPENHUMAN_EXAMPLE_MODEL` defaults to `gpt-4o-mini`. With
`OPENHUMAN_EXAMPLE_INHERIT=1` it uses `Workspace::Inherit` and
`Provider::inherit()` instead: the machine's real OpenHuman workspace and
whatever inference it is configured with.

```bash
OPENHUMAN_EXAMPLE_INHERIT=1 cargo run -p openhuman-embed --example run_turn -- "Hello."
```

## two_agents

A read-only reviewer and a full-access fixer on one `Runtime`, each with its
own access tier, working directory and model. Run it BYOK with the same three
variables as `run_turn`, or on managed inference with a TinyHumans API key:

```bash
OPENHUMAN_EXAMPLE_TINYHUMANS_API_KEY=th_... \
  cargo run -p openhuman-embed --example two_agents -- "Describe this directory."
```

The example uses the plain `openhuman_embed::Runtime::builder()`, which
installs no backend transport. Without one the core has no default backend
URL, so on the managed path also set `OPENHUMAN_EXAMPLE_BACKEND_URL` to the
backend's inference base, or managed calls answer `BACKEND_UNAVAILABLE:`. A
real host would build with `openhuman_tinyhumans::RuntimeBuilder` instead.

## Optional settings

| Variable | Effect |
| --- | --- |
| `OPENHUMAN_EXAMPLE_BACKEND_URL` | Points the core's non-inference backend calls at your own backend. |
| `OPENHUMAN_EXAMPLE_SKILLS_DIR` | Skill bundles to copy in (the reviewer only, in `two_agents`). Ignored without the `skills` feature. |

These programs make real network calls to the endpoint you configure. The
tests in [`../tests/`](../tests/README.md) cover the same paths against mocks.
The repository-root [`examples/embed_headless.rs`](../../../examples/embed_headless.rs) and [`examples/embed_kernel.rs`](../../../examples/embed_kernel.rs)
use `CoreBuilder` directly, without this crate; run them with
`cargo run -p openhuman-cli --example embed_headless`.

## Further reading

- [`gitbooks/developing/embedding.md`](../../../gitbooks/developing/embedding.md): embedding the core in another product.
- [`crates/openhuman-embed/README.md`](../README.md): the openhuman-embed crate README.
