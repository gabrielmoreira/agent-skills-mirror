#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import kb_common as common  # type: ignore

INDEX_LINK_RE = re.compile(r'\[\[([^\]|#]+)')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Check 02-Index coverage for active canonical notes.')
    parser.add_argument('--cwd', default='.')
    parser.add_argument('--project-id', default='')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = common.find_repo_root(Path(args.cwd).expanduser().resolve())
    binding = common.resolve_binding(repo_root, args.project_id or None)
    rows = common.parse_registry_md(common.registry_path(binding.project_root))
    index_path = binding.project_root / '02-Index.md'
    index_text = common.read_text(index_path)
    index_links = {match.strip() for match in INDEX_LINK_RE.findall(index_text)}

    missing: list[str] = []
    for section in ['Sources', 'Knowledge', 'Experiments', 'Results', 'Writing', 'Maps']:
        for row in rows.get(section, []):
            if row.get('Status') == 'archived':
                continue
            path = row.get('Path', '').strip()
            if not path.startswith('[['):
                continue
            target = path[2:-2]
            if target not in index_links:
                missing.append(target)

    payload = {
        'project_id': binding.project_id,
        'project_root': str(binding.project_root),
        'missing_index_entries': sorted(missing),
        'missing_count': len(missing),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
