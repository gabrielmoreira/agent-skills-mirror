#!/usr/bin/env python3
"""Check whether this installed Skill matches the latest Skill on GitHub.

Read-only: two HTTPS GET requests to api.github.com (the repository tree and the
recent commits that touched the Skill), nothing is downloaded into the Skill and
nothing is changed. Files are compared by git blob hash, so no version number
has to be bumped by hand. Contacts only GitHub, never Claude or Anthropic.

Exit codes: 0 up to date, 1 update available, 2 check failed (network, rate
limit, unexpected reply), 130 cancelled.
"""
import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_REPO = 'DUNHKpcc/Claude-Guardian'
DEFAULT_REF = 'main'
SKILL_PREFIX = 'skills/claude-guardian/'
API = 'https://api.github.com'
MAX_BYTES = 8 * 1024 * 1024
IGNORED_PARTS = {'__pycache__', '.DS_Store', '.git'}
IGNORED_SUFFIXES = ('.pyc', '.pyo')
SKILL_ROOT = Path(__file__).resolve().parents[1]


class CheckError(Exception):
    """A reason the check could not finish; reported as check_failed."""


def blob_hash(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def local_hashes(root):
    """Map relative path -> set of acceptable blob hashes (raw, and CRLF normalised to LF)."""
    found = {}
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if not path.is_file() or path.is_symlink() or IGNORED_PARTS & set(rel.parts) or path.name.endswith(IGNORED_SUFFIXES):
            continue
        data = path.read_bytes()
        # The top-level LICENSE is copied in by package_skill.py and lives outside the Skill folder upstream.
        if rel.as_posix() == 'LICENSE':
            continue
        found[rel.as_posix()] = {blob_hash(data), blob_hash(data.replace(b'\r\n', b'\n'))}
    return found


def fetch_json(url, timeout):
    request = urllib.request.Request(url, headers={'Accept': 'application/vnd.github+json',
                                                   'User-Agent': 'claude-guardian-update-check'})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 429):
            raise CheckError('GitHub 拒绝或限流了这次请求（HTTP %d），稍后再查' % exc.code)
        raise CheckError('GitHub 返回 HTTP %d' % exc.code)
    except (urllib.error.URLError, OSError) as exc:
        raise CheckError('连不上 GitHub：%s' % getattr(exc, 'reason', exc))
    if len(body) > MAX_BYTES:
        raise CheckError('GitHub 的回复过大，没有处理')
    try:
        return json.loads(body.decode('utf-8'))
    except (UnicodeDecodeError, ValueError):
        raise CheckError('GitHub 的回复不是有效的 JSON')


def remote_hashes(tree):
    if not isinstance(tree, dict) or not isinstance(tree.get('tree'), list):
        raise CheckError('GitHub 的目录树格式不对')
    if tree.get('truncated'):
        raise CheckError('GitHub 返回的目录树被截断，无法完整比较')
    found = {}
    for entry in tree['tree']:
        if not isinstance(entry, dict) or entry.get('type') != 'blob':
            continue
        path, sha = entry.get('path'), entry.get('sha')
        if isinstance(path, str) and isinstance(sha, str) and path.startswith(SKILL_PREFIX):
            found[path[len(SKILL_PREFIX):]] = sha
    if 'SKILL.md' not in found:
        raise CheckError('远端分支里没有找到 %sSKILL.md' % SKILL_PREFIX)
    return found


def recent_commits(commits, limit):
    out = []
    if not isinstance(commits, list):
        return out
    for item in commits[:limit]:
        try:
            out.append({'sha': item['sha'][:7], 'date': item['commit']['committer']['date'][:10],
                        'subject': item['commit']['message'].splitlines()[0][:160]})
        except (KeyError, TypeError, AttributeError, IndexError):
            continue
    return out


def compare(local, remote):
    changed = sorted(p for p in local.keys() & remote.keys() if remote[p] not in local[p])
    return {'changed': changed,
            'upstream_only': sorted(remote.keys() - local.keys()),
            'local_only': sorted(local.keys() - remote.keys())}


