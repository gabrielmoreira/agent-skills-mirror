#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$PWD}"
ROOT="$(cd "$ROOT" && pwd)"

python3 - "$ROOT" <<'PYEOF'
import os
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
home = Path(os.environ.get("HOME", "")).expanduser()

scan_files: list[Path] = []
for candidate in (root / "AGENTS.md", root / "CLAUDE.md"):
    if candidate.is_file():
        scan_files.append(candidate)

for pattern in (".claude/rules/*.md", ".claude/skills/*/SKILL.md"):
    scan_files.extend(sorted(root.glob(pattern)))

ref_re = re.compile(
    r"(?<![\w/.-])("
    r"@[A-Za-z0-9_~/.-]+(?:\.md|/)|"
    r"~/\.claude/[A-Za-z0-9_/.-]+(?:\.md|/)|"
    r"(?:docs|references)/[A-Za-z0-9_/.-]+\.md"
    r")"
)


def resolve_ref(source: Path, raw: str) -> Path:
    ref = raw[1:] if raw.startswith("@") else raw

    if ref.startswith("~/"):
        return (home / ref[2:]).resolve()

    path = Path(ref)
    if path.is_absolute():
        return path.resolve()

    if raw.startswith("@"):
        return (root / ref).resolve()

    if ref.startswith("docs/"):
        return (root / ref).resolve()

    if ref.startswith("references/"):
        source_parts = source.relative_to(root).parts
        if len(source_parts) >= 4 and source_parts[:2] == (".claude", "skills"):
            skill_root = root.joinpath(*source_parts[:3])
            return (skill_root / ref).resolve()
        return (root / ref).resolve()

    return (source.parent / ref).resolve()


missing: list[str] = []
seen: set[tuple[Path, int, str]] = set()
for path in scan_files:
    in_fence = False
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        for match in ref_re.finditer(line):
            raw = match.group(1)
            key = (path, lineno, raw)
            if key in seen:
                continue
            seen.add(key)

            target = resolve_ref(path, raw)
            exists = target.is_dir() if raw.endswith("/") else target.is_file()
            if not exists:
                source = path.relative_to(root)
                missing.append(f"MISSING: {source}:{lineno} -> {raw}")

if missing:
    print("\n".join(missing))
    raise SystemExit(1)

print("doc references: ok")
PYEOF
