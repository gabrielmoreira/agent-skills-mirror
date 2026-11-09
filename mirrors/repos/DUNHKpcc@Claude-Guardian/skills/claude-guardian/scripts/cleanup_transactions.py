"""Explicit C5 data quarantine, using exact, independently verified POSIX roots.

The trusted host establishes ownership, inactive applications and exclusions, and
holds exclusive access during each mutation. host_check(target_ref, scope_digest)
returns HOST_OK freshly; authorize(operation, digest, target_ref) returns True
only for the user's current exact approval. Neither callback nor the resulting
journal is proof of OS isolation, ownership attribution or user consent.

There is no discovery, purge, credential/browser adapter, uninstall, subprocess,
network, or application launch. Private manifests contain paths and file hashes,
never file contents. This is a recoverable multi-root move, not an atomic batch.
"""
import hashlib
import json
import math
import os
import re
import stat
import time
import uuid
from contextlib import contextmanager

try:
    import transactions as tx
except ModuleNotFoundError as _transaction_import_error:
    if _transaction_import_error.name != 'transactions':
        raise
    # Standalone Agent file-path loading uses this exact installed sibling,
    # without changing sys.path or relying on an earlier import by a test.
    import importlib.util as _transaction_importlib
    from pathlib import Path as _TransactionPath
    _transaction_spec = _transaction_importlib.spec_from_file_location(
        '_guardian_cleanup_transactions_support',
        _TransactionPath(__file__).with_name('transactions.py'))
    tx = _transaction_importlib.module_from_spec(_transaction_spec)
    _transaction_spec.loader.exec_module(tx)

MODE = 'C5-full-local-data'
HOST_OK = 'verified_inactive_claude_data'
MAX_ROOTS = 16
MAX_ENTRIES = 4096
MAX_BYTES = 64 * 1024 * 1024
MAX_DEPTH = 32
MAX_DOCUMENT = 4 * 1024 * 1024
_PLAN = 'guardian-cleanup-plan/0.1'
_RECEIPT = 'guardian-cleanup-receipt/0.1'
_BATCH = 'guardian-cleanup-batch/0.1'
_ID = re.compile(r'[a-zA-Z][a-zA-Z0-9_-]{0,63}\Z')
_SECRET = re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16})\Z')
_ROW = {'relative', 'kind', 'device', 'inode', 'mode', 'uid', 'gid',
        'nlink', 'size', 'mtime_ns', 'ctime_ns', 'sha256'}


class CleanupError(Exception):
    """Only fixed codes and bounded recovery identifiers are public."""
    def __init__(self, code, *, recovery_id=None, moved_count=0, stage='before_write'):
        super().__init__(code)
        self.code = code
        self.recovery_id = recovery_id
        self.moved_count = moved_count
        self.stage = stage


def _fail(code):
    raise CleanupError(code) from None


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _hex(value, length):
    return type(value) is str and len(value) == length and all(c in '0123456789abcdef' for c in value)


def _identifier(value):
    if type(value) is not str or not _ID.fullmatch(value) or _SECRET.fullmatch(value):
        _fail('INVALID_IDENTIFIER')


def _keys(value, fields):
    if type(value) is not dict or set(value) != set(fields):
        _fail('INVALID_DOCUMENT')


def _encode(value):
    budget = [500000, MAX_DOCUMENT]
    def visit(v, depth=0):
        budget[0] -= 1
        if depth > 16 or budget[0] < 0:
            _fail('INVALID_DOCUMENT')
        if type(v) is str:
            budget[1] -= len(v)
            if budget[1] < 0:
                _fail('INVALID_DOCUMENT')
        elif type(v) is dict:
            for k, item in v.items():
                if type(k) is not str:
                    _fail('INVALID_DOCUMENT')
                visit(k, depth + 1)
                visit(item, depth + 1)
        elif type(v) is list:
            for item in v:
                visit(item, depth + 1)
        elif type(v) is int:
            if abs(v) > 2**64:
                _fail('INVALID_DOCUMENT')
        elif type(v) is float:
            if not math.isfinite(v):
                _fail('INVALID_DOCUMENT')
        elif v is not None and type(v) is not bool:
            _fail('INVALID_DOCUMENT')
    visit(value)
    try:
        data = json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                          separators=(',', ':')).encode('utf-8')
    except (ValueError, TypeError, RecursionError, UnicodeError):
        _fail('INVALID_DOCUMENT')
    if len(data) > MAX_DOCUMENT:
        _fail('INVALID_DOCUMENT')
    return data


def _decode(data):
    if type(data) is not bytes or len(data) > MAX_DOCUMENT:
        _fail('INVALID_DOCUMENT')
    def pairs(items):
        result = {}
        for k, value in items:
            if k in result:
                _fail('INVALID_DOCUMENT')
            result[k] = value
        return result
    try:
        value = json.loads(data.decode('utf-8'), object_pairs_hook=pairs,
                           parse_constant=lambda _: _fail('INVALID_DOCUMENT'))
    except (ValueError, TypeError, RecursionError, UnicodeError):
        _fail('INVALID_DOCUMENT')
    _encode(value)
    return value


def _digest(value):
    return _hash(_encode(value))


