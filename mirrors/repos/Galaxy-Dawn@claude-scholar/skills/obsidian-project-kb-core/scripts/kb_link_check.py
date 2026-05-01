#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import kb_common as common  # type: ignore

WIKILINK_RE = re.compile(r'\[\[([^\]]+)\]\]')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Check wikilinks inside the bound project KB.')
    parser.add_argument('--cwd', default='.')
    parser.add_argument('--project-id', default='')
    return parser.parse_args()


def normalize_target(target: str) -> str:
    target = target.split('|', 1)[0].split('#', 1)[0].strip()
    for suffix in ('.md', '.canvas'):
        if target.endswith(suffix):
            target = target[:-len(suffix)]
            break
    return target


def build_targets(project_root: Path) -> tuple[set[str], dict[str, list[str]]]:
    exact: set[str] = set()
    stems: dict[str, list[str]] = {}
    for suffix in ('*.md', '*.canvas'):
        for path in project_root.rglob(suffix):
            rel = str(path.relative_to(project_root)).replace(os.sep, '/')
            note_ref = rel[:-len(path.suffix)]
            exact.add(note_ref)
            stems.setdefault(path.stem, []).append(note_ref)
    return exact, stems


def main() -> None:
    args = parse_args()
    repo_root = common.find_repo_root(Path(args.cwd).expanduser().resolve())
    binding = common.resolve_binding(repo_root, args.project_id or None)
    exact, stems = build_targets(binding.project_root)
    broken: list[dict[str, str]] = []

    for path in sorted(binding.project_root.rglob('*.md')):
        rel = str(path.relative_to(binding.project_root)).replace(os.sep, '/')
        if rel.startswith('_system/'):
            continue
        text = path.read_text(encoding='utf-8')
        for raw in WIKILINK_RE.findall(text):
            target = normalize_target(raw)
            if not target or target.startswith('#'):
                continue
            if target in exact:
                continue
            basename = Path(target).name
            if basename in stems and len(stems[basename]) == 1:
                continue
            broken.append({'file': rel, 'target': target})

    payload = {
        'project_id': binding.project_id,
        'project_root': str(binding.project_root),
        'broken_links': broken,
        'broken_count': len(broken),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
