#!/usr/bin/env python3
"""List the comments in scope, then prove a comment sweep changed nothing but comments.

  comments.py list [--base REF] [PATH ...]   Print every comment in scope and snapshot its files.
  comments.py check                           Compare those files with the snapshot.

The scope is the comments touching lines this branch adds or changes: the diff from the merge-base
with REF (default: origin's default branch, else main or master), including staged, unstaged, and
untracked files. PATHs (files or directories) narrow that diff; they never widen it.
Vendored, generated, minified, and migration files are skipped and listed as such.

list prints `path:line: kind: text`, where kind is
  comment    a plain comment
  doc        a Python docstring (runtime-visible as __doc__)
  directive  a comment a tool reads: suppressions, build tags, pragmas, doctests, licences, ...

check prints one line per snapshotted file and exits 1 if anything but plain comments changed:
  ok         the code is token-for-token what it was
  CODE       the code differs; the line is in the current file
  DIRECTIVE  a directive comment was removed or edited; the line is in the snapshot
"""

import argparse
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import tokenize
from collections import Counter
from pathlib import Path

C = {"line": ["//"], "block": [("/*", "*/")], "quotes": "\"'", "char": True}
JS = {"line": ["//"], "block": [("/*", "*/")], "quotes": "\"'`", "template": True, "regex": True}
HASH = {"line": ["#"], "block": [], "quotes": "\"'", "word_hash": True, "lines": True}
SHELL = {**HASH, "heredoc": re.compile(r"<<-?\s*(['\"]?)([A-Za-z_]\w*)\1")}
RUBYISH = {**HASH, "heredoc": re.compile(r"<<[~-]?(['\"]?)([A-Z_][A-Z0-9_]*)\1")}
LANGS = {
    **dict.fromkeys(".js .mjs .cjs .jsx .ts .mts .cts .tsx".split(), JS),
    **dict.fromkeys(".c .h .cc .cpp .cxx .hpp .hh .m .mm .cs .java .dart .groovy .gradle .proto .zig".split(), C),
    **dict.fromkeys(".kt .kts .scala .swift .rs".split(), {**C, "nest": True}),
    ".go": {**C, "quotes": "\"'`"},
    ".css": {"line": [], "block": [("/*", "*/")], "quotes": "\"'"},
    **dict.fromkeys(".scss .less".split(), {"line": ["//"], "block": [("/*", "*/")], "quotes": "\"'"}),
    ".php": {**C, "line": ["//", "#"], "attr_hash": True},
    ".tf": {**C, "line": ["//", "#"]},
    **dict.fromkeys(".sh .bash .zsh".split(), SHELL),
    **dict.fromkeys(".rb .rake .pl .pm".split(), RUBYISH),
    **dict.fromkeys(".fish .r .ex .exs .yaml .yml .toml .graphql .gql .nix .ps1 .cfg .ini .conf".split(), HASH),
    ".sql": {"line": ["--"], "block": [("/*", "*/")], "quotes": "'\"", "sql": True},
    ".lua": {"line": ["--"], "block": [("--[[", "]]")], "quotes": "\"'"},
    ".hs": {"line": ["--"], "block": [("{-", "-}")], "quotes": "\"", "nest": True},
    **dict.fromkeys(".html .htm .xml .svg".split(), {"line": [], "block": [("<!--", "-->")], "quotes": ""}),
    **dict.fromkeys(".vue .svelte .astro".split(), {**JS, "block": [("<!--", "-->"), ("/*", "*/")], "regex": False}),
    ".py": "python",
    ".pyi": "python",
}
NAMES = {"Dockerfile": HASH, "Containerfile": HASH, "Makefile": HASH, "GNUmakefile": HASH, "Rakefile": RUBYISH, "Gemfile": RUBYISH}
JS_LIKE = {ext for ext, spec in LANGS.items() if isinstance(spec, dict) and spec.get("template")}
JS_FAMILY = set(".js .mjs .cjs .jsx .vue .svelte .astro".split())  # where JSDoc tags are the types

SKIP_DIRS = {"node_modules", "vendor", "third_party", "third-party", "dist", "build", "out", ".next", "target", "coverage", "__pycache__", ".git", "Pods", ".venv", "venv"}
SKIP_FILE = re.compile(r"\.min\.\w+$|\.(pb|pb\.gw)\.go$|_pb2(_grpc)?\.pyi?$|\.g\.dart$|\.freezed\.dart$|\.generated\.\w+$|\.gen\.\w+$")
MIGRATION_DIR = {"migrations", "migration", "migrate", "db_migrations", "alembic"}
GENERATED = re.compile(r"@generated|DO NOT EDIT|Code generated|auto-?generated", re.I)

