# Jev

Jev is a decision model, not a text generator. Give it a request and a
handful of labelled options, and it returns a calibrated probability for
each one in about 150 milliseconds. OpenHuman uses it as a fast, cheap judge
wherever a turn needs to pick from a short list rather than write prose: tool
selection during a search, and step-by-step browser control.

The models are `jev-1.13` and `jev-latest`, built by TypeSafe AI and reached
through the TinyHumans System One proxy or, for a BYOK OpenRouter route,
directly. Pricing is $0.042 per million input tokens, output free, and a
typical tool search costs one to two thousand tokens. There is no session,
no chain of thought, and nothing to stream: one request, one set of
probabilities.

## Three question types

Jev answers three kinds of question, defined in `tinyjevclient`:

- **Choice**: probabilities over a set of named options, so the caller can
  pick the best one, the top three, or discard everything below a
  confidence floor.
- **Score**: a single calibrated number for one thing, rather than a choice
  among several.
- **Noul**: a yes/no probability, used where OpenHuman needs "does this even
  apply" rather than "which of these applies."

Tool search uses a Choice and a Noul in the same request: the Choice picks
a tool from the shortlist (plus a `none` option), and the Noul answers
whether the request needs a tool at all. Browser control uses Jev
repeatedly, once per step, to decide the next action.

## Why retrieval comes first

Jev accepts at most 255 options in one Choice, and its accuracy drops as
the option list fills with entries that have nothing to do with the
request. So nothing in OpenHuman ever hands Jev a whole tool catalogue.
`tinytools-jev` (`vendor/tinyagents/vendor/tinytools/crates/tinytools-jev/`)
narrows first and decides second:

1. A retriever (BM25 by default, or an embedding-based ranker when one is
   configured) shortlists `retrieval_k` candidates, 20 by default. This step
   is skipped when the catalogue already fits in one Choice.
2. One request to Jev: a Choice over the shortlist plus `none`, and a Noul
   asking whether the request needs a tool at all.
3. Hits come back ranked by probability, `none` removed, anything below
   `min_probability` (0.05 by default) dropped.

`JevRankerConfig::with_strategy` picks how the catalogue gets narrowed:

- `RetrieveThenDecide` (the default): retrieve top 20, decide once. Bounded
  by the retriever's recall, since a paraphrase the retriever misses never
  reaches Jev.
- `FamilyThenDecide`: one evaluation picks the candidates' family first (a
  toolkit or pack; anything without one falls into `core`), then a second
  evaluation runs per chosen family (`max_families`, default 2, run
  concurrently) over every member of that family. A family that fits in one
  Choice skips retrieval entirely, so a paraphrase is judged on meaning at
  both stages instead of being filtered out lexically before Jev sees it.

## How OpenHuman uses it

### Tool search

The tinyagents harness owns the `tool_search` / `tool_call` bridge over
every tool registered as deferred. `openhuman-tinyhumans` installs
`TinyHumansJevRanker` (`crates/openhuman-tinyhumans/src/jev/ranker.rs`) as
the process-wide ranker for that bridge
(`crates/openhuman-core/src/agent/tinyagents/discovery/`). The product
default uses `RetrieveThenDecide` with the process's embedding provider as
the retriever, so retrieval finds candidates by meaning rather than by
shared words before Jev decides among them.

