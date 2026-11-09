"""macOS: three separate, individually confirmed Claude local-state actions.

* ``keychain``: delete the Claude Code (and optionally Claude Desktop "Safe Storage")
  keychain entries, which signs the CLI/Desktop out. Entries are found with
  ``security find-generic-password`` without ever printing a secret, and removed with
  ``security delete-generic-password``. Not reversible: you sign in again.
* ``simple on|off``: set or remove ``CLAUDE_CODE_SIMPLE`` in ``~/.claude/settings.json``
  ``env`` (documented as equivalent to ``--bare``: minimal system prompt, no hooks,
  skills, plugins, MCP or CLAUDE.md discovery, and OAuth/keychain credentials are not
  read). The file is backed up first, edited as structured JSON and rewritten
  atomically; every other key, including the telemetry settings, is left untouched.
* ``timezone <IANA name>``: set the system time zone to the zone the user names, with
  ``sudo systemsetup``. The password is typed by the user into the native hidden sudo
  prompt; this module never reads it. The previous zone is printed for restoring.

Each action needs the same live-terminal ``CONFIRM <action> <digest8>`` as the cleanup
host, Claude to be not running, and a process that was not started by Claude Code or
the Claude app. There is no identity-ID rotation here or anywhere in this project.
"""
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time

import native_cleanup_mac as base

SECURITY = '/usr/bin/security'
SYSTEMSETUP = '/usr/sbin/systemsetup'
SERVICES = {'credentials': 'Claude Code-credentials', 'safe-storage': 'Claude Safe Storage'}
TELEMETRY_KEYS = ('DISABLE_TELEMETRY', 'DISABLE_ERROR_REPORTING', 'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC')
ZONE = re.compile(r'[A-Za-z0-9_+-]+(?:/[A-Za-z0-9_+-]+){0,2}\Z')
ZONEINFO = '/usr/share/zoneinfo'


class StateError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def _run(argv, *, interactive=False):
    """Fixed absolute command, no shell. Output is captured and never returned."""
    done = subprocess.run(argv, shell=False, check=False, timeout=120,
                          stdin=None if interactive else subprocess.DEVNULL,
                          stdout=None if interactive else subprocess.DEVNULL,
                          stderr=None if interactive else subprocess.DEVNULL)
    return done.returncode


def _current_zone():
    try:
        target = os.readlink('/etc/localtime')
    except OSError:
        return None
    return target.split('/zoneinfo/', 1)[1] if '/zoneinfo/' in target else None


def _wait_for_zone(zone, tries=10, delay=0.5):
    """systemsetup updates /etc/localtime asynchronously; poll briefly before calling it a failure."""
    for attempt in range(tries):
        if _current_zone() == zone:
            return True
        if attempt + 1 < tries:
            time.sleep(delay)
    return False


def _guard(console=None):
    if base._platform() != 'darwin':
        raise StateError('UNSUPPORTED_PLATFORM')
    if base.running_under_claude():
        raise StateError('RUNNING_UNDER_CLAUDE')
    if base.claude_running():
        raise StateError('ACTIVE_HOST')


def _consent(action, token, lines, console):
    digest = hashlib.sha256((action + ':' + token).encode()).hexdigest()
    if not base.terminal_consent(action, digest, lines, console):
        raise StateError('AUTHORIZATION_REQUIRED')


def keychain(services, *, console=None):
    _guard()
    names = [SERVICES[item] for item in services]
    present = []
    for name in names:
        code = _run([SECURITY, 'find-generic-password', '-s', name])
        if code == 0:
            present.append(name)
        elif code != 44:
            raise StateError('KEYCHAIN_LOOKUP_FAILED')
    if not present:
        return {'status': 'nothing_to_delete', 'deleted': 0}
    lines = ['操作: keychain', '将从钥匙串删除这些条目（不显示内容）:'] + ['  - %s' % n for n in present]
    lines += ['后果: 对应的 Claude Code / Claude 桌面端会退出登录，需要重新登录；此操作不可恢复。']
    if 'Claude Safe Storage' in present:
        lines += ['注意: Claude Safe Storage 用于解密桌面端本地数据，删除后桌面端本地登录数据可能无法再读取。']
    _consent('keychain', '|'.join(present), lines, console)
    for name in present:
        if _run([SECURITY, 'delete-generic-password', '-s', name]) not in (0, 44):
            raise StateError('KEYCHAIN_DELETE_FAILED')
    return {'status': 'deleted', 'deleted': len(present)}


