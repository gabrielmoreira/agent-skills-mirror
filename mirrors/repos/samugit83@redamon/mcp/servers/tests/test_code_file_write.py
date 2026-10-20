"""
execute_code and proxy_brain write the caller's code to a file VERBATIM and
never through a shell.

Both used to write it with `bash -c "cat << 'DELIM' > file ... DELIM"`: code
holding the delimiter on its own line ended the heredoc early, so the file was
truncated and the rest of the code ran as bash. These tests pin that the file
holds every byte of the code, that the only process started is the interpreter
on that file, and that no shell is ever spawned.

fastmcp is stubbed (identity .tool() decorator, as in test_capture_wiring) so the
tool functions are plain callables; subprocess.run is mocked and snapshots the
file at execution time.

Run: ./redamon.sh test unit   (root-agent section, per-file isolated)
"""
from __future__ import annotations

import os
import sys
import types
import unittest
import uuid
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
            return lambda fn: fn

        def run(self, *a, **k):
            pass

    _fm.FastMCP = _StubMCP
    sys.modules["fastmcp"] = _fm

import network_recon_server as nrs  # noqa: E402

PB_PREAMBLE = "import sys as _s; _s.path.insert(0, '/opt/mcp_servers'); import redamon\n"


class _Done:
    stdout = "ran"
    stderr = ""
    returncode = 0


def _run_capturing(snapshots):
    """subprocess.run stand-in: record argv and the file's bytes at run time."""
    def fake_run(argv, *a, **k):
        snapshots.append((list(argv), Path(argv[-1]).read_text(encoding="utf-8")))
        return _Done()
    return fake_run


class ExecuteCodeWritesVerbatim(unittest.TestCase):
    def setUp(self):
        self.name = f"rdmn_test_{uuid.uuid4().hex}"
        self.path = Path(f"/tmp/{self.name}.py")

    def tearDown(self):
        self.path.unlink(missing_ok=True)

    def _run(self, code):
        snaps = []
        with mock.patch.object(nrs.subprocess, "run", side_effect=_run_capturing(snaps)):
            out = nrs.execute_code(code, language="python", filename=self.name)
        return out, snaps

    def test_old_delimiter_line_is_plain_content(self):
        code = ('print("hello")\nREDAMON_CODE_EOF\nid > /tmp/pwned\n'
                "cat << 'REDAMON_CODE_EOF' > /dev/null")
        out, snaps = self._run(code)
        self.assertEqual(out, "ran")
        self.assertEqual(len(snaps), 1, "only the interpreter may run; no shell write step")
        argv, content = snaps[0]
        self.assertEqual(argv, ["python3", str(self.path)])
        self.assertEqual(content, code + "\n")

    def test_shell_metacharacters_and_unicode_survive(self):
        code = "s = '$(id) `id` \\n \"q\" ünïcødé'\nprint(s)"
        _, snaps = self._run(code)
        self.assertEqual(snaps[0][1], code + "\n")

    def test_no_shell_is_ever_spawned(self):
        snaps = []
        with mock.patch.object(nrs.subprocess, "run", side_effect=_run_capturing(snaps)), \
                mock.patch.object(nrs.subprocess, "Popen") as popen:
            nrs.execute_code("print(1)", language="python", filename=self.name)
        popen.assert_not_called()
        self.assertTrue(all(a[0][0] not in ("bash", "sh") for a in snaps))

    def test_unwritable_path_is_an_error_not_a_crash(self):
        with mock.patch("builtins.open", side_effect=PermissionError("denied")), \
                mock.patch.object(nrs.subprocess, "run") as run:
            out = nrs.execute_code("print(1)", language="python", filename=self.name)
        self.assertTrue(out.startswith("[ERROR] Failed to write code file"), out)
        run.assert_not_called()


class ProxyBrainWritesVerbatim(unittest.TestCase):
    def test_old_delimiter_line_is_plain_content(self):
        code = "print(1)\nREDAMON_PB_EOF\nid > /tmp/pwned\n"
        snaps = []
        with mock.patch.object(nrs.subprocess, "run", side_effect=_run_capturing(snaps)):
            out = nrs.proxy_brain(code, _redamon_ctx="tag")
        self.assertEqual(out, "ran")
        self.assertEqual(len(snaps), 1)
        argv, content = snaps[0]
        self.assertEqual(argv[0], "python3")
        self.assertEqual(content, PB_PREAMBLE + code + "\n")
        self.assertFalse(os.path.exists(argv[1]), "the per-run file must still be removed")


if __name__ == "__main__":
    unittest.main()
