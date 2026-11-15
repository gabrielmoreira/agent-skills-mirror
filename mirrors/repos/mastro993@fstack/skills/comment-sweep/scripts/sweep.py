#!/usr/bin/env python3
"""Bookkeeping for a comment sweep. It never decides what a comment is: the inventory does.

  sweep.py scope [--full] [--base REF] [PATH ...]   Snapshot the files in scope and split them into batches.
  sweep.py apply                                     Delete the comments the inventory marks `delete`, where it can prove the match.
  sweep.py check                                     Compare the working tree with the snapshot and the inventory.

scope: the files this branch adds or changes since its merge-base with REF (default: origin's default
branch, else main or master), staged, unstaged, and untracked included; with --full, every file in the
repo. PATHs narrow either one. Generated, vendored, minified, lock, binary, and migration files are
skipped. Everything lands in a work directory, printed first:
  tree/            the files as they are now, for check
  batch-N.files    the batch's paths, one per line
  batch-N.diff     branch scope only: the batch's diff; its `+` lines are the lines in scope

inventory.txt, which you write into the work directory, has one line per comment:
  path:LINE[-END]: kind: text => verdict: reason
kind is comment, doc, or directive; verdict is delete, trim, or keep; LINE is the line before any edit.

apply deletes a `delete` entry when its lines are nothing but that comment: a run of line comments, one
block comment, or the tail of a code line, with the same words as the entry's text. It prints the rest as
`by hand`, then as `unlisted` each line in scope that holds a comment marker and that no entry covers.
Run it again after changing the inventory: it skips the entries whose lines are already edited.

check prints one line per finding and exits 1 if there is any besides CUT:
  CODE        a changed line that no delete or trim verdict covers
  DIRECTIVE   a changed directive (not counted when its verdict is `delete: unused ...`)
  CUT         a deletion or trim it could not match to the entry's text: read it
  UNAPPLIED   a delete or trim verdict whose lines are unchanged
  UNJUDGED    an entry with no verdict;  UNPARSED  a line that is not an entry
  OUTSIDE     an entry on no line in scope: a comment the branch never touched, or a skipped file
  STRAY       a file outside the scope that changed since scope ran
then the tally (counted by the reason's words before its first comma), and the inventory again with each
surviving comment at its line now and each deleted one at its old line, marked (before).
"""

import argparse
import codecs
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

SKIP_DIRS = {"node_modules", "vendor", "third_party", "third-party", "dist", "build", "out", ".next", "target", "coverage", "__pycache__", ".git", "Pods", ".venv", "venv"}
SKIP_FILE = re.compile(r"\.min\.\w+$|\.(pb|pb\.gw)\.go$|_pb2(_grpc)?\.pyi?$|\.g\.dart$|\.freezed\.dart$|\.generated\.\w+$|\.gen\.\w+$")
LOCK_FILE = re.compile(r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|bun\.lockb?|Cargo\.lock|poetry\.lock|uv\.lock|Gemfile\.lock|composer\.lock|go\.sum|Package\.resolved|[^/]*\.lock)$")
MIGRATION_DIR = {"migrations", "migration", "migrate", "db_migrations", "alembic"}
GENERATED = re.compile(r"@generated|DO NOT EDIT|Code generated|auto-?generated", re.I)

SMALL_LINES = 4000  # up to here a sweep is small: one batch, read inline; scouts cost more than they save
BATCH_LINES, BATCH_FILES = 1500, 20

ENTRY = re.compile(r"^(?P<path>.+?):(?P<start>\d+)(?:-(?P<end>\d+))?: (?P<kind>comment|doc|directive): (?P<rest>.*)$")
VERDICT = re.compile(r"^(?P<text>.*) => (?P<verdict>delete|trim|keep): (?P<reason>.*)$")
NOT_ENTRY = re.compile(r"^(skip: |files: )")
LINE_OPENERS = ("//", "#", "--", ";", "%")
CODE_TOO = ("--", ";", "%")  # line openers that are also code punctuation in C-like languages
MARKED = re.compile(r"""(?<!:)//|/\*|<!--|(?<!\{)\{\#|\{\{!|\"{3}|'{3}|^\s*"?\#(\s|$)|\s\#\s""")  # looks like it holds a comment
HASH_IS_TEXT = {".md", ".mdx", ".markdown", ".rst", ".txt"}
BLOCKS = {"{/*": "*/}", "/*": "*/", "<!--": "-->", "{#": "#}", "{{!": "}}"}


