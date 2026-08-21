---
name: qmd
description: "Indexes local notes, docs, and transcripts with qmd hybrid retrieval (BM25 + vectors + LLM rerank) via @tobilu/qmd. Use when searching a personal knowledge base semantically without cloud APIs. Not for Obsidian vault editing (obsidian), Mesh Memory MCP worklogs (mesh-memory), or arXiv paper search (arxiv)."
version: 1.0.1
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [Search, Knowledge-Base, RAG, Notes, MCP, Local-AI]
    related_skills: [obsidian, native-mcp, arxiv]
---

# QMD — Query Markup Documents

Local, on-device search engine for personal knowledge bases. Indexes markdown
notes, meeting transcripts, documentation, and any text-based files, then
provides hybrid search combining keyword matching, semantic understanding, and
LLM-powered reranking — all running locally with no cloud dependencies.

Created by [Tobi Lütke](https://github.com/tobi/qmd). MIT licensed.

## When to Use

- User asks to search their notes, docs, knowledge base, or meeting transcripts
- User wants to find something across a large collection of markdown/text files
- User wants semantic search ("find notes about X concept") not just keyword grep
- User has already set up qmd collections and wants to query them
- User asks to set up a local knowledge base or document search system
- Keywords: "search my notes", "find in my docs", "knowledge base", "qmd", "semantic search notes"

## Prerequisites

### Node.js >= 22 (required)

**Windows (PowerShell — primary host):**

```powershell
# Check version
node --version  # must be >= 22

# Install via winget
winget install OpenJS.NodeJS.LTS

# Or via Chocolatey
choco install nodejs-lts
```

**macOS:**

```bash
node --version  # must be >= 22
brew install node@22
```

**Linux:**

```bash
node --version  # must be >= 22
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
# or with nvm:
nvm install 22 && nvm use 22
```

### SQLite with Extension Support (macOS only)

macOS system SQLite lacks extension loading. Install via Homebrew:

```bash
brew install sqlite
```

> Windows and Linux typically have extension-capable SQLite bundled or available
> via the Node.js native module — no extra step needed.

### Install qmd

```bash
npm install -g @tobilu/qmd
# or with Bun:
bun install -g @tobilu/qmd
```

First run auto-downloads 3 local GGUF models (~2GB total):

| Model | Purpose | Size |
|-------|---------|------|
| embeddinggemma-300M-Q8_0 | Vector embeddings | ~300MB |
| qwen3-reranker-0.6b-q8_0 | Result reranking | ~640MB |
| qmd-query-expansion-1.7B | Query expansion | ~1.1GB |

### Verify Installation

```bash
qmd --version
qmd status
```

## Procedure

### Quick Reference

| Command | What It Does | Speed |
|---------|-------------|-------|
| `qmd search "query"` | BM25 keyword search (no models) | ~0.2s |
| `qmd vsearch "query"` | Semantic vector search (1 model) | ~3s |
| `qmd query "query"` | Hybrid + reranking (all 3 models) | ~2-3s warm, ~19s cold |
| `qmd get <docid>` | Retrieve full document content | instant |
| `qmd multi-get "glob"` | Retrieve multiple files | instant |
| `qmd collection add <path> --name <n>` | Add a directory as a collection | instant |
| `qmd context add <path> "description"` | Add context metadata to improve retrieval | instant |
| `qmd embed` | Generate/update vector embeddings | varies |
| `qmd status` | Show index health and collection info | instant |
| `qmd mcp` | Start MCP server (stdio) | persistent |
| `qmd mcp --http --daemon` | Start MCP server (HTTP, warm models) | persistent |

### Step 1 — Add Collections

Point qmd at directories containing your documents:

**Windows (PowerShell):**

```powershell
qmd collection add $HOME\notes --name notes
qmd collection add $HOME\projects\myproject\docs --name project-docs
qmd collection add $HOME\meetings --name meetings
qmd collection list
```

**macOS / Linux:**

```bash
qmd collection add ~/notes --name notes
qmd collection add ~/projects/myproject/docs --name project-docs
qmd collection add ~/meetings --name meetings
qmd collection list
```

### Step 2 — Add Context Descriptions

Context metadata helps the search engine understand what each collection
contains. This significantly improves retrieval quality — always do this:

```bash
qmd context add qmd://notes "Personal notes, ideas, and journal entries"
qmd context add qmd://project-docs "Technical documentation for the main project"
qmd context add qmd://meetings "Meeting transcripts and action items from team syncs"
```

### Step 3 — Generate Embeddings

```bash
qmd embed
```

This processes all documents in all collections and generates vector
embeddings. **Re-run after adding new documents or collections.**

### Step 4 — Verify

```bash
qmd status   # shows index health, collection stats, model info
```

### Search Patterns

#### Fast Keyword Search (BM25)

Best for: exact terms, code identifiers, names, known phrases.
No models loaded — near-instant results.

```bash
qmd search "authentication middleware"
qmd search "handleError async"
```

#### Semantic Vector Search

Best for: natural language questions, conceptual queries.
Loads embedding model (~3s first query).

```bash
qmd vsearch "how does the rate limiter handle burst traffic"
qmd vsearch "ideas for improving onboarding flow"
```

#### Hybrid Search with Reranking (Best Quality)

Best for: important queries where quality matters most.
Uses all 3 models — query expansion, parallel BM25+vector, reranking.

```bash
qmd query "what decisions were made about the database migration"
```

#### Structured Multi-Mode Queries

Combine different search types in a single query for precision:

```bash
# BM25 for exact term + vector for concept
qmd query $'lex: rate limiter\nvec: how does throttling work under load'

# With query expansion
qmd query $'expand: database migration plan\nlex: "schema change"'
```

> **Windows PowerShell note:** Multi-line strings with `$'...'` syntax are
> bash-specific. In PowerShell, use backtick-n for newlines or pass via a
> here-string:
>
> ```powershell
> qmd query "lex: rate limiter`nvec: how does throttling work under load"
> ```

#### Query Syntax (lex/BM25 mode)

| Syntax | Effect | Example |
|--------|--------|---------|
| `term` | Prefix match | `perf` matches "performance" |
| `"phrase"` | Exact phrase | `"rate limiter"` |
| `-term` | Exclude term | `performance -sports` |

#### HyDE (Hypothetical Document Embeddings)

For complex topics, write what you expect the answer to look like:

```bash
qmd query $'hyde: The migration plan involves three phases. First, we add the new columns without dropping the old ones. Then we backfill data. Finally we cut over and remove legacy columns.'
```

#### Scoping to Collections

```bash
qmd search "query" --collection notes
qmd query "query" --collection project-docs
```

#### Output Formats

```bash
qmd search "query" --json        # JSON output (best for parsing)
qmd search "query" --limit 5     # Limit results
qmd get "#abc123"                # Get by document ID
qmd get "path/to/file.md"       # Get by file path
qmd get "file.md:50" -l 100     # Get specific line range
qmd multi-get "journals/*.md" --json  # Batch retrieve by glob
```

### MCP Integration (Recommended)

qmd exposes an MCP server that provides search tools directly to the agent
via the native MCP client. This is the preferred integration — once
configured, the agent gets qmd tools automatically without needing to load
this skill.

#### Option A: Stdio Mode (Simple)

Add to your agent's MCP config (e.g. `~/.hermes/config.yaml` or equivalent):

```yaml
mcp_servers:
  qmd:
    command: "qmd"
    args: ["mcp"]
    timeout: 30
    connect_timeout: 45
```

This registers tools: `mcp_qmd_search`, `mcp_qmd_vsearch`,
`mcp_qmd_deep_search`, `mcp_qmd_get`, `mcp_qmd_status`.

**Tradeoff:** Models load on first search call (~19s cold start),
then stay warm for the session. Acceptable for occasional use.

#### Option B: HTTP Daemon Mode (Fast, Recommended for Heavy Use)

Start the qmd daemon separately — it keeps models warm in memory:

```bash
# Start daemon (persists across agent restarts)
qmd mcp --http --daemon

# Runs on http://localhost:8181 by default
```

Then configure the agent to connect via HTTP:

```yaml
mcp_servers:
  qmd:
    url: "http://localhost:8181/mcp"
    timeout: 30
```

**Tradeoff:** Uses ~2GB RAM while running, but every query is fast
(~2-3s). Best for users who search frequently.

#### Keeping the Daemon Running

**macOS (launchd):**

```bash
cat > ~/Library/LaunchAgents/com.qmd.daemon.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.qmd.daemon</string>
  <key>ProgramArguments</key>
  <array>
    <string>qmd</string>
    <string>mcp</string>
    <string>--http</string>
    <string>--daemon</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/qmd-daemon.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/qmd-daemon.log</string>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.qmd.daemon.plist
```

**Linux (systemd user service):**

```bash
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/qmd-daemon.service << 'EOF'
[Unit]
Description=QMD MCP Daemon
After=network.target

[Service]
ExecStart=qmd mcp --http --daemon
Restart=on-failure
RestartSec=10
Environment=PATH=/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now qmd-daemon
systemctl --user status qmd-daemon
```

**Windows (Task Scheduler / PowerShell):**

```powershell
# Create a scheduled task to start qmd daemon at logon
$action = New-ScheduledTaskAction -Execute "qmd" -Argument "mcp --http --daemon"
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName "QmdDaemon" -Action $action -Trigger $trigger -Settings $settings

# Start now
Start-ScheduledTask -TaskName "QmdDaemon"

# Check status
Get-ScheduledTask -TaskName "QmdDaemon" | Get-ScheduledTaskInfo
```

#### MCP Tools Reference

Once connected, these tools are available as `mcp_qmd_*`:

| MCP Tool | Maps To | Description |
|----------|---------|-------------|
| `mcp_qmd_search` | `qmd search` | BM25 keyword search |
| `mcp_qmd_vsearch` | `qmd vsearch` | Semantic vector search |
| `mcp_qmd_deep_search` | `qmd query` | Hybrid search + reranking |
| `mcp_qmd_get` | `qmd get` | Retrieve document by ID or path |
| `mcp_qmd_status` | `qmd status` | Index health and stats |

The MCP tools accept structured JSON queries for multi-mode search:

```json
{
  "searches": [
    {"type": "lex", "query": "authentication middleware"},
    {"type": "vec", "query": "how user login is verified"}
  ],
  "collections": ["project-docs"],
  "limit": 10
}
```

### CLI Usage (Without MCP)

When MCP is not configured, use qmd directly via terminal:

```
terminal(command="qmd query 'what was decided about the API redesign' --json", timeout=30)
```

For setup and management tasks, always use terminal:

```
terminal(command="qmd collection add ~/Documents/notes --name notes")
terminal(command="qmd context add qmd://notes 'Personal research notes and ideas'")
terminal(command="qmd embed")
terminal(command="qmd status")
```

### How the Search Pipeline Works

Understanding the internals helps choose the right search mode:

1. **Query Expansion** — A fine-tuned 1.7B model generates 2 alternative
   queries. The original gets 2x weight in fusion.
2. **Parallel Retrieval** — BM25 (SQLite FTS5) and vector search run
   simultaneously across all query variants.
3. **RRF Fusion** — Reciprocal Rank Fusion (k=60) merges results.
   Top-rank bonus: #1 gets +0.05, #2-3 get +0.02.
4. **LLM Reranking** — qwen3-reranker scores top 30 candidates (0.0-1.0).
5. **Position-Aware Blending** — Ranks 1-3: 75% retrieval / 25% reranker.
   Ranks 4-10: 60/40. Ranks 11+: 40/60 (trusts reranker more for long tail).

**Smart Chunking:** Documents are split at natural break points (headings,
code blocks, blank lines) targeting ~900 tokens with 15% overlap. Code
blocks are never split mid-block.

## Pitfalls

1. **Forgetting to re-embed after adding documents** — `qmd embed` must be
   re-run when new files are added to collections. New documents will not
   appear in `vsearch` or `query` results until embeddings are generated.
2. **Skipping context descriptions** — `qmd context add` dramatically
   improves retrieval accuracy. Without context, the engine has no signal
   about what each collection contains. Always add descriptions.
3. **Cold start latency (~19s)** — Happens when models aren't loaded in
   memory. Use HTTP daemon mode (`qmd mcp --http --daemon`) to keep models
   warm, or use `qmd search` (BM25 only) when models aren't needed.
4. **macOS: "unable to load extension"** — System SQLite lacks extension
   loading. Fix: `brew install sqlite` and ensure it's on PATH before
   system SQLite.
5. **"No collections found"** — Run `qmd collection add <path> --name <name>`
   to add directories, then `qmd embed` to index them.
6. **Models downloading on first run** — Normal behavior. qmd auto-downloads
   ~2GB of GGUF models on first use. This is a one-time operation.
7. **First query in structured search gets 2x weight** — Put the most
   important/certain query first when combining lex and vec modes.
8. **PowerShell multi-line string syntax** — The bash `$'...\n...'` syntax
   does not work in PowerShell. Use backtick-n (`` `n ``) or here-strings
   for newline-separated structured queries.
