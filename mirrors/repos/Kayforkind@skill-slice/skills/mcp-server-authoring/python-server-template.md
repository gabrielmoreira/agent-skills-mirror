# Python MCP Server Template

Production patterns for the official `mcp` Python SDK using the **FastMCP** API (decorators + type hints → schemas). Pair with `reference.md` for protocol semantics and `security-checklist.md` before shipping.

## 1. Project layout & pyproject.toml

```
my-mcp-server/
├── src/my_mcp_server/
│   ├── __init__.py
│   ├── server.py        # FastMCP instance + registrations (transport-agnostic)
│   ├── __main__.py      # python -m my_mcp_server -> stdio
│   └── clients.py       # domain/API clients, config
├── tests/test_server.py
├── pyproject.toml
└── README.md
```

```toml
[project]
name = "my-mcp-server"
version = "1.0.0"
requires-python = ">=3.10"
dependencies = ["mcp>=1.0", "httpx>=0.27", "pydantic>=2"]

[project.scripts]
my-mcp-server = "my_mcp_server.server:main"     # enables `uvx my-mcp-server`

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[dependency-groups]
dev = ["pytest>=8", "pytest-asyncio>=0.24", "anyio>=4"]
```

Use `uv` throughout: `uv sync`, `uv run my-mcp-server`, `uv run pytest`. It gives hosts a deterministic launch command that doesn't depend on an activated venv.

## 2. Core server (`server.py`)

```python
from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field
from mcp.server.fastmcp import Context, FastMCP

# --- Logging: stderr ONLY. print() is forbidden in stdio servers. ----------
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("my_mcp_server")

# --- Typed lifespan: connections start once, close cleanly -----------------
@dataclass
class AppContext:
    orders: "OrdersClient"

@asynccontextmanager
async def lifespan(_: FastMCP) -> AsyncIterator[AppContext]:
    orders = await OrdersClient.connect()          # lazy/fast; heavy warmup on first call
    try:
        yield AppContext(orders=orders)
    finally:
        await orders.close()

mcp = FastMCP(
    "my-mcp-server",
    lifespan=lifespan,
    instructions=(
        "Order-management tools. Prefer search_orders to locate ids, "
        "then get_order for detail. All times UTC."
    ),
)

# --- TOOL: read-only, paginated --------------------------------------------
@mcp.tool(
    annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False}
)
async def search_orders(
    query: str = Field(description="Free-text match on customer name or order id.",
                       min_length=1, max_length=200),
    status: Literal["open", "shipped", "cancelled"] | None = Field(
        default=None, description="Filter by lifecycle status."),
    cursor: str | None = Field(default=None, description="Opaque cursor from a previous page."),
    ctx: Context = None,
) -> str:
    """Search orders by free text and optional status. Returns at most 20
    summaries per page; pass the returned cursor to page. Use get_order for
    full line-item detail. Read-only."""
    app: AppContext = ctx.request_context.lifespan_context
    page = await app.orders.search(query=query, status=status, cursor=cursor, limit=20)
    if not page.items:
        return f'No orders matched "{query}".'
    lines = [f"{o.id}  {o.customer}  {o.status}  ${o.total_usd}" for o in page.items]
    if page.next_cursor:
        lines.append(f"\n[more results: cursor={page.next_cursor}]")
    return "\n".join(lines)

# --- TOOL: mutating with structured output ---------------------------------
class RefundResult(BaseModel):
    """Return type => FastMCP derives outputSchema + emits structuredContent."""
    refund_id: str
    order_id: str
    amount_usd: float
    status: Literal["pending", "completed"]

@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": True,
                 "idempotentHint": True, "openWorldHint": True}
)
async def refund_order(
    order_id: str = Field(description="Order id, e.g. ORD-1042.", pattern=r"^ORD-\d+$"),
    idempotency_key: str = Field(description="Client-generated UUID; same key = same refund."),
    amount_usd: float | None = Field(default=None, gt=0,
                                     description="Partial refund amount. Omit for full refund."),
    ctx: Context = None,
) -> RefundResult:
    """Issue a full or partial refund for an order. Irreversible once completed.
    Reuse the same idempotency_key to retry safely; a new key issues a second refund."""
    app: AppContext = ctx.request_context.lifespan_context
    await ctx.info(f"refund requested for {order_id}")          # MCP logging -> host UI
    r = await app.orders.refund(order_id, amount_usd=amount_usd, key=idempotency_key)
    return RefundResult(**r)

# --- RESOURCE + PROMPT -------------------------------------------------------
@mcp.resource("orders://{order_id}", mime_type="application/json",
              description="Full JSON record for one order.")
async def order_record(order_id: str) -> str:
    client = await OrdersClient.connect()
    return (await client.get(order_id)).model_dump_json(indent=2)

@mcp.prompt(description="Structured workflow for investigating a problem order.")
def triage_order_issue(order_id: str) -> str:
    return (f"Investigate order {order_id}: fetch it with get_order, "
            f"check refund history, summarize root cause and next action.")

# --- entry point -------------------------------------------------------------
def main() -> None:
    mcp.run()                     # stdio by default

if __name__ == "__main__":
    main()
```

