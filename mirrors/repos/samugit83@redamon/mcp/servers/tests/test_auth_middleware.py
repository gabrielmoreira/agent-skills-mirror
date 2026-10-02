"""Unit tests for the Kali MCP bearer-auth middleware (STRIDE S10).

Pure-ASGI, no FastMCP/uvicorn/network needed. Run:
    python3 -m pytest mcp/servers/tests/test_auth_middleware.py -q
or standalone:
    python3 mcp/servers/tests/test_auth_middleware.py
"""

import asyncio
import importlib.util
import os
import sys
from pathlib import Path

# Load _auth_middleware.py directly (mcp/servers is not an importable package here).
_MW_PATH = Path(__file__).resolve().parents[1] / "_auth_middleware.py"
_spec = importlib.util.spec_from_file_location("_auth_middleware", _MW_PATH)
mw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mw)


def _drive(app, headers=None, scope_type="http"):
    """Run one request through an ASGI app; return (status, downstream_called)."""
    state = {"status": None, "downstream": False, "ws_close": None}

    scope = {"type": scope_type, "headers": headers or []}

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        if message["type"] == "http.response.start":
            state["status"] = message["status"]
        elif message["type"] == "websocket.close":
            state["ws_close"] = message.get("code")

    async def downstream(scope, receive, send):
        state["downstream"] = True
        if scope["type"] == "http":
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"ok"})

    wrapped = mw.BearerAuthASGI(downstream)
    asyncio.run(wrapped(scope, receive, send))
    return state


def _bearer(token):
    return [(b"authorization", f"Bearer {token}".encode())]


def _reset_warn():
    mw._warned_failopen = False


def run():
    results = []

    def check(name, cond):
        results.append((name, bool(cond)))

    # --- token enforced ---
    os.environ["MCP_AUTH_TOKEN"] = "s3cr3t-token"

    st = _drive(None, headers=[])  # no auth header
    check("no header -> 401", st["status"] == 401)
    check("no header -> downstream NOT called", st["downstream"] is False)

    st = _drive(None, headers=_bearer("wrong"))
    check("wrong token -> 401", st["status"] == 401)
    check("wrong token -> downstream NOT called", st["downstream"] is False)

    st = _drive(None, headers=_bearer("s3cr3t-token"))
    check("correct token -> 200", st["status"] == 200)
    check("correct token -> downstream called", st["downstream"] is True)

    # case-insensitive scheme
    st = _drive(None, headers=[(b"authorization", b"bearer s3cr3t-token")])
    check("lowercase 'bearer' scheme accepted", st["status"] == 200)

    # websocket rejection
    st = _drive(None, headers=[], scope_type="websocket")
    check("ws no token -> close 1008", st["ws_close"] == 1008)
    check("ws no token -> downstream NOT called", st["downstream"] is False)

    st = _drive(None, headers=_bearer("s3cr3t-token"), scope_type="websocket")
    check("ws correct token -> downstream called", st["downstream"] is True)

    # --- fail-CLOSED when unset (STRIDE S9 regression) ---
    # Named: test_empty_token_rejects_not_passthrough
    os.environ.pop("MCP_AUTH_TOKEN", None)
    _reset_warn()
    st = _drive(None, headers=[])
    check("token unset -> reject (downstream NOT called)", st["downstream"] is False)
    check("token unset -> 401", st["status"] == 401)
    check("token unset -> warned flag set", mw._warned_failopen is True)

    # unset token on websocket -> close 1008, not pass-through
    _reset_warn()
    st = _drive(None, headers=[], scope_type="websocket")
    check("token unset (ws) -> close 1008", st["ws_close"] == 1008)
    check("token unset (ws) -> downstream NOT called", st["downstream"] is False)

    # empty string treated as unset -> also rejects (not pass-through)
    os.environ["MCP_AUTH_TOKEN"] = ""
    _reset_warn()
    st = _drive(None, headers=[])
    check("empty token -> reject (downstream NOT called)", st["downstream"] is False)
    check("empty token -> 401", st["status"] == 401)

    # lifespan scope always passes through untouched
    _reset_warn()
    os.environ["MCP_AUTH_TOKEN"] = "s3cr3t-token"
    passed = {"v": False}

    async def life_app(scope, receive, send):
        passed["v"] = True

    async def _noop():
        return {}

    asyncio.run(mw.BearerAuthASGI(life_app)({"type": "lifespan"}, _noop, _noop))
    check("lifespan scope passes through", passed["v"] is True)

    os.environ.pop("MCP_AUTH_TOKEN", None)

    # Regression (STRIDE S9): if the SSE app cannot be built on this FastMCP
    # version, serve_sse_with_auth must FAIL CLOSED (raise / crash-loop) instead
    # of falling back to an UNAUTHENTICATED mcp.run().
    class _FakeMcp:
        def __init__(self):
            self.ran = False

        # neither sse_app nor http_app usable -> _build_sse_app raises
        def sse_app(self):
            raise AttributeError("no sse_app")

        def http_app(self, transport=None):
            raise TypeError("no http_app")

        def run(self, transport, host, port):
            self.ran = True

    fake = _FakeMcp()
    raised = False
    try:
        mw.serve_sse_with_auth(fake, host="127.0.0.1", port=0)
    except Exception:
        raised = True
    check("serve raises (fail-closed) when app build fails", raised is True)
    check("serve does NOT fall back to unwrapped mcp.run", fake.ran is False)

    # report
    failed = [n for n, ok in results if not ok]
    for n, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'} {n}")
    print(f"\n{len(results) - len(failed)} passed, {len(failed)} failed")
    return 0 if not failed else 1


# pytest entry points (so `pytest` discovers individual assertions too)
def test_all():
    assert run() == 0


if __name__ == "__main__":
    sys.exit(run())
