"""
Tier A capture-proxy routing tests for the agent-side (kali-sandbox) MCP tools.

Covers the wiring that routes execute_nuclei / execute_katana / execute_ffuf /
execute_wpscan / execute_arjun through the capture proxy (plan §20.2 no-leak):
when a signed X-Redamon-Ctx tag is present AND the proxy is reachable, the tool
appends the proxy flag + the tag header (or env + merged --headers); on the
direct path NEITHER is present so the tag can never leak to the target.

Runs on the host with `fastmcp` stubbed (identity .tool() decorator) so the tool
functions are plain callables and `subprocess.run` is mocked to capture the exact
command that would be executed.

Run: python3 mcp/servers/tests/test_capture_wiring.py
"""
from __future__ import annotations

import os
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

SERVERS = Path(__file__).resolve().parents[1]
if str(SERVERS) not in sys.path:
    sys.path.insert(0, str(SERVERS))

# --- Stub fastmcp so the server modules import and expose plain tool functions ---
if "fastmcp" not in sys.modules:
    _fm = types.ModuleType("fastmcp")

    class _StubMCP:
        def __init__(self, *a, **k):
            pass

        def tool(self, *a, **k):
            def deco(fn):
                return fn
            return deco

        def run(self, *a, **k):
            pass

    _fm.FastMCP = _StubMCP
    sys.modules["fastmcp"] = _fm

# yaml is a real dep of nuclei_server; stub only if the host lacks it.
try:
    import yaml  # noqa: F401
except Exception:  # pragma: no cover
    _y = types.ModuleType("yaml")
    _y.safe_load = lambda *a, **k: {}
    _y.safe_dump = lambda *a, **k: ""
    _y.YAMLError = Exception
    sys.modules["yaml"] = _y

import capture_routing  # noqa: E402
import network_recon_server as nrs  # noqa: E402
import nuclei_server as ns  # noqa: E402

_TEST_URL = "http://redamon-capture-proxy:8888"
_TAG = "eyJhIjoxfQ.c2ln"  # opaque, header-safe (no spaces)


class _FakeResult:
    def __init__(self):
        self.stdout = ""
        self.stderr = ""
        self.returncode = 0


class _RunSpy:
    """Replacement for subprocess.run that records the command + kwargs."""

    def __init__(self):
        self.cmd = None
        self.kwargs = None

    def __call__(self, cmd, *args, **kwargs):
        self.cmd = list(cmd)
        self.kwargs = kwargs
        return _FakeResult()


class _RoutingTestBase(unittest.TestCase):
    def setUp(self):
        # Force the proxy "reachable" and pin the URL deterministically.
        self._orig_reachable = capture_routing._reachable
        capture_routing._reachable = lambda url, timeout=1.0: True
        self._orig_env = os.environ.get("CAPTURE_PROXY_URL")
        os.environ["CAPTURE_PROXY_URL"] = _TEST_URL

    def tearDown(self):
        capture_routing._reachable = self._orig_reachable
        if self._orig_env is None:
            os.environ.pop("CAPTURE_PROXY_URL", None)
        else:
            os.environ["CAPTURE_PROXY_URL"] = self._orig_env

    def _spy(self, module):
        spy = _RunSpy()
        patcher = mock.patch.object(module.subprocess, "run", spy)
        patcher.start()
        self.addCleanup(patcher.stop)
        return spy

    @staticmethod
    def _pairs(cmd):
        """Return the set of adjacent (flag, value) pairs for easy assertions."""
        return set(zip(cmd, cmd[1:]))

    def assert_no_leak(self, cmd, env=None):
        joined = " ".join(cmd)
        self.assertNotIn("X-Redamon-Ctx", joined,
                         f"tag leaked on direct path: {cmd}")
        self.assertNotIn(_TEST_URL, joined,
                         f"proxy url leaked on direct path: {cmd}")
        if env is not None:
            self.assertNotEqual(env.get("HTTP_PROXY"), _TEST_URL)
            self.assertNotEqual(env.get("HTTPS_PROXY"), _TEST_URL)


class TestAgentCaptureRoutingGate(unittest.TestCase):
    """The pure gate in capture_routing.agent_capture_routing."""

    def setUp(self):
        self._orig = capture_routing._reachable
        os.environ["CAPTURE_PROXY_URL"] = _TEST_URL

    def tearDown(self):
        capture_routing._reachable = self._orig

    def test_empty_token_never_routes(self):
        capture_routing._reachable = lambda *a, **k: True
        self.assertEqual(capture_routing.agent_capture_routing(""), (None, None))
        self.assertEqual(capture_routing.agent_capture_routing("   "), (None, None))

    def test_unreachable_proxy_fails_open(self):
        capture_routing._reachable = lambda *a, **k: False
        self.assertEqual(capture_routing.agent_capture_routing(_TAG), (None, None))

    def test_token_and_reachable_routes(self):
        capture_routing._reachable = lambda *a, **k: True
        url, tok = capture_routing.agent_capture_routing(_TAG)
        self.assertEqual(url, _TEST_URL)
        self.assertEqual(tok, _TAG)