def _path(value):
    try:
        parts = tx._path(value)
    except tx.TransactionError:
        _fail('UNSAFE_PATH')
    if len(parts) < 2 or any(ord(c) < 32 or ord(c) == 127 or 0xd800 <= ord(c) <= 0xdfff for c in value):
        _fail('UNSAFE_PATH')
    return parts


def _overlap(a, b):
    return a == b or a.startswith(b + '/') or b.startswith(a + '/')


def _scope(roots, protected, quarantine, target, mode):
    if mode != MODE or type(mode) is not str:
        _fail('UNSUPPORTED_MODE')
    _identifier(target)
    if type(roots) is not list or not 1 <= len(roots) <= MAX_ROOTS:
        _fail('INVALID_ROOTS')
    if type(protected) is not list or not 1 <= len(protected) <= 64:
        _fail('INVALID_PROTECTED_PATHS')
    _path(quarantine)
    _path(quarantine + '/' + '0' * 32 + '/restore-' + '0' * 32 + '-0000.prepared.json')
    paths, refs = [], []
    for root in roots:
        _keys(root, ('root_ref', 'path', 'data_kind'))
        _identifier(root['root_ref'])
        _path(root['path'])
        if type(root['data_kind']) is not str or root['data_kind'] not in ('cli_app_data', 'desktop_app_data'):
            _fail('INVALID_DATA_KIND')
        if root['root_ref'] in refs or any(_overlap(root['path'], p) for p in paths):
            _fail('OVERLAPPING_ROOTS')
        refs.append(root['root_ref'])
        paths.append(root['path'])
    for p in protected:
        _path(p)
    if len(set(protected)) != len(protected):
        _fail('INVALID_PROTECTED_PATHS')
    if any(_overlap(a, b) for a in paths for b in protected):
        _fail('PROTECTED_OVERLAP')
    if any(_overlap(quarantine, p) for p in paths + protected):
        _fail('QUARANTINE_OVERLAP')
    return _digest({'roots': roots, 'protected_paths': protected,
                    'quarantine_directory': quarantine, 'target_ref': target, 'mode': mode})


def _clock(function):
    try:
        value = function()
    except Exception:
        _fail('CLOCK_UNAVAILABLE')
    if type(value) not in (int, float) or abs(value) > 1e15 or not math.isfinite(value):
        _fail('CLOCK_UNAVAILABLE')
    return value


class _Budget:
    def __init__(self, seconds, cancelled):
        if type(seconds) not in (int, float) or not 0 < seconds <= 60 or not math.isfinite(seconds):
            _fail('INVALID_DEADLINE')
        if not callable(cancelled):
            _fail('INVALID_CANCELLATION')
        self.last = _clock(time.monotonic)
        self.end = self.last + seconds
        if not self.end > self.last:
            _fail('INVALID_DEADLINE')
        self.cancelled = cancelled
        self.check()

    def check(self):
        try:
            flag = self.cancelled()
        except Exception:
            _fail('CANCELLATION_CHECK_FAILED')
        if type(flag) is not bool:
            _fail('INVALID_CANCELLATION')
        if flag:
            _fail('CANCELLED')
        now = _clock(time.monotonic)
        if now < self.last:
            _fail('CLOCK_UNAVAILABLE')
        self.last = now
        if now >= self.end:
            _fail('DEADLINE_EXCEEDED')


def _host(callback, doc, budget):
    budget.check()
    if not callable(callback):
        _fail('HOST_CHECK_REQUIRED')
    try:
        result = callback(doc['target_ref'], doc['scope_digest'])
    except Exception:
        _fail('HOST_CHECK_FAILED')
    codes = {'active_host': 'ACTIVE_HOST', 'unknown_ownership': 'OWNERSHIP_UNVERIFIED',
             'shared_scope': 'SHARED_SCOPE', 'credential_scope': 'CREDENTIAL_SCOPE',
             'browser_data_scope': 'BROWSER_DATA_SCOPE'}
    if type(result) is not str or result != HOST_OK:
        _fail(codes.get(result, 'HOST_SCOPE_UNVERIFIED') if type(result) is str else 'HOST_SCOPE_UNVERIFIED')
    budget.check()


def _authorize(callback, operation, digest, doc, budget):
    budget.check()
    if not callable(callback):
        _fail('AUTHORIZATION_REQUIRED')
    try:
        accepted = callback(operation, digest, doc['target_ref'])
    except Exception:
        _fail('AUTHORIZATION_FAILED')
    if accepted is not True:
        _fail('AUTHORIZATION_REQUIRED')
    budget.check()


@contextmanager
def _translated():
    try:
        tx._support()
        yield
    except CleanupError:
        raise
    except tx.TransactionError as exc:
        raise CleanupError(exc.code) from None
    except KeyboardInterrupt:
        _fail('CANCELLED')
    except OSError:
        _fail('IO_FAILURE')


def _directory_meta(fd, *, private=False):
    s = os.fstat(fd)
    if not stat.S_ISDIR(s.st_mode) or s.st_uid != os.geteuid() or s.st_gid != os.getegid():
        _fail('UNSUPPORTED_OWNER')
    if stat.S_IMODE(s.st_mode) & 0o7022 or (private and stat.S_IMODE(s.st_mode) != 0o700):
        _fail('UNSAFE_DIRECTORY_MODE')
    if tx._has_xattrs(fd):
        _fail('UNSUPPORTED_METADATA')
    return [s.st_dev, s.st_ino]


