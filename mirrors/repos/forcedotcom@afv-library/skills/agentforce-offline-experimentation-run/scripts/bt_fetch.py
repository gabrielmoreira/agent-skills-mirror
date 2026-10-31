#!/usr/bin/env python3
"""Fetch an agent's STDM sessions with read-only anonymous Apex: nothing is deployed.

    python3 scripts/bt_fetch.py --org <alias> --probe [--agent NAME --start DATE --end DATE]
    python3 scripts/bt_fetch.py --org <alias> --agent GPT41_Shopper_Agent \\
        --start 2026-09-01 --end 2026-10-08 --out-dir runs/fetch-shop [--exclude-sessions FILE]
    python3 scripts/sfap_replay.py --details runs/fetch-shop/details.json ...

Every query runs with `sf apex run --json` in --org, the org that holds the STDM data (with Data
Cloud One, not the agent's own org), in --dataspace. Each generated script is checked to be
read-only before it runs (SELECT queries only: no DML, no callouts) and is kept in OUT/apex/.

A data space that names the STDM DMOs and fields its own way (not ssot__AiAgentSession__dlm,
ssot__Id__c, ...) takes --stdm-names FILE, a bt.stdm_names/1 names map (references/replay-
procedure.md 1.2): the queries are sent in its names. Without it, nothing is renamed.

--probe counts the rows of each STDM DMO (and the agent's participant rows, and the sessions in
the window, when given) and prints each error as the org words it: run it first, and quote it
in an access request. With --stdm-names it also runs every query a fetch runs, with keys no row
has, and names each that fails.

The fetch finds the agent's sessions started in [--start, --end] with at least one turn, keeps
the --channels wanted (by default all but Builder*, Agent Builder's test traffic), drops the
sessions of --exclude-sessions and, with --split, those of the other split, then takes up to
--max-sessions in salted-hash order (or --order recent) and fetches them, --batch-size sessions
per Apex run.
An interrupted fetch rerun into the same --out-dir does not fetch its finished batches again.

Outputs in --out-dir (0700, files 0600): details.json (ConversationData, the --details input of
sfap_replay.py), sessions.json (SessionSummary), fetch.json (bt.fetch/1: parameters, counts,
digests; no session ids), apex/ (the scripts run). details.json holds user utterances and the
scripts hold session ids: keep them out of git.

--emit-kit DIR writes the same fetch as a kit for someone who can read the STDM data: this script,
the modules it runs, run_kit.sh with the parameters set (and the --stdm-names file), and a README.
Its out/ comes back.

Exit 0: done. 1: the fetch failed, or --probe found a required DMO unreadable (or, with
--stdm-names, a query that fails). 2: usage.
130: interrupted (rerun into the same --out-dir to go on).
"""

