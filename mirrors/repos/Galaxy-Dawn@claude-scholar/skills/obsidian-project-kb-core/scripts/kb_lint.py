#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import kb_common as common  # type: ignore

WIKILINK_RE = re.compile(r'\[\[([^\]|#]+)')
SOURCE_LINK_RE = re.compile(r'\[\[(Sources/[^\]|#]+)')
EXPERIMENT_LINK_RE = re.compile(r'\[\[(Experiments/[^\]|#]+)')
RESULT_LINK_RE = re.compile(r'\[\[(Results/[^\]|#]+)')
ARCHIVED_RESULT_LINK_RE = re.compile(r'\[\[(Archive/Results/[^\]|#]+)')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Aggregate KB lint checks and write _system/lint-report.md.')
    parser.add_argument('--cwd', default='.')
    parser.add_argument('--project-id', default='')
    return parser.parse_args()


def run_json(script_name: str, cwd: Path, project_id: str) -> dict:
    cmd = ['python3', str(SCRIPT_DIR / script_name), '--cwd', str(cwd)]
    if project_id:
        cmd.extend(['--project-id', project_id])
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def note_refs_in_file(path: Path) -> set[str]:
    text = path.read_text(encoding='utf-8')
    return {match.strip() for match in WIKILINK_RE.findall(text)}