def _identity(value):
    if type(value) is not list or len(value) != 2 or any(type(i) is not int or not 0 <= i <= 2**64 for i in value):
        _fail('INVALID_DOCUMENT')


def _ancestors(path, *, missing=False):
    """Inspect exact path components only; never resolve links or read contents."""
    parts = _path(path)
    result = []
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for index, part in enumerate(parts):
            try:
                item = os.stat(part, dir_fd=fd, follow_symlinks=False)
            except FileNotFoundError:
                if missing:
                    return result
                _fail('UNSAFE_PATH')
            if stat.S_ISLNK(item.st_mode):
                _fail('UNSAFE_PATH')
            if not (stat.S_ISDIR(item.st_mode) or stat.S_ISREG(item.st_mode)):
                _fail('UNSUPPORTED_FILE_TYPE')
            result.append([item.st_dev, item.st_ino, 'directory' if stat.S_ISDIR(item.st_mode) else 'file'])
            if index < len(parts) - 1:
                if not stat.S_ISDIR(item.st_mode):
                    _fail('UNSAFE_PATH')
                next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                if tx._identity(next_fd) != [item.st_dev, item.st_ino]:
                    os.close(next_fd)
                    _fail('CONCURRENT_CHANGE')
                os.close(fd)
                fd = next_fd
        return result
    finally:
        os.close(fd)


def _chain(value):
    if type(value) is not list or not 1 <= len(value) <= 2048:
        _fail('INVALID_DOCUMENT')
    for item in value:
        if type(item) is not list or len(item) != 3:
            _fail('INVALID_DOCUMENT')
        _identity(item[:2])
        if type(item[2]) is not str or item[2] not in ('file', 'directory'):
            _fail('INVALID_DOCUMENT')


def _boundaries(doc):
    if _ancestors(doc['quarantine_directory']) != doc['quarantine_ancestors']:
        _fail('QUARANTINE_CHANGED')
    for root in doc['roots']:
        parent = root['path'].rsplit('/', 1)[0]
        if _ancestors(parent) != root['ancestor_identities']:
            _fail('PARENT_CHANGED')
    for path, expected in zip(doc['protected_paths'], doc['protected_identities']):
        if _ancestors(path, missing=True) != expected:
            _fail('PROTECTED_PATH_CHANGED')


def _inventory_validate(rows):
    if type(rows) is not list or not 1 <= len(rows) <= MAX_ENTRIES:
        _fail('INVALID_DOCUMENT')
    names = set()
    for row in rows:
        _keys(row, _ROW)
        name = row['relative']
        if type(name) is not str or len(name) > 4096 or name.startswith('/') or '\\' in name:
            _fail('INVALID_DOCUMENT')
        parts = name.split('/') if name else []
        if len(parts) > MAX_DEPTH or any(p in ('', '.', '..') for p in parts) or any(ord(c) < 32 or ord(c) == 127 for c in name):
            _fail('INVALID_DOCUMENT')
        if name in names or (name and '/'.join(parts[:-1]) not in names):
            _fail('INVALID_DOCUMENT')
        names.add(name)
        if type(row['kind']) is not str or row['kind'] not in ('file', 'directory'):
            _fail('INVALID_DOCUMENT')
        for key in _ROW - {'relative', 'kind', 'sha256'}:
            if type(row[key]) is not int or abs(row[key]) > 2**64 or (key not in ('mtime_ns', 'ctime_ns') and row[key] < 0):
                _fail('INVALID_DOCUMENT')
        if row['mode'] > 0o777 or row['size'] > MAX_BYTES:
            _fail('INVALID_DOCUMENT')
        if row['kind'] == 'file' and (not _hex(row['sha256'], 64) or row['nlink'] != 1):
            _fail('INVALID_DOCUMENT')
        if row['kind'] == 'directory' and row['sha256'] is not None:
            _fail('INVALID_DOCUMENT')
    if rows[0]['relative'] != '':
        _fail('INVALID_DOCUMENT')


def _validate_plan(doc):
    _keys(doc, ('schema_version', 'mode', 'target_ref', 'action_id', 'created_at', 'expires_at',
                'roots', 'protected_paths', 'protected_identities', 'quarantine_directory', 'quarantine_identity', 'quarantine_ancestors', 'scope_digest'))
    if doc['schema_version'] != _PLAN or not _hex(doc['action_id'], 32):
        _fail('INVALID_DOCUMENT')
    for k in ('created_at', 'expires_at'):
        if type(doc[k]) not in (int, float) or abs(doc[k]) > 1e12 or not math.isfinite(doc[k]):
            _fail('INVALID_DOCUMENT')
    if not 0 < doc['expires_at'] - doc['created_at'] <= 600:
        _fail('INVALID_DOCUMENT')
    if type(doc['roots']) is not list or not 1 <= len(doc['roots']) <= MAX_ROOTS:
        _fail('INVALID_DOCUMENT')
    roots, entries, size = [], 0, 0
    for root in doc['roots']:
        _keys(root, ('root_ref', 'path', 'data_kind', 'parent_identity', 'ancestor_identities', 'inventory'))
        roots.append({k: root[k] for k in ('root_ref', 'path', 'data_kind')})
        _identity(root['parent_identity'])
        _chain(root['ancestor_identities'])
        _inventory_validate(root['inventory'])
        entries += len(root['inventory'])
        size += sum(r['size'] for r in root['inventory'] if r['kind'] == 'file')
    if entries > MAX_ENTRIES or size > MAX_BYTES:
        _fail('TREE_BUDGET_EXCEEDED')
    if type(doc['protected_paths']) is not list or not 1 <= len(doc['protected_paths']) <= 64:
        _fail('INVALID_PROTECTED_PATHS')
    _identity(doc['quarantine_identity'])
    _chain(doc['quarantine_ancestors'])
    if type(doc['protected_identities']) is not list or len(doc['protected_identities']) != len(doc['protected_paths']):
        _fail('INVALID_DOCUMENT')
    for chain in doc['protected_identities']:
        _chain(chain)
    if _scope(roots, doc['protected_paths'], doc['quarantine_directory'], doc['target_ref'], doc['mode']) != doc['scope_digest']:
        _fail('INVALID_DOCUMENT')


