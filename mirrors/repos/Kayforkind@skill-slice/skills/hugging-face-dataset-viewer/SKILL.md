---
name: hugging-face-dataset-viewer
description: Calls the Hugging Face Dataset Viewer HTTP API (datasets-server.huggingface.co) to validate datasets, paginate, search, or filter rows, and list parquet shards. Use when inspecting or extracting rows from Hub datasets without loading them fully. Not for model-card eval tables (hugging-face-evaluation) or training loops. Do not use as a substitute for datasets.load_dataset.
version: 1.0.1
risk: unknown
source: https://github.com/huggingface/skills/tree/main/skills/huggingface-datasets
source_repo: huggingface/skills
source_type: official
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/huggingface/skills/blob/main/LICENSE
---

# Hugging Face Dataset Viewer

## Overview

This skill covers read-only Dataset Viewer API calls against the Hugging Face Hub for dataset exploration and row extraction. It also documents optional upload flows for creating dataset repos and publishing agent session traces. All Dataset Viewer endpoints are `GET` requests against `https://datasets-server.huggingface.co`.

## When to Use

Use this skill when you need to:

- Validate, preview, or paginate rows from a Hugging Face dataset.
- Search or filter dataset rows via the Dataset Viewer API.
- Discover parquet shard URLs or retrieve dataset size/statistics.
- Upload parquet files to a dataset repo (low-dependency CLI flow).
- Publish agent session traces (Claude Code, Codex, Pi) to the Hub.

Trigger keywords: *dataset viewer, huggingface dataset, hf rows, hf splits, hf parquet, dataset pagination, dataset search, dataset filter, agent traces*.

## Prerequisites

- `curl` available on PATH (Windows 10+ ships `curl.exe`; verify with `curl --version`).
- For gated/private datasets: a Hugging Face access token with read scope. Set it as an environment variable:

```powershell
# PowerShell (Windows host — primary)
$env:HF_TOKEN = "YOUR_KEY"
```

```bash
# Bash (Linux/macOS or WSL)
export HF_TOKEN=YOUR_KEY
```

- For upload flows: Node.js/npm (`npx`) or the `hf` CLI installed (`pip install huggingface_hub`).

## Procedure

### 1. Validate dataset availability

Check whether a dataset repo exists and is processable by the Dataset Viewer.

```powershell
curl -s "https://datasets-server.huggingface.co/is-valid?dataset=stanfordnlp/imdb"
```

Response includes `preview: true` if the dataset is ready for the viewer.

### 2. Resolve config and split names

```powershell
curl -s "https://datasets-server.huggingface.co/splits?dataset=stanfordnlp/imdb"
```

Extract `config` and `split` values from the response — these are required for all row-level endpoints.

### 3. Preview first rows

```powershell
curl -s "https://datasets-server.huggingface.co/first-rows?dataset=stanfordnlp/imdb&config=plain_text&split=train"
```

### 4. Paginate rows with `/rows`

- `offset` is **0-based**.
- `length` max is **100** per request.

```powershell
curl -s "https://datasets-server.huggingface.co/rows?dataset=stanfordnlp/imdb&config=plain_text&split=train&offset=0&length=100"
curl -s "https://datasets-server.huggingface.co/rows?dataset=stanfordnlp/imdb&config=plain_text&split=train&offset=100&length=100"
```

Use response fields `num_rows_total`, `num_rows_per_page`, and `partial` to drive continuation logic. Stop when `offset + length >= num_rows_total` or when `partial` indicates the response is truncated.

### 5. Search rows with `/search`

Full-text style matching on string columns.

```powershell
curl -s "https://datasets-server.huggingface.co/search?dataset=stanfordnlp/imdb&config=plain_text&split=train&query=excellent&offset=0&length=100"
```

### 6. Filter rows with `/filter`

Predicate-based filtering using `where` and optional `orderby`.

```powershell
curl -s "https://datasets-server.huggingface.co/filter?dataset=stanfordnlp/imdb&config=plain_text&split=train&where=label=1&offset=0&length=100"
```

> Keep all filtering and searches read-only and side-effect free.

### 7. Retrieve parquet shard links

```powershell
curl -s "https://datasets-server.huggingface.co/parquet?dataset=stanfordnlp/imdb"
```

Response contains per-config/split parquet file URLs. For CLI-based parquet URL discovery or SQL queries, use the `hf-cli` skill with `hf datasets parquet` and `hf datasets sql`.

### 8. Get dataset size and column statistics

```powershell
# Size totals (num_bytes, num_rows per config/split)
curl -s "https://datasets-server.huggingface.co/size?dataset=stanfordnlp/imdb"

# Column-level statistics
curl -s "https://datasets-server.huggingface.co/statistics?dataset=stanfordnlp/imdb&config=plain_text&split=train"
```

### 9. Get Croissant metadata (if available)

```powershell
curl -s "https://datasets-server.huggingface.co/croissant?dataset=stanfordnlp/imdb"
```

### 10. Authenticated requests for gated/private datasets

