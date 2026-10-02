"""End-to-end integration proof for the MCP bearer-auth wrapper (STRIDE S10).

Stands up a REAL FastMCP SSE server wrapped in BearerAuthASGI on a uvicorn
loopback port, then drives it with the SAME client the agent uses
(langchain_mcp_adapters.MultiServerMCPClient, transport="sse"). Proves the whole
round-trip an agent tool call depends on:

  * with the correct token  -> get_tools() (SSE GET) AND a tool call (message
    POST) both succeed — i.e. the token reaches BOTH endpoints;
  * without the token        -> rejected.

This is the check unit tests can't give: that the client actually forwards the
Authorization header to the message POST, not just the SSE GET, and that the
sse_app->http_app(transport="sse") fallback yields a working server on the
installed FastMCP.

Needs fastmcp + uvicorn + httpx + langchain-mcp-adapters (present in the agent /
kali runtime). SKIPS cleanly on a bare host. Run:
    python3 mcp/servers/tests/test_sse_auth_integration.py
"""

import asyncio
import importlib.util
import os
import threading
import time
from pathlib import Path


def _load_mw():
    p = Path(__file__).resolve().parents[1] / "_auth_middleware.py"
    spec = importlib.util.spec_from_file_location("_auth_middleware", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    try:
        import uvicorn  # noqa: F401
        from fastmcp import FastMCP
        from langchain_mcp_adapters.client import MultiServerMCPClient  # noqa: F401
    except Exception as exc:
        print(f"SKIP: integration deps unavailable ({exc})")
        return 0

    import uvicorn
    from fastmcp import FastMCP
    from langchain_mcp_adapters.client import MultiServerMCPClient

    mw = _load_mw()
    os.environ["MCP_AUTH_TOKEN"] = "integration-token"

    mcp = FastMCP("probe")

    @mcp.tool
    def ping() -> str:
        return "pong"

    app = mw.BearerAuthASGI(mw._build_sse_app(mcp))
    # port 0 -> let the OS pick; then read it back.
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8791, log_level="error"))
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(1.5)

    results = []

    async def drive():
        base = "http://127.0.0.1:8791/sse"  # exact agent form: no trailing slash
        good = MultiServerMCPClient(
            {"probe": {"url": base, "transport": "sse",
                       "headers": {"Authorization": "Bearer integration-token"}}}
        )
        tools = await asyncio.wait_for(good.get_tools(), timeout=10)
        results.append(("get_tools with token (SSE GET)", any(t.name == "ping" for t in tools)))
        out = await asyncio.wait_for(tools[0].ainvoke({}), timeout=10)
        text = str(out)
        results.append(("tool call with token (message POST)", "pong" in text))

        bad = MultiServerMCPClient({"probe": {"url": base, "transport": "sse"}})
        try:
            await asyncio.wait_for(bad.get_tools(), timeout=8)
            results.append(("no-token rejected", False))
        except Exception:
            results.append(("no-token rejected", True))

    asyncio.run(drive())
    server.should_exit = True
    time.sleep(0.3)

    failed = [n for n, ok in results if not ok]
    for n, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'} {n}")
    print(f"\n{len(results) - len(failed)} passed, {len(failed)} failed")
    return 0 if not failed else 1


def test_all():
    assert main() == 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