DIRECTIVE_START = re.compile(
    r"""(
      eslint-(disable|enable)\b | jshint | tslint: | @ts-(ignore|expect-error|nocheck|check)\b | \$FlowFixMe | @flow\b
    | prettier-ignore | biome-ignore | deno-(lint-)?ignore | dprint-ignore | oxlint- | stylelint- | @jsx | @refresh\b
    | (istanbul|c8|v8|node:coverage)\s+(ignore|disable|enable) | @vite-ignore | webpack[A-Z] | [#@]__[A-Z_]+__
    | go:[a-z] | \+build\b | nolint | lint:(ignore|file-ignore) | noqa | pragma | pylint: | mypy: | pyright:
    | fmt:\s*(off|on|skip) | isort: | ruff: | -\*- | vim?: | coding[:=] | nosec | rubocop: | frozen_string_literal:
    | typed:\s*(ignore|false|true|strict|strong) | :nocov: | shellcheck | yamllint | yaml-language-server:
    | (syntax|escape|check)= | NOLINT | clang-format | cppcheck-suppress | coverity | noinspection | CHECKSTYLE
    | @formatter: | language= | NOSONAR | nosemgrep | gitleaks:allow | trufflehog:ignore | tfsec:ignore | checkov:skip
    | trivy:ignore | deepcode\s+ignore | cspell: | spell-?checker: | swiftlint: | swift-tools-version | SAFETY:
    | \[if\s | <!\[endif | htmlmin: | sourceMappingURL=
    )""",
    re.X,
)
DIRECTIVE_ANY = re.compile(
    r"SPDX-License-Identifier|copyright|\(c\)\s*\d{4}|@license|@preserve|@generated|DO NOT EDIT|@deprecated\b|^\s*Deprecated:",
    re.I | re.M,
)
DIRECTIVE_BY_EXT = {
    ".go": re.compile(r"export\s+\w+\s*$|#cgo|#include"),
    ".py": re.compile(r"type:"),
    ".pyi": re.compile(r"type:"),
    ".sql": re.compile(r"\+goose|\+migrate|name:\s*\w+\s+:\w+|changeset\s|liquibase"),
}
ESLINT_BLOCK = re.compile(r"(eslint|eslint-env|globals?|exported)\s")  # only read from /* */ comments
JSDOC_TYPE = re.compile(r"@(type|typedef|template|satisfies|import|callback|overload|implements|extends)\b|@(param|returns?|property|prop|this|enum)\s*\{")
MARKERS = re.compile(r"^(<!--|//+|/\*+!?|\{-|--\[\[|--|#+)|(\*/|-->|-\}|\]\])$")


def inner(text):
    """The comment's words without its markers or leading `*` gutter."""
    body = MARKERS.sub("", text.strip()).strip()
    return "\n".join(re.sub(r"^\s*\*\s?", "", line) for line in body.splitlines()).strip()


def kind_of(text, line, ext, doc=False):
    words = inner(text)
    by_ext = DIRECTIVE_BY_EXT.get(ext)
    if (
        (line == 1 and text.startswith("#!"))
        or text.startswith(("/*!", "/// <reference", "/// <amd-"))
        or (ext == ".sql" and text.startswith("/*+"))
        or DIRECTIVE_START.match(words)
        or DIRECTIVE_ANY.search(words)
        or (by_ext and by_ext.match(words))
        or (ext in JS_LIKE and text.startswith("/*") and ESLINT_BLOCK.match(words))
        or (ext in JS_FAMILY and JSDOC_TYPE.search(words))
        or (ext == ".rs" and "```" in words and text.startswith(("///", "//!")))
        or (doc and ">>>" in words)
    ):
        return "directive"
    return "doc" if doc else "comment"