Pass the token as a bearer header:

```powershell
curl -s -H "Authorization: Bearer $env:HF_TOKEN" "https://datasets-server.huggingface.co/rows?dataset=your-org/private-dataset&config=default&split=train&offset=0&length=100"
```

### 11. Upload parquet files to a dataset repo

**Zero local dependencies (Hub UI):**

1. Create a dataset repo in the browser: `https://huggingface.co/new-dataset`
2. Upload parquet files via the repo "Files and versions" page.
3. Verify shards appear in the Dataset Viewer:

```powershell
curl -s "https://datasets-server.huggingface.co/parquet?dataset=YOUR_NAMESPACE/YOUR_REPO"
```

**Low-dependency CLI flow (`npx @huggingface/hub`):**

```powershell
# Set auth token
$env:HF_TOKEN = "YOUR_KEY"

# Upload parquet folder (auto-creates repo if missing)
npx -y @huggingface/hub upload datasets/YOUR_NAMESPACE/YOUR_REPO ./local/parquet-folder data

# Upload as private repo on creation
npx -y @huggingface/hub upload datasets/YOUR_NAMESPACE/YOUR_REPO ./local/parquet-folder data --private
```

After upload, call `/parquet` to discover `<config>/<split>/<shard>` values for querying.

### 12. Publish agent session traces

The Hub auto-detects raw agent session traces from Claude Code, Codex, and Pi Agent. Upload them as original JSONL files and the Hub tags the dataset as `Traces` and enables the trace viewer.

Common local session directories:

- Claude Code: `~/.claude/projects`
- Codex: `~/.codex/sessions`
- Pi: `~/.pi/agent/sessions`

> **Always default to private dataset repos** — traces can contain prompts, file paths, tool outputs, secrets, or PII. Preserve raw `.jsonl` files and nest them by project/cwd rather than uploading every session at the dataset root.

```powershell
# Create private dataset repo
hf repos create YOUR_NAMESPACE/YOUR_REPO --type dataset --private --exist-ok

# Upload Codex sessions nested by project
hf upload YOUR_NAMESPACE/YOUR_REPO ~/.codex/sessions codex/YOUR_PROJECT --type dataset
```

## Pitfalls

- **`length` exceeds 100**: The API caps `length` at 100 for `/rows`, `/search`, and `/filter`. Requesting more returns at most 100 rows — do not assume you received the full requested count.
- **Missing `config` or `split`**: Row-level endpoints require both parameters. Always call `/splits` first if you do not know them.
- **Gated/private datasets without auth**: Requests silently return 401/403 or empty results. Always pass `Authorization: Bearer <HF_TOKEN>` for non-public datasets.
- **URL encoding**: Query parameters (especially `where`, `query`, `dataset`) must be URL-encoded. Spaces, `&`, `=`, and special characters break the request if not encoded.
- **`partial` flag**: When `/rows` returns `partial: true`, the response is truncated and does not represent all matching rows. Use `num_rows_total` to determine how many pages remain.
- **Trace uploads with secrets**: Agent traces can embed file contents, API keys, or PII from tool outputs. Always use `--private` and review contents before uploading.
- **Flat trace uploads**: Uploading all `.jsonl` files to the dataset root makes the trace viewer hard to navigate. Nest by project or cwd directory.
- **PowerShell variable expansion**: In PowerShell, use `$env:HF_TOKEN` (not `$HF_TOKEN`) for environment variable expansion inside double-quoted strings. In single-quoted strings, no expansion occurs.

## Verification

### Verify dataset is valid and viewer-ready

```powershell
curl -s "https://datasets-server.huggingface.co/is-valid?dataset=stanfordnlp/imdb"
```

Expected: JSON with `"preview": true`.

### Verify splits are resolved

```powershell
curl -s "https://datasets-server.huggingface.co/splits?dataset=stanfordnlp/imdb"
```

Expected: JSON with a `splits` array containing `config` and `split` names.

### Verify row pagination works

```powershell
curl -s "https://datasets-server.huggingface.co/rows?dataset=stanfordnlp/imdb&config=plain_text&split=train&offset=0&length=5"
```

Expected: JSON with `rows` array (5 entries) and `num_rows_total` field.

### Verify parquet links exist

```powershell
curl -s "https://datasets-server.huggingface.co/parquet?dataset=stanfordnlp/imdb"
```

Expected: JSON with `parquet_files` array containing URLs ending in `.parquet`.

### Verify authenticated access (private dataset)

```powershell
curl -s -H "Authorization: Bearer $env:HF_TOKEN" "https://datasets-server.huggingface.co/is-valid?dataset=YOUR_NAMESPACE/YOUR_PRIVATE_REPO"
```

Expected: JSON with `"preview": true` (not a 401/403 error).

## Related skills

- `hf-cli` — Use for `hf datasets parquet` and `hf datasets sql` when you need CLI-based parquet discovery or SQL queries over dataset shards.
- `huggingface-hub` — Use for general Hub operations (model upload, repo management, space deployment).