9. **CJK / multilingual content** — The default embedding model is
   English-optimized. Set `QMD_EMBED_MODEL` environment variable for
   non-English content:
   ```bash
   export QMD_EMBED_MODEL="your-multilingual-model"
   ```
   ```powershell
   $env:QMD_EMBED_MODEL = "your-multilingual-model"
   ```

## Verification

### Verify Installation

```bash
qmd --version
# Expected: prints version number, e.g. 1.0.0

qmd status
# Expected: shows index health, collection stats, model info
```

### Verify Collections Are Indexed

```bash
qmd collection list
# Expected: lists all added collections with paths

qmd status
# Expected: shows document counts per collection, embedding status
```

### Verify Search Works

```bash
# Fast keyword search — should return results in ~0.2s
qmd search "test" --limit 3

# Semantic search — first run loads model (~3s), then returns results
qmd vsearch "test query" --limit 3

# Hybrid search — first run cold (~19s), warm ~2-3s
qmd query "test query" --limit 3 --json
```

### Verify MCP Daemon (if using HTTP mode)

```bash
# Check daemon is running on port 8181
curl http://localhost:8181/mcp
# Expected: HTTP response from MCP server
```

**Windows PowerShell:**

```powershell
Invoke-WebRequest -Uri "http://localhost:8181/mcp" -UseBasicParsing
# Expected: HTTP 200 response
```