def scan(src, spec):
    """Split source into code tokens and comments: ([(token, line)], [(text, line, own_line)])."""
    tokens, comments = [], []
    i, n, line = 0, len(src), 1
    word, word_line = [], 1
    braces = []  # one counter per open `${` in a template literal
    last_code_line = 0

    def emit(tok, at):
        nonlocal last_code_line
        if spec.get("lines") and tokens and at > last_code_line:
            tokens.append(("\n", at))
        tokens.append((tok, at))
        last_code_line = at + tok.count("\n")

    def flush():
        if word:
            emit("".join(word), word_line)
            word.clear()

    def own_line(at):
        return not src[src.rfind("\n", 0, at) + 1 : at].strip()

    def prev_sig():
        return tokens[-1][0] if tokens else ""

    def read_quoted(j, q, escapes=True):
        k = j + 1
        while k < n:
            if escapes and src[k] == "\\":
                k += 2
                continue
            if src[k] == q:
                return k + 1
            if src[k] == "\n" and q in "\"'" and not spec.get("sql"):
                return k  # unterminated: stop at end of line
            k += 1
        return n

    def read_template(j):
        """From just after ` or }, to just past the closing ` or the next ${."""
        k = j
        while k < n:
            if src[k] == "\\":
                k += 2
                continue
            if src[k] == "`":
                return k + 1, False
            if src.startswith("${", k):
                return k + 2, True
            k += 1
        return n, False

    heredocs = []  # delimiters whose bodies start on the next line

    while i < n:
        c = src[i]
        if c == "\n" and heredocs:
            flush()
            start = i + 1
            for delim in heredocs:
                m = re.compile(rf"^[ \t]*{re.escape(delim)}[ \t]*$", re.M).search(src, start)
                start = m.end() if m else n
            emit(src[i + 1 : start], line + 1)
            line += src.count("\n", i, start)
            heredocs.clear()
            i = start
            continue
        m = spec.get("heredoc") and c == "<" and spec["heredoc"].match(src, i)
        if m:
            flush()
            heredocs.append(m.group(2))
            emit(m.group(0), line)
            i = m.end()
            continue
        matched = False
        for opener, closer in spec["block"]:
            if src.startswith(opener, i):
                flush()
                depth, k = 1, i + len(opener)
                while k < n and depth:
                    if spec.get("nest") and src.startswith(opener, k):
                        depth, k = depth + 1, k + len(opener)
                    elif src.startswith(closer, k):
                        depth, k = depth - 1, k + len(closer)
                    else:
                        k += 1
                comments.append((src[i:k], line, own_line(i)))
                line += src.count("\n", i, k)
                i, matched = k, True
                break
        if matched:
            continue
        marker = next((m for m in spec["line"] if src.startswith(m, i)), None)
        if marker == "#" and spec.get("attr_hash") and src.startswith("#[", i):
            marker = None
        if marker == "#" and spec.get("word_hash") and i > 0 and not (src[i - 1].isspace() or src[i - 1] == ";"):
            marker = None
        if marker:
            flush()
            k = src.find("\n", i)
            k = n if k < 0 else k
            comments.append((src[i:k], line, own_line(i)))
            i = k
            continue
        if braces and c in "{}":
            flush()
            if c == "{":
                braces[-1] += 1
            elif braces[-1]:
                braces[-1] -= 1
            else:
                braces.pop()
                k, opened = read_template(i + 1)
                emit(src[i:k], line)
                line += src.count("\n", i, k)
                if opened:
                    braces.append(0)
                i = k
                continue
            emit(c, line)
            i += 1
            continue
        if c in spec["quotes"]:
            flush()
            if c == "`" and spec.get("template"):
                k, opened = read_template(i + 1)
                if opened:
                    braces.append(0)
            elif c == "'" and spec.get("char") and not re.match(r"'(\\.|[^\\'\n])'", src[i : i + 4]) and not re.match(r"'\\u\{?[0-9a-fA-F]+\}?'", src[i : i + 12]):
                emit(c, line)  # a lifetime or label, not a char literal
                i += 1
                continue
            elif src.startswith(c * 3, i) and c != "`":
                k = src.find(c * 3, i + 3)
                k = n if k < 0 else k + 3
            else:
                k = read_quoted(i, c, escapes=c != "`")
            emit(src[i:k], line)
            line += src.count("\n", i, k)
            i = k
            continue
        if c == "/" and spec.get("regex") and not word and (not tokens or prev_sig() in set("(,=:[!&|?{};+-*%<>~^") or prev_sig() in ("return", "typeof", "case", "in", "of", "void", "yield", "await")):
            k, in_class = i + 1, False
            while k < n and src[k] != "\n":
                if src[k] == "\\":
                    k += 2
                    continue
                if src[k] == "[":
                    in_class = True
                elif src[k] == "]":
                    in_class = False
                elif src[k] == "/" and not in_class:
                    break
                k += 1
            if k < n and src[k] == "/":
                k += 1
                while k < n and src[k].isalpha():
                    k += 1
                emit(src[i:k], line)
                i = k
                continue
        if c == "\n":
            flush()
            line += 1
        elif c.isspace():
            flush()
        elif c.isalnum() or c in "_$":
            if not word:
                word_line = line
            word.append(c)
        else:
            flush()
            emit(c, line)
        i += 1
    flush()
    return tokens, comments