def _validate_receipt(doc):
    _keys(doc, ('schema_version', 'plan', 'recovery_id', 'observation'))
    if doc['schema_version'] != _RECEIPT:
        _fail('INVALID_DOCUMENT')
    _validate_plan(doc['plan'])
    if doc['recovery_id'] != doc['plan']['action_id']:
        _fail('INVALID_DOCUMENT')
    obs = doc['observation']
    _keys(obs, ('batch_identity', 'manifest_snapshot', 'roots'))
    _identity(obs['batch_identity'])
    try:
        tx._snapshot(obs['manifest_snapshot'])
    except tx.TransactionError:
        _fail('INVALID_DOCUMENT')
    if type(obs['roots']) is not list or len(obs['roots']) != len(doc['plan']['roots']):
        _fail('INVALID_DOCUMENT')
    for item, root in zip(obs['roots'], doc['plan']['roots']):
        _keys(item, ('root_ref', 'location', 'inventory'))
        if item['root_ref'] != root['root_ref'] or item['location'] not in ('original', 'quarantine'):
            _fail('INVALID_DOCUMENT')
        _inventory_validate(item['inventory'])
        if not _same_tree(item['inventory'], root['inventory'], moved=True):
            _fail('INVALID_DOCUMENT')


class _Private:
    __slots__ = ('_blob',)
    def __init__(self, document):
        data = _encode(document)
        self._validate(_decode(data))
        object.__setattr__(self, '_blob', data)
    def __setattr__(self, key, value):
        _fail('IMMUTABLE_DOCUMENT')
    def __repr__(self):
        return '<' + type(self).__name__ + ' private>'
    def __reduce__(self):
        _fail('PRIVATE_DOCUMENT')
    def private_material(self):
        value = _decode(self._blob)
        self._validate(value)
        return value
    def digest(self):
        self.private_material()
        return _hash(self._blob)


class CleanupPlan(_Private):
    _validate = staticmethod(_validate_plan)
    def preview(self):
        doc = self.private_material()
        return {'operation': 'quarantine', 'state': 'planned', 'root_count': len(doc['roots']),
                'entry_count': sum(len(r['inventory']) for r in doc['roots']),
                'byte_count': sum(i['size'] for r in doc['roots'] for i in r['inventory'] if i['kind'] == 'file'),
                'action_digest': self.digest(), 'native_acceptance': 'not_run',
                'ownership': 'host_assertion_required', 'permanent_purge': 'unsupported'}


class CleanupReceipt(_Private):
    _validate = staticmethod(_validate_receipt)
    @property
    def recovery_id(self):
        return self.private_material()['recovery_id']
    def preview(self):
        doc = self.private_material()
        roots = doc['observation']['roots']
        count = sum(r['location'] == 'quarantine' for r in roots)
        return {'operation': 'cleanup_observation', 'state': 'quarantined' if count == len(roots) else 'restored' if count == 0 else 'partial',
                'root_count': len(roots), 'quarantined_count': count, 'original_count': len(roots) - count,
                'recovery_id': self.recovery_id, 'action_digest': self.digest(),
                'native_acceptance': 'not_run', 'permanent_purge': 'unsupported'}