def main() -> None:
    args = parse_args()
    repo_root = common.find_repo_root(Path(args.cwd).expanduser().resolve())
    binding = common.resolve_binding(repo_root, args.project_id or None)

    registry_check = run_json('kb_registry_check.py', repo_root, binding.project_id)
    link_check = run_json('kb_link_check.py', repo_root, binding.project_id)
    index_check = run_json('kb_index_check.py', repo_root, binding.project_id)
    canvas_check = run_json('kb_canvas_check.py', repo_root, binding.project_id)

    rows = common.parse_registry_md(common.registry_path(binding.project_root))
    knowledge_without_sources: list[str] = []
    for row in rows.get('Knowledge', []):
        target = row.get('Path', '')
        if not target.startswith('[['):
            continue
        note_ref = target[2:-2]
        note_path = binding.project_root / f'{note_ref}.md'
        if note_path.exists():
            text = note_path.read_text(encoding='utf-8')
            if not SOURCE_LINK_RE.search(text):
                knowledge_without_sources.append(note_ref)

    experiments_without_results: list[str] = []
    experiments_with_only_archived_results: list[str] = []
    for row in rows.get('Experiments', []):
        target = row.get('Path', '')
        if not target.startswith('[['):
            continue
        note_ref = target[2:-2]
        note_path = binding.project_root / f'{note_ref}.md'
        if note_path.exists():
            text = note_path.read_text(encoding='utf-8')
            has_active_result = bool(RESULT_LINK_RE.search(text))
            has_archived_result = bool(ARCHIVED_RESULT_LINK_RE.search(text))
            if not has_active_result and not has_archived_result:
                experiments_without_results.append(note_ref)
            elif has_archived_result and not has_active_result:
                experiments_with_only_archived_results.append(note_ref)

    result_refs = {row.get('Path', '')[2:-2] for row in rows.get('Results', []) if row.get('Path', '').startswith('[[')}
    results_without_experiments: list[str] = []
    for note_ref in sorted(result_refs):
        note_path = binding.project_root / f'{note_ref}.md'
        if note_path.exists():
            text = note_path.read_text(encoding='utf-8')
            if not EXPERIMENT_LINK_RE.search(text):
                results_without_experiments.append(note_ref)

    archived_refs = {row.get('Archived Path', '')[2:-2] for row in rows.get('Archive', []) if row.get('Archived Path', '').startswith('[[')}
    active_notes_referencing_archived_notes: list[str] = []
    active_md_files = []
    for p in binding.project_root.rglob('*.md'):
        rel = str(p.relative_to(binding.project_root)).replace(os.sep, '/')
        if rel.startswith('Archive/') or rel.startswith('_system/'):
            continue
        active_md_files.append(p)
    for path in active_md_files:
        refs = note_refs_in_file(path)
        shared = sorted(ref for ref in refs if ref in archived_refs)
        for ref in shared:
            active_notes_referencing_archived_notes.append(f'{path.relative_to(binding.project_root).as_posix()} -> {ref}')

    daily_candidates: list[str] = []
    for daily_path in sorted((binding.project_root / 'Daily').glob('*.md')):
        text = daily_path.read_text(encoding='utf-8')
        if 'TODO' in text or 'Open Questions' in text or 'Promote' in text:
            daily_candidates.append(daily_path.relative_to(binding.project_root).as_posix())

    summary_rows = [
        ('Broken links', 'pass' if link_check['broken_count'] == 0 else 'fail', link_check['broken_count']),
        ('Missing registry entries', 'pass' if not registry_check['missing_registry_entries'] else 'fail', len(registry_check['missing_registry_entries'])),
        ('Dangling registry entries', 'pass' if not registry_check['dangling_registry_entries'] else 'fail', len(registry_check['dangling_registry_entries'])),
        ('Missing index entries', 'pass' if index_check['missing_count'] == 0 else 'warn', index_check['missing_count']),
        ('Canvas issues', 'pass' if canvas_check['issue_count'] == 0 else 'warn', canvas_check['issue_count']),
        ('Knowledge without sources', 'pass' if not knowledge_without_sources else 'warn', len(knowledge_without_sources)),
        ('Experiments without results', 'pass' if not experiments_without_results else 'warn', len(experiments_without_results)),
        ('Experiments with only archived results', 'pass' if not experiments_with_only_archived_results else 'warn', len(experiments_with_only_archived_results)),
        ('Results without experiments', 'pass' if not results_without_experiments else 'warn', len(results_without_experiments)),
        ('Daily promotion candidates', 'pass' if not daily_candidates else 'warn', len(daily_candidates)),
        ('Active notes referencing archived notes', 'pass' if not active_notes_referencing_archived_notes else 'warn', len(active_notes_referencing_archived_notes)),
    ]

    lines = ['# Lint Report', '', f'Last checked: {common.now_iso()}', '', '## Summary', '', '| Check | Status | Count |', '|---|---|---|']
    lines.extend(f'| {name} | {status} | {count} |' for name, status, count in summary_rows)
    lines.extend(['', '## Issues', ''])

    def add_issue_block(title: str, items: list[str]) -> None:
        lines.append(f'### {title}')
        if items:
            lines.extend(f'- {item}' for item in items)
        else:
            lines.append('- None.')
        lines.append('')

    add_issue_block('Missing Registry Entries', registry_check['missing_registry_entries'])
    add_issue_block('Dangling Registry Entries', registry_check['dangling_registry_entries'])
    add_issue_block('Broken Wikilinks', [f"{item['file']} -> {item['target']}" for item in link_check['broken_links']])
    add_issue_block('Missing Index Entries', index_check['missing_index_entries'])
    add_issue_block('Canvas Issues', [f"{item['file']} -> {item['issue']}" for item in canvas_check['canvas_issues']])
    add_issue_block('Knowledge Notes Without Sources', knowledge_without_sources)
    add_issue_block('Experiments Without Results', experiments_without_results)
    add_issue_block('Experiments With Only Archived Results', experiments_with_only_archived_results)
    add_issue_block('Results Without Experiments', results_without_experiments)
    add_issue_block('Daily Promotion Candidates', daily_candidates)
    add_issue_block('Active Notes Referencing Archived Notes', active_notes_referencing_archived_notes)

    lines.extend(['## Recommended Fixes', ''])
    fixes: list[str] = []
    if registry_check['missing_registry_entries']:
        fixes.append('Add registry rows for all missing canonical notes.')
    if link_check['broken_count']:
        fixes.append('Repair or remove broken wikilinks before the next sync.')
    if index_check['missing_count']:
        fixes.append('Update 02-Index.md so active canonical notes remain navigable.')
    if experiments_with_only_archived_results:
        fixes.append('Decide whether archived result links should stay historical or be promoted back into active Results.')
    if daily_candidates:
        fixes.append('Promote durable content from Daily into Knowledge, Experiments, Results, or Writing.')
    if not fixes:
        fixes.append('No action required.')
    lines.extend(f'- {fix}' for fix in fixes)
    lines.append('')

    report_path = binding.project_root / '_system' / 'lint-report.md'
    common.write_text(report_path, '\n'.join(lines))

    payload = {
        'project_id': binding.project_id,
        'project_root': str(binding.project_root),
        'lint_report': str(report_path),
        'broken_links': link_check['broken_count'],
        'missing_registry_entries': len(registry_check['missing_registry_entries']),
        'missing_index_entries': index_check['missing_count'],
        'knowledge_without_sources': len(knowledge_without_sources),
        'experiments_without_results': len(experiments_without_results),
        'experiments_with_only_archived_results': len(experiments_with_only_archived_results),
        'results_without_experiments': len(results_without_experiments),
        'daily_promotion_candidates': len(daily_candidates),
        'active_notes_referencing_archived_notes': len(active_notes_referencing_archived_notes),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
