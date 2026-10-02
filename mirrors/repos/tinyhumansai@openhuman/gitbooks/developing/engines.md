# Pluggable engines

OpenHuman routes four kinds of work, chat and reasoning, embeddings, memory,
and web search, through a config key rather than a hardcoded client. Each has
a managed default that needs no key, plus a bring-your-own-key or local path.
This page is the map of what's supported and the exact key or environment
variable that selects it; the linked pages under Features cover setup and
tradeoffs.

## LLM providers

Chat, reasoning, vision, and coding workloads route through per-workload
provider fields (`chat_provider`, `reasoning_provider`, `agentic_provider`,
`coding_provider`, `vision_provider`, and more), each a string of the form
`<slug>:<model>`. Leaving a field unset, blank, or set to `cloud` keeps it on
the managed default.

Supported routes:

- **Managed (TinyHumans)**: the default. Access to the OpenRouter model
  catalogue with no key to manage.
- **Local**: a runtime the user installs and runs (Ollama, LM Studio, MLX,
  OMLX), addressed as `ollama:<model>`, `lmstudio:<model>`, `mlx:<model>` or
  `omlx:<model>`, with the endpoint in `[local_ai] base_url`. OpenHuman does
  not install the runtime or download models; the user pulls them.
- **A local OpenAI-compatible endpoint**: any server that speaks the OpenAI
  chat API, as `local-openai:<model>` or registered with its own slug and
  endpoint.
- **Claude Code / Claude Agent SDK**: a provider slug that shells out to an
  installed Claude Code CLI instead of calling a hosted API.
- **26 BYOK slugs**, each shipped with a preset endpoint so only a key is
  needed: `openai`, `anthropic`, `google`, `openrouter`, `orcarouter`, `groq`,
  `mistral`, `deepseek`, `together`, `fireworks`, `cerebras`, `xai`,
  `moonshot`, `gmi`, `huggingface`, `nvidia`, `zai`, `minimax`, `stepfun`,
  `kilocode`, `deepinfra`, `novita`, `venice`, `vercel-ai-gateway`, `sumopod`,
  `modelscope`.

Provider definitions live under `crates/openhuman-core/src/inference/provider/`
(`factory.rs` resolves a `<slug>:<model>` string to a client; `types.rs` holds
the provider shapes). Full setup and the local-model capability table are
in [Local models & bring your own
key](../features/model-routing/local-and-byok-models.md); routing behavior
and fallback order are in [Automatic Model
Routing](../features/model-routing/README.md).

## Embeddings

Memory Tree embeddings route through a separate provider selection
(`embeddings.update_settings` over RPC, or `embeddings_provider` for
per-workload override), independent of the chat provider:

- **Managed** (default): the OpenHuman backend's Voyage-backed embedding
  endpoint. Works on a fresh install with no local daemon.
- **Voyage**: direct Voyage AI API with your own key.
- **OpenAI**: cloud embeddings via the OpenAI API.
- **Cohere**: the Cohere embed API with your own key.
- **Ollama**: a local model the user has pulled, `bge-m3` recommended
  (`ollama pull bge-m3`). The Memory Tree's on-disk
  vector format is fixed at 1024 dimensions, so a smaller embedding model
  (`all-minilm`, 384 dimensions, or `nomic-embed-text`, 768) fails the
  dimension check at embed time.
- **Custom**: any OpenAI-compatible embeddings endpoint.

Implementation: `crates/openhuman-core/src/inference/embedding_host/` (`mod.rs`
lists the providers; `factory.rs` builds the client; `schemas.rs` defines the
`embeddings.*` RPC surface, including `set_api_key` per provider slug).

## Memory

The memory contract (`tinymemory-api`, vendored at `vendor/tinymemory/`)
defines a driver-neutral `MemoryProvider` trait. Engines are built by
`tinymemory::factory` (`list_engines`, `build_provider`), and
`tinymemory::migrate::copy_all` copies a store from one to another: the keyed
records, then whatever families both engines serve (document titles and tags,
goals, the learned profile, the conversation history) and the ingested
content, re-sent raw so the new engine rebuilds its own summaries.