def check(root=SKILL_ROOT, repo=DEFAULT_REPO, ref=DEFAULT_REF, timeout=8.0, commits=5, fetch=fetch_json):
    quoted_repo = '/'.join(urllib.parse.quote(part, safe='') for part in repo.split('/'))
    quoted_ref = urllib.parse.quote(ref, safe='')
    report = {'repo': repo, 'ref': ref, 'skill_root': str(root)}
    try:
        if not (root / 'SKILL.md').is_file():
            raise CheckError('本地 Skill 目录里没有 SKILL.md：%s' % root)
        local = local_hashes(root)
        remote = remote_hashes(fetch('%s/repos/%s/git/trees/%s?recursive=1' % (API, quoted_repo, quoted_ref), timeout))
        diff = compare(local, remote)
        try:
            history = recent_commits(fetch('%s/repos/%s/commits?sha=%s&path=%s&per_page=%d' % (
                API, quoted_repo, quoted_ref, urllib.parse.quote(SKILL_PREFIX.rstrip('/'), safe=''), commits), timeout), commits)
        except CheckError:
            history = []  # The file comparison already answered the question; history is a bonus.
    except CheckError as exc:
        report.update(status='check_failed', reason=str(exc))
        return report
    report.update(diff, recent_updates=history,
                  status='update_available' if diff['changed'] or diff['upstream_only'] else 'up_to_date')
    return report


def summary(report):
    lines = []
    status = report['status']
    if status == 'check_failed':
        lines.append('没查到更新：%s。本次先用已安装的版本继续。' % report['reason'])
        return '\n'.join(lines)
    if status == 'up_to_date':
        lines.append('Skill 已是最新（与 %s 的 %s 分支一致）。' % (report['repo'], report['ref']))
    else:
        lines.append('Skill 有更新：%d 个文件和远端不同，远端新增 %d 个文件。' % (
            len(report['changed']), len(report['upstream_only'])))
        for label, key in (('不同', 'changed'), ('远端新增', 'upstream_only')):
            names = report[key]
            if names:
                lines.append('  %s：%s%s' % (label, '、'.join(names[:12]), ' 等' if len(names) > 12 else ''))
    if report['local_only']:
        lines.append('本地独有 %d 个文件（自己加的，或远端已删除）：%s' % (
            len(report['local_only']), '、'.join(report['local_only'][:12])))
    if report['recent_updates']:
        lines.append('远端最近的更新：')
        for item in report['recent_updates']:
            lines.append('  %s %s %s' % (item['date'], item['sha'], item['subject']))
    return '\n'.join(lines)


EXIT = {'up_to_date': 0, 'update_available': 1, 'check_failed': 2}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Compare this installed Skill with the latest one on GitHub (read-only; '
                                                 'contacts only api.github.com).')
    sub = parser.add_subparsers(dest='command', required=True)
    go = sub.add_parser('check', help='compare local files with the remote branch and list recent updates')
    go.add_argument('--repo', default=DEFAULT_REPO, help='owner/name on GitHub (default %(default)s)')
    go.add_argument('--ref', default=DEFAULT_REF, help='branch to compare with (default %(default)s)')
    go.add_argument('--timeout', type=float, default=8.0, help='seconds per request (default %(default)s)')
    go.add_argument('--json', action='store_true', help='print the JSON report instead of the summary')
    args = parser.parse_args(argv)
    if args.timeout <= 0 or args.timeout > 60:
        parser.error('--timeout must be between 0 and 60 seconds')
    if args.repo.count('/') != 1 or not all(args.repo.split('/')):
        parser.error('--repo must look like owner/name')
    try:
        report = check(repo=args.repo, ref=args.ref, timeout=args.timeout)
    except KeyboardInterrupt:
        print('已取消，没有检查更新。', file=sys.stderr)
        return 130
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')  # The Windows console default cannot print Chinese.
    print(json.dumps(report, ensure_ascii=False, indent=1) if args.json else summary(report))
    return EXIT[report['status']]


if __name__ == '__main__':
    sys.exit(main())
