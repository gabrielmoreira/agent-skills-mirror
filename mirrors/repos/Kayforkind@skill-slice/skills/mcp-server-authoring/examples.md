# MCP Server Examples

Worked designs showing the rules from `SKILL.md`/`reference.md` applied end-to-end, plus bad→good comparisons. Code style matches the two template files; snippets here focus on the *decisions*, not boilerplate.

## Example 1 — Read-only codebase search server (TypeScript, stdio)

**Brief**: let the model search a local docs/code folder without shell access.

**Design decisions**
- stdio (local files, single user), TypeScript (npx distribution).
- Two tools, not five: `search_text` (find) + `read_slice` (retrieve). No `list_all_files` — that's blob-dumping; search covers discovery.
- Sandbox root from env `SEARCH_ROOT`, path-traversal enforcement per `security-checklist.md §3`.
- Result caps: 30 matches/page with cursor; `read_slice` caps at 300 lines per call.

```typescript
server.registerTool("search_text", {
  title: "Search text in workspace",
  description:
    "Search file contents under the configured workspace root (regex or literal). " +
    "Returns up to 30 matches per page as `path:line: excerpt`; pass cursor to page. " +
    "Follow up with read_slice for surrounding context. Read-only; binary files skipped.",
  inputSchema: {
    pattern: z.string().min(1).max(300).describe("Literal text, or regex if is_regex=true."),
    is_regex: z.boolean().default(false).describe("Treat pattern as a regular expression."),
    glob: z.string().optional().describe("Filename filter, e.g. '**/*.md'. Default: all text files."),
    cursor: z.string().optional().describe("Opaque cursor from a previous page."),
  },
  annotations: { readOnlyHint: true, idempotentHint: true, openWorldHint: false },
}, async (args) => { /* ripgrep-style walk; 100ms regex timeout to kill catastrophic backtracking */ });

server.registerTool("read_slice", {
  title: "Read file slice",
  description:
    "Read up to 300 lines of one file inside the workspace root, with line numbers. " +
    "Use after search_text to pull context. Larger files: call repeatedly with start_line.",
  inputSchema: {
    path: z.string().describe("Path relative to the workspace root (from search_text results)."),
    start_line: z.number().int().min(1).default(1).describe("First line to return (1-based)."),
    max_lines: z.number().int().min(1).max(300).default(120).describe("Line count cap."),
  },
  annotations: { readOnlyHint: true, idempotentHint: true, openWorldHint: false },
}, async ({ path, start_line, max_lines }) => {
  const abs = resolveInsideSandbox(path);          // realpath + prefix check, throws ToolishError
  /* stream lines start_line..start_line+max_lines; note "truncated at N; file has M lines" */
});
```

**Why this shape works**: the pair forms a search→read loop the model already knows from coding agents; caps keep every result context-cheap; regex timeout + sandbox close the two real attack surfaces.

## Example 2 — REST API wrapper (Python, stdio): outcome-shaped, not endpoint-shaped

**Brief**: expose an issue tracker (say, 25 REST endpoints) to the model.

**Wrong** (endpoint mirroring): `list_projects`, `get_project`, `list_issues`, `get_issue`, `create_issue`, `update_issue`, `list_comments`, `add_comment`, `list_labels`, `add_label`, `remove_label`, `list_users`, … 25 tools ≈ 25KB of descriptors in every prompt, and the model must choreograph 4-call chains for simple asks.

**Right** — five task tools:

| Tool | Wraps | Notes |
|---|---|---|
| `search_issues` | search + list + filters | cursor pagination, ≤20/page |
| `get_issue` | issue + comments + labels in ONE result | the model always wants them together |
| `create_issue` | create + label + assign | one call = one user intent; `idempotency_key` |
| `update_issue` | update/status/assign/labels | only provided fields change; `dry_run` default false |
| `add_comment` | comment create | markdown body, length-capped |

```python
@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def get_issue(
    issue_key: str = Field(description="Issue key, e.g. PROJ-123.", pattern=r"^[A-Z][A-Z0-9]+-\d+$"),
    ctx: Context = None,
) -> str:
    """Fetch one issue with its comments and labels in a single result.
    Use search_issues first if you only know words from the title."""
    app = ctx.request_context.lifespan_context
    async with app.limiter:                                   # semaphore + token bucket
        try:
            issue = await app.api.issue(issue_key, expand=["comments", "labels"])
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ToolError(f"{issue_key} not found. Use search_issues to locate the right key.")
            if e.response.status_code == 429:
                retry = e.response.headers.get("Retry-After", "60")
                raise ToolError(f"Tracker rate limit hit. Retry after {retry}s.")
            raise ToolError(f"Tracker API error {e.response.status_code}. Logged; may be transient.")
    return render_issue_markdown(issue, max_comments=10)      # "…and 14 older comments" marker
```

**Error mapping table** (pattern to copy): 401/403 → "credential problem, check env var X" · 404 → "not found + which search tool to use" · 409 → "conflict + current state summary" · 429 → "retry-after passthrough" · 5xx → "upstream down, transient". Every branch tells the model its *next move*.

## Example 3 — Read-only database analytics (Python): constrained raw SQL

**Brief**: let the model answer questions over a Postgres warehouse.

**Design decisions**
- Raw-SQL tool is acceptable **only** read-only: connection uses a `SELECT`-only role (defense in depth), plus statement gating.
- `get_schema` tool (or `schema://tables` resource) so the model doesn't guess column names — the #1 failure mode of DB servers.
- Row cap + statement timeout server-side, regardless of the query.