def scan_python(src):
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    tokens, comments = [], []
    sig = [t for t in toks if t.type not in (tokenize.NL, tokenize.COMMENT)]
    docs, ends = set(), set()  # docstring starts, and the NEWLINEs that end those statements
    for k, t in enumerate(sig):
        before = sig[k - 1].type if k else tokenize.NEWLINE
        after = sig[k + 1].type if k + 1 < len(sig) else tokenize.NEWLINE
        if t.type == tokenize.STRING and before in (tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT) and after in (tokenize.NEWLINE, tokenize.ENDMARKER):
            docs.add(t.start)
            if k + 1 < len(sig) and after == tokenize.NEWLINE:
                ends.add(sig[k + 1].start)
    for t in toks:
        if t.type == tokenize.COMMENT:
            comments.append((t.string, t.start[0], not t.line[: t.start[1]].strip()))
        elif t.type == tokenize.STRING and t.start in docs:
            comments.append((t.string, t.start[0], True, "doc"))
        elif t.type in (tokenize.INDENT, tokenize.DEDENT, tokenize.NEWLINE):
            if not (t.type == tokenize.NEWLINE and t.start in ends):
                tokens.append((tokenize.tok_name[t.type], t.start[0]))
        elif t.type not in (tokenize.NL, tokenize.ENDMARKER):
            tokens.append((t.string, t.start[0]))
    return tokens, comments


def spec_for(path):
    return NAMES.get(Path(path).name) or LANGS.get(Path(path).suffix.lower())


def lex(path, src):
    """([(token, line)], [(text, line, kind)]) or None when no lexer fits."""
    src = src.replace("\r\n", "\n")
    spec, ext = spec_for(path), Path(path).suffix.lower()
    if spec is None:
        return None
    if spec == "python":
        try:
            tokens, raw = scan_python(src)
        except (tokenize.TokenError, SyntaxError):
            tokens, raw = scan(src, {**HASH, "lines": False})
    else:
        tokens, raw = scan(src, spec)
    return tokens, merge_runs([(*r[:3], kind_of(r[0], r[1], ext, doc=len(r) > 3)) for r in raw], ext)


def merge_runs(raw, ext):
    """Join own-line comments on consecutive lines into one comment, as a reader sees them.

    Directive lines stay alone so a block can't hide them, except in `///` and `//!` doc blocks,
    which are judged whole (a doctest spans many lines)."""
    merged = []
    for text, line, own, kind in raw:
        marker = re.match(r"\s*(///|//!|//|#|--)?", text).group(1)
        if merged and own and merged[-1][3] and marker and marker == merged[-1][4]:
            prev_text, prev_line, prev_kind, _, _ = merged[-1]
            joinable = marker in ("///", "//!") or (kind == prev_kind == "comment")
            if joinable and line == prev_line + prev_text.count("\n") + 1:
                joined = prev_text + "\n" + text
                merged[-1] = [joined, prev_line, kind_of(joined, prev_line, ext), True, marker]
                continue
        merged.append([text, line, kind, own and not text.lstrip().startswith(("/*", "<!--")), marker])
    return [(text, line, kind) for text, line, kind, _, _ in merged]


def git(*args, check=True):
    done = subprocess.run(["git", "-c", "core.quotePath=false", *args], capture_output=True, text=True)
    if check and done.returncode:
        sys.exit(f"git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout


def repo_root():
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return Path(out.stdout.strip()) if out.returncode == 0 else Path.cwd()


def default_base():
    head = git("symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD", check=False).strip()
    if head:
        return head
    for ref in ("main", "master", "origin/main", "origin/master"):
        if subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref], capture_output=True).returncode == 0:
            return ref
    sys.exit("No base branch found: pass --base REF.")


def added_lines(base):
    """{path: set of added line numbers, or None for a wholly new file}, relative to the repo root."""
    mb = git("merge-base", "HEAD", base).strip()
    added, path = {}, None
    for row in git("diff", "--unified=0", "--no-color", "--no-ext-diff", "--find-renames", mb, "--").splitlines():
        if row.startswith("+++ "):
            path = None if row == "+++ /dev/null" else row[6:]
            if path:
                added.setdefault(path, set())
        elif row.startswith("@@") and path:
            m = re.match(r"@@ -\S+ \+(\d+)(?:,(\d+))? @@", row)
            start, count = int(m.group(1)), int(m.group(2) or 1)
            added[path].update(range(start, start + count))
    for path in git("ls-files", "--others", "--exclude-standard").splitlines():
        added[path] = None
    return added