How schemas are derived: **type hints + `Field(...)` → inputSchema; the docstring → description; a Pydantic/TypedDict/dataclass return type → outputSchema + structuredContent** (a plain `str` return becomes a text block). One source of truth — keep hints and docstrings honest, they are your descriptor.

## 3. Error handling

```python
from mcp.server.fastmcp.exceptions import ToolError

@mcp.tool()
async def get_order(order_id: str, ctx: Context = None) -> str:
    """Fetch one order's full record as JSON."""
    app = ctx.request_context.lifespan_context
    try:
        order = await app.orders.get(order_id)
    except OrderNotFound:
        # ToolError message reaches the model verbatim (isError=True). Make it actionable.
        raise ToolError(
            f"Order {order_id} not found. Verify the id via search_orders before retrying."
        )
    except UpstreamRateLimit as e:
        raise ToolError(f"Rate-limited by upstream API. Retry after {e.retry_at.isoformat()}.")
    except Exception:
        log.exception("get_order failed")               # detail -> stderr only
        raise ToolError("Internal error; logged. Do not retry with identical input.")
    return order.model_dump_json(indent=2)
```

Rules: `ToolError` (or any raised exception — FastMCP converts it, but generic tracebacks can leak paths, so catch broad and re-raise `ToolError` with a clean message) → `isError: true` execution error. Schema violations are rejected by the SDK **before** your function runs — don't re-validate what the signature already enforces; do validate semantics (existence, permissions, ranges across fields).

## 4. Logging without breaking stdio

Three sinks; only these:

```python
log.info("search q=%s", query[:40])          # 1) stderr via logging.basicConfig above
await ctx.info("refund issued")              # 2) MCP notifications/message -> host UI
await ctx.debug(...) / ctx.warning(...) / ctx.error(...)
# 3) NOTHING. Never print(). Audit deps too (tqdm, warnings, banners).
```

stdout-cleanliness smoke test:

```powershell
# PowerShell — every stdout line must parse as JSON:
$p = Start-Process -FilePath uv -ArgumentList "run","my-mcp-server" `
     -RedirectStandardOutput out.jsonl -RedirectStandardError err.log -PassThru -NoNewWindow
Start-Sleep 2; Stop-Process $p.Id
Get-Content out.jsonl | ForEach-Object { $_ | ConvertFrom-Json | Out-Null }
```

Common Windows gotcha: cp1252 console encoding mangles non-ASCII JSON — always launch with `PYTHONUTF8=1` (see §8).

## 5. Progress, cancellation, long work

```python
import anyio

@mcp.tool()
async def export_report(month: str, ctx: Context = None) -> str:
    """Export a monthly report. Reports progress; supports cancellation."""
    total = await count_rows(month)
    done = 0
    for chunk_start in range(0, total, 500):
        await export_chunk(month, chunk_start, 500)     # keep awaits granular ->
        done = min(chunk_start + 500, total)            # cancellation lands between them
        await ctx.report_progress(progress=done, total=total,
                                  message=f"exported {done}/{total}")
    return f"Export complete: {total} rows -> exports/{month}.csv"