```python
@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def run_query(
    sql: str = Field(description="A single read-only SELECT/WITH statement.", max_length=5000),
    ctx: Context = None,
) -> str:
    """Run one read-only SQL query. Call get_schema first to see tables/columns.
    Results cap at 200 rows — aggregate in SQL rather than paging raw rows."""
    stmt = sqlglot.parse_one(sql, read="postgres")            # real parser, not regex
    if stmt.find(exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Alter, exp.Create, exp.Command):
        raise ToolError("Only SELECT/WITH queries are allowed on this connection.")
    app = ctx.request_context.lifespan_context
    rows = await app.db.fetch(f"SELECT * FROM ({stmt.sql()}) q LIMIT 201",
                              timeout=15)                     # deadline < host timeout
    truncated = len(rows) > 200
    return to_markdown_table(rows[:200]) + ("\n\n[truncated at 200 rows — aggregate instead]" if truncated else "")
```

## Example 4 — Long-running render job (TypeScript): job pattern

**Brief**: video render takes 3–10 minutes — far beyond any host timeout.

**Wrong**: one `render_video` tool that blocks for 8 minutes (even with progress, hosts cap total time; a disconnect wastes the render).

**Right** — three small tools around persistent job state:

```typescript
// start_render: validates input, enqueues, returns IMMEDIATELY
//   -> { jobId: "rj_7f3a", status: "queued", eta_seconds: 420 }
//   annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false }
// get_render_status(job_id): poll; while running returns progress + eta,
//   when done returns a resource_link to the artifact:
//   { type: "resource_link", uri: "file:///renders/rj_7f3a.mp4", mimeType: "video/mp4" }
// cancel_render(job_id): idempotent (cancelling a finished job is a no-op success)
```

Job state lives on disk (`jobs.json`/SQLite) — stdio servers restart whenever the host does, and in-memory jobs would orphan the render. Descriptions must teach the loop: `start_render`'s description ends with *"Then poll get_render_status every ~30s until status is 'done'."*

## Example 5 — Resources + prompt composition (any SDK)

A config-inspector server showing when the non-tool primitives earn their keep:

- Resource `env://summary` — redacted runtime config (user attaches it to context manually; no tool-call round trip).
- Resource template `logfile://{service}/{date}` — parameterized reads; completions on `service`.
- Prompt `diagnose_service(service)` — canned workflow: read `env://summary`, read latest `logfile://…`, correlate, propose fixes.
- One tool `tail_log(service, lines≤500)` for the interactive path.

Rule of thumb applied: data the *user* curates → resource; canned multi-step workflow the *user* triggers → prompt; anything the *model* decides to invoke → tool.

## Bad → good gallery

### Tool description

```text
BAD:  "Manages orders."
BAD:  "This tool can be used to search for orders in the system by various criteria." (padding, no limits)
GOOD: "Search orders by free text and optional status. Returns at most 20 summaries per
       page (cursor to page). Use get_order for full line-item detail; use refund_order
       to act on one. Read-only. Dates are UTC ISO-8601."
```
The good one routes (when to use), chains (what to call next), and bounds (page size, tz) in three sentences.

### Schema

```jsonc
// BAD — model must hallucinate the contract:
{ "type": "object", "properties": { "options": { "type": "object" } } }

// GOOD — closed, described, defaulted:
{ "type": "object",
  "properties": {
    "status": { "type": "string", "enum": ["open", "shipped", "cancelled"],
                "description": "Filter by lifecycle status." },
    "limit":  { "type": "integer", "minimum": 1, "maximum": 20, "default": 10,
                "description": "Max results (hard cap 20)." } },
  "required": [], "additionalProperties": false }
```

### Result

```text
BAD:  [478KB JSON dump of 3,000 orders]
GOOD: "3,000 orders match. First 20 below (cursor=eyJv… for more). Consider status/date filters.
       ORD-1042  Acme GmbH   open      $1,204.00
       …"
```

### Error

```text
BAD:  { "content": [{ "type": "text", "text": "Error" }], "isError": true }
BAD:  Traceback (most recent call last): File "~\srv\..."   (leaks paths; teaches nothing)
GOOD: { "content": [{ "type": "text",
        "text": "Order ORD-99 not found. Order ids look like ORD-<number>; use search_orders to locate the right id." }],
        "isError": true }
```

### Naming

```text
BAD:  process_data, doOrderStuff, OrdersAPI_v2_endpoint_search, get, tool1
GOOD: search_orders, get_order, refund_order, export_order_report
```
`verb_noun`, snake_case, mutually non-confusable, ≤64 chars.

## Cursor install snippets (recap)

```jsonc
// %USERPROFILE%\.cursor\mcp.json — global; or <project>\.cursor\mcp.json — per project
{
  "mcpServers": {
    "workspace-search": {                      // Example 1 (TS, built locally)
      "command": "C:\\Program Files\\nodejs\\node.exe",
      "args": ["C:\\Users\\user\\srv\\workspace-search\\dist\\index.js"],
      "env": { "SEARCH_ROOT": "C:\\Users\\user\\projects" }
    },
    "issue-tracker": {                         // Example 2 (Python via uv)
      "command": "uv",
      "args": ["--directory", "C:\\Users\\user\\srv\\issue-tracker", "run", "issue-tracker"],
      "env": { "TRACKER_TOKEN": "…", "PYTHONUTF8": "1" }
    }
  }
}
```

Verification loop after install: host's MCP panel shows the server green → tools listed → run one read-only tool → check host logs (stderr) if anything is red. Deeper troubleshooting and reload behavior → `mcp-cursor-integration` skill.
