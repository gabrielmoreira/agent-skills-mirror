"""
Capture-proxy routing tests for execute_playwright (both modes).

Focus on the Tier A fix: self-contained scripts (which bring their own
`sync_playwright()`) previously bypassed capture because the wrapper's proxy=/
extra_http_headers kwargs never applied. `_capture_launch_patch` now forces the
proxy + stamps the X-Redamon-Ctx header via a launch/new_context monkeypatch.

Run: python3 mcp/servers/tests/test_playwright_capture.py
"""
from __future__ import annotations

import ast
import os
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

SERVERS = Path(__file__).resolve().parents[1]
if str(SERVERS) not in sys.path:
    sys.path.insert(0, str(SERVERS))

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

import capture_routing  # noqa: E402
import playwright_server as pw  # noqa: E402

_TEST_URL = "http://redamon-capture-proxy:8888"
_TAG = "eyJhIjoxfQ.c2ln"
_SELF_CONTAINED = "with sync_playwright() as p:\n    page = p.chromium.launch().new_page()\n    page.goto('http://t/')\n"


class _PwBase(unittest.TestCase):
    def setUp(self):
        self._orig_reach = capture_routing._reachable
        self._orig_env = os.environ.get("CAPTURE_PROXY_URL")
        os.environ["CAPTURE_PROXY_URL"] = _TEST_URL

    def tearDown(self):
        capture_routing._reachable = self._orig_reach
        if self._orig_env is None:
            os.environ.pop("CAPTURE_PROXY_URL", None)
        else:
            os.environ["CAPTURE_PROXY_URL"] = self._orig_env

    def _reachable(self, ok):
        capture_routing._reachable = lambda *a, **k: ok


class TestCaptureLaunchPatch(_PwBase):
    def test_empty_when_no_token(self):
        self._reachable(True)
        self.assertEqual(pw._capture_launch_patch(""), "")

    def test_empty_when_unreachable(self):
        self._reachable(False)
        self.assertEqual(pw._capture_launch_patch(_TAG), "")

    def test_patch_is_valid_python_and_complete(self):
        self._reachable(True)
        patch = pw._capture_launch_patch(_TAG)
        self.assertTrue(patch, "expected a non-empty patch when routing")
        ast.parse(patch)  # raises if the generated code is malformed
        # proxy forced + tag stamped
        self.assertIn(_TEST_URL, patch)
        self.assertIn(f'"X-Redamon-Ctx": {_TAG!r}', patch)
        # all three interception points patched
        self.assertIn("BrowserType.launch =", patch)
        self.assertIn("Browser.new_context =", patch)
        self.assertIn("BrowserType.launch_persistent_context =", patch)

    def test_tag_is_header_safe(self):
        # A tag with a space would break the header line; the real tag is b64url.
        self._reachable(True)
        patch = pw._capture_launch_patch(_TAG)
        self.assertNotIn("X-Redamon-Ctx:  ", patch)


class TestCaptureArgsWrappedMode(_PwBase):
    def test_routed_returns_kwargs(self):
        self._reachable(True)
        proxy_kw, hdr_kw = pw._capture_playwright_args(_TAG)
        self.assertIn(_TEST_URL, proxy_kw)
        self.assertIn("proxy=", proxy_kw)
        self.assertIn("X-Redamon-Ctx", hdr_kw)
        self.assertIn(_TAG, hdr_kw)

    def test_direct_returns_empty(self):
        self._reachable(True)
        self.assertEqual(pw._capture_playwright_args(""), ("", ""))
        self._reachable(False)
        self.assertEqual(pw._capture_playwright_args(_TAG), ("", ""))


class TestScriptModeIntegration(_PwBase):
    def _run_capture(self, script, token):
        captured = {}

        def fake_run(final_script, timeout=60):
            captured["script"] = final_script
            return "ok"

        with mock.patch.object(pw, "_run_playwright_script", fake_run):
            pw._execute_script_mode(script, ctx_token=token)
        return captured.get("script", "")

    def test_self_contained_routed_injects_capture_patch(self):
        self._reachable(True)
        final = self._run_capture(_SELF_CONTAINED, _TAG)
        self.assertIn("_pw_orig_launch", final)          # the base _LAUNCH_PATCH
        self.assertIn("X-Redamon-Ctx", final)            # capture patch present
        self.assertIn(_TEST_URL, final)
        self.assertIn(_SELF_CONTAINED.strip(), final)    # user script preserved

    def test_self_contained_direct_no_leak(self):
        self._reachable(False)  # proxy unreachable -> fail open
        final = self._run_capture(_SELF_CONTAINED, _TAG)
        self.assertNotIn("X-Redamon-Ctx", final)
        self.assertNotIn(_TEST_URL, final)

    def test_self_contained_no_token_no_leak(self):
        self._reachable(True)
        final = self._run_capture(_SELF_CONTAINED, "")
        self.assertNotIn("X-Redamon-Ctx", final)


if __name__ == "__main__":
    unittest.main(verbosity=2)
