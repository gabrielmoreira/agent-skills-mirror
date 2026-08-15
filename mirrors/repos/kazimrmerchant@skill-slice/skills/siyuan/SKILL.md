---
name: siyuan
description: "Drives the SiYuan kernel HTTP API via curl to search, read, create, update, and delete blocks and documents, run SQL, and export Markdown. Use when managing a self-hosted SiYuan (思源笔记) knowledge base. Not for Obsidian vault notes, Apple Notes MCP search, or Notion."
version: 1.0.1
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SiYuan, Notes, Knowledge Base, PKM, API]
    related_skills: [obsidian, notion]
    homepage: https://github.com/siyuan-note/siyuan
prerequisites:
  env_vars: [SIYUAN_TOKEN]
  commands: [curl, jq]
required_environment_variables:
  - name: SIYUAN_TOKEN
    prompt: SiYuan API token
    help: "Settings > About in SiYuan desktop app"
  - name: SIYUAN_URL
    prompt: SiYuan instance URL (default http://127.0.0.1:6806)
    required_for: remote instances
---

# SiYuan Note API

Use the [SiYuan](https://github.com/siyuan-note/siyuan) kernel API via curl to search, read, create, update, and delete blocks and documents in a self-hosted knowledge base. No extra tools needed — just `curl` and an API token.

## When to Use

- User asks to search, read, create, update, or delete content in a SiYuan knowledge base.
- User mentions "SiYuan", "思源笔记", or references a self-hosted PKM with block-level IDs.
- User wants to run SQL queries against their notes database or export documents as Markdown.
- User needs to manage notebooks, documents, blocks, or block attributes programmatically.

## Prerequisites

1. Install and run SiYuan (desktop app or Docker container).
2. Get your API token: **Settings > About > API token** in the SiYuan desktop app.
3. Store credentials in `${HERMES_HOME:-~/.hermes}/.env`:

   ```
   SIYUAN_TOKEN=your_token_here
   SIYUAN_URL=http://127.0.0.1:6806
   ```

   `SIYUAN_URL` defaults to `http://127.0.0.1:6806` if not set.

4. Ensure `curl` and `jq` are available on PATH.

**Windows (PowerShell) note:** In PowerShell, use `$env:SIYUAN_TOKEN` and `$env:SIYUAN_URL` instead of `$SIYUAN_TOKEN`. For multi-line JSON bodies, prefer writing the JSON to a temp file and using `-d "@file.json"` to avoid quoting issues, or use single-quoted here-strings.

## Procedure

### API Basics

All SiYuan API calls are **POST with a JSON body** — even read-only operations. Never use GET.

Every request follows this pattern:

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/..." \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"param": "value"}'
```

Responses are JSON:

```json
{"code": 0, "msg": "", "data": { ... }}
```

`code: 0` means success. Any other value is an error — check `msg` for details. Always verify `code == 0` before processing `data`.

**ID format:** SiYuan IDs look like `20210808180117-6v0mkxr` (14-digit timestamp + 7 alphanumeric chars). Reject any ID that does not match the pattern `YYYYMMDDHHmmss-xxxxxxx`.

### Quick Reference

| Operation | Endpoint |
|-----------|----------|
| Full-text search | `/api/search/fullTextSearchBlock` |
| SQL query | `/api/query/sql` |
| Read block (Kramdown) | `/api/block/getBlockKramdown` |
| Read child blocks | `/api/block/getChildBlocks` |
| Get human-readable path | `/api/filetree/getHPathByID` |
| Get block attributes | `/api/attr/getBlockAttrs` |
| List notebooks | `/api/notebook/lsNotebooks` |
| List documents | `/api/filetree/listDocsByPath` |
| Create notebook | `/api/notebook/createNotebook` |
| Create document | `/api/filetree/createDocWithMd` |
| Append block | `/api/block/appendBlock` |
| Prepend block | `/api/block/prependBlock` |
| Insert block | `/api/block/insertBlock` |
| Update block | `/api/block/updateBlock` |
| Rename document | `/api/filetree/renameDocByID` |
| Set attributes | `/api/attr/setBlockAttrs` |
| Delete block | `/api/block/deleteBlock` |
| Delete document | `/api/filetree/removeDocByID` |
| Delete notebook | `/api/notebook/removeNotebook` |
| Export as Markdown | `/api/export/exportMdContent` |

### Step 1 — Verify Connectivity

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/notebook/lsNotebooks" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.code, .data.notebooks[] | {id, name, closed}'
```

If `code` is not `0`, the token or URL is wrong.

### Step 2 — Search (Full-Text)

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/search/fullTextSearchBlock" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "meeting notes", "page": 0}' | jq '.data.blocks[:5]'
```

### Step 3 — Search (SQL)

Query the blocks database directly. **Only SELECT statements are safe.** Never send INSERT, UPDATE, DELETE, or DROP.

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/query/sql" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"stmt": "SELECT id, content, type, box FROM blocks WHERE content LIKE '\''%keyword%'\'' AND type='\''p'\'' LIMIT 20"}' | jq '.data'
```

Useful columns: `id`, `parent_id`, `root_id`, `box` (notebook ID), `path`, `content`, `type`, `subtype`, `created`, `updated`.

### Step 4 — Read Block Content (Kramdown)

Returns block content in Kramdown (Markdown-like) format.

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/getBlockKramdown" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "20210808180117-6v0mkxr"}' | jq '.data.kramdown'
```

### Step 5 — Read Child Blocks

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/getChildBlocks" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "20210808180117-6v0mkxr"}' | jq '.data'
```

### Step 6 — Get Human-Readable Path

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/filetree/getHPathByID" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "20210808180117-6v0mkxr"}' | jq '.data'
```

### Step 7 — Get Block Attributes

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/attr/getBlockAttrs" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "20210808180117-6v0mkxr"}' | jq '.data'
```

### Step 8 — List Notebooks

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/notebook/lsNotebooks" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.data.notebooks[] | {id, name, closed}'
```

### Step 9 — List Documents in a Notebook

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/filetree/listDocsByPath" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notebook": "NOTEBOOK_ID", "path": "/"}' | jq '.data.files[] | {id, name}'
```

### Step 10 — Create a Notebook

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/notebook/createNotebook" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My New Notebook"}' | jq '.data.notebook.id'
```

### Step 11 — Create a Document

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/filetree/createDocWithMd" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notebook": "NOTEBOOK_ID",
    "path": "/Meeting Notes/2026-03-22",
    "markdown": "# Meeting Notes\n\n- Discussed project timeline\n- Assigned tasks"
  }' | jq '.data'
```

### Step 12 — Append Block to a Document or Block

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/appendBlock" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parentID": "DOCUMENT_OR_BLOCK_ID",
    "data": "New paragraph added at the end.",
    "dataType": "markdown"
  }' | jq '.data'
