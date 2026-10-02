"""
Unit test for SessionProgressHandler._send_json's client-disconnect guard (issue
#159): a client that polls the MSF progress/session endpoint and hangs up
mid-response must NOT raise a BrokenPipe that cascades into do_GET's error handler
and a noisy double traceback in the kali-sandbox logs.

metasploit_server imports fastmcp (heavy) only for the MCP tool surface, and its
server never starts on import (guarded by __main__). We stub fastmcp and load the
module by path, then exercise the pure HTTP handler method in isolation.

Run: python3 -m pytest mcp/servers/tests/test_metasploit_progress.py -q
  or python3 mcp/servers/tests/test_metasploit_progress.py
"""
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

# Stub fastmcp so `from fastmcp import FastMCP` + module-level `mcp = FastMCP(...)`
# succeed without the real dependency.
sys.modules.setdefault("fastmcp", mock.MagicMock())

_PATH = Path(__file__).resolve().parents[1] / "metasploit_server.py"
_spec = importlib.util.spec_from_file_location("metasploit_server", _PATH)
msf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(msf)

Handler = msf.SessionProgressHandler


def _handler(write_side_effect=None):
    """A SessionProgressHandler without running BaseHTTPRequestHandler.__init__ (no
    real socket/request); the HTTP header helpers are stubbed so we isolate the guard
    around the body write."""
    h = Handler.__new__(Handler)
    h.wfile = mock.Mock()
    if write_side_effect:
        h.wfile.write.side_effect = write_side_effect
    h.send_response = mock.Mock()
    h.send_header = mock.Mock()
    h.end_headers = mock.Mock()
    return h


class TestSendJsonBrokenPipeGuard(unittest.TestCase):
    def test_happy_path_writes_payload(self):
        h = _handler()
        h._send_json(200, {"ok": True})
        h.wfile.write.assert_called_once()
        self.assertEqual(h.wfile.write.call_args[0][0], b'{"ok": true}')

    def test_broken_pipe_is_swallowed(self):
        h = _handler(write_side_effect=BrokenPipeError(32, "Broken pipe"))
        # Must NOT raise: the pre-fix code let this bubble up, so do_GET then tried to
        # write a 500 to the same dead socket -> the double BrokenPipe traceback.
        h._send_json(200, {"progress": []})

    def test_connection_reset_is_swallowed(self):
        h = _handler(write_side_effect=ConnectionResetError("reset"))
        h._send_json(500, {"error": "boom"})

    def test_serialization_error_still_raises(self):
        # A non-serialisable payload is a real bug, not a disconnect -> must surface,
        # not be swallowed by the pipe guard (json.dumps runs before the socket try).
        h = _handler()
        with self.assertRaises(TypeError):
            h._send_json(200, {"bad": object()})


class TestSendStatusBrokenPipeGuard(unittest.TestCase):
    """The body-less 404/204 paths (do_GET/POST/DELETE/OPTIONS else-branches) must
    also swallow a client disconnect, not just _send_json."""

    def _status_handler(self, side_effect=None):
        h = Handler.__new__(Handler)
        h.send_response = mock.Mock()
        h.end_headers = mock.Mock(side_effect=side_effect)
        return h

    def test_happy_path(self):
        h = self._status_handler()
        h._send_status(404)
        h.send_response.assert_called_once_with(404)
        h.end_headers.assert_called_once()

    def test_broken_pipe_is_swallowed(self):
        h = self._status_handler(side_effect=BrokenPipeError(32, "Broken pipe"))
        h._send_status(404)  # must NOT raise

    def test_connection_reset_is_swallowed(self):
        h = self._status_handler(side_effect=ConnectionResetError("reset"))
        h._send_status(204)  # must NOT raise


if __name__ == "__main__":
    unittest.main()