### Verify Document Retrieval

```bash
# Get a document by ID (from search results)
qmd get "#abc123"

# Get a document by file path
qmd get "path/to/file.md"

# Get a specific line range
qmd get "file.md:50" -l 100
```

## Data Storage

- **Index & vectors:** `~/.cache/qmd/index.sqlite`
- **Windows equivalent:** `$env:USERPROFILE\.cache\qmd\index.sqlite`
- **Models:** Auto-downloaded to local cache on first run
- **No cloud dependencies** — everything runs locally

## Best Practices

1. **Always add context descriptions** — `qmd context add` dramatically
   improves retrieval accuracy. Describe what each collection contains.
2. **Re-embed after adding documents** — `qmd embed` must be re-run when
   new files are added to collections.
3. **Use `qmd search` for speed** — when you need fast keyword lookup
   (code identifiers, exact names), BM25 is instant and needs no models.
4. **Use `qmd query` for quality** — when the question is conceptual or
   the user needs the best possible results, use hybrid search.
5. **Prefer MCP integration** — once configured, the agent gets native
   tools without needing to load this skill each time.
6. **Daemon mode for frequent users** — if the user searches their
   knowledge base regularly, recommend the HTTP daemon setup.
7. **First query in structured search gets 2x weight** — put the most
   important/certain query first when combining lex and vec.

## References

- [GitHub: tobi/qmd](https://github.com/tobi/qmd)
- [QMD Changelog](https://github.com/tobi/qmd/blob/main/CHANGELOG.md)

## Related Skills

- **obsidian** — if the user's notes are in Obsidian vaults, qmd can index
  the vault directory directly
- **native-mcp** — for general MCP server configuration guidance
- **arxiv** — for searching academic papers (complementary to local notes)