def _scan(parent_fd, name, budget, device, counts=None, forbidden=(), seen=None):
    counts = [0, 0] if counts is None else counts
    rows = []
    seen = set() if seen is None else seen
    def walk(pfd, leaf, relative, depth):
        budget.check()
        if depth > MAX_DEPTH or counts[0] >= MAX_ENTRIES:
            _fail('TREE_BUDGET_EXCEEDED')
        before = os.stat(leaf, dir_fd=pfd, follow_symlinks=False)
        key = (before.st_dev, before.st_ino)
        if key in forbidden:
            _fail('PROTECTED_ALIAS')
        if key in seen:
            _fail('DUPLICATE_IDENTITY')
        seen.add(key)
        if not (stat.S_ISREG(before.st_mode) or stat.S_ISDIR(before.st_mode)):
            _fail('UNSUPPORTED_FILE_TYPE')
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        if stat.S_ISDIR(before.st_mode):
            flags |= os.O_DIRECTORY
        fd = os.open(leaf, flags, dir_fd=pfd)
        try:
            s = os.fstat(fd)
            if (s.st_dev, s.st_ino) != (before.st_dev, before.st_ino):
                _fail('CONCURRENT_CHANGE')
            if s.st_dev != device:
                _fail('CROSS_FILESYSTEM')
            if s.st_uid != os.geteuid() or s.st_gid != os.getegid():
                _fail('UNSUPPORTED_OWNER')
            if stat.S_IMODE(s.st_mode) & 0o7000 or tx._has_xattrs(fd):
                _fail('UNSUPPORTED_METADATA')
            directory = stat.S_ISDIR(s.st_mode)
            if directory and stat.S_IMODE(s.st_mode) & 0o022:
                _fail('UNSAFE_DIRECTORY_MODE')
            if not directory and s.st_nlink != 1:
                _fail('UNSUPPORTED_FILE_TYPE')
            counts[0] += 1
            row = {'relative': relative, 'kind': 'directory' if directory else 'file',
                   'device': s.st_dev, 'inode': s.st_ino, 'mode': stat.S_IMODE(s.st_mode),
                   'uid': s.st_uid, 'gid': s.st_gid, 'nlink': s.st_nlink, 'size': s.st_size,
                   'mtime_ns': s.st_mtime_ns, 'ctime_ns': s.st_ctime_ns, 'sha256': None}
            rows.append(row)
            if directory:
                names = []
                # Bounded enumeration, never list an unbounded directory first.
                with os.scandir(fd) as entries:
                    for entry in entries:
                        budget.check()
                        if len(names) + counts[0] >= MAX_ENTRIES:
                            _fail('TREE_BUDGET_EXCEEDED')
                        child = entry.name
                        if type(child) is not str or any(ord(c) < 32 or ord(c) == 127 or 0xd800 <= ord(c) <= 0xdfff for c in child) or '\\' in child:
                            _fail('UNSUPPORTED_FILENAME')
                        names.append(child)
                for child in sorted(names):
                    walk(fd, child, relative + '/' + child if relative else child, depth + 1)
            else:
                if s.st_size > MAX_BYTES - counts[1]:
                    _fail('TREE_BUDGET_EXCEEDED')
                h, length = hashlib.sha256(), 0
                while True:
                    budget.check()
                    block = os.read(fd, 65536)
                    if not block:
                        break
                    length += len(block)
                    if length > MAX_BYTES - counts[1]:
                        _fail('TREE_BUDGET_EXCEEDED')
                    h.update(block)
                counts[1] += length
                row['sha256'] = h.hexdigest()
                if length != s.st_size:
                    _fail('CONCURRENT_CHANGE')
            after = os.fstat(fd)
            if (s.st_dev, s.st_ino, s.st_size, s.st_mode, s.st_mtime_ns, s.st_ctime_ns, s.st_nlink) != (after.st_dev, after.st_ino, after.st_size, after.st_mode, after.st_mtime_ns, after.st_ctime_ns, after.st_nlink):
                _fail('CONCURRENT_CHANGE')
            linked = os.stat(leaf, dir_fd=pfd, follow_symlinks=False)
            if (linked.st_dev, linked.st_ino) != (s.st_dev, s.st_ino):
                _fail('CONCURRENT_CHANGE')
        finally:
            os.close(fd)
    walk(parent_fd, name, '', 0)
    return rows


def _same_tree(actual, expected, *, moved=False):
    if len(actual) != len(expected):
        return False
    for a, e in zip(actual, expected):
        # POSIX rename changes the moved root's ctime, not its descendants.
        omit = {'ctime_ns'} if moved and a['relative'] == '' else set()
        if {k: v for k, v in a.items() if k not in omit} != {k: v for k, v in e.items() if k not in omit}:
            return False
    return True


def _exists(fd, name):
    try:
        os.stat(name, dir_fd=fd, follow_symlinks=False)
        return True
    except FileNotFoundError:
        return False


def _forbidden(doc):
    result = {tuple(doc['quarantine_identity'])}
    for path, chain in zip(doc['protected_paths'], doc['protected_identities']):
        if len(chain) == len(_path(path)):
            result.add(tuple(chain[-1][:2]))
    return result


def _reserve(doc):
    """Reserve every persisted envelope before a batch can be created."""
    widest = 2**64
    snapshot = {'sha256': 'f' * 64, 'size': MAX_DOCUMENT, 'mode': 0o600,
                'uid': widest, 'gid': widest, 'device': widest, 'inode': widest,
                'mtime_ns': -widest, 'ctime_ns': -widest}
    rows = []
    for root in doc['roots']:
        inventory = _decode(_encode(root['inventory']))
        # Renaming may update root ctime; reserve the widest supported integer.
        inventory[0]['ctime_ns'] = -widest
        rows.append({'root_ref': root['root_ref'], 'location': 'quarantine', 'inventory': inventory})
    envelope = {'schema_version': _BATCH, 'plan': doc, 'batch_identity': [widest, widest]}
    _encode(envelope)
    _encode({'schema_version': _RECEIPT, 'plan': doc, 'recovery_id': doc['action_id'],
             'observation': {'batch_identity': [widest, widest], 'manifest_snapshot': snapshot, 'roots': rows}})
    for index, root in enumerate(rows):
        _encode({'schema_version': 'guardian-cleanup-step/0.1', 'operation': 'restore_cleanup',
                 'receipt_digest': 'f' * 64, 'index': index, 'root_ref': root['root_ref'],
                 'slot': 'root-0000', 'observation': root})


