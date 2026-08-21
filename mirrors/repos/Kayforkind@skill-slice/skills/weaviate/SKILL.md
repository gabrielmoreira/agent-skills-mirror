---
name: weaviate
description: "Operates Weaviate Cloud or self-hosted collections with weaviate-client v4: list/create, import, semantic/hybrid/keyword search, Query Agent. Use when the user names Weaviate. Not for local Chroma (chroma), Pinecone serverless (pinecone), or FAISS-only kNN. Never hardcode WEAVIATE_API_KEY."
version: 1.0.1
category: databases
risk: critical
source: community
source_repo: weaviate/agent-skills
source_type: official
date_added: "2026-06-29"
author: Weaviate
tags: [weaviate, vector-database, semantic-search, hybrid-search, data-import]
tools: [python, weaviate]
license: "BSD-3-Clause"
license_source: "https://github.com/weaviate/agent-skills/blob/main/LICENSE"
---

# Weaviate Database Operations

Comprehensive access to Weaviate vector databases: search operations, natural language queries, schema inspection, data exploration, filtered fetching, collection creation, and data imports.

## When to Use

- Inspect Weaviate collections, schemas, or data distribution.
- Run semantic, hybrid, keyword, filtered, or Query Agent searches against Weaviate.
- Import CSV, JSON, JSONL, or PDF data into a Weaviate collection.
- Create example data or a new collection for a Weaviate-backed workflow.

**Trigger keywords:** weaviate, vector database, collection, semantic search, hybrid search, keyword search, query agent, vectorize, import data, schema inspection.

### Weaviate Cloud Instance

