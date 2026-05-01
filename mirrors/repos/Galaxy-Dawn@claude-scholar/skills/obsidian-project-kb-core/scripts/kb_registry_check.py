#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import kb_common as common  # type: ignore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Check registry coverage for the bound project KB.')
    parser.add_argument('--cwd', default='.')
    parser.add_argument('--project-id', default='')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = common.find_repo_root(Path(args.cwd).expanduser().resolve())
    binding = common.resolve_binding(repo_root, args.project_id or None)
    rels = common.scan_canonical_relpaths(binding.project_root)
    rows = common.parse_registry_md(common.registry_path(binding.project_root))

    active_entries: list[tuple[str, str]] = []
    ids: dict[str, list[str]] = {}
    for section, entries in rows.items():
        if section == 'Archive':
            continue
        for row in entries:
            link = row.get('Path', '')
            active_entries.append((section, link))
            rid = row.get('ID', '')
            if rid:
                ids.setdefault(rid, []).append(link)

    desired = {common.wikilink(rel) for rel in rels}
    registered = {link for _, link in active_entries if link}
    missing = sorted(rel for rel in rels if common.wikilink(rel) not in registered)
    dangling = sorted(link for link in registered if link not in desired)
    duplicate_ids = {rid: paths for rid, paths in ids.items() if len(paths) > 1}

    payload = {
        'project_id': binding.project_id,
        'project_root': str(binding.project_root),
        'canonical_count': len(rels),
        'registered_count': len(registered),
        'missing_registry_entries': missing,
        'dangling_registry_entries': dangling,
        'duplicate_ids': duplicate_ids,
        'coverage_ok': not missing and not dangling and not duplicate_ids,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