What the user can pick (Settings > Memory Engine, or `openhuman.memory_engine_*`
over RPC):

| id | what | endpoint | key |
| --- | --- | --- | --- |
| `tinymemory` | the compiled local TinyCortex module (default, nothing leaves the device) | none | none |
| `tinyhumans` | CortexDB hosted by the TinyHumans backend, billed in credits | the backend origin, forced | the signed-in session (or API key), read live on every call |
| `supermemory`, `mem0`, `cognee`, `cortex`, `agentmemory` | the user's own service | from the form | from the form, kept in the OS keychain |

The switch is applied in process: `memory::ops::engine` validates the request,
stores any key under the keychain entry `memory-<id>`, writes
`[subsystems.memory] driver` plus `drivers.<id>` (`class = "external"`,
`transport = "http"`, `credential_ref = "keychain:memory-<id>"`,
`trust_state = "trusted"` because the user chose it in the UI), and calls
`memory::binding::rebind`, which drops the stale bindings, re-points the
context and publishes `MemoryDriverChanged`. Bindings already held by a running
agent session or the learning facet cache keep the previous engine until that
session or the app restarts (derived contexts that keep the parent's memory
config share its binding handle, so they follow a switch; one with its own
`[subsystems.memory]` keeps that override). Every switch runs under one process-wide
lock, `engine_set` is refused while a migration runs, and the commit reloads the
config fresh and patches only `[subsystems.memory]`. Migration (`engine_migrate`) copies first and
switches only after a clean copy; the source is never modified, and a failed
run leaves the active engine alone. The job reports each step it runs
(`step`, `steps`), and a step one engine cannot serve is skipped and named
rather than failed. Re-sending content is the user's choice
(`replay_content`, on by default, since hosted memory bills for what it reads
again); a piece the new engine refuses is reported in the job's `note` instead
of holding the switch back, because the old engine keeps it and its sync can
bring it again. When the host syncs sources into the new engine itself (hosted
memory), reader-based sources (`mem_src:` ids) are left out of the replay: the
host's own sync sends them from scratch. A running copy can be cancelled (`engine_migrate_cancel`, between pages), is
bounded by `OPENHUMAN_MEMORY_MIGRATE_TIMEOUT_SECS` (default 2 hours) and fails, not
hangs, if its task panics. Records written while a copy runs may be missing from
the new engine; the job result carries a `note` saying so, and this migration does not provide a second-pass delta copy. `OPENHUMAN_MEMORY_DRIVER` pins the engine and makes the switch RPCs
refuse.

