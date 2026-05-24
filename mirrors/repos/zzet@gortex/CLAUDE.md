# Gortex

Code intelligence engine written in Go. Indexes repositories into an in-memory knowledge graph and exposes it via CLI and MCP Server.

## Build & Test

```bash
go build -o gortex ./cmd/gortex/   # requires CGO (tree-sitter C bindings)
go test -race ./...                 # all test packages must pass
```

## Codebase Overview

- **Languages:** go (primary)
- **Entry point:** `cmd/gortex/main.go`
- **Source:** 1,338 Go files (728 non-test) across the `cmd/` and `internal/` trees
- **Graph size:** ~31k nodes, ~206k edges when the daemon indexes this repo

## MANDATORY: Use Gortex MCP tools instead of Read/Grep/Glob

Gortex is registered as an MCP server. You **MUST** prefer graph queries over file reads on every task in this repo — `search_symbols`, `find_usages`, `get_symbol_source`, `get_editing_context`, `smart_context`, `edit_symbol` / `edit_file` / `rename_symbol` / `batch_edit`. PreToolUse hooks deny `Read` / `Grep` / `Glob` against indexed source; the deny message names the right tool. The MCP server registers 120+ tools — all of them eagerly published in `tools/list` by default; set `GORTEX_LAZY_TOOLS=1` to opt into the lazy / `tools_search` discovery flow when the client honours `notifications/tools/list_changed`. The cross-project rule tables live in `~/.claude/CLAUDE.md` — neither is restated here. This file carries only project-specific guidance.

### Discovery (read once, then keep using)

- **Graph schema** — `gortex://schema` resource (node kinds, edge kinds, what each carries).
- **Analyzer rollups** — `gortex://report`, `gortex://surprises`, `gortex://god-nodes`, `gortex://questions`, `gortex://audit`.
- **Bootstrap state** — `gortex://stats`, `gortex://index-health`, `gortex://workspace`, `gortex://repos`, `gortex://active-project`.

### LLM provider (powers `ask` and `search_symbols assist:` modes)

Selected via `llm.provider` in `.gortex.yaml` or `~/.config/gortex/config.yaml`. The HTTP and subprocess providers are pure Go — available without `-tags llama`.

| Provider | Backend | Requires |
|---|---|---|
| `local` (default) | in-process llama.cpp | `-tags llama` build + `llm.local.model` (a `.gguf` path) |
| `anthropic` | Messages API | `llm.anthropic.model` + `ANTHROPIC_API_KEY` |
| `openai` | Chat Completions | `llm.openai.model` + `OPENAI_API_KEY` |
| `ollama` | Ollama daemon | `llm.ollama.model` (+ `llm.ollama.host`, default `localhost:11434`) |
| `claudecli` | `claude` CLI subprocess | `claude` on `$PATH` (signed in once); optional `llm.claudecli.model` (`sonnet`/`opus`/…). Reuses the user's Claude Code subscription. |
| `codex` | OpenAI `codex` CLI subprocess | `codex` on `$PATH` (signed in once); optional `llm.codex.model`. Runs `codex exec` in a read-only sandbox; reuses the user's Codex / ChatGPT sign-in. |
| `gemini` | Google Gemini `generateContent` REST | `llm.gemini.model` (default `gemini-2.5-pro`) + `GEMINI_API_KEY`. Structured output via `responseSchema` (`additionalProperties` stripped — Gemini rejects it). |
| `bedrock` | AWS Bedrock Converse API (SigV4) | `llm.bedrock.model_id` (e.g. `anthropic.claude-sonnet-4-20250514-v1:0`) + `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` (+ optional `AWS_SESSION_TOKEN` for STS). Region defaults to `us-east-1` (`llm.bedrock.region`). Structured output via forced `respond` tool. No AWS SDK dependency — SigV4 is implemented in ~100 LOC of stdlib. |
| `deepseek` | DeepSeek Chat Completions (OpenAI-compatible) | `llm.deepseek.model` (default `deepseek-chat`) + `DEEPSEEK_API_KEY`. Structured output uses `response_format: json_object` plus a schema hint in the system prompt — DeepSeek does not support strict `json_schema`. |

`GORTEX_LLM_PROVIDER` / `GORTEX_LLM_MODEL` / `GORTEX_LLM_CLAUDECLI_BINARY` / `GORTEX_LLM_CODEX_BINARY` / `GORTEX_LLM_BEDROCK_REGION` override the file config. `GORTEX_LLM_MODEL` targets the active provider's model field (Gemini → `llm.gemini.model`, Bedrock → `llm.bedrock.model_id`, DeepSeek → `llm.deepseek.model`, etc.). If the active provider can't construct (missing model / API key, `local` without `-tags llama`, `claudecli` / `codex` without `claude` / `codex` on `$PATH`, `bedrock` without AWS credentials), the daemon logs a warning and `ask` stays unregistered — fall through to direct tools.

