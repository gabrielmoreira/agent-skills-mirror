"""
Agent-side (kali-sandbox) capture-proxy routing (mitmproxy integration, Phase 1).

The agent signs an opaque X-Redamon-Ctx tag and passes it to a target-facing MCP
tool as `_redamon_ctx`. This helper decides whether to actually route the tool's
traffic through the capture proxy: only when a tag is present AND the proxy is
reachable (§20.1 fail-open). The kali worker holds NO signing key — it just
carries the token verbatim.

CRITICAL (§20.2, tag-leak guard): the caller adds the proxy flag + the
X-Redamon-Ctx header ONLY in the branch where this returns a URL. On the direct
path the header is never present, so internal identifiers can't leak to a target.

kali-sandbox reaches the (orchestrator- or compose-spawned) proxy at its container
DNS name on pentest-net: redamon-capture-proxy:8888. Overridable via CAPTURE_PROXY_URL.
"""
import os
import socket
from urllib.parse import urlparse

_DEFAULT_PROXY_URL = "http://redamon-capture-proxy:8888"


def proxy_url() -> str:
    return os.environ.get("CAPTURE_PROXY_URL", _DEFAULT_PROXY_URL)


def _reachable(url: str, timeout: float = 1.0) -> bool:
    try:
        p = urlparse(url)
        host = p.hostname or "redamon-capture-proxy"
        port = p.port or 8888
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def agent_capture_routing(ctx_token: str):
    """
    Return (proxy_url, ctx_token) when the tool should route through the capture
    proxy, else (None, None). `ctx_token` is the opaque signed tag from the agent.
    """
    token = (ctx_token or "").strip()
    if not token:
        return (None, None)
    url = proxy_url()
    if not _reachable(url):
        return (None, None)
    return (url, token)