def git(*args, check=True):
    done = subprocess.run(["git", "-c", "core.quotePath=false", *args], capture_output=True, text=True)
    if check and done.returncode:
        sys.exit(f"git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout


def repo_root():
    return Path(git("rev-parse", "--show-toplevel").strip())


def work_dir(root):
    return Path(tempfile.gettempdir()) / "comment-sweep" / hashlib.sha1(str(root).encode()).hexdigest()[:12]


def default_base():
    head = git("symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD", check=False).strip()
    if head:
        return head
    for ref in ("origin/main", "origin/master", "main", "master"):
        if subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref], capture_output=True).returncode == 0:
            return ref
    sys.exit("No base branch found: pass --base REF.")


def plural(n, noun, ending="s"):
    return f"{n} {noun}{'' if n == 1 else ending}"


def read_lines(path):
    return Path(path).read_bytes().decode("utf-8", "surrogateescape").splitlines(keepends=True)


def write_lines(path, lines):
    Path(path).write_bytes("".join(lines).encode("utf-8", "surrogateescape"))


def skip_reason(rel, root):
    path, parts = root / rel, Path(rel).parts
    if any(p in SKIP_DIRS for p in parts[:-1]):
        return "vendored or build output"
    if any(p.lower() in MIGRATION_DIR for p in parts[:-1]):
        return "migration (checksum tools hash the whole file)"
    if SKIP_FILE.search(rel):
        return "generated or minified"
    if LOCK_FILE.search(rel):
        return "lock file"
    if path.is_symlink() or not path.is_file():
        return "not a regular file"
    head = path.read_bytes()[:8192]
    if b"\0" in head:
        return "binary"
    if GENERATED.search(b"\n".join(head.splitlines()[:5]).decode("utf-8", "replace")):
        return "generated"
    return None


def dirty_paths():
    rows, paths = git("status", "--porcelain", "-z", "-uall").split("\0"), set()
    while rows:
        row = rows.pop(0)
        if row:
            paths.add(row[3:])
            if row[0] in "RC":
                rows.pop(0)  # the path it was renamed or copied from
    return sorted(paths)


def names(out):
    return [name for name in out.split("\0") if name]


def header_path(row):
    """The path on a `+++ b/<path>` diff header: git ends one holding a space with a tab, and quotes odd names."""
    path = row[4:].rstrip("\t")
    if path.startswith('"'):
        path = codecs.escape_decode(path[1:-1])[0].decode("utf-8", "surrogateescape")
    return path.removeprefix("b/")


def inside(path, root):
    """The path relative to the repo root, or exit when it lies outside the repo."""
    try:
        return str(Path(path).resolve().relative_to(root))
    except ValueError:
        sys.exit(f"{path}: outside the repository at {root}")