If the user does not have an instance yet, direct them to the cloud console to register and create a free sandbox: [Weaviate Cloud](https://console.weaviate.cloud/signin?utm_source=github&utm_campaign=agent_skills).

## Prerequisites

### Environment Variables

**Required (must be set before any script runs):**

| Variable | Purpose |
|---|---|
| `WEAVIATE_URL` | Weaviate Cloud cluster URL |
| `WEAVIATE_API_KEY` | Weaviate API key |

**External Provider Keys (auto-detected — set only the keys your collections use):**

See `references/environment_requirements.md` for the full list of supported providers and their variable names. Common ones include `OPENAI_APIKEY`, `COHERE_APIKEY`, `ANTHROPIC_APIKEY`, and `AWS_ACCESS_KEY` / `AWS_SECRET_ACCESS_KEY` for the `text2vec_weaviate` vectorizer.

> **HARD RULE:** Never hardcode secrets in scripts or commit them to version control. Use environment variables or a `.env` file. All examples in this skill use `YOUR_KEY` placeholders.

### Windows Host (PowerShell)

The primary host is Windows with PowerShell. When setting environment variables in the current session:

```powershell
$env:WEAVIATE_URL = "https://your-cluster.weaviate.cloud"
$env:WEAVIATE_API_KEY = "YOUR_KEY"
```

For a persistent user-level setting:

```powershell
[Environment]::SetEnvironmentVariable("WEAVIATE_URL", "https://your-cluster.weaviate.cloud", "User")
[Environment]::SetEnvironmentVariable("WEAVIATE_API_KEY", "YOUR_KEY", "User")
```

All `uv run` commands below work identically in PowerShell and bash. Multi-line commands using `\` (backslash continuation) should be replaced with backtick `` ` `` in PowerShell, or run as a single line.

### Python / uv

Scripts are executed via `uv run` from this skill's `scripts/` directory. Ensure `uv` is installed and available on `PATH`.

## Procedure

### Step 0 — Load the right reference before acting

Each operation has a dedicated reference file under `references/`. **Load the reference file that matches the operation before running the corresponding script.** This ensures you pass correct flags and understand output shape.

| Operation | Script | Reference to load first |
|---|---|---|
| List collections | `scripts/list_collections.py` | `references/list_collections.md` |
| Get collection details | `scripts/get_collection.py` | `references/get_collection.md` |
| Explore collection data | `scripts/explore_collection.py` | `references/explore_collection.md` |
| Create collection | `scripts/create_collection.py` | `references/create_collection.md` |
| Import data | `scripts/import.py` | `references/import_data.md` |
| Create example data | `scripts/example_data.py` | `references/example_data.md` |
| Query Agent — Ask | `scripts/ask.py` | `references/ask.md` |
| Query Agent — Search | `scripts/query_search.py` | `references/query_search.md` |
| Hybrid search | `scripts/hybrid_search.py` | `references/hybrid_search.md` |
| Semantic search | `scripts/semantic_search.py` | `references/semantic_search.md` |
| Keyword search | `scripts/keyword_search.py` | `references/keyword_search.md` |
| Fetch & filter | `scripts/fetch_filter.py` | `references/fetch_filter.md` |

Also load `references/environment_requirements.md` whenever you need to configure or troubleshoot provider API keys.

### Step 1 — Discover available collections

Always start here if you don't know what exists:

```bash
uv run scripts/list_collections.py
```

Load `references/list_collections.md` for flag details and output format.

### Step 2 — (Optional) Create example data if the instance is empty

If no collections exist and the user wants toy data to experiment with, ask the user first, then:

```bash
uv run scripts/example_data.py
```

Load `references/example_data.md` before running.

### Step 3 — Inspect a collection's schema

```bash
uv run scripts/get_collection.py --name "COLLECTION_NAME"
```

Load `references/get_collection.md` for property-level details, vectorizer config, replication factor, and multi-tenancy status.

### Step 4 — Explore data distribution and content

```bash
uv run scripts/explore_collection.py "COLLECTION_NAME"
```

Load `references/explore_collection.md` to understand top values, data distribution, and sample objects.

### Step 5 — Create a collection (required before importing CSV/JSON/JSONL)

```bash
uv run scripts/create_collection.py CollectionName \
  --properties '[{"name": "title", "data_type": "text"}, {"name": "body", "data_type": "text"}]'
```

> **HARD RULE:** Do not specify a vectorizer unless the user explicitly requests one. The default `text2vec_weaviate` is used automatically.

Load `references/create_collection.md` for full property type reference and options.

### Step 6 — Import data into an existing collection

```bash
uv run scripts/import.py "data.csv" --collection "CollectionName"
```

Supported formats: CSV, JSON, JSONL, PDF.

> **HARD RULE:** For PDF imports, the collection is created automatically — skip Step 5. For all other formats, the collection must already exist.

Load `references/import_data.md` for format-specific flags, batch sizing, and error handling.

### Step 7 — Choose and run the right search

| User intent | Script | Reference |
|---|---|---|
| AI-powered direct answer with source citations across multiple collections | `scripts/ask.py` | `references/ask.md` |
| Browse/explore raw objects across multiple collections | `scripts/query_search.py` | `references/query_search.md` |
| General search (default when unsure) | `scripts/hybrid_search.py` | `references/hybrid_search.md` |
| Conceptually similar content (intent > keywords) | `scripts/semantic_search.py` | `references/semantic_search.md` |
| Exact terms, IDs, SKUs, specific text patterns | `scripts/keyword_search.py` | `references/keyword_search.md` |
| Retrieve specific objects by ID or strict filtered subsets | `scripts/fetch_filter.py` | `references/fetch_filter.md` |

**Default choice:** `hybrid_search.py` — provides the best balance of semantic understanding and exact keyword matching. Use this when unsure which search type to pick.

Load the matching reference file before running any search script to confirm required flags (e.g., `--query`, `--collection`, `--limit`, `--json`).

### Output Formats

All scripts support:

- **Markdown tables** — default and recommended for interactive use.
- **JSON** — pass `--json` flag for programmatic consumption.

## Pitfalls

- **`WEAVIATE_URL not set`** → Set the environment variable (see Prerequisites). In PowerShell, confirm with `$env:WEAVIATE_URL`.
- **`Collection not found`** → Run `scripts/list_collections.py` to see available collections. Collection names are case-sensitive.
- **Authentication error** → Check both `WEAVIATE_API_KEY` and any vectorizer provider keys (e.g., `OPENAI_APIKEY`, `COHERE_APIKEY`). See `references/environment_requirements.md`.
- **Importing into a non-existent collection** → For CSV/JSON/JSONL, create the collection first (Step 5). Only PDF import auto-creates the collection.
- **Specifying a vectorizer when not asked** → **HARD RULE:** Never set a vectorizer unless the user explicitly requests one. The default `text2vec_weaviate` is used.
- **Wrong search type** → If results are poor, switch to `hybrid_search.py` as the safe default. Use `keyword_search.py` only for exact matches; `semantic_search.py` only for conceptual similarity.
- **Multi-line commands in PowerShell** → Backslash `\` line continuation is bash syntax. In PowerShell use backtick `` ` `` or run as a single line.
- **Data exposure risk** → Data import, collection creation, and Query Agent operations can change or expose user data. **Always confirm the target instance and collection name before running scripts.**
- **No backup coverage** → These scripts do not replace broader data-governance, backup, or production migration procedures.

## Verification

### Verify environment is configured

```bash
uv run scripts/list_collections.py
```

Expected: a markdown table (or JSON with `--json`) listing collections, or an empty result if the instance is new. No `WEAVIATE_URL not set` or authentication errors.

### Verify a collection exists and has data

```bash
uv run scripts/get_collection.py --name "COLLECTION_NAME"
uv run scripts/explore_collection.py "COLLECTION_NAME"
```

Expected: schema details (properties, data types, vectorizer config) from `get_collection.py`, and data distribution / sample objects from `explore_collection.py`.

### Verify a search returns results

```bash
uv run scripts/hybrid_search.py --collection "COLLECTION_NAME" --query "example query" --limit 5
```

Expected: a markdown table with result rows containing object properties and a score/distance column. If using `--json`, valid JSON array output.

### Verify import succeeded

```bash
uv run scripts/explore_collection.py "COLLECTION_NAME"
```

Expected: object count and sample rows reflecting the imported data.

## Related Skills

- **databases** category siblings — for other vector and relational database operations.
- **data-import** tagged skills — for ETL pipelines feeding Weaviate.
