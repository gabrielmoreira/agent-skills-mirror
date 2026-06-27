#!/usr/bin/env python3
"""Codex hook adapter for oh-story writing projects.

This script intentionally has no third-party dependencies. It adapts the core
story guardrails to Codex hook stdin/stdout JSON contracts.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


HOOK_CWD: Path | None = None


def read_hook_input() -> dict[str, Any]:
    global HOOK_CWD
    # Read raw UTF-8 bytes, not the locale-decoded text stream: Codex/Claude tool
    # payloads carry Chinese 正文/细纲 paths, and Windows Python defaults stdin to the
    # ANSI code page (cp1252/cp936), which mojibakes them so the prose guard never
    # matches and silently allows (issue #164 class — same fix as the bash hooks).
    raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    if not raw.strip():
        return {}
    try:
        obj = json.loads(raw)
        if not isinstance(obj, dict):
            return {}
        cwd = obj.get("cwd")
        if isinstance(cwd, str) and Path(cwd).is_dir():
            HOOK_CWD = Path(cwd).resolve()
        return obj
    except Exception:
        return {}


def emit(obj: dict[str, Any] | None) -> None:
    if obj:
        # Write UTF-8 bytes directly: Windows Python stdout defaults to the ANSI code
        # page and would garble/raise on the Chinese deny reasons and additionalContext.
        sys.stdout.buffer.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))


def _deployed_root_from_file() -> Path | None:
    """Self-locate the project root from this script's deployed path.

    story-setup deploys this hook to <root>/.codex/hooks/story_codex_hook.py, so the
    project root is __file__'s great-grandparent. This is the most reliable resolver on
    Windows: the launcher computes the root in (Git Bash) shell as an MSYS path like
    /c/proj, which does NOT survive as a native-Python env var or cwd — but __file__ is
    always a native path. So a non-git project launched from a nested cwd still resolves.
    """
    try:
        here = Path(__file__).resolve()
    except Exception:
        return None
    if here.parent.name == "hooks" and here.parent.parent.name == ".codex":
        root = here.parent.parent.parent
        if root.is_dir():
            return root
    return None


def project_root() -> Path:
    for env_name in ("CODEX_PROJECT_DIR", "CLAUDE_PROJECT_DIR"):
        value = os.environ.get(env_name)
        if not value:
            continue
        try:
            candidate = Path(value)
            if candidate.is_dir():
                return candidate.resolve()
        except Exception:
            pass
    deployed = _deployed_root_from_file()
    if deployed is not None:
        return deployed
    start = HOOK_CWD if HOOK_CWD and HOOK_CWD.is_dir() else Path.cwd()
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(start),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if out:
            return Path(out).resolve()
    except Exception:
        pass
    return start.resolve()


def safe_rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return str(path)


def read_active_book(root: Path) -> Path | None:
    active_file = root / ".active-book"
    if active_file.exists():
        first = active_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        if first:
            candidate = (root / first[0].strip()).resolve()
            try:
                candidate.relative_to(root.resolve())
            except Exception:
                candidate = None  # type: ignore[assignment]
            if candidate and candidate.exists():
                return candidate
    for track in root.glob("**/追踪"):
        if any(part.startswith(".") for part in track.relative_to(root).parts):
            continue
        return track.parent
    for body in root.glob("**/正文"):
        if any(part.startswith(".") for part in body.relative_to(root).parts):
            continue
        return body.parent
    for body_file in root.glob("**/正文.md"):
        if any(part.startswith(".") for part in body_file.relative_to(root).parts):
            continue
        return body_file.parent
    return None


def hook_context(event: str, text: str) -> dict[str, Any]:
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}


def session_start() -> None:
    root = project_root()
    messages: list[str] = []
    sentinel = root / ".story-deployed"
    if sentinel.exists():
        sent_text = sentinel.read_text(encoding="utf-8", errors="ignore")
        if "target_cli:" not in sent_text:
            messages.append("[story-setup] .story-deployed 缺少 target_cli 字段；建议重新运行 $story-setup。")
        elif "codex" not in re.search(r"target_cli:\s*(.*)", sent_text).group(1):  # type: ignore[union-attr]
            messages.append("[story-setup] 当前部署标记未包含 codex；如需 Codex hooks/agents，请重新运行 $story-setup 并选择 Codex。")
    book = read_active_book(root)
    if book:
        ctx = book / "追踪" / "上下文.md"
        if ctx.exists():
            messages.append(f"[story context] Active book: {safe_rel(root, book)}. Read {safe_rel(root, ctx)} before continuing long-form writing.")
        else:
            messages.append(f"[story context] Active story project detected: {safe_rel(root, book)}.")
    if messages:
        emit(hook_context("SessionStart", "\n".join(messages)))


def resolve_target(root: Path, target: str) -> Path:
    normalized = target.replace("\\", "/")
    p = Path(normalized)
    return p if p.is_absolute() else (root / p).resolve()


def extract_prose_targets_from_command(command: str) -> list[str]:
    # Only treat a 正文 path as a write target when it is the destination of an actual
    # write op (redirection / tee / touch / cp|mv dest). Scanning the whole command would
    # flag any heredoc body, doc string, or grep pattern that merely *mentions*
    # 正文/第N章.md and wrongly deny the edit.
    token = r"['\"]?([^\s'\"<>|;&()]*正文[^\s'\"<>|;&()]*)['\"]?"
    targets: list[str] = []
    for m in re.finditer(r">>?\s*" + token, command):  # > dest, >> dest, cat >dest
        targets.append(m.group(1))
    # Use an explicit start/separator class, not \b: \b is Unicode-aware in Python re but ASCII-only
    # in JS, so an ASCII boundary keeps this identical to opencode plugin.ts (parity).
    for m in re.finditer(r"(?:^|[\s;&|(){}<>])(?:tee(?:\s+-a)?|touch)\s+" + token, command):
        targets.append(m.group(1))
    # cp/mv: the write destination is the last positional arg of the segment. Parse it (regex can't
    # tell a 正文 source from a 正文 dest, and a trailing 2>/dev/null / >log / || breaks end-anchoring).
    for seg in re.split(r"[;&|\n]", command):
        seg = re.split(r"\d*[<>]", seg)[0]  # drop redirections (incl. 2>) and everything after
        words = seg.split()
        if len(words) >= 2 and words[0] in ("cp", "mv"):
            positionals = [w for w in words[1:] if not w.startswith("-")]
            if positionals and "正文" in positionals[-1]:
                targets.append(positionals[-1].strip("'\""))
    return targets


def extract_apply_patch_targets(command: str) -> list[str]:
    targets: list[str] = []
    for line in command.splitlines():
        m = re.match(r"^\*\*\* (?:Add|Update) File: (.+)$", line.strip())
        if m:
            targets.append(m.group(1).strip())
    return targets


def target_paths_from_hook(obj: dict[str, Any]) -> list[Path]:
    root = project_root()
    tool_name = str(obj.get("tool_name") or "")
    tool_input = obj.get("tool_input") if isinstance(obj.get("tool_input"), dict) else {}
    assert isinstance(tool_input, dict)
    raw_targets: list[str] = []
    for key in ("file_path", "filePath", "path", "target", "filename"):
        value = tool_input.get(key)
        if isinstance(value, str):
            raw_targets.append(value)
    command = tool_input.get("command")
    if isinstance(command, str):
        if tool_name == "Bash":
            raw_targets.extend(extract_prose_targets_from_command(command))
        else:
            raw_targets.extend(extract_apply_patch_targets(command))
            raw_targets.extend(extract_prose_targets_from_command(command))
    return [resolve_target(root, t) for t in raw_targets if t]


def prose_block_reason(root: Path, abs_path: Path) -> str | None:
    base = abs_path.name
    parent = abs_path.parent.name
    if base == "正文.md":
        if abs_path.exists():
            return None
        book_dir = abs_path.parent
        if (root / "拆文库" / book_dir.name).exists():
            return None
        if not (book_dir / "设定.md").exists():
            return None
        if not (book_dir / "小节大纲.md").exists():
            return f"⛔ 写正文被拦截：{safe_rel(root, abs_path)} 缺少同目录 小节大纲.md。先按 story-short-write 完成小节大纲再写正文。"
        return None
    if parent != "正文":
        return None
    if not re.match(r"^第.*章.*\.md$", base):
        return None
    if abs_path.exists():
        return None
    m = re.match(r"^第0*(\d+)章", base)
    if not m:
        return None
    num = m.group(1)
    book_dir = abs_path.parent.parent
    if (root / "拆文库" / book_dir.name).exists():
        return None
    outline_dir = book_dir / "大纲"
    found = False
    if outline_dir.is_dir():
        for candidate in outline_dir.iterdir():
            fm = re.match(r"^细纲_第0*(\d+)章.*\.md$", candidate.name)
            if fm and fm.group(1) == num:
                found = True
                break
    if not found:
        return f"⛔ 写正文被拦截：第 {num} 章缺少细纲（{safe_rel(root, outline_dir)}/细纲_第{num}章.md）。先按 story-long-write 单章流程补建细纲再写正文。"
    return None


def pre_tool_prose_guard(obj: dict[str, Any]) -> None:
    root = project_root()
    for path in target_paths_from_hook(obj):
        reason = prose_block_reason(root, path)
        if reason:
            emit({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            })
            return


def find_command(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("command", "cmd", "script"):
            if isinstance(value.get(key), str):
                return value[key]
        for key in ("tool_input", "input", "parameters", "args"):
            found = find_command(value.get(key))
            if found:
                return found
    return ""


def is_git_commit_command(raw: str) -> bool:
    raw = raw.replace("\r\n", "\n").replace("\r", "\n").replace("\n", " ; ")
    try:
        lexer = shlex.shlex(raw, posix=True, punctuation_chars="();|&{}")
        lexer.whitespace_split = True
        tokens = list(lexer)
    except TypeError:
        try:
            tokens = shlex.split(raw, posix=True)
        except Exception:
            tokens = raw.split()
    except Exception:
        tokens = raw.split()
    assignment = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
    separators = {";", "&&", "||", "|", "|&", "&"}
    openers = {"(", "{"}
    closers = {")",
        "}",
    }
    control_words = {"then", "do", "else", "elif"}
    wrappers = {"command", "noglob"}
    git_options_with_value = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--super-prefix", "--config-env"}

    def skip_shell_wrappers(i: int) -> int:
        while i < len(tokens):
            tok = tokens[i]
            if tok in openers or assignment.match(tok) or tok in wrappers:
                i += 1
                continue
            if tok == "env":
                i += 1
                while i < len(tokens):
                    if assignment.match(tokens[i]) or tokens[i] in {"-i", "--ignore-environment"}:
                        i += 1
                        continue
                    break
                continue
            break
        return i

    def is_git_commit_at(i: int) -> bool:
        if i >= len(tokens) or tokens[i] != "git":
            return False
        i += 1
        while i < len(tokens):
            tok = tokens[i]
            if tok in closers or tok in separators:
                return False
            if tok == "commit":
                return True
            if tok == "--":
                i += 1
                continue
            if tok in git_options_with_value:
                i += 2
                continue
            if any(tok.startswith(prefix + "=") for prefix in git_options_with_value if prefix.startswith("--")):
                i += 1
                continue
            if tok.startswith("-c") and tok != "-c":
                i += 1
                continue
            if tok.startswith("-"):
                i += 1
                continue
            return False
        return False

    segment_start = True
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok in separators or tok in control_words:
            segment_start = True
            i += 1
            continue
        if segment_start or tok in openers:
            start = skip_shell_wrappers(i)
            if is_git_commit_at(start):
                return True
            segment_start = False
        i += 1
    return False


def staged_markdown_warnings(root: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "-c", "core.quotepath=false", "diff", "--cached", "--relative", "--name-only", "--diff-filter=ACM", "-z", "--", "."],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return ""
    warnings: list[str] = []
    for raw in proc.stdout.split(b"\0"):
        if not raw:
            continue
        file = raw.decode("utf-8", errors="ignore")
        if not file.endswith(".md"):
            continue
        full = root / file
        if not full.exists():
            continue
        text = full.read_text(encoding="utf-8", errors="ignore")
        if file == "正文.md" or "/正文.md" in file or file.startswith("正文/") or "/正文/" in file:
            hits = []
            for idx, line in enumerate(text.splitlines(), 1):
                if re.search(r"(身高|体重|年龄)(\s|　)*(：|:)(\s|　)*[0-9]+", line):
                    hits.append(f"{idx}:{line}")
            if hits:
                warnings.append(f"⚠ {file}: Hardcoded character attributes found (should reference 设定/ files):\n" + "\n".join(hits))
        if file.startswith("设定/") or "/设定/" in file:
            if not re.search(r"^(\s|　)*(名字|姓名|名称|name|Name)(\s|　)*(：|:)", text, re.M):
                warnings.append(f"⚠ {file}: Setting file missing required fields (name/名字: ...)")
    if not warnings:
        return ""
    return "=== Story Commit Warnings (advisory only, not blocking) ===\n" + "\n".join(warnings) + "\n=== End Warnings ==="


def pre_tool_commit_advisory(obj: dict[str, Any]) -> None:
    command = find_command(obj)
    if not command or not is_git_commit_command(command):
        return
    warnings = staged_markdown_warnings(project_root())
    if warnings:
        emit(hook_context("PreToolUse", warnings))


def compact_summary(event: str) -> None:
    root = project_root()
    lines = ["=== Story Compact Summary ==="]
    book = read_active_book(root)
    if book:
        ctx = book / "追踪" / "上下文.md"
        if ctx.exists():
            line_count = len(ctx.read_text(encoding="utf-8", errors="ignore").splitlines())
            lines.append(f"Writing context: {safe_rel(root, ctx)} ({line_count} lines)")
        else:
            lines.append(f"Active story project: {safe_rel(root, book)}")
    else:
        lines.append("Active state: not found")
    try:
        # -z + bytes so a Chinese filename under a user-global core.quotepath=false can't raise
        # UnicodeDecodeError on a Windows ANSI code page (these are counts only).
        changed = subprocess.check_output(["git", "-C", str(root), "-c", "core.quotepath=false", "diff", "--name-only", "-z"], stderr=subprocess.DEVNULL)
        staged = subprocess.check_output(["git", "-C", str(root), "-c", "core.quotepath=false", "diff", "--name-only", "--cached", "-z"], stderr=subprocess.DEVNULL)
        n_changed = len([x for x in changed.split(b"\0") if x])
        n_staged = len([x for x in staged.split(b"\0") if x])
        lines.append(f"Git: {n_changed} unstaged, {n_staged} staged")
    except Exception:
        pass
    emit({"systemMessage": "\n".join(lines)})


def stop_event() -> None:
    # Stop hooks require JSON on stdout. Default: no-op JSON success.
    emit({"continue": True})


def main() -> int:
    event = sys.argv[1] if len(sys.argv) > 1 else ""
    obj = read_hook_input()
    if event == "session-start":
        session_start()
    elif event == "pre-tool-prose-guard":
        pre_tool_prose_guard(obj)
    elif event == "pre-tool-commit-advisory":
        pre_tool_commit_advisory(obj)
    elif event == "pre-compact":
        compact_summary("PreCompact")
    elif event == "post-compact":
        compact_summary("PostCompact")
    elif event == "stop":
        stop_event()
    else:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