```

- `ctx.report_progress` no-ops harmlessly if the client sent no `progressToken`.
- Cancellation arrives as task cancellation in anyio — it propagates at `await` points; use `finally:` blocks for cleanup rather than checking flags.
- **Never** call blocking/sync I/O (`requests`, `time.sleep`, heavy pandas) directly in an async tool — it freezes the whole server. Wrap: `await anyio.to_thread.run_sync(blocking_fn)`. If wall time can exceed ~60s, use the job pattern (`start_export` returns a job id; `get_export_status` polls) — `reference.md §5`.

## 6. Streamable HTTP variant

```python
# Same registrations; different run mode.
mcp = FastMCP("my-mcp-server", lifespan=lifespan, host="127.0.0.1", port=8000,
              stateless_http=False)   # True = no per-session state; easiest to scale

def main_http() -> None:
    mcp.run(transport="streamable-http")        # serves on /mcp

# Or mount inside an existing ASGI app:
# from starlette.applications import Starlette
# from starlette.routing import Mount
# app = Starlette(routes=[Mount("/", app=mcp.streamable_http_app())],
#                 lifespan=lambda app: mcp.session_manager.run())
# uvicorn my_mcp_server.server:app --host 127.0.0.1 --port 8000
```

Bind `127.0.0.1` unless you have TLS + token auth in front; validate `Origin`; see `security-checklist.md §HTTP`. Prefer `stateless_http=True` for multi-replica deployments (no sticky sessions), stateful for single-instance with subscriptions.

## 7. Testing

```python
# tests/test_server.py
import pytest
from mcp.shared.memory import create_connected_server_and_client_session
from my_mcp_server.server import mcp

pytestmark = pytest.mark.anyio

async def test_descriptors_are_well_formed():
    async with create_connected_server_and_client_session(mcp._mcp_server) as client:
        tools = (await client.list_tools()).tools
        for t in tools:
            assert t.name.isidentifier() or "-" in t.name       # naming sanity
            assert t.description and len(t.description) > 30
            assert t.inputSchema["type"] == "object"

async def test_refund_bad_id_is_actionable_error():
    async with create_connected_server_and_client_session(mcp._mcp_server) as client:
        res = await client.call_tool("refund_order",
            {"order_id": "ORD-999999", "idempotency_key": "6f6e…"})
        assert res.isError
        assert "search_orders" in res.content[0].text           # tells model what to do
```

Interactive: `npx @modelcontextprotocol/inspector uv run my-mcp-server` — exercise happy path, schema-invalid input (protocol error), semantic failure (`isError`), cursor round-trip. Also do one **real-host** smoke test; Inspector is more forgiving than hosts about stdout noise.

## 8. Packaging & host install (Windows-safe)

```jsonc
// %USERPROFILE%\.cursor\mcp.json  (or <project>\.cursor\mcp.json)
{
  "mcpServers": {
    // Preferred: uv with explicit project dir — no venv activation, no PATH luck
    "my-mcp-server": {
      "command": "uv",
      "args": ["--directory", "C:\\Users\\user\\srv\\my-mcp-server", "run", "my-mcp-server"],
      "env": { "ORDERS_API_KEY": "…", "PYTHONUTF8": "1" }
    },
    // uvx from a published package:
    "my-mcp-server-uvx": {
      "command": "cmd",
      "args": ["/c", "uvx", "my-mcp-server"],
      "env": { "ORDERS_API_KEY": "…", "PYTHONUTF8": "1" }
    },
    // Absolute interpreter (most deterministic):
    "my-mcp-server-py": {
      "command": "C:\\Users\\user\\srv\\my-mcp-server\\.venv\\Scripts\\python.exe",
      "args": ["-m", "my_mcp_server"],
      "env": { "ORDERS_API_KEY": "…", "PYTHONUTF8": "1" }
    }
  }
}
```

Pitfalls: GUI hosts don't see your conda/venv/nvm PATH — absolute paths win; `uv`/`uvx` may need the `cmd /c` wrapper if the host can't resolve `.exe` shims; always set `PYTHONUTF8=1`. Full Cursor wiring → `mcp-cursor-integration` skill.