import argparse
import hashlib
import json
import os
import shlex
import shutil
import sys
import tempfile
import traceback
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from btlib import SCHEMA_KIT  # noqa: E402
from btlib import fetch as fetchlib  # noqa: E402
from btlib import splits as splitlib  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
KIT_MODULES = ("__init__.py", "fetch.py", "redact.py", "splits.py", "stdm.py")  # all bt_fetch.py imports


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--probe", action="store_true", help="count the rows each STDM DMO gives, print the errors")
    mode.add_argument("--emit-kit", metavar="DIR", help="write this fetch as a kit for someone with STDM access")
    p.add_argument("--org", help="alias or username of the org holding the STDM data")
    p.add_argument("--dataspace", default="default", help="Data Cloud data space (default %(default)s)")
    p.add_argument("--stdm-names", metavar="FILE",
                   help="the data space's own DMO and field names, a bt.stdm_names/1 file (default: the "
                        "ssot__ names, as they are)")
    p.add_argument("--agent", help="the agent's API name (participant ssot__AiAgentApiName__c)")
    p.add_argument("--start", help="sessions started from this date or ISO 8601 time (UTC)")
    p.add_argument("--end", help="... up to this one; a date alone includes its whole day")
    p.add_argument("--out-dir", metavar="DIR", help="where the fetch goes (created 0700; must not hold a fetch)")
    p.add_argument("--max-sessions", type=int, default=fetchlib.MAX_SESSIONS,
                   help="sessions to fetch at most (default %(default)s)")
    p.add_argument("--channels", help="comma-separated channel names to keep (default: all but Builder*)")
    p.add_argument("--exclude-sessions", metavar="FILE",
                   help="never fetch these sessions: a file that names them, e.g. one ID per line, a "
                        "units.jsonl, a sessions or details JSON, a replay CSV (references/splits.md)")
    p.add_argument("--val-fraction", type=float, metavar="F", help="session split as sfap_replay.py labels it")
    p.add_argument("--split", choices=splitlib.SPLITS, help="fetch only this split (needs --val-fraction)")
    p.add_argument("--split-salt", default=splitlib.DEFAULT_SALT, help="salt of the split (default %(default)s)")
    p.add_argument("--order", choices=("hash", "recent"), default="hash",
                   help="which sessions come first when there are more than --max-sessions: a salted hash "
                        "(an even sample, stable when the window grows) or the newest (default %(default)s)")
    p.add_argument("--sample-salt", default=fetchlib.SAMPLE_SALT, help="salt of --order hash (default %(default)s)")
    p.add_argument("--batch-size", type=int, default=fetchlib.BATCH_SIZE,
                   help="sessions per Apex run, halved when a run hits a limit (default %(default)s)")
    p.add_argument("--timeout", type=int, default=fetchlib.APEX_TIMEOUT, help="seconds per Apex run")
    p.add_argument("--dry-run", action="store_true", help="find and select the sessions, print the counts, write nothing")
    p.add_argument("--overwrite", action="store_true", help="replace an earlier fetch in --out-dir")
    args = p.parse_args(argv)
    if not args.emit_kit and not args.org:
        p.error("--org is required (the org whose STDM data to read)")
    if not args.probe:
        missing = [f"--{n}" for n in ("agent", "start", "end") if not getattr(args, n)]
        if missing:
            p.error(" ".join(missing) + " required")
        if not (args.emit_kit or args.dry_run or args.out_dir):
            p.error("--out-dir is required (or --dry-run)")
    if args.val_fraction is not None and not 0 < args.val_fraction < 1:
        p.error("--val-fraction must be in (0, 1)")
    if args.split and args.val_fraction is None:
        p.error("--split needs --val-fraction (and the --split-salt of the units)")
    if args.max_sessions < 1 or args.batch_size < 1 or args.timeout < 1:
        p.error("--max-sessions, --batch-size and --timeout must be >= 1")
    args.channels = [c.strip() for c in args.channels.split(",") if c.strip()] if args.channels else None
    return args


def read_excluded(path):
    if not path:
        return frozenset()
    try:
        return frozenset(splitlib.read_session_ids(path))
    except (OSError, splitlib.SplitError) as e:
        raise fetchlib.FetchError(f"--exclude-sessions {path}: {e}") from None


def read_names(path):
    """The StdmNames of --stdm-names, or None: the default names."""
    return fetchlib.load_names(path) if path else None