class TestNucleiRouting(_RoutingTestBase):
    def test_routed_appends_proxy_and_header(self):
        spy = self._spy(ns)
        ns.execute_nuclei("-u http://t/ -jsonl", _redamon_ctx=_TAG)
        self.assertIn(("-proxy", _TEST_URL), self._pairs(spy.cmd))
        self.assertIn(("-H", f"X-Redamon-Ctx: {_TAG}"), self._pairs(spy.cmd))
        self.assertEqual(spy.cmd[0], "nuclei")

    def test_direct_path_no_leak(self):
        spy = self._spy(ns)
        ns.execute_nuclei("-u http://t/ -jsonl", _redamon_ctx="")
        self.assert_no_leak(spy.cmd)


class TestKatanaRouting(_RoutingTestBase):
    def test_routed_appends_proxy_and_header_and_keeps_silent(self):
        spy = self._spy(nrs)
        nrs.execute_katana("-u https://t/ -d 2", _redamon_ctx=_TAG)
        self.assertIn(("-proxy", _TEST_URL), self._pairs(spy.cmd))
        self.assertIn(("-H", f"X-Redamon-Ctx: {_TAG}"), self._pairs(spy.cmd))
        self.assertIn("-silent", spy.cmd)  # auto-injected, still present

    def test_direct_path_no_leak(self):
        spy = self._spy(nrs)
        nrs.execute_katana("-u https://t/ -d 2", _redamon_ctx="")
        self.assert_no_leak(spy.cmd)


class TestFfufRouting(_RoutingTestBase):
    def test_routed_appends_x_and_header_and_keeps_noninteractive(self):
        spy = self._spy(nrs)
        nrs.execute_ffuf("-w /tmp/w.txt -u http://t/FUZZ", _redamon_ctx=_TAG)
        self.assertIn(("-x", _TEST_URL), self._pairs(spy.cmd))
        self.assertIn(("-H", f"X-Redamon-Ctx: {_TAG}"), self._pairs(spy.cmd))
        self.assertIn("-noninteractive", spy.cmd)

    def test_direct_path_no_leak(self):
        spy = self._spy(nrs)
        nrs.execute_ffuf("-w /tmp/w.txt -u http://t/FUZZ", _redamon_ctx="")
        self.assert_no_leak(spy.cmd)


class TestWpscanRouting(_RoutingTestBase):
    def test_routed_adds_proxy_and_headers(self):
        spy = self._spy(nrs)
        nrs.execute_wpscan("--url http://t/ --no-banner", _redamon_ctx=_TAG)
        self.assertIn(("--proxy", _TEST_URL), self._pairs(spy.cmd))
        self.assertIn("--headers", spy.cmd)
        hv = spy.cmd[spy.cmd.index("--headers") + 1]
        self.assertIn(f"X-Redamon-Ctx: {_TAG}", hv)

    def test_routed_merges_into_existing_headers(self):
        spy = self._spy(nrs)
        nrs.execute_wpscan(
            "--url http://t/ --headers 'Authorization: Bearer abc'",
            _redamon_ctx=_TAG)
        # exactly one --headers, user header preserved, tag appended
        self.assertEqual(spy.cmd.count("--headers"), 1)
        hv = spy.cmd[spy.cmd.index("--headers") + 1]
        self.assertIn("Authorization: Bearer abc", hv)
        self.assertIn(f"X-Redamon-Ctx: {_TAG}", hv)

    def test_direct_path_no_leak(self):
        spy = self._spy(nrs)
        nrs.execute_wpscan("--url http://t/ --no-banner", _redamon_ctx="")
        self.assert_no_leak(spy.cmd)


class TestArjunRouting(_RoutingTestBase):
    def test_routed_sets_env_proxy_and_headers(self):
        spy = self._spy(nrs)
        nrs.execute_arjun("-u http://t/api", _redamon_ctx=_TAG)
        self.assertEqual(spy.kwargs.get("env", {}).get("HTTP_PROXY"), _TEST_URL)
        self.assertEqual(spy.kwargs.get("env", {}).get("HTTPS_PROXY"), _TEST_URL)
        self.assertIn("--headers", spy.cmd)
        hv = spy.cmd[spy.cmd.index("--headers") + 1]
        self.assertIn(f"X-Redamon-Ctx: {_TAG}", hv)

    def test_routed_merges_into_existing_headers(self):
        spy = self._spy(nrs)
        nrs.execute_arjun(
            "-u http://t/api --headers 'Authorization: Bearer abc'",
            _redamon_ctx=_TAG)
        self.assertEqual(spy.cmd.count("--headers"), 1)
        hv = spy.cmd[spy.cmd.index("--headers") + 1]
        self.assertIn("Authorization: Bearer abc", hv)
        self.assertIn(f"X-Redamon-Ctx: {_TAG}", hv)

    def test_direct_path_no_leak(self):
        spy = self._spy(nrs)
        nrs.execute_arjun("-u http://t/api", _redamon_ctx="")
        self.assert_no_leak(spy.cmd, env=spy.kwargs.get("env", {}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