`llm.routing` (off by default) routes the `ask` agent to a cheaper or more capable model by graph-derived task complexity — set `routing.enabled`, `routing.simple_model`, `routing.complex_model`; the chosen `model` / `complexity` ride on the `ask` response.

`search_symbols assist:` modes: `auto` (default — skips LLM for identifier queries, expands NL queries), `on` (forces expansion+rerank), `off` (pure BM25), `deep` (adds a body-grounded verification pass; +1.5–4 s; quality is highly model-dependent — unreliable on 3B local models, fine on 7B+ or hosted).

### Non-obvious capabilities worth knowing

- **`compress_bodies: true`** on `read_file` / `get_symbol_source` / `get_editing_context` elides function bodies to stubs while keeping signatures + doc-comments + structure. ~30–40% of original tokens. 14 languages.
- **Overlay sessions** (`overlay_push`, `overlay_list`, `overlay_drop`, `compare_with_overlay`) let editor extensions push unsaved buffers as a per-session shadow graph — every subsequent tool call reads through it without mutating base. Bound to the MCP session lifecycle; idle TTL via `GORTEX_OVERLAY_IDLE_TTL` (default 30m).
- **Speculative execution** (`preview_edit`, `simulate_chain`) takes an LSP `WorkspaceEdit` and returns the graph diff + broken callers/implementors + impact rollup + suggested tests + (optional) LSP diagnostics — disk untouched. `simulate_chain` with `keep: true` promotes the final state into a real overlay.
- **MCP 2026 Streamable HTTP** at `POST /mcp` — `gortex server` always mounts it; `gortex daemon --http-addr <addr>` opts the daemon in (non-localhost binds require `--http-auth-token`).
- **Session memory** (`save_note`, `query_notes`, `distill_session`) persists agent-authored notes per repo, auto-linked to symbols mentioned in the body. Notes survive daemon restarts and context compactions, scoped to the session's workspace.
- **Development memories** (`store_memory`, `query_memories`, `surface_memories`) — cross-session, symbol-linked durable knowledge that compounds the longer a team uses Gortex. Memories carry `kind` (invariant / constraint / convention / gotcha / decision / incident / reference), `importance` (1..5), `confidence` (0..1), and are surfaced *proactively* by `surface_memories` when their anchor symbols / files enter the agent's working set.
- **Artifacts** — non-code knowledge files (DB schemas, API specs, ADRs, infra configs) declared in `.gortex.yaml` `artifacts:` are indexed as `artifact` nodes; `search_artifacts` / `get_artifact` surface them and `EdgeReferences` links code to the spec it implements.
- **Code search beyond symbols** — `search_text` is a trigram-indexed literal / regex search (the grep replacement for non-symbol strings); `search_ast` runs structural tree-sitter queries; `analyze kind=sast` is a 190-rule, CWE/OWASP-tagged security scan across 8 languages.
- **Push notifications** — beyond `notifications/diagnostics`, the server pushes `graph_invalidated` (graph hot-reload), `daemon_health`, `stale_refs`, and `workspace_readiness`. `subscribe_*` once per session instead of polling.
- **`get_architecture`** — one-call architectural snapshot (languages, communities, hotspots, processes); pass `resolution` for a hierarchical symbol → file → package → service → system rollup.
- **`analyze` is a 57-kind dispatcher** — beyond the structural kinds, it now covers `impact` (composite change-risk score), `health_score` (per-symbol A–F grade), `sast` / `named` / `unsafe_patterns` (security), `clusters`, `connectivity_health`, `tests_as_edges`, and more.

## MANDATORY: Session memory — save, recall, distill

The `save_note` / `query_notes` / `distill_session` triplet is the agent's durable scratchpad. The graph remembers code; these tools remember **why you made a call**. Without them, every compaction erases hard-won context.

Three triggers — not suggestions:

1. **After a context compaction (or at session start in a touched repo)** — **call** `distill_session` first thing. Returns top symbols, pinned notes, decisions, and recent excerpts from prior sessions in this workspace. Use the digest to seed your mental model before reading any file.
2. **At every decision point** — **call** `save_note tags:"decision" body:"<what+why>"` when you pick an approach, reject an alternative, discover a non-obvious constraint, or commit to an invariant. Mention the affected symbol/file by ID (`pkg/foo.go::Bar`) so the auto-linker attaches the note to the graph. Pin (`pinned:true`) anything that should survive the store cap.
3. **Before editing a symbol you've touched before** — **call** `query_notes symbol_id:"<id>"`. Prior decisions, bug-fix notes, or "do not change this without …" warnings ride on the symbol's note list and you should see them before re-deriving (or worse, reverting) past work.