def run_probe(args):
    names = read_names(args.stdm_names)
    with tempfile.TemporaryDirectory(prefix="bt_fetch_") as tmp:
        f = fetchlib.Fetcher(args.org, os.path.join(tmp, "apex"), args.dataspace, timeout=args.timeout, names=names)
        got = fetchlib.probe(f, args.agent, args.start, args.end)
    print(f"STDM probe of {args.org}, data space {args.dataspace} (row counts, read-only):")
    labels = {"agent": f"participant rows of {args.agent}", "window": "sessions started in the window"}
    if names is not None:
        print(f"names: {names.source} (sha256 {names.sha256})" + (f": {names.about}" if names.about else ""))
        for key, table in fetchlib.PROBE_DMOS.items():  # table: the default name, quoted
            labels[key] = f"{key} ({names.dmo(table[1:-1])})"
        labels.update((key, "query: " + what) for key, what in fetchlib.SHAPES.items())
    width = max(len(labels.get(key, key)) for key in got)
    for key, res in got.items():
        print(f"  {labels.get(key, key):<{width}}  " + (f"{res['rows']}" if "rows" in res else f"ERROR {res['error']}"))
    unreadable = [k for k in fetchlib.REQUIRED_DMOS if "error" in got[k]]
    if unreadable:
        print(f"not readable: {', '.join(unreadable)}. A fetch needs them; quote the errors above in an access "
              "request, or hand someone with access a kit (--emit-kit).")
        return 1
    if names is None:
        print("the DMOs a fetch reads are readable")
        return 0
    failed = [what for key, what in fetchlib.SHAPES.items() if "error" in got[key]]
    if failed:
        print(f"these queries fail with the names of {names.source}: {', '.join(failed)}. The errors above "
              "name what the data space lacks; fix the names map, and probe again.")
        return 1
    print("the DMOs a fetch reads are readable, and every query a fetch runs works with these names")
    return 0


def prepare_out_dir(out_dir, overwrite):
    if os.path.isfile(os.path.join(out_dir, "fetch.json")) and not overwrite:
        raise fetchlib.FetchError(f"{out_dir} already holds a fetch (fetch.json); use a new --out-dir or --overwrite")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
        os.chmod(out_dir, 0o700)  # user utterances inside
    elif overwrite:  # the old fetch's files go first: one that stops early must not pass for it
        fetchlib.clear_outputs(out_dir)


def run_fetch(args):
    exclude = read_excluded(args.exclude_sessions)
    names = read_names(args.stdm_names)
    kw = dict(channels=args.channels, exclude=exclude, split=args.split, val_fraction=args.val_fraction,
              split_salt=args.split_salt, order=args.order, sample_salt=args.sample_salt,
              max_sessions=args.max_sessions, batch_size=args.batch_size, log=print,
              params={"exclude_sessions": os.path.basename(args.exclude_sessions) if args.exclude_sessions else None,
                      "batch_size": args.batch_size})
    if args.dry_run:
        with tempfile.TemporaryDirectory(prefix="bt_fetch_") as tmp:
            f = fetchlib.Fetcher(args.org, os.path.join(tmp, "apex"), args.dataspace, timeout=args.timeout,
                                 names=names)
            fetchlib.fetch(f, args.agent, args.start, args.end, dry_run=True, **kw)
        print("dry run: nothing fetched")
        return 0
    prepare_out_dir(args.out_dir, args.overwrite)
    f = fetchlib.Fetcher(args.org, os.path.join(args.out_dir, "apex"), args.dataspace, timeout=args.timeout,
                         names=names)
    m = fetchlib.fetch(f, args.agent, args.start, args.end, out_dir=args.out_dir, **kw)
    c = m["counts"]
    print(f"fetched {c['fetched']} sessions, {c['turns']} turns, {c['llm_steps']} LLM steps in {c['apex_runs']} "
          f"Apex runs: {os.path.join(args.out_dir, 'details.json')}")
    if os.path.isfile(os.path.join(HERE, "sfap_replay.py")):
        print(f"next: python3 {os.path.join(HERE, 'sfap_replay.py')} --details "
              f"{os.path.join(args.out_dir, 'details.json')} ...")
    else:  # a kit
        print(f"send back the whole {args.out_dir} dir (README.md)")
    return 0


_RUN_KIT = """#!/usr/bin/env bash
# Fetch the STDM sessions of {agent} for a backtest, with read-only anonymous Apex (README.md).
# Usage: ./run_kit.sh <org-alias> [data-space] [more bt_fetch.py flags: --probe, --dry-run, --overwrite]
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
if [ $# -lt 1 ]; then
  echo "usage: $0 <org-alias> [data-space] [--probe | --dry-run | --overwrite]" >&2
  exit 2
fi
org="$1"; shift
dataspace={dataspace}
if [ $# -gt 0 ] && [ "${{1#-}}" = "$1" ]; then dataspace="$1"; shift; fi
exec python3 "$here/bt_fetch.py" --org "$org" --dataspace "$dataspace" \\
  {flags} \\
  --out-dir "$here/out" "$@"
"""

