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
    parser = argparse.ArgumentParser(description='Scaffold a project KB skeleton.')
    parser.add_argument('--cwd', default='.')
    parser.add_argument('--project-id', default='')
    parser.add_argument('--vault-path', default='')
    parser.add_argument('--project-name', default='')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--note-language', default='en')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = common.find_repo_root(Path(args.cwd).expanduser().resolve())
    if args.vault_path:
        result = common.bootstrap_binding(
            repo_root,
            Path(args.vault_path),
            project_name=args.project_name or None,
            force=args.force,
            note_language=args.note_language,
        )
    else:
        binding = common.resolve_binding(repo_root, args.project_id or None)
        common.ensure_project_scaffold(binding.project_root, binding.project_slug, common.titleize_slug(binding.project_slug), force=args.force)
        result = {
            'project_id': binding.project_id,
            'project_root': str(binding.project_root),
            'scaffold_refreshed': True,
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