What to save vs. skip:
- **Save:** decisions ("chose X over Y because Z"), non-obvious constraints, follow-ups ("revisit when …"), bug reproductions, surprising graph findings, partial-progress hand-offs.
- **Skip:** play-by-play of what you just did (the diff says it), code patterns derivable from the graph, anything already in CLAUDE.md.

Useful tags: `decision`, `bug`, `follow-up`, `gotcha`, `invariant`. `decision`-tagged notes are surfaced in their own section by `distill_session`.

## MANDATORY: Development memories — store, query, surface

`save_note` is a **per-session scratchpad**; `store_memory` is the **workspace-wide durable knowledge base**. The two are complementary, not redundant:

| | `save_note` (session) | `store_memory` (cross-session) |
|---|---|---|
| Scope | session_id | workspace-wide |
| Lifetime | survives compaction | survives daemon restarts, agent changes, team rotation |
| Audience | future-you in this session | every future agent in this workspace |
| Surfacing | `distill_session` (manual) | `surface_memories` (proactive, ranked) |
| Right when | "remember this for the next 30 min" | "every agent touching `Bar` should know this" |

Three triggers — not suggestions:

1. **At task start, after `smart_context`** — **call** `surface_memories task:"<task>" symbol_ids:"<top hits from smart_context>"`. Returns memories ranked by anchor symbol overlap, file overlap, task-keyword hits, importance, pinning, recency, and confidence. Memories prefixed with `match_reasons:["symbol:pkg/foo.go::Bar"]` are direct evidence the memory applies to your working set. If `surface_memories` returns nothing, don't probe further.
2. **When you discover a durable fact worth teaching the team** — **call** `store_memory kind:"<invariant|gotcha|convention|decision|constraint|incident>" body:"<what+why>" symbol_ids:"pkg/foo.go::Bar" importance:5`. Pin (`pinned:true`) anything load-bearing. Set `kind` honestly: `invariant` means "violating this breaks the system", `gotcha` means "an agent will get this wrong without warning". Title (`title:"..."`) the memory if the body is long — it becomes the headline.
3. **When a memory is no longer true** — **call** `store_memory id:"<new>" supersedes:"<old-id>" body:"<corrected fact>"`. The old memory stays in the store (for audit) but is hidden from `surface_memories` by default. Don't delete unless the original was wrong; supersession preserves history.

What to store vs. skip:
- **Store:** invariants ("Bar must hold the lock"), conventions ("this package never uses gob"), incident learnings ("once, doing X under Y crashed prod"), API contracts not enforced by types, debugging traps, cross-cutting decisions with non-obvious rationale.
- **Skip:** anything derivable from the code (the graph already knows), session-local play-by-play (use `save_note`), CLAUDE.md content (it's already loaded), one-off observations with no actionable consequence.

Useful kinds and tags: `invariant`, `constraint`, `convention`, `gotcha`, `decision`, `incident`, `reference`. Tag liberally — `query_memories tag:"<x>"` is the primary lookup path when you don't know the anchor symbol.

## Required workflow (every task on this repo)

These are not suggestions — run each step at the trigger.

1. **Always call** `graph_stats` first to confirm the daemon is up and orient (check `per_repo` in multi-repo mode).
2. If `total_nodes` is 0, **call** `index_repository` with `"."` before anything else.
3. In multi-repo mode, **call** `get_active_project` to see scope; use `set_active_project` to switch.
4. For every new task, **call** `smart_context` with the task description before reading any file.
5. Immediately after `smart_context`, **call** `surface_memories task:"<task>" symbol_ids:"<top hits>"` to pick up any cross-session invariants / gotchas / decisions anchored to your working set. Skipping this re-derives knowledge other agents have already recorded.
6. Before editing a file, **call** `get_editing_context` on it first.
7. Before changing any function signature, **call** `verify_change` to catch broken callers and interface implementors (cross-repo).
8. For any refactor, **call** `get_edit_plan` for the dependency-ordered file list, then **`batch_edit`** to apply atomically.
9. After every edit, **call** `check_guards` (team conventions) then `get_test_targets` (includes cross-repo tests).
10. Before committing, **call** `detect_changes` for scope and `diff_context` for graph-enriched review.
11. When the task is done, **call** `feedback action: "record"` to score which `smart_context` suggestions were useful / not needed / missing. This is required — it improves future context quality. If the task surfaced a durable invariant / decision / gotcha worth teaching the team, **also call** `store_memory` so the next agent inherits the lesson.