def cmd_scope(args):
    root = repo_root()
    paths = [inside(p, root) for p in args.paths]  # git runs from the root, whatever the cwd
    base = None if args.full else git("-C", str(root), "merge-base", "HEAD", args.base or default_base()).strip()
    untracked = names(git("-C", str(root), "ls-files", "-z", "--others", "--exclude-standard", "--", *paths))
    if args.full:
        tracked = set(names(git("-C", str(root), "ls-files", "-z", "--", *paths)))
    else:
        tracked = set(names(git("-C", str(root), "diff", "-z", "--name-only", "--diff-filter=d", "--find-renames", base, "--", *paths)))
    work = work_dir(root)
    shutil.rmtree(work, ignore_errors=True)
    (work / "tree").mkdir(parents=True)

    added = {}  # path -> [[first line, count]] of the lines the branch adds or changes
    diff_args = ("-C", str(root), "diff", "--unified=0", "--no-color", "--no-ext-diff", "--find-renames")
    if base and tracked:
        path = None
        for row in git(*diff_args, base, "--", *sorted(tracked)).splitlines():
            if row.startswith("+++ "):
                path = None if row == "+++ /dev/null" else header_path(row)
            elif row.startswith("@@") and path:
                start, count = re.match(r"@@ -\S+ \+(\d+)(?:,(\d+))? @@", row).groups()
                added.setdefault(path, []).append([int(start), int(1 if count is None else count)])

    files, hunks, skipped = {}, {}, []
    for rel in sorted(tracked | set(untracked)):
        reason = skip_reason(rel, root)
        if reason:
            skipped.append((rel, reason))
            continue
        hunks[rel] = added.get(rel, []) if base and rel in tracked else [[1, len(read_lines(root / rel))]]
        lines = sum(count for _, count in hunks[rel])
        if lines:
            files[rel] = lines
            (work / "tree" / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / rel, work / "tree" / rel)

    total = sum(files.values())
    big = total > SMALL_LINES
    wanted = max(-(-len(files) // BATCH_FILES), -(-total // BATCH_LINES)) if big else 1
    loads = {rel: lines / BATCH_LINES + 1 / BATCH_FILES for rel, lines in files.items()}  # a batch fills on either count
    share = sum(loads.values()) / wanted
    batches, batch, carried = [], [], 0.0
    for rel in files:
        batch.append(rel)
        carried += loads[rel]
        if carried >= share * (len(batches) + 1) - 1e-9 and len(batches) < wanted - 1:
            batches.append(batch)
            batch = []
    if batch:
        batches.append(batch)

    for n, batch in enumerate(batches, 1):
        (work / f"batch-{n}.files").write_text("\n".join(batch) + "\n")
        if base:
            changed = [f for f in batch if f in tracked]
            diff = git(*diff_args, base, "--", *changed) if changed else ""
            for rel in (f for f in batch if f not in tracked):
                diff += git(*diff_args, "--no-index", "--", "/dev/null", rel, check=False)
            (work / f"batch-{n}.diff").write_text(diff)
    meta = {"root": str(root), "files": sorted(files), "hunks": {f: hunks[f] for f in files}, "dirty": dirty_paths()}
    (work / "meta.json").write_text(json.dumps(meta))

    print(f"work: {work}")
    branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    print("scope: full" if args.full else f"scope: branch {branch} vs {args.base or default_base()} ({base[:7]})")
    for rel, reason in skipped:
        print(f"skip: {rel} — {reason}")
    for n, batch in enumerate(batches, 1):
        print(f"batch-{n}: {plural(len(batch), 'file')}, {plural(sum(files[f] for f in batch), 'line')}")
    print(f"{'big' if big else 'small'}: {plural(len(files), 'file')}, {plural(total, 'line')} in scope, {plural(len(batches), 'batch', 'es')}")


def load(root=None):
    root = root or repo_root()
    work = work_dir(root)
    if not (work / "meta.json").exists():
        sys.exit("No snapshot: run `sweep.py scope` first.")
    return root, work, json.loads((work / "meta.json").read_text())


def read_inventory(work, root):
    """([entry], [problem line]); an entry is a dict with path, start, end, kind, text, verdict, reason."""
    path = work / "inventory.txt"
    if not path.exists():
        sys.exit(f"No inventory: write it to {path}")
    entries, problems = [], []
    for raw in path.read_text(encoding="utf-8").splitlines():
        row = raw.strip()
        if not row or NOT_ENTRY.match(row):
            continue
        m = ENTRY.match(row)
        if not m:
            problems.append(f"UNPARSED {row}")
            continue
        entry = m.groupdict()
        rel = entry["path"].removeprefix("./")
        entry["path"] = str(Path(rel).relative_to(root)) if Path(rel).is_absolute() and Path(rel).is_relative_to(root) else rel
        entry["start"] = int(entry["start"])
        entry["end"] = int(entry["end"] or entry["start"])
        judged = VERDICT.match(entry.pop("rest"))
        entry.update(judged.groupdict() if judged else {"text": m["rest"], "verdict": None, "reason": ""})
        if not judged:
            problems.append(f"UNJUDGED {where(entry)}: {entry['text'][:80]}")
        entries.append(entry)
    return entries, problems


def outside(entries, meta):
    """A problem line for each entry that sits on no line in scope: the sweep leaves those comments alone."""
    problems = []
    for entry in entries:
        hunks = meta["hunks"].get(entry["path"])
        if not any(start <= entry["end"] and entry["start"] < start + count for start, count in hunks or []):
            why = "no line of it is in scope" if hunks else "not a file in scope"
            problems.append(f"OUTSIDE {where(entry)}: {why}: {entry['text'][:60]}")
    return problems


def where(entry, start=None, end=None):
    start, end = start or entry["start"], end or entry["end"]
    return f"{entry['path']}:{start}" + (f"-{end}" if end != start else "")


def alnum(text):
    return re.sub(r"[\W_]+", "", text).lower()


def same_words(lines, text):
    """True when the lines hold the entry's words and nothing else (or start with them, if the text was cut)."""
    text = text.rstrip()
    cut = text.endswith(("…", "..."))
    got, want = alnum("".join(lines)), alnum(text.rstrip("….") if cut else text)
    return bool(want) and (got.startswith(want) if cut else got == want)


def is_whole(lines, text):
    """True when the lines are exactly one comment: a run of line comments, or one block comment."""
    body = [line.strip() for line in lines]
    if not body or not body[0]:
        return False
    opener = next((o for o in LINE_OPENERS if body[0].startswith(o)), None)
    if opener:
        shape = all(b.startswith(opener) for b in body)
    else:
        closer = next((c for o, c in BLOCKS.items() if body[0].startswith(o)), None)
        joined = "\n".join(body)
        shape = bool(closer) and joined.endswith(closer) and joined.count(closer) == 1
    return shape and same_words(lines, text)


def is_tail(tail, text):
    """True when the tail is one comment, opener first, holding the entry's words and nothing else.

    A tail cut at code punctuation (`--; /* note */`, `; // note`) starts with an opener that is also
    code and holds a real comment's opener, so it fails even though its words match."""
    tail = tail.strip()
    opener = next((o for o in (*BLOCKS, *LINE_OPENERS) if tail.startswith(o)), None)
    if opener is None:
        return False
    body = tail[len(opener) :]
    if opener in BLOCKS:
        if not body.endswith(BLOCKS[opener]):
            return False
        body = body[: -len(BLOCKS[opener])]
    body = body.lstrip(opener[-1] + "!")  # `///`, `//!`, `/**`, `##`, `<!---`
    if opener in CODE_TOO and any(o in body for o in (*BLOCKS, "//", "#")):
        return False
    return same_words([body], text)


def tail_start(line, text):
    """Index where a trailing comment with the entry's words starts on a code line, else None."""
    for opener in (*BLOCKS, *LINE_OPENERS):  # the code-punctuation openers last
        at = line.find(opener)
        while at > 0:
            if line[:at].strip() and is_tail(line[at:], text):
                return at
            at = line.find(opener, at + 1)
    return None


def cmd_apply(_args):
    root, work, meta = load()
    entries, problems = read_inventory(work, root)
    problems += outside(entries, meta)
    if problems:
        sys.exit("\n".join(problems) + "\nFix the inventory first.")
    left, done, todo = [], 0, 0
    by_file = {}
    for entry in entries:
        by_file.setdefault(entry["path"], []).append(entry)
    for rel, group in by_file.items():
        lines = read_lines(root / rel)
        changes, mapping = diff_file(read_lines(work / "tree" / rel), lines)
        edited = {change[1] for change in changes if change[0] != "add"}
        before = list(lines)
        for entry in sorted(group, key=lambda e: -e["start"]):
            old = range(entry["start"] - 1, entry["end"])
            if entry["verdict"] == "keep" or edited & set(old):
                continue  # nothing to do, or done already
            todo += entry["verdict"] == "delete"
            at = mapping.get(old.start, len(lines))
            span = lines[at : at + len(old)] if [mapping.get(i) for i in old] == list(range(at, at + len(old))) else []
            if entry["verdict"] == "trim":
                left.append((entry, "trim"))
            elif is_whole(span, entry["text"]):
                del lines[at : at + len(span)]
                above = next((n for n in range(at + 1) if n == at or lines[at - 1 - n].strip()), 0)
                below = next((n for n in range(len(lines) - at + 1) if at + n == len(lines) or lines[at + n].strip()), 0)
                if at + below == len(lines):
                    del lines[at - above : at]  # the comment ended the file
                else:
                    del lines[at : at + (below if above == at else min(above, below))]  # the blank lines the removal doubles
                done += 1
            elif len(span) == 1 and (cut := tail_start(span[0], entry["text"])) is not None:
                lines[at] = span[0][:cut].rstrip() + span[0][len(span[0].rstrip("\r\n")) :]
                done += 1
            else:
                left.append((entry, "no exact match"))
        if lines != before:
            write_lines(root / rel, lines)
    report = [f"applied {done} of {todo} deletes"]
    for entry, why in sorted(left, key=lambda item: (item[0]["path"], item[0]["start"])):
        report.append(f"by hand ({why}): {where(entry)}: {entry['text'][:80]}")
    unlisted = []
    for rel in meta["files"]:
        listed = {n for e in by_file.get(rel, []) for n in range(e["start"], e["end"] + 1)}
        old = read_lines(work / "tree" / rel)
        for n in (n for start, count in meta["hunks"][rel] for n in range(start, start + count)):
            hit = n not in listed and n <= len(old) and MARKED.search(old[n - 1])
            if hit and not (hit.group().strip(' "') == "#" and Path(rel).suffix in HASH_IS_TEXT):
                unlisted.append(f"unlisted: {rel}:{n}: {show([old[n - 1]], 80)}")
    report += unlisted[:40] + ([f"unlisted: and {len(unlisted) - 40} more"] if len(unlisted) > 40 else [])
    print("\n".join(report))


def squash(line):
    """The line with its indentation kept and every other run of blanks collapsed."""
    body = line.rstrip()
    indent = len(body) - len(body.lstrip())
    return body[:indent] + " ".join(body.split())


def related(old, new):
    """True when new could be old with words removed: the pairing test inside a changed hunk."""
    want, it = re.findall(r"\w+", new), iter(re.findall(r"\w+", old))
    return bool(want) and all(word in it for word in want)


def show(lines, limit=100):
    text = " ".join(" ".join(lines).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def pair(old, new):
    """{old index: new index} for the lines of a changed hunk that survived, in order."""
    pairs, k = {}, 0
    for i, line in enumerate(old):  # first the lines that only lost their tail or their spacing
        for j in range(k, len(new)):
            kept = squash(new[j])
            if kept.strip() and squash(line).startswith(kept):
                pairs[i], k = j, j + 1
                break
    for i, line in enumerate(old):  # then the lines that lost words elsewhere
        if i in pairs:
            continue
        low = max((j for p, j in pairs.items() if p < i), default=-1) + 1
        high = min((j for p, j in pairs.items() if p > i), default=len(new))
        free = (j for j in range(low, high) if j not in pairs.values() and related(line, new[j]))
        if (j := next(free, None)) is not None:
            pairs[i] = j
    return pairs


def diff_file(old, new):
    """(changes, line map): changes are ("del", i), ("mod", i, j), ("add", j), 0-based; the map sends old i to new j."""
    changes, mapping = [], {}
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if op == "equal":
            mapping.update(zip(range(i1, i2), range(j1, j2)))
            continue
        pairs = pair(old[i1:i2], new[j1:j2])
        for i in range(i1, i2):
            if i - i1 not in pairs:
                changes.append(("del", i))
                continue
            mapping[i] = j1 + pairs[i - i1]
            if squash(old[i]) != squash(new[mapping[i]]):
                changes.append(("mod", i, mapping[i]))
        changes += [("add", j) for j in range(j1, j2) if j - j1 not in pairs.values()]
    return changes, mapping


def cmd_check(_args):
    root, work, meta = load()
    entries, problems = read_inventory(work, root)
    cuts, after = [], []
    by_file = {}
    for entry in entries:
        by_file.setdefault(entry["path"], []).append(entry)
    problems += outside(entries, meta)

    for rel in meta["files"]:
        old = read_lines(work / "tree" / rel)
        new = read_lines(root / rel) if (root / rel).is_file() else []
        changes, mapping = diff_file(old, new)
        group = by_file.get(rel, [])
        cover = {}  # old line index -> entry
        for entry in group:
            cover.update(dict.fromkeys(range(entry["start"] - 1, entry["end"]), entry))
        touched = {}  # id(entry) -> [change]
        for change in changes:
            if change[0] == "add":
                if new[change[1]].strip():
                    problems.append(f"CODE {rel}:+{change[1] + 1}: {show([new[change[1]]])}")
                continue
            i = change[1]
            entry = cover.get(i)
            if entry and entry["verdict"] in ("delete", "trim"):
                touched.setdefault(id(entry), []).append(change)
            elif entry and entry["kind"] == "directive":
                problems.append(f"DIRECTIVE {rel}:{i + 1}: {show([old[i]])}")
            elif old[i].strip():
                problems.append(f"CODE {rel}:{i + 1}: {show([old[i]])}")
        for entry in group:
            span = range(entry["start"] - 1, entry["end"])
            hits = touched.get(id(entry), [])
            if entry["verdict"] in ("delete", "trim"):
                lines = old[span.start : span.stop]
                if entry["kind"] == "directive" and hits:
                    proven = entry["reason"].lower().startswith("unused")  # the verdict claims its tool no longer needs it
                    (cuts if proven else problems).append(f"DIRECTIVE {where(entry)}: {show(lines)}")
                if not hits or (entry["verdict"] == "delete" and len(hits) < len([l for l in lines if l.strip()]) and all(h[0] == "del" for h in hits)):
                    problems.append(f"UNAPPLIED {where(entry)}: {entry['text'][:80]}")
                elif entry["verdict"] == "trim":
                    left = [new[mapping[i]] for i in span if i in mapping]
                    cuts.append(f"CUT {where(entry)}: trimmed to: {show(left) or '(nothing)'}")
                elif all(h[0] == "del" for h in hits):
                    if not is_whole(lines, entry["text"]):
                        cuts.append(f"CUT {where(entry)}: removed: {show(lines)}")
                else:
                    for _, i, j in (h for h in hits if h[0] == "mod"):
                        kept = squash(new[j])
                        gone = squash(old[i])[len(kept) :] if squash(old[i]).startswith(kept) else None
                        if gone is None or not is_tail(gone, entry["text"]):
                            cuts.append(f"CUT {rel}:{i + 1}: was: {show([old[i]])} now: {show([new[j]])}")
            now = sorted(mapping[i] + 1 for i in span if i in mapping)
            spot = where(entry, now[0], now[-1]) if now and entry["verdict"] != "delete" else where(entry) + " (before)"
            after.append(f"{spot}: {entry['kind']}: {show([entry['text']], 70)} => {entry['verdict']}: {entry['reason']}")

    strays = set(dirty_paths()) - set(meta["dirty"]) - set(meta["files"])
    problems += [f"STRAY {rel}" for rel in sorted(strays)]

    for row in problems + cuts:
        print(row)
    tally = Counter(f"{e['verdict']}: {re.split(r'[,;(]| - ', e['reason'])[0].strip().lower()}" for e in entries if e["verdict"])
    verdicts = Counter(e["verdict"] for e in entries if e["verdict"])
    print(f"{plural(len(entries), 'comment')} in {plural(len(by_file), 'file')}: " + ", ".join(f"{verdicts[v]} {v}" for v in ("delete", "trim", "keep") if verdicts[v]))
    for name, count in sorted(tally.items(), key=lambda item: (("delete", "trim", "keep").index(item[0].split(":")[0]), -item[1])):
        print(f"  {count} {name}")
    print("where each comment is now:")
    for row in after:
        print(f"  {row}")
    if problems:
        print(f"FAILED: {len(problems)} to fix" + (f", {len(cuts)} to read" if cuts else ""))
        sys.exit(1)
    print(f"ok, once you have read the {len(cuts)} above" if cuts else "ok")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    scope = sub.add_parser("scope")
    scope.add_argument("--full", action="store_true")
    scope.add_argument("--base")
    scope.add_argument("paths", nargs="*")
    scope.set_defaults(run=cmd_scope)
    sub.add_parser("apply").set_defaults(run=cmd_apply)
    sub.add_parser("check").set_defaults(run=cmd_check)
    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