_README = """# STDM fetch kit: {agent}

Fetches up to {max_sessions} Agentforce sessions of the agent `{agent}`, started from {start} to
{end} (UTC), from the Session Tracing data (STDM) of a Data Cloud data space. They are the
input of an offline backtest. Made by `bt_fetch.py --emit-kit` (code sha {code_sha}).

## What it does

`run_kit.sh` runs `bt_fetch.py`, which writes small anonymous Apex scripts and runs each with
`sf apex run --json --file <script> --target-org <your org>`. They only read:

- SELECT queries through `ConnectApi.CdpQuery.queryAnsiSqlV2` on the DMOs
  {session}, {participant}, {interaction},
  {message} and {step} (and a row count of
  {generation} and {gateway} with `--probe`);
- a SOQL query of GenAiPlannerDefinition (Id, DeveloperName, MasterLabel), only when no session
  names the agent.

There is no DML, no callout, nothing is deployed and nothing is changed in the org. Each script
is checked before it runs (`btlib/fetch.py`, `check_read_only`: only the words those reads need,
and SELECT statements only) and stays in `out/apex/` for you to read.

{names_note}## Run it

Needs python3 (3.9 or later) and the Salesforce CLI `sf`, logged in to the org that holds the
STDM data, as a user who can query its data space.

    ./run_kit.sh <org-alias> --probe                 # can this user read the STDM DMOs? (counts only)
    ./run_kit.sh <org-alias> --dry-run               # how many sessions would come (counts only)
    ./run_kit.sh <org-alias>                         # the fetch, into out/
    ./run_kit.sh <org-alias> <data-space> ...        # another data space than {dataspace}

{exclude_note}## What to send back

The whole `out/` dir: `details.json` (the conversations), `sessions.json`, `fetch.json` (what was
asked and the counts) and `apex/` (the scripts that ran). The conversations hold what users
wrote: share them only the way your team shares production transcripts.
"""

_NAMES_NOTE = """## Names

This data space names the STDM DMOs and fields its own way. The queries are sent in the names
of `stdm_names.json` (sha256 {sha256}){user_agent}.{about} `--probe` also runs every query
the fetch runs, with keys no row has, and names each that fails.

"""


