"""
PersistentMsfConsole.interact_session must not let a session command reach the
msfconsole prompt as a second line.

msfconsole reads its stdin line by line and runs any line it does not recognise
as a LOCAL shell command (AllowCommandPassthru defaults on), as root in the
kali-sandbox. The operator UI sends one command per request through
/sessions/{id}/interact; a newline in it used to end the `sessions -c "..."`
line and run the rest in the sandbox instead of on the target. Unknown session
ids fall back to the shell path, so this needed no live session at all.

metasploit_server imports fastmcp only for its tool surface and starts nothing
on import or construction; fastmcp is stubbed and the msfconsole process faked.

Run: ./redamon.sh test unit   (root-agent section, per-file isolated)
"""
import importlib.util
import shlex
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.modules.setdefault("fastmcp", mock.MagicMock())

_PATH = Path(__file__).resolve().parents[1] / "metasploit_server.py"
_spec = importlib.util.spec_from_file_location("metasploit_server", _PATH)
msf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(msf)


def _console(session_type="shell"):
    """A console whose msfconsole echoes the command, prints one line, then the
    prompt, so the shell path's read loop ends at once."""
    c = msf.PersistentMsfConsole()
    c._session_details = [{"id": 1, "type": session_type}]
    c.process = mock.Mock()

    def _echo(line):
        c.output_queue.put(line)
        c.output_queue.put("target-output")
        c.output_queue.put("msf6 > ")

    c.process.stdin.write.side_effect = _echo
    c._quick_execute = mock.Mock(return_value="")
    return c


INJECTIONS = [
    "x\nid > /workspace/exfil/id.txt",
    "x\r\nid",
    "x\rid",
    "id\x00",
    "x\x1b[A",
    "x\x03",
    "x\x1a",
    "x\x7f",
]


class ControlCharactersAreRefused(unittest.TestCase):
    def test_shell_path_writes_nothing_to_msfconsole(self):
        for cmd in INJECTIONS:
            with self.subTest(cmd=cmd):
                c = _console("shell")
                out = c.interact_session(1, cmd)
                self.assertTrue(out["output"].startswith("[ERROR]"), out)
                c.process.stdin.write.assert_not_called()
                c._quick_execute.assert_not_called()

    def test_meterpreter_path_writes_nothing_to_msfconsole(self):
        # "x\nbackground\nid" would leave the session and run `id` at msf>.
        for cmd in INJECTIONS + ["sysinfo\nbackground\nid"]:
            with self.subTest(cmd=cmd):
                c = _console("meterpreter")
                out = c.interact_session(1, cmd)
                self.assertTrue(out["output"].startswith("[ERROR]"), out)
                c._quick_execute.assert_not_called()
                c.process.stdin.write.assert_not_called()

    def test_unknown_session_id_is_refused_too(self):
        # The cache-miss path defaults to "shell"; the refusal comes first.
        c = _console("shell")
        c._session_details = []
        out = c.interact_session(999, "x\nid")
        self.assertTrue(out["output"].startswith("[ERROR]"), out)
        c._quick_execute.assert_not_called()
        c.process.stdin.write.assert_not_called()

    def test_refusal_does_not_hold_the_console_lock(self):
        c = _console("shell")
        c.interact_session(1, "x\nid")
        self.assertTrue(c.lock.acquire(blocking=False))
        c.lock.release()


class ShellPathQuoting(unittest.TestCase):
    """msfconsole splits the line with Shellwords; POSIX shlex agrees with it for
    every escape the console emits (\\\\ and \\"), so a round-trip proves the
    target receives exactly the operator's command as ONE argument."""

    COMMANDS = [
        "id",
        'echo "hi there"',
        "x\\",
        'a\\"; id; echo "',
        "$(id) and `id`",
        "dir C:\\Windows\\System32",
        "it's",
        "printf 'a\\tb'",
        "cut -f1\t-d:",
    ]

    def test_single_line_round_trips_as_one_argument(self):
        for cmd in self.COMMANDS:
            with self.subTest(cmd=cmd):
                c = _console("shell")
                out = c.interact_session(1, cmd)
                c.process.stdin.write.assert_called_once()
                line = c.process.stdin.write.call_args[0][0]
                self.assertTrue(line.endswith(" -i 1\n"), line)
                self.assertEqual(line.count("\n"), 1)
                self.assertEqual(shlex.split(line), ["sessions", "-c", cmd, "-i", "1"])
                self.assertEqual(out, {"busy": False, "output": "target-output"})


class HttpHandlerRejectsNonStringCommand(unittest.TestCase):
    def _post(self, body):
        h = msf.SessionProgressHandler.__new__(msf.SessionProgressHandler)
        h.path = "/sessions/1/interact"
        h._read_json_body = mock.Mock(return_value=body)
        h._send_json = mock.Mock()
        console = mock.Mock()
        with mock.patch.object(msf, "get_msf_console", return_value=console):
            h.do_POST()
        return h._send_json.call_args[0], console

    def test_list_command_is_a_400_not_a_crash(self):
        (status, _), console = self._post({"command": ["id"]})
        self.assertEqual(status, 400)
        console.interact_session.assert_not_called()

    def test_string_command_is_forwarded(self):
        (status, _), console = self._post({"command": "id"})
        self.assertEqual(status, 200)
        console.interact_session.assert_called_once_with(1, "id")


if __name__ == "__main__":
    unittest.main()