```

Also available:
- `/api/block/prependBlock` — same params, inserts at the beginning.
- `/api/block/insertBlock` — uses `previousID` instead of `parentID` to insert after a specific block.

### Step 13 — Update Block Content

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/updateBlock" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "BLOCK_ID",
    "data": "Updated content here.",
    "dataType": "markdown"
  }' | jq '.data'
```

### Step 14 — Rename a Document

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/filetree/renameDocByID" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "DOCUMENT_ID", "title": "New Title"}'
```

### Step 15 — Set Block Attributes

Custom attributes must be prefixed with `custom-`:

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/attr/setBlockAttrs" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "BLOCK_ID",
    "attrs": {
      "custom-status": "reviewed",
      "custom-priority": "high"
    }
  }'
```

### Step 16 — Delete a Block

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/deleteBlock" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "BLOCK_ID"}'
```

To delete a whole document: use `/api/filetree/removeDocByID` with `{"id": "DOC_ID"}`.
To delete a notebook: use `/api/notebook/removeNotebook` with `{"notebook": "NOTEBOOK_ID"}`.

### Step 17 — Export Document as Markdown

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/export/exportMdContent" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "DOCUMENT_ID"}' | jq -r '.data.content'
```

## Block Types

Common `type` values in SQL queries:

| Type | Description |
|------|-------------|
| `d` | Document (root block) |
| `p` | Paragraph |
| `h` | Heading |
| `l` | List |
| `i` | List item |
| `c` | Code block |
| `m` | Math block |
| `t` | Table |
| `b` | Blockquote |
| `s` | Super block |
| `html` | HTML block |

