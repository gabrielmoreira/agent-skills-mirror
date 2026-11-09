"""Fixed macOS host for the C5 cleanup core, with a live-terminal consent step.

``cleanup_cli.py`` refuses every root operation without a reviewed host. This module
is that host for macOS only. It supplies the four obligations the dispatcher needs:

* ``verify``: the device/user context matches; every root is on a fixed list of
  Claude-owned locations (the owner's macOS cleanup guide, the official Claude Code
  data documentation and a reviewed third-party cleanup list) split into
  ``regenerable`` caches/logs, ``persistent`` Desktop data and ``conversation``
  records (``~/.claude/projects`` and ``history.jsonl``, only when the user chose to
  remove them); nothing under the protected part of ``~/.claude`` (settings, skills,
  plugins, credentials ...) may be a root or inside one; no Claude process is running; and a
  content-verified backup made by this module matches the root, wherever the root
  currently is (active location or the quarantine batch).
* ``approve``: consent is typed by the user in a real terminal, bound to the
  operation and the review digest. No flag, saved JSON, callback or model output can
  supply it, and there is no non-interactive mode. To keep it from nagging, only the
  steps that copy sensitive data or move data ask: ``create_backup``, one ``plan``
  prompt (it covers reading the scope and saving the plan), ``quarantine`` and
  ``restore_cleanup``. Reconciling and saving the private receipt only read what the
  user already approved and write a private record, so they do not ask again.
* ``exclusive``: Claude must not be running when the section is entered or left.
  macOS has no mandatory lock, so this detects and fails; it cannot prevent a start.
* ``cancelled``.

It never deletes anything permanently, never touches credentials in the keychain or
browser data, and never uninstalls applications. Roots that contain a credential file
(``.credentials.json``) or the global CLI config (``~/.claude.json``) are refused as
``credential_scope``; handle those separately. The host also refuses to run when it
was started from Claude Code or the Claude app (``RUNNING_UNDER_CLAUDE``). Process detection is by executable
name, so a Node-launched Claude Code session is not seen: the confirmation text asks
the user to quit every Claude and Claude Code session first.
"""
from contextlib import contextmanager
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import threading

import cleanup_cli
import cleanup_transactions as core
import native_clash_verge_mac as clash

MANIFEST = 'guardian-cleanup-backup/0.1'
BACKUP_PARENT = '.claude-guardian/backups'
MAX_ENTRIES = 2_000_000
CLAUDE_COMMANDS = frozenset({'claude', 'Claude', 'Claude Helper', 'Claude Helper (GPU)',
                             'Claude Helper (Renderer)', 'Claude Helper (Plugin)'})
CLAUDE_BUNDLES = ('/Applications/Claude.app/',)
PHRASE = re.compile(r'CONFIRM [a-z_]{3,24} [0-9a-f]{8}\Z')
OPERATIONS = ('read_hash_scope', 'save_plan', 'quarantine', 'read_reconcile', 'save_receipt',
              'restore_cleanup', 'create_backup')
# One typed phrase per group; the prompt always shows the host's own verified scope.
CONSENT_GROUP = {'read_hash_scope': 'plan', 'save_plan': 'plan', 'quarantine': 'quarantine',
                 'restore_cleanup': 'restore_cleanup', 'create_backup': 'create_backup'}
NO_PROMPT = frozenset({'read_reconcile', 'save_receipt'})  # read-only / private record
CONSEQUENCE = {
    'create_backup': '复制所选目录到私有备份目录（含登录状态等敏感文件，目录权限 0700），并写入内容哈希清单',
    'plan': '读取所选目录做哈希、生成并保存计划（只读，不移动数据）',
    'quarantine': '把所选目录从原位置移到私有隔离目录；移走后相关 Claude 应用会像全新安装一样启动，登录状态会丢失；备份和隔离数据保留，可恢复',
    'restore_cleanup': '把隔离目录里的数据移回原位置',
}