def skip_reason(rel, root):
    parts = Path(rel).parts
    if any(p in SKIP_DIRS for p in parts[:-1]):
        return "vendored or build output"
    if any(p.lower() in MIGRATION_DIR for p in parts[:-1]):
        return "migration (checksum tools hash the whole file)"
    if SKIP_FILE.search(rel):
        return "generated or minified"
    try:
        with open(root / rel, encoding="utf-8", errors="replace") as fh:
            head = "".join(fh.readline() for _ in range(5))
    except OSError:
        return "unreadable"
    if GENERATED.search(head):
        return "generated"
    if spec_for(rel) is None:
        return "no lexer for this file type: review it by hand"
    return None


def snapshot_dir(root):
    return Path(tempfile.gettempdir()) / "comment-sweep" / hashlib.sha1(str(root).encode()).hexdigest()[:12]


def read(path):
    return Path(path).read_text(encoding="utf-8", errors="replace")


def cmd_list(args):
    root = repo_root()
    base = args.base or default_base()
    scope = added_lines(base)
    if args.paths:
        within = [Path(p).resolve().relative_to(root) for p in args.paths]
        scope = {rel: lines for rel, lines in scope.items() if any(w in (Path(rel), *Path(rel).parents) for w in within)}
    if not scope:
        sys.exit(f"Nothing in scope: this branch changes no files{' under ' + ' '.join(args.paths) if args.paths else ''} since {base}.")
    snap = snapshot_dir(root)
    shutil.rmtree(snap, ignore_errors=True)
    snap.mkdir(parents=True)
    kept, total = [], 0
    for rel in sorted(scope):
        if not (root / rel).is_file():
            continue
        reason = skip_reason(rel, root)
        if reason:
            print(f"{rel}: skip: {reason}")
            continue
        _, comments = lex(rel, read(root / rel))
        lines = scope[rel]
        for text, start, kind in comments:
            span = range(start, start + text.count("\n") + 1)
            if lines is None or any(n in lines for n in span):
                first = " ".join(text.split())
                print(f"{rel}:{start}: {kind}: {first[:160]}{'…' if len(first) > 160 else ''}")
                total += 1
        (snap / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, snap / rel)
        kept.append(rel)
    (snap / ".manifest.json").write_text(json.dumps({"root": str(root), "files": kept}))
    print(f"{total} comments in scope across {len(kept)} files; snapshot taken for `check`.")


def cmd_check(_args):
    root = repo_root()
    snap = snapshot_dir(root)
    try:
        files = json.loads((snap / ".manifest.json").read_text())["files"]
    except FileNotFoundError:
        sys.exit("No snapshot: run `comments.py list` before editing.")
    failed = False
    for rel in files:
        if not (root / rel).is_file():
            print(f"CODE       {rel}  file was deleted")
            failed = True
            continue
        old_tokens, old_comments = lex(rel, read(snap / rel))
        new_tokens, new_comments = lex(rel, read(root / rel))
        old_text, new_text = [t for t, _ in old_tokens], [t for t, _ in new_tokens]
        if old_text != new_text:
            k = next((k for k, (a, b) in enumerate(zip(old_text, new_text)) if a != b), min(len(old_text), len(new_text)))
            at = new_tokens[k][1] if k < len(new_tokens) else (new_tokens[-1][1] if new_tokens else 1)
            near = " ".join(t.replace("\n", "⏎") for t in new_text[max(0, k - 3) : k + 4])
            print(f"CODE       {rel}:{at}  code differs from the snapshot near: {near[:120]}")
            failed = True
        directives_now = Counter(" ".join(t.split()) for t, _, kind in new_comments if kind == "directive")
        for text, start, kind in old_comments:
            key = " ".join(text.split())
            if kind != "directive":
                continue
            if directives_now[key]:
                directives_now[key] -= 1
            else:
                print(f"DIRECTIVE  {rel}:{start}  removed or edited: {key[:120]}")
                failed = True
        before = Counter(" ".join(t.split()) for t, _, _ in old_comments)
        after = Counter(" ".join(t.split()) for t, _, _ in new_comments)
        removed, added = sum((before - after).values()), sum((after - before).values())
        if old_text == new_text:
            print(f"ok         {rel}  -{removed} +{added} comments")
    print("FAILED: revert every CODE change; keep a DIRECTIVE change only if its tool proves it unused." if failed else "PASSED: only comments changed.")
    return 1 if failed else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_list = sub.add_parser("list", help="print the comments in scope and snapshot their files")
    p_list.add_argument("--base", help="branch the current one will merge into")
    p_list.add_argument("paths", nargs="*", help="files or directories that narrow the branch diff")
    sub.add_parser("check", help="compare the snapshotted files with the working tree")
    args = parser.parse_args()
    return cmd_list(args) if args.cmd == "list" else cmd_check(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
