"""P0-3 — `redagraph ask` must present the scanner key to /text-to-cypher.

`_agent_post` (the /graph/exec path) has always sent `X-Internal-Key:
SCANNER_API_KEY`, but `cmd_ask` sent no header at all. That was harmless while
/text-to-cypher was unauthenticated; once it carries `require_internal_auth`
(P0-3) a header-less `ask` returns 401 and the Graph -> Terminal `ask` command
breaks. This pins the header on both paths so they cannot drift apart again.

Run:
    python -m unittest mcp.tests.test_redagraph_ask_auth -v
"""

from __future__ import annotations

import os
import sys
import types
import unittest
from unittest import mock

_mcp_servers_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "servers")
sys.path.insert(0, _mcp_servers_dir)

import redagraph  # noqa: E402


class _Resp:
    status_code = 200

    def json(self):
        return {"cypher": "MATCH (i:IP) RETURN i.address"}

    @property
    def text(self):
        return ""


def _args(question="list ips"):
    return types.SimpleNamespace(question=question, show=False, format="plain")


class RedagraphAskAuthTests(unittest.TestCase):
    def _post_headers(self, env):
        captured = {}

        def fake_post(url, **kw):
            captured["url"] = url
            captured["headers"] = kw.get("headers")
            return _Resp()

        with mock.patch.dict(os.environ, env, clear=False):
            if "SCANNER_API_KEY" not in env:
                os.environ.pop("SCANNER_API_KEY", None)
            with mock.patch.object(redagraph, "_execute", return_value=[]):
                with mock.patch("requests.post", side_effect=fake_post):
                    redagraph.cmd_ask(_args(), "u1", "p1")
        return captured

    def test_ask_sends_the_scanner_key(self):
        captured = self._post_headers({"SCANNER_API_KEY": "scan-tok"})
        self.assertIn("text-to-cypher", captured["url"])
        self.assertEqual(captured["headers"].get("X-Internal-Key"), "scan-tok")

    def test_ask_sends_no_header_when_there_is_no_key(self):
        # A token-less dev stack: the agent's guard fails open there, and
        # sending an empty key would be rejected once a key IS set.
        captured = self._post_headers({})
        self.assertNotIn("X-Internal-Key", captured["headers"] or {})

    def test_ask_never_sends_the_master_key(self):
        # The worker is the least-trusted tier and must not hold INTERNAL_API_KEY.
        captured = self._post_headers(
            {"SCANNER_API_KEY": "scan-tok", "INTERNAL_API_KEY": "master-secret"}
        )
        self.assertNotIn("master-secret", str(captured["headers"]))


if __name__ == "__main__":
    unittest.main()