def _fresh(doc, budget):
    budget.check()
    now = _clock(time.time)
    if not math.isfinite(now) or not doc['created_at'] <= now <= doc['expires_at']:
        _fail('PLAN_EXPIRED')


def plan(roots, protected_paths, quarantine_directory, target_ref, *, mode=MODE,
         host_check=None, max_seconds=30, cancelled=lambda: False):
    """Read only the selected roots after the host validates their full scope."""
    with _translated():
        budget = _Budget(max_seconds, cancelled)
        # Snapshot strict JSON before invoking caller code.
        args = _decode(_encode({'roots': roots, 'protected_paths': protected_paths,
                               'quarantine_directory': quarantine_directory, 'target_ref': target_ref, 'mode': mode}))
        scope = _scope(args['roots'], args['protected_paths'], args['quarantine_directory'], args['target_ref'], args['mode'])
        doc = dict(args, scope_digest=scope)
        _host(host_check, doc, budget)
        protected_identities = [_ancestors(p, missing=True) for p in doc['protected_paths']]
        quarantine_ancestors = _ancestors(doc['quarantine_directory'])
        with tx._directory(doc['quarantine_directory']) as qfd:
            qid = _directory_meta(qfd, private=True)
        doc.update(protected_identities=protected_identities, quarantine_identity=qid)
        forbidden = _forbidden(doc)
        expanded, counts, seen = [], [0, 0], set()
        for root in doc['roots']:
            budget.check()
            with tx._parent(root['path']) as (pfd, name):
                pid = _directory_meta(pfd)
                rows = _scan(pfd, name, budget, qid[0], counts, forbidden, seen)
                expanded.append(dict(root, parent_identity=pid, ancestor_identities=_ancestors(root['path'].rsplit('/', 1)[0]), inventory=rows))
        now = _clock(time.time)
        doc.update(schema_version=_PLAN, action_id=uuid.uuid4().hex, created_at=now,
                   expires_at=now + 600, roots=expanded, quarantine_identity=qid,
                   protected_identities=protected_identities, quarantine_ancestors=quarantine_ancestors)
        _host(host_check, doc, budget)
        _boundaries(doc)
        result = CleanupPlan(doc)
        _reserve(doc)
        budget.check()
        return result


def _plan(value):
    if type(value) is not CleanupPlan:
        _fail('INVALID_PLAN')
    doc = value.private_material()
    _reserve(doc)
    return doc


@contextmanager
def _quarantine_directory(doc):
    _boundaries(doc)
    with tx._directory(doc['quarantine_directory']) as qfd:
        if _directory_meta(qfd, private=True) != doc['quarantine_identity']:
            _fail('QUARANTINE_CHANGED')
        yield qfd


def _originals(doc, budget):
    _boundaries(doc)
    counts, seen = [0, 0], set()
    for root in doc['roots']:
        with tx._parent(root['path']) as (pfd, name):
            if _directory_meta(pfd) != root['parent_identity']:
                _fail('PARENT_CHANGED')
            current = _scan(pfd, name, budget, doc['quarantine_identity'][0], counts, _forbidden(doc), seen)
            if current != root['inventory']:
                _fail('TARGET_CHANGED')


def _journal(fd, name, value):
    tx._write(fd, name, _encode(value), 0o600)
    os.fsync(fd)


def _manifest(fd, doc, batch_identity):
    raw, snapshot = tx._read(fd, 'manifest.json')
    if snapshot['mode'] != 0o600:
        _fail('RECOVERY_CONFLICT')
    envelope = _decode(raw)
    _keys(envelope, ('schema_version', 'plan', 'batch_identity'))
    if envelope != {'schema_version': _BATCH, 'plan': doc, 'batch_identity': batch_identity}:
        _fail('RECOVERY_CONFLICT')
    return snapshot


@contextmanager
def _batch(doc):
    with _quarantine_directory(doc) as qfd:
        name = doc['action_id']
        fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=qfd)
        try:
            identity = _directory_meta(fd, private=True)
            snapshot = _manifest(fd, doc, identity)
            yield qfd, fd, identity, snapshot
        finally:
            os.close(fd)


def _observe(doc, fd, batch_identity, snapshot, budget):
    _boundaries(doc)
    with tx._directory(doc['quarantine_directory'] + '/' + doc['action_id']) as live:
        if _directory_meta(live, private=True) != batch_identity:
            _fail('RECOVERY_CONFLICT')
    rows, counts, seen = [], [0, 0], set()
    for index, root in enumerate(doc['roots']):
        budget.check()
        with tx._parent(root['path']) as (pfd, name):
            if _directory_meta(pfd) != root['parent_identity']:
                _fail('PARENT_CHANGED')
            slot = 'root-' + str(index).zfill(4)
            original, quarantined = _exists(pfd, name), _exists(fd, slot)
            if original == quarantined:
                _fail('RECOVERY_CONFLICT')
            inventory = _scan(pfd if original else fd, name if original else slot,
                              budget, doc['quarantine_identity'][0], counts, _forbidden(doc), seen)
            if not _same_tree(inventory, root['inventory'], moved=True):
                _fail('RECOVERY_CONFLICT')
            rows.append({'root_ref': root['root_ref'], 'location': 'original' if original else 'quarantine',
                         'inventory': inventory})
    return {'batch_identity': batch_identity, 'manifest_snapshot': snapshot, 'roots': rows}