The ranker resolves its Jev route and credential fresh on every search
rather than caching them at install time, because a desktop can sign in and
out while the process keeps running. The route is `agent.tool_search.jev_route`
(see [Configuration](#configuration)): the TinyHumans proxy, TypeSafe's own
API, or OpenRouter's System One API. The built Jev client is cached by
route, credential and backend URL, so a stable session does not rebuild an HTTP
client on every search. When the process has no usable embedding provider,
`TinyHumansJevRanker` refuses outright and the harness answers with its own
BM25 ranking instead of running a Jev decision over a lexical shortlist that
would only add a network round trip for no gain.

### Browser control

`crates/openhuman-core/src/modules/browser_task.rs` hands browser tasks to
TinyComputer's task members (`StartTask`, then `AwaitTask` until the task
pauses or finishes), confined to the browser surface and the allowed websites.
The decision model is chosen in `[computer] decision_model` — Jev (through
the hosted proxy when signed in, or the user's OpenRouter key), OpenJev, or
Sage — and a failed step goes to the rescue model (`[computer] rescue_model`,
up to `max_rescues` times) before the task fails. An irreversible step pauses
as `needs_approval`; the browser tool holds it behind a one-use token and only
`confirm_pending`, through the host approval gate, answers `ContinueTask`.

## Measured results

From `docs/plans/jev-tool-search-baseline.md`, measured 2026-09-22 against
215 core tools plus 1,000 recorded Composio actions, with 160 hand-written
requests (66 mapped to a Composio action, 63 to a core tool, 31 that no tool
should answer):

| Ranker | Top-1 | Top-3 | Needless calls (of 31) | p50 latency |
| --- | --- | --- | --- | --- |
| BM25 | 22.5% | 38.0% | 26 | 28 ms |
| Jev, BM25 top-20 then decide | 57.4% | 62.0% | 1 | 1.5 s |
| Jev, embedding top-20 then decide (product default) | 62.0% | 66.7% | 1 | 1.5 s |
| Jev, family then decide | 62.0-64.3% | 67.4-69.0% | 1 | 1.3 s |

On the Composio-only slice, `FamilyThenDecide` with an embedding cut for
oversized families reaches 80.3% top-1 and 87.9% top-3, against BM25's 18.2%
and 36.4%. The gap comes mostly from retrieval, not the decision itself:
under `RetrieveThenDecide` with BM25 shortlisting, Jev's Composio top-3
(72.7%) lands exactly on BM25's recall@20, meaning Jev is choosing correctly
from everything it was shown but a paraphrase like "ping alex" for
`SLACK_SEND_MESSAGE` never reaches it. Letting Jev pick the family first
removes the shortlist for every toolkit that fits in one Choice and lifts
Composio top-3 into the high 80s.

Needless tool calls collapse under any Jev configuration: BM25 answers 26 of
31 tool-less requests with a (wrong) tool anyway, while Jev's `none` option
and `needs_tool` Noul let it abstain on all but one.

## Configuration

`ToolSearchConfig` (`crates/openhuman-core/src/config/schema/agent.rs`) is
the `[agent.tool_search]` block:

```toml
[agent.tool_search]
ranker = "jev"   # "jev" (default) | "auto" | "bm25" | "compare"
jev_route = "auto"   # "auto" (default) | "tinyhumans" | "typesafe" | "openrouter"
# jev_base_url = "http://127.0.0.1:18080"   # typesafe/openrouter origin override
top_k = 3
```

- `ranker = "jev"`: use the installed decision-model ranker, falling back to
  BM25 only when it fails or the process has no TinyHumans credential.
- `"auto"`: same fallback behaviour as `"jev"`.
- `"bm25"`: the built-in lexical ranker only, no network call.
- `"compare"`: serve Jev, but also record the BM25 ranking in the
  `tool.searched` telemetry, so the two can be compared on live traffic
  without changing what the model sees.
- `jev_route`: where the Jev decision calls go. `"auto"` uses the TinyHumans
  credential when the process has one, else `TYPESAFE_API_KEY` (direct to
  TypeSafe), else an OpenRouter key (`OPENROUTER_API_KEY`, or the stored
  `openrouter` BYOK key). `"tinyhumans"`, `"typesafe"` and `"openrouter"` pin
  one route and never fall through to another credential. Override per launch
  with `OPENHUMAN_JEV_ROUTE`.
- `jev_base_url`: replaces the API origin of the `typesafe` / `openrouter`
  routes (a metering proxy, a mirror). Remote origins must be HTTPS; HTTP is
  accepted for literal loopback IPs only. Override per launch with
  `OPENHUMAN_JEV_BASE_URL`.
- `top_k`: how many matches a search returns when the model does not ask for
  a specific number. Three by default, enough to choose from without
  returning so many schemas that the point of deferring them is lost.

Without an embedding provider, or without a credential for the selected Jev
route, tool search falls back to BM25 automatically, so `auto` and `jev` cost
nothing extra with no credential. A BYOK setup with no TinyHumans account
needs an embedding provider that does not depend on one (for example
`memory.embedding_provider = "custom:<OpenAI-compatible endpoint>"`) as well as
a TypeSafe or OpenRouter key.

## Running the benchmark

```bash
cargo run -p openhuman-cli --bin tool-search-bench -- --ranker all --misses
cargo run -p openhuman-cli --bin tool-search-bench -- --ranker jev --family --embedding
cargo run -p openhuman-cli --bin tool-search-bench -- --dump-catalogue
```

`OPENHUMAN_BACKEND_API_KEY` (or `TYPESAFE_API_KEY`) selects the credential;
without one the bench ranks through the signed-in TinyHumans session, same
as the product.

## Where the code lives

- `vendor/tinyagents/vendor/tinytools/crates/tinytools-jev/`: the
  transport-neutral `ToolRanker` implementation, its retrieval strategies,
  and the `JevRankerConfig` / `JevRanking` types.
- `crates/openhuman-tinyhumans/src/jev/`: the TinyHumans-specific evaluator
  (`TinyJevEvaluator`, over `tinyjevclient`) and the process-installed
  ranker (`TinyHumansJevRanker`).
- `crates/openhuman-core/src/agent/tinyagents/discovery/`: the host slot
  that holds the installed ranker and turns `[agent.tool_search]` into the
  policy a turn runs with.
- `crates/openhuman-core/src/modules/browser_task.rs`: the browser-task
  entry point that runs `JevController`.
- `docs/plans/jev-tool-search-baseline.md`: the full benchmark writeup this
  page's numbers come from.

See also: [Performance](performance.md) for the wider cost and density
picture, [Pluggable engines](engines.md) for the other swappable pieces
around inference and memory, and [Embedding OpenHuman](embedding.md) for
running an agent as a library, including one that uses tool search.
