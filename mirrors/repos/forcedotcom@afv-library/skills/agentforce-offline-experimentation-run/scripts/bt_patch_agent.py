#!/usr/bin/env python3
"""Make a scored patch's edit ops in the .agent file: the version that ships is the one scored.

    python3 scripts/bt_patch_agent.py AGENT PATCH --out FILE [--overwrite]

AGENT is an .agent file, or a retrieved bundle dir holding one. PATCH is the patch file the replay
scored (sfap_replay.py --patch). The edited .agent goes to --out, never over AGENT, and the change
is printed as a unified diff. Only the lines an edit changes are rewritten, at their block's
indent and in its | style.

An op is refused, and nothing is written, when its edit in the .agent could differ from the edit
the replay made to the requests, or cannot be written as intended (references/patching.md, "The
same edit in the .agent"). Exit 0: written. Exit 2: refused, or a file could not be read or
written.
"""

import argparse
import difflib
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from btlib import agentpatch  # noqa: E402
from btlib import patch as patchlib  # noqa: E402
from btlib.agentsrc import AgentSourceError, agent_file  # noqa: E402
from btlib.redact import redact  # noqa: E402


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("agent", help=".agent file, or a bundle dir holding one")
    p.add_argument("patch", help="the patch file the replay scored (bt.patch/1)")
    p.add_argument("--out", metavar="FILE", required=True, help="where to write the edited .agent (not AGENT)")
    p.add_argument("--overwrite", action="store_true", help="replace --out if it exists")
    return p.parse_args(argv)


def same_file(a, b):
    return os.path.realpath(a) == os.path.realpath(b) or (os.path.exists(b) and os.path.samefile(a, b))


def read_text(path):
    """The text as it is: universal newlines would turn CR LF into LF on every line."""
    with open(path, encoding="utf-8", newline="") as f:
        try:
            return f.read()
        except UnicodeDecodeError:
            raise AgentSourceError(f"{path}: not UTF-8 text")


def load_ops(path):
    try:
        return patchlib.load_patch(path)
    except UnicodeDecodeError:
        raise patchlib.PatchError("not UTF-8 text")


def summary_lines(report):
    out = []
    for r in report:
        n = len(r["edits"])
        out.append(f"op {r['id']} ({r['op']} {r['target']}): " + (f"{n} edit(s)" if n else "no change"))
    return out


def main(argv=None):
    args = parse_args(argv)
    try:
        path = agent_file(args.agent)
        if same_file(path, args.out):
            print(f"error: --out is the input {path}: write the edited agent to another file", file=sys.stderr)
            return 2
        if os.path.exists(args.out) and not args.overwrite:
            print(f"error: {args.out} exists (--overwrite replaces it)", file=sys.stderr)
            return 2
        try:
            ops = load_ops(args.patch)
        except patchlib.PatchError as e:
            print(f"error: {args.patch}: {redact(str(e))}", file=sys.stderr)
            return 2
        text = read_text(path)
        new, report = agentpatch.patch_agent(text, ops, path)
        with open(args.out, "w" if args.overwrite else "x", encoding="utf-8", newline="") as f:
            f.write(new)
    except agentpatch.AgentPatchError as e:
        print(f"error: refused ({e.reason}): {redact(str(e))}; nothing written", file=sys.stderr)
        return 2
    except AgentSourceError as e:
        print(f"error: {redact(str(e))}", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"error: {e.filename or ''}: {e.strerror or e}", file=sys.stderr)
        return 2
    except Exception as e:  # a bug: say where, never a half-checked file
        frame = traceback.extract_tb(e.__traceback__)[-1]
        print(f"error: bt_patch_agent failed ({type(e).__name__} at {os.path.basename(frame.filename)}:{frame.lineno})",
              file=sys.stderr)
        return 2
    for line in difflib.unified_diff(text.splitlines(True), new.splitlines(True), fromfile=path, tofile=args.out):
        sys.stdout.write(redact(line) if line.endswith("\n") else redact(line) + "\n\\ No newline at end of file\n")
    for line in summary_lines(report):
        print(line)
    print(f"written: {args.out}" + ("" if new != text else " (unchanged)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
