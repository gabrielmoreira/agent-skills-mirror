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
    parser = argparse.ArgumentParser(description='Validate project canvas files.')
    parser.add_argument('--cwd', default='.')
    parser.add_argument('--project-id', default='')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = common.find_repo_root(Path(args.cwd).expanduser().resolve())
    binding = common.resolve_binding(repo_root, args.project_id or None)
    issues: list[dict[str, str]] = []
    for canvas_path in sorted((binding.project_root / 'Maps').glob('*.canvas')):
        rel = str(canvas_path.relative_to(binding.project_root)).replace(os.sep, '/')
        try:
            data = json.loads(canvas_path.read_text(encoding='utf-8'))
        except Exception as exc:
            issues.append({'file': rel, 'issue': f'invalid-json: {exc}'})
            continue
        for node in data.get('nodes', []):
            if node.get('type') != 'file':
                continue
            file_ref = str(node.get('file', '')).strip()
            if not file_ref:
                issues.append({'file': rel, 'issue': 'file-node-missing-path'})
                continue
            target = binding.vault_path / file_ref
            if not target.exists():
                issues.append({'file': rel, 'issue': f'missing-target: {file_ref}'})

    payload = {
        'project_id': binding.project_id,
        'project_root': str(binding.project_root),
        'canvas_issues': issues,
        'issue_count': len(issues),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
