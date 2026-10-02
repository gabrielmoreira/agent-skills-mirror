"""execute_curl must disable curl's URL globbing (--globoff / -g).

curl treats `{ } [ ]` as URL-glob metacharacters by default, so an SSTI /
template / array payload like `{{7*7}}`, `${7*7}`, or `id[0]=` makes curl reject
the URL with error 3 (CURLE_URL_MALFORMAT) BEFORE any request is sent - the probe
never leaves the harness (observed live: 80+ curl-error-3 failures on the SSTI
target). `_globoff_args` forces globbing off so those payloads reach the target.

Run:
    python -m unittest mcp.tests.test_curl_globoff -v
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest import mock

_mcp_servers_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "servers")
sys.path.insert(0, _mcp_servers_dir)

# fastmcp only ships inside the kali-sandbox image; stub it so the server module
# imports for a pure-logic unit test (identity @mcp.tool() decorator).
if "fastmcp" not in sys.modules:
    class _FakeMCP:
        def __init__(self, *a, **kw):
            pass
        def tool(self, *a, **kw):
            def _identity(fn):
                return fn
            return _identity
        def __getattr__(self, name):
            return mock.MagicMock()
    _fastmcp_mod = mock.MagicMock()
    _fastmcp_mod.FastMCP = _FakeMCP
    sys.modules["fastmcp"] = _fastmcp_mod

from network_recon_server import _globoff_args  # noqa: E402


class GloboffArgsLogicTests(unittest.TestCase):
    def test_prepends_g_to_brace_payload(self):
        out = _globoff_args(["-s", "http://t/?p={{7*7}}"])
        self.assertEqual(out, ["-g", "-s", "http://t/?p={{7*7}}"])

    def test_prepends_g_to_bracket_payload(self):
        self.assertEqual(_globoff_args(["http://t/?id[0]=1"]),
                         ["-g", "http://t/?id[0]=1"])

    def test_prepends_g_to_dollar_template_payload(self):
        self.assertEqual(_globoff_args(["http://t/?p=${7*7}"]),
                         ["-g", "http://t/?p=${7*7}"])

    def test_prepends_g_to_plain_args(self):
        # always on; harmless and simpler than sniffing for glob chars
        self.assertEqual(_globoff_args(["-s", "http://t/"]),
                         ["-g", "-s", "http://t/"])

    def test_empty_args(self):
        self.assertEqual(_globoff_args([]), ["-g"])

    def test_g_precedes_the_url(self):
        out = _globoff_args(["http://t/?p={{7*7}}"])
        self.assertLess(out.index("-g"), out.index("http://t/?p={{7*7}}"))

    # --- idempotency: never double the flag when the caller already set it -----
    def test_no_double_when_short_g_present(self):
        self.assertEqual(_globoff_args(["-g", "http://t/"]), ["-g", "http://t/"])

    def test_no_double_when_long_globoff_present(self):
        self.assertEqual(_globoff_args(["--globoff", "http://t/"]),
                         ["--globoff", "http://t/"])

    def test_no_double_when_g_is_midway(self):
        self.assertEqual(_globoff_args(["-s", "-g", "http://t/"]),
                         ["-s", "-g", "http://t/"])

    def test_applying_twice_is_stable(self):
        once = _globoff_args(["http://t/?p={{7}}"])
        self.assertEqual(_globoff_args(once), once)

    def test_input_not_mutated(self):
        src = ["-s", "http://t/"]
        _globoff_args(src)
        self.assertEqual(src, ["-s", "http://t/"])  # returns a new list


class ExecuteCurlWiringTest(unittest.TestCase):
    """Pin that execute_curl actually routes its args through _globoff_args."""

    def test_execute_curl_calls_globoff(self):
        with open(os.path.join(_mcp_servers_dir, "network_recon_server.py")) as f:
            src = f.read()
        # the arg build inside execute_curl must go through the globoff helper
        self.assertIn("_globoff_args(shlex.split(args))", src)


class ExecuteCurlInvocationTest(unittest.TestCase):
    """End-to-end (best-effort): the tool invokes `curl -g ...`. Skips gracefully
    if the decorated tool's raw fn or its runtime deps aren't accessible."""

    def test_curl_invoked_with_globoff(self):
        from unittest.mock import patch
        from subprocess import CompletedProcess
        import network_recon_server as n
        raw = getattr(n.execute_curl, "fn", None) or getattr(n.execute_curl, "__wrapped__", None)
        if raw is None or not callable(raw):
            self.skipTest("decorated tool fn not accessible in this fastmcp version")
        try:
            with patch.object(n.subprocess, "run") as mrun:
                mrun.return_value = CompletedProcess(args=[], returncode=0, stdout="ok", stderr="")
                raw("-s 'http://t/?p={{7*7}}'")
        except Exception as e:                       # runtime dep (capture_routing) etc.
            self.skipTest(f"execute_curl runtime path unavailable: {e}")
        argv = mrun.call_args[0][0]
        self.assertEqual(argv[0], "curl")
        self.assertIn("-g", argv)
        self.assertIn("http://t/?p={{7*7}}", argv)
        self.assertLess(argv.index("-g"), argv.index("http://t/?p={{7*7}}"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