def _receipt(doc, observation):
    return CleanupReceipt({'schema_version': _RECEIPT, 'plan': doc,
                           'recovery_id': doc['action_id'], 'observation': observation})


def reconcile(plan, recovery_id, *, host_check=None, max_seconds=30, cancelled=lambda: False):
    """Read current exact-root locations; does not infer historical completion."""
    with _translated():
        budget, doc = _Budget(max_seconds, cancelled), _plan(plan)
        if type(recovery_id) is not str or recovery_id != doc['action_id']:
            _fail('INVALID_RECOVERY_ID')
        _host(host_check, doc, budget)
        with _batch(doc) as (_, fd, identity, snapshot):
            observed = _observe(doc, fd, identity, snapshot, budget)
            _host(host_check, doc, budget)
            # Callback may have changed the tree; never return a cached success.
            repeated = _observe(doc, fd, identity, _manifest(fd, doc, identity), budget)
            if repeated != observed:
                _fail('RECOVERY_CONFLICT')
            result = _receipt(doc, repeated)
            budget.check()
            return result


def quarantine(plan, *, authorize=None, host_check=None, exclusive_access=False,
               max_seconds=30, cancelled=lambda: False):
    """Move selected roots into their private same-filesystem recovery batch."""
    recovery_id, moved, stage = None, 0, 'before_write'
    try:
        with _translated():
            budget, doc = _Budget(max_seconds, cancelled), _plan(plan)
            if exclusive_access is not True:
                _fail('EXCLUSIVE_ACCESS_REQUIRED')
            _fresh(doc, budget)
            _host(host_check, doc, budget)
            digest = plan.digest()
            _authorize(authorize, 'quarantine', digest, doc, budget)
            _host(host_check, doc, budget)
            _fresh(doc, budget)
            _originals(doc, budget)
            with _quarantine_directory(doc) as qfd:
                if _exists(qfd, doc['action_id']):
                    _fail('BATCH_ALREADY_EXISTS')
                budget.check()
                recovery_id = doc['action_id']
                os.mkdir(recovery_id, 0o700, dir_fd=qfd)
                stage = 'batch_created'
                os.fsync(qfd)
                fd = os.open(recovery_id, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=qfd)
                try:
                    identity = _directory_meta(fd, private=True)
                    _journal(fd, 'manifest.json', {'schema_version': _BATCH, 'plan': doc, 'batch_identity': identity})
                    expected = _observe(doc, fd, identity, _manifest(fd, doc, identity), budget)
                    for index, root in enumerate(doc['roots']):
                        stage = 'before_move'
                        _host(host_check, doc, budget)
                        _authorize(authorize, 'quarantine', digest, doc, budget)
                        _host(host_check, doc, budget)
                        _fresh(doc, budget)
                        with _quarantine_directory(doc):
                            pass
                        if _observe(doc, fd, identity, _manifest(fd, doc, identity), budget) != expected:
                            _fail('TARGET_CHANGED')
                        slot = 'root-' + str(index).zfill(4)
                        journal = {'schema_version': 'guardian-cleanup-step/0.1', 'operation': 'quarantine',
                                   'plan_digest': digest, 'index': index, 'root_ref': root['root_ref'], 'slot': slot}
                        _journal(fd, 'move-' + str(index).zfill(4) + '.prepared.json', journal)
                        budget.check()
                        with tx._parent(root['path']) as (pfd, name):
                            if _directory_meta(pfd) != root['parent_identity'] or _exists(fd, slot):
                                _fail('TARGET_CHANGED')
                            if _scan(pfd, name, budget, doc['quarantine_identity'][0]) != expected['roots'][index]['inventory']:
                                _fail('TARGET_CHANGED')
                            stage = 'move_outcome_unknown'
                            os.rename(name, slot, src_dir_fd=pfd, dst_dir_fd=fd)
                            stage = 'after_move_not_verified'
                            moved += 1
                            os.fsync(pfd)
                            os.fsync(fd)
                        current = _observe(doc, fd, identity, _manifest(fd, doc, identity), budget)
                        if current['roots'][index]['location'] != 'quarantine':
                            _fail('RECOVERY_CONFLICT')
                        # Validate all unrelated roots against the last observation.
                        for j, old in enumerate(expected['roots']):
                            if j != index and current['roots'][j] != old:
                                _fail('RECOVERY_CONFLICT')
                        expected = current
                        stage = 'after_move_verified'
                        _journal(fd, 'move-' + str(index).zfill(4) + '.done.json', dict(journal, observation=current['roots'][index]))
                    _host(host_check, doc, budget)
                    if _observe(doc, fd, identity, _manifest(fd, doc, identity), budget) != expected:
                        _fail('RECOVERY_CONFLICT')
                    result = _receipt(doc, expected)
                    _journal(fd, 'receipt.json', result.private_material())
                    budget.check()
                    return result
                finally:
                    os.close(fd)
    except CleanupError as exc:
        exc.recovery_id, exc.moved_count, exc.stage = recovery_id, moved, stage
        raise