`binding::admit` admits `tinymemory` (with `tinycortex` kept as a legacy
alias), `null`, the first-party `tinyhumans` (no `drivers` entry, implicitly
trusted) and any factory engine configured `class = "external"` with
`trust_state = "trusted"`. An untrusted external driver, or an id the factory
does not know, is still refused, and a build without the `memory-remote` gate
refuses every external driver ("external driver transport is not implemented
yet"). A driver that fails to build falls back to `null` with the reason
surfaced in `memory.engine_get` and on the event bus, never silently. It falls
back to `null`, not to the local module, so nothing is written locally while the
user chose a remote engine; the UI says memory is paused. A construction failure
(keychain locked, transport not installed yet) is retried on the next resolve after
30 seconds; an admission refusal stays cached.

On a remote engine the mandatory-surface fallbacks are bounded: recency reads at
most two `export_page` calls of `min(limit*4, 200)` records, and the document list
scans at most 10 namespaces and returns at most 200 documents with a `truncated`
flag. The proper fix is a bounded `recent(namespace, limit)` on the tinymemory
contract, an upstream follow-up. Hosted 402 and 401 errors from ordinary memory
RPCs read `INSUFFICIENT_CREDITS:` and `SESSION_EXPIRED:` too; a 403 (a credential
the engine refuses, such as an API key without the memory scope) reads
`MEMORY_FORBIDDEN:` and never signs the user out, and a timeout, refused
connection, 429 or 5xx that outlasts the retries reads `MEMORY_UNREACHABLE:`.

Not every engine advertises every capability family, and the RPCs of a family
an engine lacks answer a clean "does not support" error (see the
[`memory/driver` README](../../crates/openhuman-core/src/memory/driver/README.md)
for the full table).

- **Hosted engine.** It serves `goals`, `tool_memory`, `documents`, `sources`
  (the sink connector sync writes to), `maintenance` (a health report),
  `retrieval`, `ingest`, `profile`, `episodic`, `scoring` and `tree`.
  Connector sync, goals, tool rules, documents, episodic memory and the learned
  profile work there, the memory doctor reports the hosted service's health,
  and the Brain graph draws the facts, beliefs and concepts the server derived
  from what was written.
- **Direct CortexDB engine.** It serves none of those.
- **Neither.** No remote engine serves `graph`, `chunks`, `entities`,
  `source_sync` or `coding_sessions`.

Brain's sync panels (activity and history) need `sources`, its coding-sessions
card needs `coding_sessions`, and the controls and status that work on a local
chunk store (reset, rebuild, vault, pipeline status) need `chunks`. Each shows
"Not available", or is left out, on an engine without its family. Hosted memory
runs no source pipeline of its own, so the host syncs local folder, GitHub, RSS
and web-page sources itself: it reads them and sends the items through the
engine's sink, from the Sync button, Apply all, and a daily schedule
(`memory/sources/hosted_sync.rs`, `hosted_periodic.rs`). The host records what
the sink accepted, so a run sends only new or changed items and one stopped by
its budget carries on where it stopped. A file removed from a synced folder
stays in memory, and removing the source keeps what it synced, as on the local
engine; deleting the source's memory forgets all of it.

Hosted CortexDB ranks its recall without scoring it: a hit carries its rank and
no signal (no similarity, keyword, graph, episodic or freshness), with or
without the retrieval family. Auto-recall keeps such notes in the engine's
order, its first three, behind the same gate that decides whether a message
needs memory at all, and hybrid search keeps the engine's order. Situational
preferences and the contradiction check need a measured similarity and stay
empty there. Summaries need a model the hosted engine does not reach, so a
segment's recap is the heuristic one. A lookup the engine refuses (out of credits, session not accepted,
credential refused, unreachable) puts a one-line reason in the recall block
instead of an empty result, so the model says memory is unavailable rather than
that something was never stored.

Related pages: [Memory](../features/obsidian-wiki/README.md) and its
sub-pages for what TinyCortex actually does (memory tree, scoring, retrieval,
git-backed diffs).

## Web search

`[search] engine` selects the active provider; only one is active at a time,
mirroring the LLM provider model:

- `managed` (default): backend-proxied, no key needed.
- `parallel`: search, extract, chat, research, enrich, and dataset tools
  against the Parallel API.
- `brave`: Brave Search (web, news, images, videos).
- `querit`: Querit web search.
- `exa`: Exa neural search (search, find-similar, contents). Direct to
  `api.exa.ai`, never through the managed backend.
- `tavily`: Tavily search and extract (web, news, finance). Direct to
  `api.tavily.com`.
- `disabled`: no search tools registered.

A BYOK engine selected without a stored key falls back to `managed` rather
than leaving the agent with no search tool at all.

SearXNG is a separate toggle (`[searxng] enabled`, `base_url`) rather than a
`search.engine` value, since it points at a self-hosted instance instead of a
vendor API. Engine definitions live under
`crates/openhuman-core/src/search/engines/`, one file per provider; the
selector and provider resolution are in `crates/openhuman-core/src/search/mod.rs`
and `crates/openhuman-core/src/config/schema/tools/search.rs`.

See [Web Search](../features/native-tools/web-search.md) for the tool surface
each engine exposes.