def emit_kit(args):
    """A self-contained copy of this fetch; returns the kit dir."""
    kit = args.emit_kit
    if os.path.exists(kit) and (not os.path.isdir(kit) or os.listdir(kit)):
        raise fetchlib.FetchError(f"{kit} exists and is not an empty dir")
    fetchlib.check_name(args.agent)
    fetchlib.check_name(args.dataspace, "data space name")
    start, end = fetchlib.window_bound(args.start), fetchlib.window_bound(args.end, end=True)
    exclude = read_excluded(args.exclude_sessions)
    names = read_names(args.stdm_names)
    os.makedirs(os.path.join(kit, "btlib"), exist_ok=True)
    os.chmod(kit, 0o700)
    files = {"bt_fetch.py": os.path.join(HERE, "bt_fetch.py")}
    files.update({"btlib/" + name: os.path.join(HERE, "btlib", name) for name in KIT_MODULES})
    if names is not None:
        files["stdm_names.json"] = args.stdm_names
    for rel, src in files.items():
        shutil.copyfile(src, os.path.join(kit, rel))
    if names is not None:
        os.chmod(os.path.join(kit, "stdm_names.json"), 0o600)  # data, like the kit's other files
    flags =["--agent", args.agent, "--start", start, "--end", end, "--max-sessions", str(args.max_sessions),
             "--batch-size", str(args.batch_size), "--order", args.order, "--sample-salt", args.sample_salt]
    if args.channels:
        flags += ["--channels", ",".join(args.channels)]
    if args.split:
        flags += ["--val-fraction", repr(args.val_fraction), "--split", args.split, "--split-salt", args.split_salt]
    texts = {"run_kit.sh": _RUN_KIT.format(agent=args.agent, dataspace=shlex.quote(args.dataspace),
                                           flags=" ".join(shlex.quote(x) for x in flags)
                                           + (' --stdm-names "$here/stdm_names.json"' if names else "")
                                           + (' --exclude-sessions "$here/exclude_sessions.txt"' if exclude else ""))}
    if exclude:  # the ids are the org's own, and the kit goes to people who can read its sessions
        texts["exclude_sessions.txt"] = ("# sessions this fetch must not return (already in the backtest)\n"
                                         + "".join(s + "\n" for s in sorted(exclude)))
    dmos = {key: table[1:-1] for key, table in fetchlib.PROBE_DMOS.items()}  # the default names, unquoted
    names_note = ""
    if names is not None:
        dmos = {key: names.dmo(name) for key, name in dmos.items()}
        about = names.about + ("" if names.about.endswith((".", "!", "?")) else ".") if names.about else ""
        names_note = _NAMES_NOTE.format(
            sha256=names.sha256, about=f" It says: {about}" if about else "",
            user_agent=f", each with the userAgent `{names.user_agent}`" if names.user_agent else "")
    texts["README.md"] = _README.format(
        agent=args.agent, max_sessions=args.max_sessions, start=start, end=end, dataspace=args.dataspace,
        code_sha=fetchlib.code_sha(), names_note=names_note, **dmos,
        exclude_note=(f"`exclude_sessions.txt` lists {len(exclude)} sessions the backtest already has; the fetch "
                      "skips them.\n\n" if exclude else ""))
    for rel, text in texts.items():
        fetchlib.write_private(os.path.join(kit, rel), text)
    os.chmod(os.path.join(kit, "run_kit.sh"), 0o700)
    shas = {}
    for rel in sorted(list(files) + list(texts)):
        with open(os.path.join(kit, rel), "rb") as fh:
            shas[rel] = hashlib.sha256(fh.read()).hexdigest()[:16]
    manifest = {"schema": SCHEMA_KIT, "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "params": {"agent": args.agent, "window": [start, end], "dataspace": args.dataspace,
                           "max_sessions": args.max_sessions, "batch_size": args.batch_size,
                           "channels": args.channels, "order": args.order, "sample_salt": args.sample_salt,
                           "split": None if not args.split else {"split": args.split, "val_fraction": args.val_fraction,
                                                                 "salt": args.split_salt},
                           "excluded_ids": len(exclude)},
                "code": {"fetch_sha256": fetchlib.code_sha()}, "files": shas}
    if names is not None:
        manifest["params"]["stdm_names"] = names.manifest()
    fetchlib.write_private(os.path.join(kit, "kit.json"), json.dumps(manifest, indent=2) + "\n")
    print(f"kit: {kit} ({len(shas) + 1} files); they run ./run_kit.sh <org-alias> and send back {kit}/out/")
    return kit


def main(argv=None):
    args = parse_args(argv)
    try:
        if args.emit_kit:
            emit_kit(args)
            return 0
        return run_probe(args) if args.probe else run_fetch(args)
    except fetchlib.FetchError as e:
        print(f"error: {fetchlib.mask_ids(str(e))}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"error: {fetchlib.mask_ids(str(e))}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("interrupted: rerun into the same --out-dir to go on from the finished batches", file=sys.stderr)
        return 130
    except Exception as e:  # a bug, or an answer it did not foresee: no traceback (it can quote session data)
        frame = traceback.extract_tb(e.__traceback__)[-1]
        print(f"error: bt_fetch failed ({type(e).__name__} at {os.path.basename(frame.filename)}:{frame.lineno}: "
              f"{fetchlib.mask_ids(str(e))[:200]})", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
