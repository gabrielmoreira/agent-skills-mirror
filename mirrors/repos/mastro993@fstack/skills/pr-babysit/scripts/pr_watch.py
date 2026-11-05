#!/usr/bin/env python3
"""Watch a GitHub pull request's CI and review activity through the gh CLI.

  pr_watch.py snapshot [PR]   Print the PR's current state and mark everything shown as seen.
  pr_watch.py wait [PR]       Poll until something new needs attention, print it, and exit.

PR is a number, URL, or branch; it defaults to the current branch's PR. Seen state lives in
$XDG_CACHE_HOME/pr-babysit (default ~/.cache), keyed by the PR's GitHub node ID, so it is the same
from any directory or worktree.
Items authored by the gh-authenticated user count as seen: they are the babysitter's own replies.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

PR_FIELDS = (
    "id,number,url,title,state,isDraft,headRefName,headRefOid,baseRefName,"
    "mergeable,mergeStateStatus,reviewDecision,reviewRequests"
)
CHECK_FIELDS = "name,bucket,state,link,workflow"
ACTIVITY_QUERY = """
query($owner: String!, $repo: String!, $number: Int!) {
  viewer { login }
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 100) {
        nodes {
          id isResolved isOutdated path line
          comments(first: 50) { nodes { id author { login } body url } }
        }
      }
      reviews(last: 50) { nodes { id author { login } state body } }
      comments(last: 50) { nodes { id author { login } body url } }
    }
  }
}
"""
FAILED = {"fail", "cancel"}
DONE = {"pass", "skipping", "fail", "cancel"}


class GhError(Exception):
    pass


def gh(*args):
    proc = subprocess.run(["gh", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise GhError(f"gh {' '.join(args[:3])}: {proc.stderr.strip() or proc.returncode}")
    return proc.stdout


def fetch_checks(number, repo):
    # gh exits 1 when a check failed, 8 while some are pending, and 1 with "no checks reported"
    # when there are none, so judge by the output rather than the exit code.
    proc = subprocess.run(["gh", "pr", "checks", str(number), "-R", repo, "--json", CHECK_FIELDS],
                          capture_output=True, text=True)
    if proc.stdout.strip():
        return json.loads(proc.stdout)
    if "no checks" in proc.stderr:
        return []
    raise GhError(f"gh pr checks: {proc.stderr.strip() or proc.returncode}")


def fetch(pr_arg):
    pr = json.loads(gh("pr", "view", *pr_arg, "--json", PR_FIELDS))
    host, owner, repo = re.match(r"https?://([^/]+)/([^/]+)/([^/]+)/pull/", pr["url"]).groups()
    checks = fetch_checks(pr["number"], f"{host}/{owner}/{repo}")
    host_args = [] if host == "github.com" else ["--hostname", host]
    data = json.loads(gh("api", "graphql", *host_args, "-f", f"query={ACTIVITY_QUERY}",
                         "-f", f"owner={owner}", "-f", f"repo={repo}", "-F", f"number={pr['number']}"))
    pr["viewer"] = data["data"]["viewer"]["login"]
    pr["activity"] = data["data"]["repository"]["pullRequest"]
    pr["checks"] = checks
    pr["key"] = pr["id"]
    return pr


def state_path(key):
    base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return base / "pr-babysit" / f"{key}.json"


def load_state(key):
    path = state_path(key)
    if path.exists():
        return json.loads(path.read_text())
    return {"seen": [], "checks": {}, "passed": [], "conflicts": [], "behind": []}


def save_state(key, state):
    path = state_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state))


def login(node):
    return (node.get("author") or {}).get("login") or "ghost"


def excerpt(text, limit=300):
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def activity_items(pr):
    """Yield (id, author, thread id or None, line) for every comment and review on the PR."""
    act = pr["activity"]
    for thread in act["reviewThreads"]["nodes"]:
        where = f"{thread['path']}:{thread['line'] or '?'}"
        for c in thread["comments"]["nodes"]:
            yield c["id"], login(c), thread["id"], f"review comment {where} by {login(c)} [thread {thread['id']}]: {excerpt(c['body'])}"
    for r in act["reviews"]["nodes"]:
        if r["body"] or r["state"] in ("APPROVED", "CHANGES_REQUESTED"):
            yield r["id"], login(r), None, f"review {r['state']} by {login(r)}: {excerpt(r['body'])}"
    for c in act["comments"]["nodes"]:
        yield c["id"], login(c), None, f"comment by {login(c)}: {excerpt(c['body'])} ({c['url']})"


def new_events(pr, state):
    """Return (event lines, ids of awaiting-reply threads with new comments) for everything not yet
    shown, and record it as seen. Those threads are listed by summary(), so they get no event line."""
    events, new_threads, seen = [], set(), set(state["seen"])
    awaiting = {t["id"] for t in awaiting_reply(pr)}
    if pr["state"] != "OPEN":
        events.append(f"PR {pr['state']}")
    for item_id, author, thread_id, line in activity_items(pr):
        if item_id not in seen and author != pr["viewer"]:
            if thread_id in awaiting:
                new_threads.add(thread_id)
            else:
                events.append(f"NEW {line}")
        seen.add(item_id)
    state["seen"] = sorted(seen)

    head, checks = pr["headRefOid"], pr["checks"]
    shown = state["checks"].setdefault(head, {})
    for c in checks:
        if c["bucket"] in FAILED and shown.get(c["name"]) != c["bucket"]:
            events.append(f"CHECK FAILED {c['name']} ({c['bucket']}) {c['link']}")
        if c["bucket"] in DONE:
            shown[c["name"]] = c["bucket"]
        else:
            shown.pop(c["name"], None)  # re-running: report its next result again
    state["checks"] = {head: shown}  # older heads no longer matter
    if checks and all(c["bucket"] in DONE for c in checks) and not any(c["bucket"] in FAILED for c in checks):
        if head not in state["passed"]:
            events.append(f"CHECKS PASSED on {head[:7]}")
            state["passed"].append(head)
    if pr["mergeable"] == "CONFLICTING" and head not in state["conflicts"]:
        events.append(f"MERGE CONFLICT with {pr['baseRefName']}")
        state["conflicts"].append(head)
    if pr["mergeStateStatus"] == "BEHIND" and head not in state.setdefault("behind", []):
        events.append(f"BEHIND {pr['baseRefName']}: the branch must be updated before it can merge")
        state["behind"].append(head)
    return events, new_threads


def awaiting_reply(pr):
    """Unresolved threads whose last comment is not ours."""
    return [t for t in pr["activity"]["reviewThreads"]["nodes"]
            if not t["isResolved"] and t["comments"]["nodes"]
            and login(t["comments"]["nodes"][-1]) != pr["viewer"]]


def summary(pr, new_threads=()):
    checks = pr["checks"]
    counts = {b: sum(c["bucket"] == b for c in checks) for b in ("pass", "fail", "cancel", "pending", "skipping")}
    pending_review = [r.get("login") or r.get("name") for r in pr["reviewRequests"]]
    waiting = awaiting_reply(pr)
    blockers = []
    if pr["state"] != "OPEN":
        blockers.append(f"PR is {pr['state']}")
    if not checks:
        blockers.append("no checks reported yet")
    elif counts["fail"] or counts["cancel"]:
        blockers.append("checks failing")
    elif counts["pending"]:
        blockers.append("checks pending")
    if pr["reviewDecision"] not in ("APPROVED", "", None):
        blockers.append(f"review {pr['reviewDecision']}")
    if pr["mergeable"] != "MERGEABLE":
        blockers.append(f"mergeable {pr['mergeable']}")
    elif pr["mergeStateStatus"] == "BEHIND":
        blockers.append(f"behind {pr['baseRefName']}")
    if waiting:
        blockers.append(f"{len(waiting)} thread(s) awaiting reply")
    if pr["isDraft"]:
        blockers.append("draft")

    lines = [
        f"PR #{pr['number']} {pr['title']} — {pr['url']}",
        f"state {pr['state']}{' (draft)' if pr['isDraft'] else ''} · head {pr['headRefName']} @ {pr['headRefOid'][:7]} → {pr['baseRefName']}"
        f" · mergeable {pr['mergeable']} ({pr['mergeStateStatus']}) · review {pr['reviewDecision'] or 'none required'}"
        + (f" · awaiting review from {', '.join(pending_review)}" if pending_review else ""),
        "checks: " + (", ".join(f"{n} {b}" for b, n in counts.items() if n) or "none"),
    ]
    lines += [f"  {c['bucket'].upper()} {c['name']} {c['link']}" for c in checks if c["bucket"] in FAILED]
    for t in waiting:
        last = t["comments"]["nodes"][-1]
        lines.append(f"  {'NEW ' if t['id'] in new_threads else ''}awaiting reply: thread {t['id']} {t['path']}:{t['line'] or '?'}"
                     f"{' (outdated)' if t['isOutdated'] else ''} — {login(last)}: {excerpt(last['body'], 160)}")
    lines.append("READY: yes" if not blockers else "READY: no — " + "; ".join(blockers))
    return "\n".join(lines)


def cmd_snapshot(pr_arg):
    pr = fetch(pr_arg)
    state = load_state(pr["key"])
    events, new_threads = new_events(pr, state)
    save_state(pr["key"], state)
    print(summary(pr, new_threads))
    if events:
        print("\nNew since last look:\n" + "\n".join(events))


def cmd_wait(pr_arg, interval, timeout):
    deadline, failures = time.monotonic() + timeout, 0
    while True:
        try:
            pr = fetch(pr_arg)
            failures = 0
        except (GhError, json.JSONDecodeError, KeyError, TypeError) as err:
            failures += 1
            if failures >= 5:
                print(f"ERROR: giving up after 5 failed polls: {err}")
                return 1
        else:
            state = load_state(pr["key"])
            events, new_threads = new_events(pr, state)
            save_state(pr["key"], state)
            if new_threads:
                events.append(f"NEW comments on {len(new_threads)} thread(s) awaiting reply, marked NEW below")
            if events:
                print("\n".join(events) + "\n\n" + summary(pr, new_threads))
                return 0
        if time.monotonic() + interval > deadline:
            print(f"NO CHANGE in {timeout // 60} min. Re-arm the wait.")
            return 0
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["snapshot", "wait"])
    parser.add_argument("pr", nargs="?", help="PR number, URL, or branch (default: current branch)")
    parser.add_argument("--interval", type=int, default=int(os.environ.get("PR_WATCH_INTERVAL", 15)),
                        help="seconds between polls (default 15)")
    parser.add_argument("--timeout", type=int, default=1500, help="seconds before giving up quietly (default 1500)")
    args = parser.parse_args()
    pr_arg = [args.pr] if args.pr else []
    try:
        if args.command == "snapshot":
            cmd_snapshot(pr_arg)
            return 0
        return cmd_wait(pr_arg, args.interval, args.timeout)
    except GhError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
