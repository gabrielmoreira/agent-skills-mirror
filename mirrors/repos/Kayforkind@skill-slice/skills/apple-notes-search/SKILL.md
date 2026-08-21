---
name: apple-notes-search
description: "Runs on-device semantic plus keyword search and Swanson-ABC connection-discovery over the user's Apple Notes via the apple-notes MCP. Use when finding, recalling, synthesizing, or bridging notes on macOS. Not for Obsidian, SiYuan, Notion, or Apple Reminders."
version: 1.0.1
risk: critical
source: community
source_repo: connerkward/mcp-apple-notes
source_type: community
date_added: "2026-06-16"
tags: [apple-notes, search, mcp, macos, semantic-search, knowledge]
tools: [claude-code]
license: "MIT"
license_source: "https://github.com/connerkward/mcp-apple-notes/blob/main/LICENSE"
plugin:
  targets:
    codex: blocked
    claude: blocked
  setup:
    type: manual
    summary: "Requires third-party MCP setup and macOS Full Disk Access; keep out of plugin-safe bundles."
    docs: SKILL.md
---

# Apple Notes search & connection-discovery

`apple-notes` is an MCP server for semantic search and connection-discovery across the
user's own Apple Notes — hybrid search, Swanson-ABC bridges, entity threads, and cited
synthesis over everything they've written. Embeddings, search, BM25, clustering, and
bridges run **on-device**; only **synthesis generation** calls an LLM (local OR cloud,
the user's choice).

## When to Use

- Use when the user wants to **find, recall, or look up** something from their own Apple
  Notes ("search my notes for X", "what did I write about X", "did I ever note Y").
- Use when the user wants to surface **non-obvious connections** across their notes
  ("find bridges/connections across my notes", "what links X and Y", "show related notes").
- Use when the user wants to **synthesize a position** from their notes ("summarize what I
  think about X from my notes", "pull together everything I've written on X").
- Also use for "index my Apple Notes", tag/folder queries, and "what's connected to X".
- Do **not** use for creating reminders, or for non-Apple-Notes note systems.

## Prerequisites

- macOS with Apple Notes.
- `bun` installed (`brew install oven-sh/bun/bun`).
- Full Disk Access granted to the `bun` binary.
- MCP server registered in the client (Claude Code or Claude Desktop).

## Procedure

1. **Check if the MCP is connected.** If `apple-notes` tools are not available, the server isn't registered yet — do the Setup below before anything else. If tools exist but a search returns "not indexed" or empty, run `index-notes` first.
2. **Setup (walk the user through this):**
   a. **Install bun** (if absent): `brew install oven-sh/bun/bun`
   b. **Clone + install deps:**
      ```bash
      git clone https://github.com/connerkward/mcp-apple-notes
      cd mcp-apple-notes
      git checkout <reviewed-tag-or-commit>
      bun install
      ```
   c. **Grant Full Disk Access to bun.** Run `which bun`, then open System Settings → Privacy & Security → Full Disk Access, click `+`, and add that exact `bun` binary path (commonly `/opt/homebrew/bin/bun` or `/usr/local/bin/bun`). Without this the server cannot read NoteStore.sqlite and every call fails with a permissions error.
   d. **Register the MCP server** (pick the user's client):
      - Claude Code: `claude mcp add apple-notes -- bun /absolute/path/to/mcp-apple-notes/index.ts --stdio`
      - Claude Desktop: add to `claude_desktop_config.json`:
        ```json
        { "mcpServers": { "apple-notes": {
            "command": "/Users/<you>/.bun/bin/bun",
            "args": ["/Users/<you>/mcp-apple-notes/index.ts", "--stdio"] } } }
        ```
      - As a Claude Code plugin (bundles this skill too): `/plugin marketplace add connerkward/ckw-skills` then `/plugin install apple-notes@connerkward`.
   e. **Restart the client**, then tell the user to ask **"Index my Apple Notes"** (or call `index-notes`). First index of ~1,800 notes takes a few seconds.
3. **Tool selection:**
   - `index-notes`: First run, or to force a rebuild. Background job with live progress.
   - `search-notes`: **Default search.** Hybrid semantic + BM25, re-ranked. Optional `folder`, `modifiedAfter`, `modifiedBefore`. "What did I write about X."
   - `find-notes`: Exact substring match (like the Apple Notes search box). Use when the user wants a literal string, not meaning. Optional `folder`, date range.
   - `get-note`: Fetch one full note by title (fuzzy fallback).
   - `list-notes`: Notes by recency. Optional `folder`, date range, `limit`.
   - `list-folders`: All folders + note counts.
   - `list-tags` / `search-by-tag`: `#hashtag` inventory / notes carrying a given tag.
   - `related-notes`: Notes related to a given one via shared tags, `[[wikilinks]]`, and vector similarity. "Show me related notes."
   - `bridge-notes`: **Swanson-ABC bridges** — non-obvious connections: pairs (A, C) not directly similar but both strongly tied to a shared intermediary B. "Find non-obvious connections across my notes." Optional `folder`, `limit`. No LLM.
   - `feed`: Ranked evidence-first connection stream (bridges + abstraction pairs + entity threads) as JSON. Optional `limit`.
   - `entity-notes` / `list-entities`: "Where else do I talk about Mercedes?" Entity chips → notes by mention weight. **Needs the optional entity graph db** (`~/.mcp-apple-notes/layered_graph.db`); if absent these report how to generate it.
   - `get-tables`: Pull pipe/tab tables out of a note.
   - `create-note` / `update-note`: Create or edit a note.
   - `check-changes`: Did notes change since last index? (does not trigger re-index)
   - `index-health`: Sync status, last-indexed time, note count. Run this if results seem stale.
4. **Synthesis:** For "synthesize what I think about X" the synthesis lives in the **web app** endpoint (`GET /api/synthesize?q=` at `http://localhost:3741/` when run with `bun index.ts`), which writes a grounded answer with inline `[n]` citations back to source notes.

## Pitfalls

- **Index before the first search.** No index → empty/garbage results; run `index-notes`.
- **Auto re-index:** each search does ~1ms change detection and kicks ONE background incremental index if notes changed — search returns immediately from the current index and catches up when the job lands. If a just-edited note is missing, it's the catch-up lag; re-run the search.
- **Score:** `score = RRF(vector, BM25) × title_boost × recency_factor`.
- **Temporal queries** (`recent`, `latest`, `today`) auto-shift to a 1-day recency half-life at 70% weight; normal queries keep relevance primary (90-day half-life, 10%).
- **Synthesis is the only cloud-capable part.** It needs an LLM: local via LM Studio / Ollama (`SYNTH_BASE_URL=http://localhost:1234/v1 SYNTH_MODEL=<model> OPENAI_API_KEY=local`, notes stay on-device) or real OpenAI (funded `OPENAI_API_KEY`, defaults to `gpt-4o-mini`). Everything else — embeddings, search, BM25, clustering, bridges, entities — is on-device.
- **Entity tools require the optional layered graph database**; without it, use hybrid search, exact search, related notes, or bridges instead.
- **macOS and Apple Notes only**; it does not search Obsidian, Notion, Google Docs, or other note stores.
- **Local filesystem permissions:** The MCP server needs local filesystem permissions to read Apple Notes data, so setup cannot be completed purely inside a remote shell.

## Verification

- **Check MCP connection:** Attempt to call `index-health`. If it returns sync status, last-indexed time, and note count, the MCP is connected.
- **Check index status:** If search returns "not indexed" or empty, run `index-notes` and check `index-health` again.
- **Verify synthesis endpoint:** If the web app is running (`bun index.ts`), verify the endpoint with `curl "http://localhost:3741/api/synthesize?q=test"` and check for a grounded answer with inline citations.