def _write_json(path, data):
    mode = os.stat(path).st_mode & 0o777 if os.path.exists(path) else 0o600
    fd, name = tempfile.mkstemp(prefix='.settings.', dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def simple_mode(state, *, console=None):
    if state not in ('on', 'off'):
        raise StateError('INVALID_ARGUMENTS')
    _guard()
    home = base._home()
    path = home + '/.claude/settings.json'
    try:
        if os.path.exists(path):
            with open(path, 'rb') as handle:
                raw = handle.read()
        else:
            raw = b'{}'
        data = json.loads(raw.decode('utf-8'))
    except (OSError, ValueError, UnicodeError):
        raise StateError('SETTINGS_UNREADABLE') from None
    if type(data) is not dict or type(data.get('env', {})) is not dict:
        raise StateError('SETTINGS_STRUCTURE_UNSUPPORTED')
    env = dict(data.get('env', {}))
    if state == 'on':
        env['CLAUDE_CODE_SIMPLE'] = '1'
    else:
        env.pop('CLAUDE_CODE_SIMPLE', None)
    updated = dict(data)
    updated['env'] = env
    if state == 'off' and 'CLAUDE_CODE_SIMPLE' not in data.get('env', {}):
        return {'status': 'unchanged'}
    if updated == data:
        return {'status': 'unchanged'}
    lines = ['操作: simple_mode (%s)' % state, '文件: %s（修改前自动备份）' % path,
             '后果: ' + ('启用后使用最小系统提示词，只保留 Bash、文件读写工具，不自动发现 hooks、skills、plugins、MCP、自动记忆和 CLAUDE.md；'
                        '不读取 OAuth 令牌和钥匙串凭据，认证只能用 ANTHROPIC_API_KEY 或 apiKeyHelper，订阅登录在此模式下不可用。'
                        if state == 'on' else '移除该设置，恢复正常模式。'),
             '其余设置（含遥测相关键）保持不变。']
    _consent('simple_mode', state + ':' + hashlib.sha256(raw).hexdigest(), lines, console)
    backup_dir = home + '/' + base.BACKUP_PARENT
    os.makedirs(backup_dir, mode=0o700, exist_ok=True)
    backup = '%s/settings.json.%s' % (backup_dir, datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    fd = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    _write_json(path, updated)
    with open(path, encoding='utf-8') as handle:
        after = json.load(handle)
    if any(after.get('env', {}).get(k) != data.get('env', {}).get(k) for k in TELEMETRY_KEYS):
        raise StateError('TELEMETRY_SETTINGS_CHANGED')
    return {'status': 'updated', 'state': state, 'backup_created': True}


def timezone(zone, *, console=None):
    if type(zone) is not str or not ZONE.fullmatch(zone) or '..' in zone or not os.path.isfile('%s/%s' % (ZONEINFO, zone)):
        raise StateError('INVALID_TIMEZONE')
    _guard()
    before = _current_zone()
    if before == zone:
        return {'status': 'unchanged'}
    lines = ['操作: timezone', '当前时区: %s' % (before or '未知'), '目标时区: %s' % zone,
             '后果: 修改整台 Mac 的系统时区（影响所有应用的时间显示和时间戳）。需要管理员密码：只在随后出现的 sudo 隐藏提示里输入，本工具不读取。',
             '恢复: sudo systemsetup -settimezone %s' % (before or '<原时区>')]
    _consent('timezone', '%s>%s' % (before, zone), lines, console)
    if _run(['/usr/bin/sudo', SYSTEMSETUP, '-settimezone', zone], interactive=True) != 0:
        raise StateError('TIMEZONE_CHANGE_FAILED')
    if not _wait_for_zone(zone):
        raise StateError('TIMEZONE_VERIFY_FAILED')
    return {'status': 'updated', 'previous': before, 'current': zone}


def main(argv=None, *, console=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        if argv[:1] == ['keychain']:
            if any(not a.startswith('--service=') for a in argv[1:]):
                raise StateError('INVALID_ARGUMENTS')
            chosen = [a.split('=', 1)[1] for a in argv[1:]] or ['credentials']
            if any(c not in SERVICES for c in chosen):
                raise StateError('INVALID_ARGUMENTS')
            result = keychain(sorted(set(chosen)), console=console)
        elif argv[:1] == ['simple'] and len(argv) == 2:
            result = simple_mode(argv[1], console=console)
        elif argv[:1] == ['timezone'] and len(argv) == 2:
            result = timezone(argv[1], console=console)
        else:
            raise StateError('INVALID_ARGUMENTS')
    except StateError as exc:
        document = {'status': 'blocked', 'code': exc.code}
        if exc.code in base.HINTS:
            document['hint'] = base.HINTS[exc.code]
        print(json.dumps(document), file=sys.stderr)
        return 2
    except (OSError, subprocess.SubprocessError):
        print(json.dumps({'status': 'blocked', 'code': 'IO_FAILURE'}), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