def _platform():
    return sys.platform


def _home():
    import pwd
    return pwd.getpwuid(os.geteuid()).pw_dir


def _list_processes():
    return clash._list_processes()


def context_ref():
    """Opaque device/user binding; a hash only, no names."""
    import socket
    raw = '%d:%s:%s' % (os.geteuid(), socket.gethostname(), _home())
    return 'mac-' + hashlib.sha256(raw.encode()).hexdigest()[:16]


# Under ~/.claude: caches and refetched files (official "nothing user-facing" rows plus
# the reviewed third-party cache list). Everything else there is protected.
CLI_REGENERABLE = ('cache', 'stats-cache.json', 'telemetry', 'usage-data', 'usage.jsonl',
                   'usage.with-fix.jsonl', 'remote-settings.json', 'policy-limits.json',
                   'policy-limits.json.stamp.json', 'shell-snapshots', 'statsig', 'logs', 'image-cache',
                   'debug')
# Conversation records (transcripts with auto memory, prompt history). They can hold old
# command output such as a real public IP, so the user may choose to move them out;
# the Agent asks first (owner 2026-10-25). Never part of a default scope.
CLI_CONVERSATION = ('projects', 'history.jsonl')
CLI_PROTECTED = frozenset({
    '.credentials.json', 'CLAUDE.md', 'agent-memory', 'agents', 'backups', 'commands', 'daemon',
    'file-history', 'hooks', 'jobs', 'keybindings.json', 'mcp-servers',
    'output-styles', 'plans', 'plugins', 'rules', 'scripts', 'session-env', 'sessions',
    'settings.json', 'settings.local.json', 'skills', 'tasks', 'themes', 'todos', 'uploads',
    'workflows'})
LIBRARY_REGENERABLE = ('Library/Caches/claude-cli-nodejs', 'Library/Logs/Claude')
LIBRARY_DESKTOP = ('Library/Application Support/Claude', 'Library/Application Support/Claude-3p',
                   'Library/Application Support/claude-code-desktop',
                   'Library/Application Support/com.anthropic.claudefordesktop',
                   'Library/HTTPStorages/com.anthropic.claudefordesktop',
                   'Library/Preferences/com.anthropic.claudefordesktop.plist',
                   'Library/Saved Application State/com.anthropic.claudefordesktop.savedState',
                   'Library/WebKit/com.anthropic.claudefordesktop')


def is_protected(path, home):
    """The whole ~/.claude, or anything at or under a protected entry of it."""
    claude = home + '/.claude'
    if path == claude:
        return True
    if not path.startswith(claude + '/'):
        return False
    return path[len(claude) + 1:].split('/')[0] in CLI_PROTECTED


def tier(path, home):
    """'regenerable' (caches/logs), 'persistent' (Desktop data, sign-in state),
    'conversation' (transcripts and prompt history) or None."""
    if is_protected(path, home):
        return None
    claude = home + '/.claude/'
    if path.startswith(claude) and path[len(claude):] in CLI_REGENERABLE:
        return 'regenerable'
    if path.startswith(claude) and path[len(claude):] in CLI_CONVERSATION:
        return 'conversation'
    if path in [home + '/' + item for item in LIBRARY_REGENERABLE]:
        return 'regenerable'
    parent, name = os.path.split(path)
    library = home + '/Library'
    if ((parent == library + '/Caches' and name.startswith('com.anthropic.claudefordesktop'))
            or (parent == library + '/Logs/DiagnosticReports' and name.startswith('Claude'))
            or (parent == library + '/Application Support/CrashReporter' and name.startswith('Claude'))):
        return 'regenerable'
    if path in [home + '/' + item for item in LIBRARY_DESKTOP]:
        return 'persistent'
    if (parent == library + '/Preferences/ByHost' and name.startswith('com.anthropic.claudefordesktop')
            and name.endswith('.plist')):
        return 'persistent'
    return None


