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
- **Local**: Ollama or LM Studio, set under `[local_ai]` with
  `provider = "ollama"` or `"lm_studio"`, plus MLX on macOS.
- **A local OpenAI-compatible endpoint**: any server that speaks the OpenAI
  chat API, registered with its own slug and endpoint.
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
the provider shapes). Full setup, the local-model capability table, and RAM
tier presets are in [Local models & bring your own
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
- **Ollama**: a local model, `bge-m3` recommended. The Memory Tree's on-disk
  vector format is fixed at 1024 dimensions, so a smaller embedding model
  (`all-minilm`, 384 dimensions, or `nomic-embed-text`, 768) fails the
  dimension check at embed time.
- **Custom**: any OpenAI-compatible embeddings endpoint.

Implementation: `crates/openhuman-core/src/inference/embedding_host/` (`mod.rs`
lists the providers; `factory.rs` builds the client; `schemas.rs` defines the
`embeddings.*` RPC surface, including `set_api_key` per provider slug).

## Memory

The memory contract (`tinymemory-api`, vendored at `vendor/tinymemory/`)
defines a driver-neutral `MemoryProvider` trait and ships adapter crates for
six remote engines: Supermemory, Mem0, Cognee, CortexDB, AgentMemory, and
LivingBrain (`vendor/tinymemory/crates/tinymemory-remote/`).

What actually binds today is narrower than that adapter list. OpenHuman's
host-side binding (`crates/openhuman-core/src/memory/binding.rs`, function
`admit`) only accepts the compiled TinyMemory module (id `tinymemory`, with
`tinycortex` kept as a legacy config alias) or the `null` driver; an external
driver configured under `[subsystems.memory.drivers.<id>]` is refused with
"external driver transport is not implemented yet." TinyCortex is the memory
engine every OpenHuman install actually runs. The `[subsystems.memory]`
config block (`driver`, `hooks`, `drivers`, and the `OPENHUMAN_MEMORY_DRIVER`
env var) already parses and persists, ahead of the wiring that will make a
non-default `driver` value actually switch engines; nothing reads it at
runtime yet beyond the module/null choice above.

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