## Examples

### Find all headings containing "project" and show their document paths

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/query/sql" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"stmt": "SELECT id, content, root_id FROM blocks WHERE type='\''h'\'' AND content LIKE '\''%project%'\'' LIMIT 50"}' \
  | jq '.data[]'
```

### Create a daily journal document and append a task

```bash
# 1. Create the document
DOC_ID=$(curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/filetree/createDocWithMd" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notebook": "NOTEBOOK_ID",
    "path": "/Journal/2026-03-22",
    "markdown": "# 2026-03-22"
  }' | jq -r '.data')

# 2. Append a task block
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/appendBlock" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"parentID\": \"$DOC_ID\", \"data\": \"- [ ] Review pull requests\", \"dataType\": \"markdown\"}"
```

## Pitfalls

- **All endpoints are POST** — even read-only operations like search and SQL. Do not use GET.
- **SQL safety**: only use SELECT queries. INSERT/UPDATE/DELETE/DROP are dangerous and should never be sent.
- **ID validation**: IDs match the pattern `YYYYMMDDHHmmss-xxxxxxx`. Reject anything else before making API calls.
- **Error responses**: always check `code != 0` in responses before processing `data`. The `msg` field contains the error message.
- **Large documents**: block content and export results can be very large. Use `LIMIT` in SQL and pipe through `jq` to extract only what you need.
- **Notebook IDs**: when working with a specific notebook, get its ID first via `lsNotebooks` — do not assume the notebook name is the ID.
- **Custom attributes**: must be prefixed with `custom-`. Attributes without this prefix may be ignored or overwritten by SiYuan internals.
- **PowerShell quoting**: nested single quotes in SQL JSON bodies are painful in PowerShell. Write the JSON to a temp file and use `curl -d "@body.json"` to avoid quoting hell.
- **Closed notebooks**: `lsNotebooks` returns both open and closed notebooks. Filter on `closed` if you only want accessible notebooks.

## Verification

1. **Check token and connectivity:**

   ```bash
   curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/notebook/lsNotebooks" \
     -H "Authorization: Token $SIYUAN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{}' | jq '.code'
   ```

   Expected output: `0`

2. **Verify a search returns results:**

   ```bash
   curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/search/fullTextSearchBlock" \
     -H "Authorization: Token $SIYUAN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"query": "test", "page": 0}' | jq '.data.blocks | length'
   ```

   Expected output: a non-negative integer.

3. **Verify a block read succeeds:**

   ```bash
   curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/getBlockKramdown" \
     -H "Authorization: Token $SIYUAN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"id": "20210808180117-6v0mkxr"}' | jq '.code, .data.kramdown'
   ```

   Expected: `0` followed by the block's Kramdown content.

## Alternative: MCP Server

If you prefer a native integration instead of curl, install the SiYuan MCP server:

```yaml
# In ~/.hermes/config.yaml under mcp_servers:
mcp_servers:
  siyuan:
    command: npx
    args: ["-y", "@porkll/siyuan-mcp"]
    env:
      SIYUAN_TOKEN: "YOUR_TOKEN"
      SIYUAN_URL: "http://127.0.0.1:6806"
```

## Related Skills

- **obsidian** — local Markdown-based PKM with file-system access.
- **notion** — cloud-based workspace with database and page APIs.