def restore(receipt, *, authorize=None, host_check=None, exclusive_access=False,
            max_seconds=30, cancelled=lambda: False):
    """Separately approved restore; existing or changed original data blocks it."""
    recovery_id, moved, stage = None, 0, 'before_write'
    try:
        with _translated():
            budget = _Budget(max_seconds, cancelled)
            if type(receipt) is not CleanupReceipt:
                _fail('INVALID_RECEIPT')
            material = receipt.private_material()
            doc, expected = material['plan'], material['observation']
            if exclusive_access is not True:
                _fail('EXCLUSIVE_ACCESS_REQUIRED')
            _host(host_check, doc, budget)
            if not any(r['location'] == 'quarantine' for r in expected['roots']):
                _fail('NOTHING_TO_RESTORE')
            digest = receipt.digest()
            _authorize(authorize, 'restore_cleanup', digest, doc, budget)
            _host(host_check, doc, budget)
            with _batch(doc) as (_, fd, identity, snapshot):
                if _observe(doc, fd, identity, snapshot, budget) != expected:
                    _fail('RECOVERY_CONFLICT')
                recovery_id = doc['action_id']
                attempt = uuid.uuid4().hex
                for index, root in enumerate(doc['roots']):
                    if expected['roots'][index]['location'] == 'original':
                        continue
                    stage = 'before_move'
                    _host(host_check, doc, budget)
                    _authorize(authorize, 'restore_cleanup', digest, doc, budget)
                    _host(host_check, doc, budget)
                    with _quarantine_directory(doc):
                        pass
                    if _observe(doc, fd, identity, _manifest(fd, doc, identity), budget) != expected:
                        _fail('RECOVERY_CONFLICT')
                    slot = 'root-' + str(index).zfill(4)
                    journal = {'schema_version': 'guardian-cleanup-step/0.1', 'operation': 'restore_cleanup',
                               'receipt_digest': digest, 'index': index, 'root_ref': root['root_ref'], 'slot': slot}
                    prefix = 'restore-' + attempt + '-' + str(index).zfill(4)
                    _journal(fd, prefix + '.prepared.json', journal)
                    budget.check()
                    with tx._parent(root['path']) as (pfd, name):
                        if _directory_meta(pfd) != root['parent_identity'] or _exists(pfd, name):
                            _fail('RECOVERY_CONFLICT')
                        if _scan(fd, slot, budget, doc['quarantine_identity'][0]) != expected['roots'][index]['inventory']:
                            _fail('RECOVERY_CONFLICT')
                        stage = 'move_outcome_unknown'
                        os.rename(slot, name, src_dir_fd=fd, dst_dir_fd=pfd)
                        stage = 'after_move_not_verified'
                        moved += 1
                        os.fsync(pfd)
                        os.fsync(fd)
                    current = _observe(doc, fd, identity, _manifest(fd, doc, identity), budget)
                    if current['roots'][index]['location'] != 'original':
                        _fail('RECOVERY_CONFLICT')
                    for j, old in enumerate(expected['roots']):
                        if j != index and current['roots'][j] != old:
                            _fail('RECOVERY_CONFLICT')
                    expected = current
                    stage = 'after_move_verified'
                    _journal(fd, prefix + '.done.json', dict(journal, observation=current['roots'][index]))
                _host(host_check, doc, budget)
                if _observe(doc, fd, identity, _manifest(fd, doc, identity), budget) != expected:
                    _fail('RECOVERY_CONFLICT')
                result = _receipt(doc, expected)
                _journal(fd, 'restore-' + attempt + '.receipt.json', result.private_material())
                budget.check()
                return result
    except CleanupError as exc:
        exc.recovery_id, exc.moved_count, exc.stage = recovery_id, moved, stage
        raise


def load_manifest(path, expected_digest, target_ref, *, max_seconds=30, cancelled=lambda: False):
    """Load one authorized private manifest; never recursively inspect its paths."""
    with _translated():
        budget = _Budget(max_seconds, cancelled)
        _path(path)
        _identifier(target_ref)
        if not _hex(expected_digest, 64):
            _fail('INVALID_DIGEST')
        with tx._parent(path) as (fd, name):
            _directory_meta(fd, private=True)
            if name != 'manifest.json':
                _fail('INVALID_MANIFEST_PATH')
            budget.check()
            raw, snapshot = tx._read(fd, name)
            budget.check()
            if snapshot['mode'] != 0o600:
                _fail('INVALID_DOCUMENT')
            envelope = _decode(raw)
            _keys(envelope, ('schema_version', 'plan', 'batch_identity'))
            if envelope['schema_version'] != _BATCH or envelope['batch_identity'] != tx._identity(fd):
                _fail('RECOVERY_CONFLICT')
        result = CleanupPlan(envelope['plan'])
        doc = result.private_material()
        if result.digest() != expected_digest:
            _fail('DIGEST_MISMATCH')
        if doc['target_ref'] != target_ref:
            _fail('TARGET_MISMATCH')
        if path != doc['quarantine_directory'] + '/' + doc['action_id'] + '/manifest.json':
            _fail('INVALID_MANIFEST_PATH')
        _reserve(doc)
        budget.check()
        return result
