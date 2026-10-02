"""Tests for the network_recon_server output-formatting contract.

Pins the FAPP-48 fix: wrappers must distinguish success-with-no-match from
tool failure based on `result.returncode`, rather than collapsing both into
the same "[INFO] No <thing> found" string when stdout happens to be empty.

The helper `_format_subprocess_result` encodes the contract once for the 13
wrappers that subprocess.run-shape; these tests exercise that helper directly.

Run:
    python -m unittest mcp.tests.test_network_recon_wrapper_format -v
"""

from __future__ import annotations

import os
import sys
import unittest
from subprocess import CompletedProcess
from unittest import mock

# Import the helper. The MCP server module lives one dir up from tests/.
_mcp_servers_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "servers",
)
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

from network_recon_server import _format_subprocess_result  # noqa: E402


def _mk(returncode: int, stdout: str = "", stderr: str = "") -> CompletedProcess:
    """Build a CompletedProcess for tests without invoking a real subprocess."""
    return CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


class FormatSubprocessResultTests(unittest.TestCase):
    """Pins the three-way contract: success-with-content / success-no-match /
    failure are surfaced as distinguishable strings."""

    def test_success_with_content_returns_stdout(self):
        result = _mk(0, stdout='{"host": "example.com", "status_code": 200}\n')
        out = _format_subprocess_result(
            result, tool_name="execute_httpx",
            no_match_msg="[INFO] No live hosts found",
        )
        self.assertIn("example.com", out)
        self.assertIn("200", out)
        self.assertNotIn("No live hosts found", out)
        self.assertNotIn("[ERROR]", out)

    def test_success_with_empty_stdout_returns_no_match_msg(self):
        result = _mk(0, stdout="", stderr="[INF] Sending requests to 1 targets\n")
        out = _format_subprocess_result(
            result, tool_name="execute_httpx",
            no_match_msg="[INFO] No live hosts found",
            stderr_filter=lambda l: bool(l) and not l.startswith('[INF]'),
        )
        self.assertEqual(out, "[INFO] No live hosts found")

    def test_failure_returncode_surfaces_error_with_returncode(self):
        """The load-bearing assertion. Pre-fix this would have returned the
        same no_match_msg as the legit no-match case, hiding the failure."""
        result = _mk(
            1, stdout="",
            stderr="httpx: error: invalid target syntax 'not-a-url'\n",
        )
        out = _format_subprocess_result(
            result, tool_name="execute_httpx",
            no_match_msg="[INFO] No live hosts found",
            stderr_filter=lambda l: bool(l) and not l.startswith('[INF]'),
        )
        self.assertIn("[ERROR]", out)
        self.assertIn("execute_httpx", out)
        self.assertIn("returncode=1", out)
        self.assertIn("invalid target syntax", out)
        self.assertNotIn("No live hosts found", out)

    def test_failure_returncode_with_no_stderr(self):
        """Subprocess died silently with no useful stderr — still surface the
        returncode so the LLM doesn't trust an empty payload."""
        result = _mk(139, stdout="", stderr="")
        out = _format_subprocess_result(
            result, tool_name="execute_naabu",
            no_match_msg="[INFO] No open ports found",
        )
        self.assertIn("[ERROR]", out)
        self.assertIn("execute_naabu", out)
        self.assertIn("returncode=139", out)
        # No stderr trim should appear when stderr was empty.
        self.assertNotIn("stderr=", out)

    def test_stderr_filter_keeps_only_non_info_lines(self):
        """Filter callable is applied to stderr before deciding what to keep
        and (on success) what to append to stdout."""
        result = _mk(
            0, stdout="200 http://example.com\n",
            stderr="[INF] Targets loaded: 1\n[ERR] TLS handshake aborted\n",
        )
        out = _format_subprocess_result(
            result, tool_name="execute_httpx",
            no_match_msg="[INFO] No live hosts found",
            stderr_filter=lambda l: bool(l) and not l.startswith('[INF]'),
        )
        self.assertIn("200 http://example.com", out)
        self.assertIn("[STDERR]", out)
        self.assertIn("TLS handshake aborted", out)
        self.assertNotIn("Targets loaded", out)  # [INF] filtered out

    def test_failure_with_filtered_stderr_includes_kept_lines(self):
        """When the run fails, the error string should include only the
        filter-kept stderr (LLM doesn't need to see noise)."""
        result = _mk(
            2, stdout="",
            stderr=(
                "[INF] Loading targets\n"
                "[ERR] cannot resolve example.invalid: NXDOMAIN\n"
                "[INF] Closing\n"
            ),
        )
        out = _format_subprocess_result(
            result, tool_name="execute_httpx",
            no_match_msg="[INFO] No live hosts found",
            stderr_filter=lambda l: bool(l) and not l.startswith('[INF]'),
        )
        self.assertIn("[ERROR]", out)
        self.assertIn("returncode=2", out)
        self.assertIn("NXDOMAIN", out)
        self.assertNotIn("Loading targets", out)
        self.assertNotIn("Closing", out)

    def test_ansi_codes_stripped_from_both_streams(self):
        result = _mk(
            0,
            stdout="\x1b[32m200\x1b[0m http://example.com\n",
            stderr="\x1b[31m[ERR]\x1b[0m something\n",
        )
        out = _format_subprocess_result(
            result, tool_name="execute_httpx",
            no_match_msg="[INFO] No live hosts found",
        )
        self.assertIn("200 http://example.com", out)
        self.assertNotIn("\x1b[", out)

    def test_default_stderr_filter_keeps_non_empty(self):
        result = _mk(0, stdout="ok", stderr="warn1\n\nwarn2\n")
        out = _format_subprocess_result(
            result, tool_name="kali_shell",
            no_match_msg="[INFO] Command completed with no output",
        )
        self.assertIn("warn1", out)
        self.assertIn("warn2", out)

    def test_long_stderr_trimmed_to_2000_chars_in_error_path(self):
        long_stderr = "panic\n" + ("x" * 5000)
        result = _mk(1, stdout="", stderr=long_stderr)
        out = _format_subprocess_result(
            result, tool_name="execute_curl",
            no_match_msg="[INFO] No response received",
        )
        self.assertIn("[ERROR]", out)
        self.assertIn("returncode=1", out)
        # Trim cap is 2000 chars after the "stderr=" label.
        stderr_section = out.split("stderr=", 1)[1] if "stderr=" in out else ""
        self.assertLessEqual(len(stderr_section), 2000)


if __name__ == "__main__":
    unittest.main()