def classify(path, home):
    """data_kind of a fixed Claude-owned location, or None when it is not on the list."""
    if tier(path, home) is None:
        return None
    return 'cli_app_data' if (path.startswith(home + '/.claude/') or path.endswith('claude-cli-nodejs')) \
        else 'desktop_app_data'


def allowed_locations(home):
    """Human-readable list for proposing a scope; patterns are shown, never expanded."""
    return {'regenerable': ['~/.claude/' + item for item in CLI_REGENERABLE]
            + ['~/' + item for item in LIBRARY_REGENERABLE]
            + ['~/Library/Caches/com.anthropic.claudefordesktop*', '~/Library/Logs/DiagnosticReports/Claude*',
               '~/Library/Application Support/CrashReporter/Claude*'],
            'persistent': ['~/' + item for item in LIBRARY_DESKTOP]
            + ['~/Library/Preferences/ByHost/com.anthropic.claudefordesktop*.plist'],
            'conversation': ['~/.claude/' + item for item in CLI_CONVERSATION],
            'protected_in_dot_claude': sorted(CLI_PROTECTED)}


def _ancestor_commands():
    """Executable paths of this process's ancestors (comm only, never arguments)."""
    import subprocess
    found, pid = [], os.getppid()
    for _ in range(16):
        try:
            done = subprocess.run(['/bin/ps', '-p', str(pid), '-o', 'ppid=,comm='], capture_output=True, text=True,
                                  timeout=5, check=False, shell=False, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
        except (OSError, subprocess.SubprocessError, UnicodeError):
            raise RuntimeError('process ancestry unavailable') from None
        parts = done.stdout.strip().split(None, 1)
        if done.returncode != 0 or len(parts) < 2 or not parts[0].isdigit():
            break
        found.append(parts[1].strip())
        if int(parts[0]) <= 1 or int(parts[0]) == pid:
            break
        pid = int(parts[0])
    return found


def running_under_claude():
    """True when an ancestor is Claude Code or the Claude app; unknown ancestry counts as yes."""
    try:
        commands = _ancestor_commands()
    except Exception:
        return True
    return any(c.startswith(CLAUDE_BUNDLES) or os.path.basename(c) in ('claude', 'claude-code') for c in commands)


def _signature(path):
    """Stat-only inventory; symlinks are recorded, never followed."""
    rows, stack, count = [], [(path, '')], 0
    while stack:
        current, rel = stack.pop()
        info = os.lstat(current)
        count += 1
        if count > MAX_ENTRIES:
            raise OSError('too many entries')
        mode = stat.S_IMODE(info.st_mode)
        if stat.S_ISLNK(info.st_mode):
            rows.append([rel, 'link', 0, info.st_mtime_ns, mode, os.readlink(current)])
        elif stat.S_ISREG(info.st_mode):
            rows.append([rel, 'file', info.st_size, info.st_mtime_ns, mode, None])
        elif stat.S_ISDIR(info.st_mode):
            rows.append([rel, 'dir', 0, info.st_mtime_ns, mode, None])
            with os.scandir(current) as entries:
                stack.extend((entry.path, rel + '/' + entry.name if rel else entry.name) for entry in entries)
        else:
            raise OSError('unsupported file type')
    return sorted(rows)


def _comparable(rows):
    # Directory mtimes change when the backup is read or the tree is moved; compare
    # names, kinds, sizes, file mtimes, modes and link targets.
    return [[r[0], r[1], r[2], r[3] if r[1] == 'file' else 0, r[4], r[5]] for r in rows]


def _hash_tree(path, rows):
    hashes = {}
    for rel, kind, *_ in rows:
        if kind == 'file':
            digest = hashlib.sha256()
            with open(os.path.join(path, rel) if rel else path, 'rb') as handle:
                for chunk in iter(lambda: handle.read(1 << 20), b''):
                    digest.update(chunk)
            hashes[rel] = digest.hexdigest()
    return hashes


def claude_running():
    """True while a Claude app/CLI process is visible; no process list means not proven inactive."""
    try:
        commands = _list_processes()
    except Exception:
        return True
    return any(c.startswith(CLAUDE_BUNDLES) or os.path.basename(c) in CLAUDE_COMMANDS for c in commands)


def terminal_consent(operation, digest, lines, console=None):
    """Consent typed in a real terminal: CONFIRM <operation> <first 8 hex of digest>.

    stdin and stdout must both be TTYs; anything else, including an empty or different
    answer, is a refusal. There is no flag, file or non-interactive path.
    """
    stdin, stdout = console if console else (sys.stdin, sys.stdout)
    try:
        interactive = stdin.isatty() and stdout.isatty()
    except Exception:
        interactive = False
    if not interactive:
        return False
    expected = 'CONFIRM %s %s' % (operation, digest[:8])
    try:
        stdout.write('\n== Claude-Guardian 确认 ==\n' + '\n'.join(lines)
                     + '\n要继续，请输入: %s\n其他任何输入都取消: ' % expected)
        stdout.flush()
        answer = stdin.readline().strip()
    except (OSError, EOFError, KeyboardInterrupt):
        return False
    return PHRASE.fullmatch(answer) is not None and answer == expected


class MacCleanupHost:
    def __init__(self, scope, *, console=None):
        self.scope = cleanup_cli._scope(scope)
        self.scope_digest = core._scope(scope['roots'], scope['protected_paths'], scope['quarantine_directory'],
                                        scope['target_ref'], scope['mode'])
        self.console = console
        self._cancel = threading.Event()
        self._consent = set()
        self._backup_hashes_checked = False
        self.last_refusal = None

    # -- helpers ---------------------------------------------------------
    def backup_directory(self):
        return '%s/%s/%s' % (_home(), BACKUP_PARENT, self.scope['backup_ref'])

    def _claude_running(self):
        return claude_running()

    def _locate(self, index, root):
        """Active path if present, otherwise the quarantined root of the single batch."""
        path = root['path']
        try:
            info = os.lstat(path)
        except FileNotFoundError:
            batches = []
            quarantine = self.scope['quarantine_directory']
            try:
                names = os.listdir(quarantine)
            except OSError:
                return None
            for name in names:
                candidate = '%s/%s/root-%04d' % (quarantine, name, index)
                if os.path.lexists(candidate):
                    batches.append(candidate)
            return batches[0] if len(batches) == 1 else None
        except OSError:
            return None
        return None if stat.S_ISLNK(info.st_mode) or info.st_uid != os.geteuid() else path

    def _manifest(self):
        directory = self.backup_directory()
        if directory not in self.scope['protected_paths']:
            return None
        flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
        try:
            fd = os.open(directory + '/manifest.json', flags)
            with os.fdopen(fd, 'rb') as handle:
                value = json.loads(handle.read(64 * 1024 * 1024).decode('utf-8'))
        except (OSError, ValueError, UnicodeError):
            return None
        roots = self.scope['roots']
        if (type(value) is not dict or value.get('schema_version') != MANIFEST
                or value.get('backup_ref') != self.scope['backup_ref']
                or [r.get('path') for r in value.get('roots', [])] != [r['path'] for r in roots]):
            return None
        return value

    def _backup_ok(self, manifest):
        directory = self.backup_directory()
        if not self._backup_hashes_checked:
            for index, entry in enumerate(manifest['roots']):
                data = '%s/data/root-%04d' % (directory, index)
                try:
                    rows = _signature(data)
                    if _hash_tree(data, rows) != entry['hashes']:
                        return False
                except OSError:
                    return False
            self._backup_hashes_checked = True
        return True

    # -- host interface --------------------------------------------------
    def verify(self, target, scope_digest, bindings):
        result = self._check(target, scope_digest, bindings)
        self.last_refusal = None if result == core.HOST_OK else result
        return result

    def _check(self, target, scope_digest, bindings):
        if _platform() != 'darwin':
            return 'unsupported_platform'
        scope = self.scope
        if (target != scope['target_ref'] or scope_digest != self.scope_digest
                or bindings != {k: scope[k] for k in ('backup_ref', 'host_context_ref')}
                or scope['host_context_ref'] != context_ref()):
            return 'context_mismatch'
        home = _home()
        for root in scope['roots']:
            if root['path'] == home + '/.claude.json':
                return 'credential_scope'
            if is_protected(root['path'], home):
                return 'shared_scope'
            if classify(root['path'], home) != root['data_kind']:
                return 'unknown_ownership'
        if self._claude_running():
            return 'active_host'
        manifest = self._manifest()
        if manifest is None or not self._backup_ok(manifest):
            return 'backup_unverified'
        for index, root in enumerate(scope['roots']):
            located = self._locate(index, root)
            if located is None:
                return 'root_missing'
            try:
                rows = _signature(located)
            except OSError:
                return 'root_unreadable'
            if any(os.path.basename(r[0]) == '.credentials.json' for r in rows):
                return 'credential_scope'
            if _comparable(rows) != _comparable(manifest['roots'][index]['signature']):
                return 'backup_unverified'
        return core.HOST_OK

    def approve(self, operation, digest, target, private_review):
        if operation not in OPERATIONS or type(digest) is not str or not re.fullmatch(r'[0-9a-f]{64}', digest):
            return False
        if operation in NO_PROMPT:
            return True  # Reads what was already approved and saves a private record.
        group = CONSENT_GROUP[operation]
        key = (group, target)
        if key in self._consent:
            return True
        scope = self.scope
        home = _home()
        labels = {'regenerable': '可再生缓存/日志', 'persistent': '桌面端持久数据（含登录状态）',
                  'conversation': '对话记录（含自动记忆和输入历史；移走后无法续接旧会话）', None: '未知'}
        chosen = any(tier(r['path'], home) == 'conversation' for r in scope['roots'])
        lines = ['操作: %s' % group, '目标: %s' % target, '要处理的目录:']
        lines += ['  - %s [%s]' % (r['path'], labels[tier(r['path'], home)]) for r in scope['roots']]
        lines += ['受保护路径:'] + ['  - %s' % p for p in scope['protected_paths']]
        lines += ['隔离目录: %s' % scope['quarantine_directory'], '备份: %s' % self.backup_directory(),
                  '后果: %s' % CONSEQUENCE.get(group, '只读或保存私有记录，不移动数据'),
                  ('本次包含对话记录：旧会话会被移到隔离目录，Claude Code 里看不到也无法续接，需要时可恢复。' if chosen
                   else '对话记录不在本次范围。') + '~/.claude 里的设置、skills、插件、凭据等始终受保护，不会被处理。',
                  '请先退出所有 Claude 桌面端和 Claude Code 会话。永久删除、钥匙串、浏览器数据都不在此范围。']
        if terminal_consent(group, digest, lines, self.console):
            self._consent.add(key)
            return True
        return False

    @contextmanager
    def exclusive(self, target, scope_digest, bindings):
        if self.verify(target, scope_digest, bindings) != core.HOST_OK:
            raise RuntimeError('host scope unverified')
        yield
        if self._claude_running():
            raise RuntimeError('Claude started during cleanup')

    def cancelled(self):
        return self._cancel.is_set()

    # -- backup ----------------------------------------------------------
    def create_backup(self, approve=True):
        """Copy the roots to the private backup directory and write the hash manifest."""
        if _platform() != 'darwin':
            raise core.CleanupError('UNSUPPORTED_PLATFORM')
        scope = self.scope
        directory = self.backup_directory()
        if directory not in scope['protected_paths']:
            raise core.CleanupError('BACKUP_NOT_PROTECTED')
        if scope['host_context_ref'] != context_ref():
            raise core.CleanupError('HOST_BINDING_MISMATCH')
        home = _home()
        if any(is_protected(r['path'], home) for r in scope['roots']):
            raise core.CleanupError('SHARED_SCOPE')
        if any(classify(r['path'], home) != r['data_kind'] for r in scope['roots']):
            raise core.CleanupError('OWNERSHIP_UNVERIFIED')
        if self._claude_running():
            raise core.CleanupError('ACTIVE_HOST')
        if approve and not self.approve('create_backup', hashlib.sha256(
                (self.scope_digest + scope['backup_ref']).encode()).hexdigest(), scope['target_ref'], None):
            raise core.CleanupError('AUTHORIZATION_REQUIRED')
        parent = os.path.dirname(directory)
        os.makedirs(parent, mode=0o700, exist_ok=True)
        os.chmod(os.path.dirname(parent), 0o700)
        os.chmod(parent, 0o700)
        os.mkdir(directory, 0o700)
        entries = []
        for index, root in enumerate(scope['roots']):
            source = root['path']
            before = _signature(source)
            target = '%s/data/root-%04d' % (directory, index)
            os.makedirs(os.path.dirname(target), mode=0o700, exist_ok=True)
            if os.path.isdir(source) and not os.path.islink(source):
                shutil.copytree(source, target, symlinks=True, copy_function=shutil.copy2)
            else:
                shutil.copy2(source, target, follow_symlinks=False)
            self._private(target)
            hashes = _hash_tree(target, _signature(target))
            if _comparable(_signature(source)) != _comparable(before) or hashes != _hash_tree(source, before):
                raise core.CleanupError('SOURCE_CHANGED_DURING_BACKUP')
            entries.append({'root_ref': root['root_ref'], 'path': source, 'signature': before, 'hashes': hashes})
        manifest = json.dumps({'schema_version': MANIFEST, 'backup_ref': scope['backup_ref'],
                               'roots': entries}, sort_keys=True).encode()
        fd = os.open(directory + '/manifest.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as handle:
            handle.write(manifest)
            handle.flush()
            os.fsync(handle.fileno())
        self._backup_hashes_checked = False
        return {'status': 'backup_created', 'roots': len(entries),
                'files': sum(len(e['hashes']) for e in entries), 'manifest_sha256': hashlib.sha256(manifest).hexdigest()}

    @staticmethod
    def _private(path):
        for current, dirs, files in os.walk(path, followlinks=False):
            os.chmod(current, 0o700)
            for name in files:
                full = os.path.join(current, name)
                if not os.path.islink(full):
                    os.chmod(full, 0o600)
        if os.path.isfile(path) and not os.path.islink(path):
            os.chmod(path, 0o600)


HINTS = {
    'RUNNING_UNDER_CLAUDE': '请在普通终端（不是 Claude Code 或 Claude 桌面端里）运行这条命令。',
    'ACTIVE_HOST': '请先退出所有 Claude 桌面端和 Claude Code 会话，再重试；退出后仍提示，多半是残留的后台进程（例如 chrome-native-host），用 ps -axo pid,comm | grep -i claude 查看，确认后结束它。',
    'AUTHORIZATION_REQUIRED': '需要你在真实终端里输入确认页上显示的 CONFIRM 短语；没有终端，或输入不一致，都不会继续。',
    'UNSUPPORTED_PLATFORM': '这个脚本只支持 macOS。Windows 请看 references/windows-cleanup.md。',
    'SCOPE_REQUIRED': '请用 --scope（plan、backup）或 --host-scope（其余命令）给出范围文件。',
    'INVALID_ENTRY_FILE': '--entry-file 需要是权限 0600 的私有 JSON 文件。',
    'INVALID_ARGUMENTS': '命令只支持 context、allowed、backup、plan、quarantine、reconcile、restore。',
    'shared_scope': '这个路径属于受保护范围（设置、skills、插件、凭据等），请改选缓存、日志、桌面端数据或对话记录；allowed 命令会列出可选项。',
    'credential_scope': '这个范围含登录凭据，不能作为清理根；退出登录请用 native_claude_state_mac.py keychain。',
    'unknown_ownership': '这个路径不在固定清单里；allowed 命令会列出可选项。',
    'backup_unverified': '备份不存在、内容不一致或目录在备份之后变过：请先重新运行 backup。',
    'root_missing': '找不到这个根目录（原位置和隔离批次里都没有）。',
    'context_mismatch': 'scope 里的 host_context_ref 与这台机器不符：用 context 命令重新取一个。',
    'active_host': '请先退出所有 Claude 桌面端和 Claude Code 会话，再重试；退出后仍提示，多半是残留的后台进程（例如 chrome-native-host），用 ps -axo pid,comm | grep -i claude 查看，确认后结束它。',
}


def _blocked(code, **extra):
    document = {'status': 'blocked', 'code': code}
    document.update(extra)
    if code in HINTS:
        document['hint'] = HINTS[code]
    print(json.dumps(document), file=sys.stderr)


def main(argv=None, *, console=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if _platform() != 'darwin':
        _blocked('UNSUPPORTED_PLATFORM')
        return 2
    if argv[:1] == ['context']:
        print(json.dumps({'host_context_ref': context_ref()}))
        return 0
    if argv[:1] == ['allowed']:
        print(json.dumps({'allowed': allowed_locations(_home()), 'not_in_scope': [
            '~/.claude (whole directory)', '~/.claude.json (credential_scope)', '~/.local/bin/claude',
            '~/.local/share/claude', '/Applications/Claude.app', 'keychain (see native_claude_state_mac.py)',
            'browser site data']}))
        return 0
    if running_under_claude():
        _blocked('RUNNING_UNDER_CLAUDE')
        return 2
    command = argv[0] if argv else ''
    if command not in ('backup', 'plan', 'quarantine', 'reconcile', 'restore'):
        _blocked('INVALID_ARGUMENTS')
        return 2
    rest, scope_path, entry = argv[1:], None, None
    if '--entry-file' in rest:
        position = rest.index('--entry-file')
        entry_path = rest[position + 1] if position + 1 < len(rest) else None
        del rest[position:position + 2]
        try:
            entry = cleanup_cli._load(entry_path) if entry_path else None
        except (core.CleanupError, cleanup_cli.CLIError, OSError, ValueError):
            _blocked('INVALID_ENTRY_FILE')
            return 2
    if '--host-scope' in rest:
        position = rest.index('--host-scope')
        scope_path = rest[position + 1] if position + 1 < len(rest) else None
        del rest[position:position + 2]
    elif command in ('plan', 'backup') and '--scope' in rest:
        position = rest.index('--scope')
        scope_path = rest[position + 1] if position + 1 < len(rest) else None
    if scope_path is None:
        _blocked('SCOPE_REQUIRED')
        return 2
    try:
        host = MacCleanupHost(cleanup_cli._load(scope_path, cleanup_cli.SCOPE_LIMIT), console=console)
        if command == 'backup':
            print(json.dumps(host.create_backup(), sort_keys=True))
            return 0
        code = cleanup_cli.main([command] + rest, host=host, entry_request=entry)
        if code != 0 and host.last_refusal:
            document = {'host_refusal': host.last_refusal}
            if host.last_refusal in HINTS:
                document['hint'] = HINTS[host.last_refusal]
            print(json.dumps(document), file=sys.stderr)
        return code
    except (core.CleanupError, cleanup_cli.CLIError) as exc:
        _blocked(getattr(exc, 'code', None) or str(exc))
        return 2


if __name__ == '__main__':
    sys.exit(main())
