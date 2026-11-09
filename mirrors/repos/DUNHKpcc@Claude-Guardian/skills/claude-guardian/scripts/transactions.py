"""Narrow offline exact-file transactions; not a native configuration adapter.

No CLI permission switch proves consent. The trusted host must verify the actual
user approval, target binding, permissions and exclusive-access boundary, then
supply authorize(operation, digest, target_ref) -> True. It is called again just
before commit to permit cancellation. Returning True is a host assertion, not
cryptographic evidence of consent. A malicious caller already has Python/file
access; this module is not a security boundary against that caller.

Only existing, single-link regular files on POSIX with descriptor-relative,
no-follow operations are supported. No creation/deletion, directory cleanup,
registry, keychain, native system setting, network request or shell execution.
Host must exclude concurrent writers for the whole operation: POSIX rename is
atomic but is not compare-and-swap. Advisory locks alone cannot guarantee this.
Multi-file atomicity, crash recovery of application state, ACL/xattr preservation
and application-effective verification are not claimed. The file owner/group
must equal the executing effective user/group; other ownership is rejected. Files with xattrs are
rejected. Backups and recovery manifests are never automatically deleted.

Plans contain private replacement bytes. Do not log/serialize plans into public
reports. preview() emits only hashes/lengths; it never emits content or paths.
"""
import base64
import ctypes
import hashlib
import json
import math
import os
import stat
import sys
import time
import uuid
from contextlib import contextmanager

MAX_BYTES = 4 * 1024 * 1024
MAX_BASE64 = 4 * ((MAX_BYTES + 2) // 3)
MAX_DOCUMENT = MAX_BASE64 + 32768


class TransactionError(Exception):
    """Stable non-secret error code, with optional recovery identifier."""

    def __init__(self, code, recovery_id=None, *, attempt_id=None, cleanup_code=None):
        super().__init__(code)
        self.code = code
        self.recovery_id = recovery_id
        self.attempt_id = attempt_id
        self.cleanup_code = cleanup_code


def _fail(code):
    raise TransactionError(code) from None


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _bounded_document(document):
    """Accept bounded plain JSON data before serialization; never echo payloads."""
    budget = [256, MAX_DOCUMENT]
    def visit(value, depth):
        budget[0] -= 1
        if depth > 8 or budget[0] < 0:
            _fail('INVALID_DOCUMENT')
        if type(value) is str:
            budget[1] -= len(value)
            if budget[1] < 0:
                _fail('INVALID_DOCUMENT')
        elif type(value) is dict:
            if len(value) > 64:
                _fail('INVALID_DOCUMENT')
            for key, item in value.items():
                if type(key) is not str:
                    _fail('INVALID_DOCUMENT')
                visit(key, depth + 1)
                visit(item, depth + 1)
        elif type(value) is list:
            if len(value) > 64:
                _fail('INVALID_DOCUMENT')
            for item in value:
                visit(item, depth + 1)
        elif type(value) is int:
            if abs(value) > 2**64:
                _fail('INVALID_DOCUMENT')
        elif type(value) is float:
            if not math.isfinite(value):
                _fail('INVALID_DOCUMENT')
        elif value is not None and type(value) is not bool:
            _fail('INVALID_DOCUMENT')
    visit(document, 0)


def digest(document):
    """Digest bounded plain JSON data; digest validity does not prove consent."""
    _bounded_document(document)
    try:
        encoded = json.dumps(document, sort_keys=True, separators=(',', ':'),
                             ensure_ascii=True, allow_nan=False).encode()
        if len(encoded) > MAX_DOCUMENT:
            _fail('INVALID_DOCUMENT')
        return _hash(encoded)
    except (ValueError, TypeError, RecursionError, OverflowError):
        _fail('INVALID_DOCUMENT')


def _journal_bytes(document):
    """Use the same bounded encoding for persisted journals and their digests."""
    digest(document)
    return json.dumps(document, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode()


def _copy(document):
    digest(document)
    return json.loads(json.dumps(document, allow_nan=False))


def _hex(value, length):
    return (type(value) is str and len(value) == length
            and all(c in '0123456789abcdef' for c in value))


def _snapshot(value):
    fields = {'sha256', 'size', 'mode', 'uid', 'gid', 'device', 'inode',
              'mtime_ns', 'ctime_ns'}
    if type(value) is not dict or set(value) != fields or not _hex(value['sha256'], 64):
        _fail('INVALID_SNAPSHOT')
    for key in fields - {'sha256'}:
        if type(value[key]) is not int or abs(value[key]) > 2**64:
            _fail('INVALID_SNAPSHOT')
        if key not in ('mtime_ns', 'ctime_ns') and value[key] < 0:
            _fail('INVALID_SNAPSHOT')
    if value['size'] > MAX_BYTES or value['mode'] > 0o777:
        _fail('INVALID_SNAPSHOT')


def _path(value):
    # Do not normalize, expand variables/home markers, resolve or glob paths.
    if type(value) is not str or len(value) > 4096 or not value.startswith('/'):
        _fail('UNSAFE_PATH')
    parts = value.split('/')[1:]
    if not parts or any(p in ('', '.', '..') for p in parts):
        _fail('UNSAFE_PATH')
    if any(c in value for c in ('\x00', '\\', '~', '$', '*', '?', '[', ']')):
        _fail('UNSAFE_PATH')
    return parts


def _backup_path_budget(path):
    # All generated records must remain reopenable by the same strict path API.
    _path(path)
    _path(path + '/' + '0' * 32 + '/restore-' + '0' * 32 + '.prepared.json')


def _recovery_document_budget(plan, backup_directory):
    """Reserve all future recovery envelopes before creating any write batch.

    Legal Unicode paths expand under JSON escaping. A plan or prepared record
    fitting the bound does not imply its applied/restore journal will fit. Use
    maximal allowed snapshot integer widths, never a guessed constant allowance.
    These placeholders are size estimates only and are never persisted.
    """
    widest = {'sha256': 'f' * 64, 'size': MAX_BYTES, 'mode': 0o777,
              'uid': 2**64, 'gid': 2**64, 'device': 2**64, 'inode': 2**64,
              'mtime_ns': -(2**64), 'ctime_ns': -(2**64)}
    witness = {'name': '.guardian-stage-' + 'f' * 32, 'snapshot': widest}
    common = {'plan': plan, 'backup_directory': backup_directory, 'batch': 'f' * 32,
              'batch_identity': [2**64, 2**64], 'replacement': witness}
    _journal_bytes(dict(common, schema_version='exact-file-recovery/2',
                        state='applied', applied_snapshot=widest))
    _journal_bytes(dict(common, schema_version='exact-file-restore/1',
                        state='restore_prepared', attempt_id='f' * 32,
                        source_digest='f' * 64, source_snapshot=widest))


def _support():
    if (os.name != 'posix' or not hasattr(os, 'O_NOFOLLOW')
            or not hasattr(os, 'O_DIRECTORY') or os.open not in os.supports_dir_fd
            or (sys.platform != 'darwin' and not callable(getattr(os, 'listxattr', None)))):
        _fail('PLATFORM_UNSUPPORTED')


# macOS 15 and later let the kernel add this attribute to every file a local process
# creates or writes, and it cannot be removed. It carries no user content and no writer
# semantics, so it alone is not treated as extra metadata; any other name still is.
_KERNEL_PROVENANCE = b'com.apple.provenance\0'


def _has_xattrs(fd):
    """Inspect the already-open file, with no pathname fallback or value reads.

    Darwin ABI verified against Apple's xnu/bsd/sys/xattr.h and flistxattr(2):
    https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/xattr.h
    https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/flistxattr.2.html
    A NULL buffer requests only the required size; no untrusted-size allocation and
    no attribute values. XATTR_SHOWCOMPRESSION includes compression metadata normally
    hidden from the list. Only when the required size is exactly that of the single
    name ``com.apple.provenance`` is the list read, into a fixed buffer of that size,
    and only that one name is tolerated. Any failure blocks the transaction.
    Listing observes attributes accessible to the current execution identity.
    """
    if type(fd) is not int or not 0 <= fd <= 2**31 - 1:
        _fail('XATTR_CHECK_FAILED')
    if sys.platform == 'darwin':
        try:
            # Fixed trusted OS library, never find_library/search-path resolution.
            library = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
            query = library.flistxattr
            query.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
            query.restype = ctypes.c_ssize_t
            size = query(fd, None, 0, 0x0020)  # XATTR_SHOWCOMPRESSION
            if type(size) is not int or not 0 <= size <= 2**(ctypes.sizeof(ctypes.c_ssize_t) * 8 - 1) - 1:
                _fail('XATTR_CHECK_FAILED')
            if size != len(_KERNEL_PROVENANCE):
                return size > 0
            buffer = ctypes.create_string_buffer(len(_KERNEL_PROVENANCE))
            second = query(fd, buffer, len(_KERNEL_PROVENANCE), 0x0020)
            if second != len(_KERNEL_PROVENANCE):
                _fail('XATTR_CHECK_FAILED')
            return buffer.raw != _KERNEL_PROVENANCE
        except (OSError, AttributeError, TypeError, ValueError):
            _fail('XATTR_CHECK_FAILED')
    try:
        # CPython's supported fd form on Linux; never convert fd back to a path.
        return bool(os.listxattr(fd))
    except (OSError, AttributeError, TypeError, ValueError):
        _fail('XATTR_CHECK_FAILED')


def _close_preserving(fd, primary):
    try:
        os.close(fd)
    except (OSError, KeyboardInterrupt) as exc:
        if primary is not None:
            if not getattr(primary, 'cleanup_code', None):
                primary.cleanup_code = 'DESCRIPTOR_CLOSE_FAILED'
        else:
            code = 'CANCELLED' if isinstance(exc, KeyboardInterrupt) else 'IO_FAILURE'
            raise TransactionError(code, cleanup_code='DESCRIPTOR_CLOSE_FAILED') from None


@contextmanager
def _directory(path):
    _support()
    parts = _path(path)
    fd = None
    primary = None
    try:
        try:
            fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
            for part in parts:
                next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                  dir_fd=fd)
                previous_fd, fd = fd, next_fd
                _close_preserving(previous_fd, None)
        except OSError:
            _fail('UNSAFE_OR_UNAVAILABLE_DIRECTORY')
        yield fd
    except BaseException as exc:
        primary = exc
        raise
    finally:
        if fd is not None:
            _close_preserving(fd, primary)


@contextmanager
def _parent(path):
    parts = _path(path)
    if len(parts) < 2:
        _fail('ROOT_TARGET_UNSUPPORTED')
    with _directory('/' + '/'.join(parts[:-1])) as fd:
        yield fd, parts[-1]


def _identity(fd):
    s = os.fstat(fd)
    return [s.st_dev, s.st_ino]


def _read(fd, name):
    f = None
    primary = None
    try:
        f = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        s = os.fstat(f)
        if not stat.S_ISREG(s.st_mode) or s.st_nlink != 1:
            _fail('UNSUPPORTED_FILE_TYPE')
        if (s.st_size > MAX_BYTES or s.st_uid != os.geteuid()
                or s.st_gid != os.getegid()):
            _fail('UNSUPPORTED_FILE_SIZE_OR_OWNER')
        if stat.S_IMODE(s.st_mode) & 0o7000 or _has_xattrs(f):
            _fail('UNSUPPORTED_FILE_METADATA')
        data = bytearray()
        while len(data) <= MAX_BYTES:
            block = os.read(f, min(65536, MAX_BYTES + 1 - len(data)))
            if not block:
                break
            data.extend(block)
        after = os.fstat(f)
        if len(data) > MAX_BYTES:
            _fail('UNSUPPORTED_FILE_SIZE_OR_OWNER')
        if (s.st_size, s.st_mtime_ns, s.st_ctime_ns) != (
                after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            _fail('CONCURRENT_CHANGE')
        return bytes(data), {'sha256': _hash(data), 'size': len(data),
                             'mode': stat.S_IMODE(s.st_mode), 'uid': s.st_uid,
                             'gid': s.st_gid, 'device': s.st_dev, 'inode': s.st_ino,
                             'mtime_ns': s.st_mtime_ns, 'ctime_ns': s.st_ctime_ns}
    except OSError:
        primary = TransactionError('UNSAFE_OR_UNAVAILABLE_FILE')
        raise primary from None
    except BaseException as exc:
        primary = exc
        raise
    finally:
        if f is not None:
            _close_preserving(f, primary)


def plan(path, proposed, target_ref, *, ttl_seconds=600, now=None):
    """Read one exact file; no writes. Caller has already authorized this read."""
    if not isinstance(proposed, bytes) or len(proposed) > MAX_BYTES:
        _fail('INVALID_PROPOSED_BYTES')
    if not isinstance(target_ref, str) or not target_ref or len(target_ref) > 200:
        _fail('INVALID_TARGET')
    if type(ttl_seconds) not in (int, float) or not 0 < ttl_seconds <= 3600:
        _fail('INVALID_EXPIRY')
    now = time.time() if now is None else now
    if type(now) not in (int, float) or abs(now) > 1e12 or not math.isfinite(now):
        _fail('INVALID_EXPIRY')
    with _parent(path) as (fd, name):
        before, snapshot = _read(fd, name)
        parent_identity = _identity(fd)
    return {'schema_version': 'exact-file-plan/1', 'action_id': uuid.uuid4().hex,
            'operation': 'replace_existing_file', 'target_ref': target_ref,
            'path': path, 'parent_identity': parent_identity,
            'before': snapshot, 'after_sha256': _hash(proposed),
            'proposed_base64': base64.b64encode(proposed).decode('ascii'),
            'created_at': now, 'expires_at': now + ttl_seconds}


def _validate(p, now=None):
    _bounded_document(p)
    keys = {'schema_version', 'action_id', 'operation', 'target_ref', 'path',
            'parent_identity', 'before', 'after_sha256', 'proposed_base64',
            'created_at', 'expires_at'}
    if not isinstance(p, dict) or set(p) != keys:
        _fail('INVALID_PLAN')
    if p['schema_version'] != 'exact-file-plan/1' or p['operation'] != 'replace_existing_file':
        _fail('INVALID_PLAN')
    _path(p['path'])
    _snapshot(p['before'])
    identity = p['parent_identity']
    if (not _hex(p['action_id'], 32) or not _hex(p['after_sha256'], 64)
            or type(identity) is not list or len(identity) != 2
            or any(type(n) is not int or not 0 <= n <= 2**64 for n in identity)
            or type(p['target_ref']) is not str or not 0 < len(p['target_ref']) <= 200
            or type(p['proposed_base64']) is not str
            or len(p['proposed_base64']) > MAX_BASE64):
        _fail('INVALID_PLAN')
    for key in ('created_at', 'expires_at'):
        if type(p[key]) not in (int, float) or not math.isfinite(p[key]) or abs(p[key]) > 1e12:
            _fail('INVALID_PLAN')
    try:
        proposed = base64.b64decode(p['proposed_base64'], validate=True)
    except (ValueError, TypeError):
        _fail('INVALID_PLAN')
    if (len(proposed) > MAX_BYTES or _hash(proposed) != p['after_sha256']
            or not 0 < p['expires_at'] - p['created_at'] <= 3600
            or (now is not None and not p['created_at'] <= now < p['expires_at'])):
        _fail('INVALID_OR_EXPIRED_PLAN')
    return proposed


def _identity_value(value):
    if (type(value) is not list or len(value) != 2
            or any(type(n) is not int or not 0 <= n <= 2**64 for n in value)):
        _fail('INVALID_RECOVERY')


def _witness(value, expected_hash, expected_size, before):
    if (type(value) is not dict or set(value) != {'name', 'snapshot'}
            or type(value['name']) is not str
            or not value['name'].startswith('.guardian-stage-')
            or not _hex(value['name'][16:], 32)):
        _fail('INVALID_RECOVERY')
    _snapshot(value['snapshot'])
    snapshot = value['snapshot']
    if (snapshot['sha256'] != expected_hash or snapshot['size'] != expected_size
            or any(snapshot[k] != before[k] for k in ('mode', 'uid', 'gid', 'device'))):
        _fail('INVALID_RECOVERY')


def _same_renamed_file(actual, staged):
    # rename may change ctime. This establishes a present candidate, not history.
    return all(actual[k] == staged[k] for k in staged if k != 'ctime_ns')


def _recovery_shape(document):
    _bounded_document(document)
    keys = {'schema_version', 'plan', 'backup_directory', 'batch', 'state',
            'applied_snapshot'}
    if type(document) is not dict:
        _fail('INVALID_RECOVERY')
    version = document.get('schema_version')
    if version == 'exact-file-recovery/2':
        keys |= {'replacement', 'batch_identity'}
    elif version != 'exact-file-recovery/1':
        _fail('INVALID_RECOVERY')
    if set(document) != keys or document['state'] not in ('prepared', 'applied'):
        _fail('INVALID_RECOVERY')
    proposed = _validate(document['plan'])  # Expiry is irrelevant to fresh recovery.
    _path(document['backup_directory'])
    if not _hex(document['batch'], 32):
        _fail('INVALID_RECOVERY')
    p = document['plan']
    if version == 'exact-file-recovery/2':
        _identity_value(document['batch_identity'])
        _witness(document['replacement'], p['after_sha256'], len(proposed), p['before'])
    if document['state'] == 'prepared':
        if document['applied_snapshot'] is not None:
            _fail('INVALID_RECOVERY')
    else:
        actual = document['applied_snapshot']
        _snapshot(actual)
        if (actual['sha256'] != p['after_sha256'] or actual['size'] != len(proposed)
                or any(actual[k] != p['before'][k] for k in ('mode', 'uid', 'gid', 'device'))):
            _fail('INVALID_RECOVERY')
        if version == 'exact-file-recovery/2' and not _same_renamed_file(
                actual, document['replacement']['snapshot']):
            _fail('INVALID_RECOVERY')
    return document


def _recovery(document):
    # Keep prepared admission separate, including malformed prepared receipts.
    _bounded_document(document)
    if type(document) is dict and document.get('state') == 'prepared':
        _fail('RECOVERY_REQUIRES_RECONCILIATION')
    return _recovery_shape(document)


def _context_error(exc, batch=None, attempt=None):
    code = (exc.code if isinstance(exc, TransactionError) else
            'CANCELLED' if isinstance(exc, KeyboardInterrupt) else 'IO_FAILURE')
    return TransactionError(code, getattr(exc, 'recovery_id', None) or batch,
                            attempt_id=getattr(exc, 'attempt_id', None) or attempt,
                            cleanup_code=getattr(exc, 'cleanup_code', None))


def preview(p):
    """Content-free diff, suitable for a non-secret report.

Host must separately present a vetted/redacted semantic diff to the user.
Arbitrary content cannot be safely automatically redacted by this library.
"""
    proposed = _validate(p, time.time())
    return {'plan_digest': digest(p), 'before_sha256': p['before']['sha256'],
            'after_sha256': _hash(proposed), 'before_size': p['before']['size'],
            'after_size': len(proposed), 'changed': p['before']['sha256'] != _hash(proposed),
            'verification_scope': 'exact_file_bytes_only'}


def _authorize(callback, operation, document, target_ref):
    if not callable(callback):
        _fail('AUTHORIZATION_REQUIRED')
    try:
        accepted = callback(operation, digest(document), target_ref)
    except KeyboardInterrupt:
        _fail('CANCELLED')
    except Exception:
        _fail('AUTHORIZATION_CANCELLED')
    if accepted is not True:
        _fail('AUTHORIZATION_DENIED')


def _write(fd, name, data, mode=0o600):
    f = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o600, dir_fd=fd)
    primary = None
    try:
        view = memoryview(data)
        while view:
            n = os.write(f, view)
            if n <= 0:
                _fail('WRITE_FAILED')
            view = view[n:]
        os.fchmod(f, mode)
        os.fsync(f)
    except BaseException as exc:
        primary = exc
        raise
    finally:
        _close_preserving(f, primary)
    os.fsync(fd)


def _check_parent(path, expected):
    with _parent(path) as (fd, _):
        if _identity(fd) != expected:
            _fail('PARENT_CHANGED')


def _replace(fd, name, data, snapshot, path, parent_identity, before_commit,
             on_staged=None, on_committing=None):
    staging = '.guardian-stage-' + uuid.uuid4().hex
    staged = None
    renamed = False
    primary = None
    try:
        _write(fd, staging, data, snapshot['mode'])
        staged_data, staged = _read(fd, staging)
        if staged_data != data:
            _fail('STAGING_VERIFY_FAILED')
        if on_staged is not None:
            on_staged(staging, staged)
        before_commit()
        _check_parent(path, parent_identity)
        if _read(fd, staging)[1] != staged:
            _fail('STAGING_CHANGED')
        if _read(fd, name)[1] != snapshot:
            _fail('STALE_FILE')
        if on_committing is not None:
            on_committing(staging, staged)
            _check_parent(path, parent_identity)
            if _read(fd, staging)[1] != staged:
                _fail('STAGING_CHANGED')
            if _read(fd, name)[1] != snapshot:
                _fail('STALE_FILE')
        os.replace(staging, name, src_dir_fd=fd, dst_dir_fd=fd)
        renamed = True
        os.fsync(fd)
        _check_parent(path, parent_identity)
        actual, state = _read(fd, name)
        if actual != data or not _same_renamed_file(state, staged):
            _fail('POST_WRITE_VERIFY_FAILED')
        return state
    except BaseException as exc:
        primary = exc
        raise
    finally:
        # Never unlink a pathname after its stage was successfully renamed.
        # Unknown/foreign partial stages are retained, never swept by name.
        if not renamed:
            cleanup = None
            try:
                os.stat(staging, dir_fd=fd, follow_symlinks=False)
                if staged is None or _read(fd, staging)[1] != staged:
                    cleanup = 'STAGING_RETAINED'
                else:
                    os.unlink(staging, dir_fd=fd)
                    os.fsync(fd)
            except FileNotFoundError:
                pass
            except (OSError, TransactionError, KeyboardInterrupt):
                cleanup = 'STAGING_CLEANUP_FAILED'
            if cleanup:
                if primary is not None:
                    primary.cleanup_code = cleanup
                else:
                    raise TransactionError(cleanup)


def apply(p, *, target_ref, backup_directory, authorize=None,
          exclusive_access=False):
    """Apply one plan; backup_directory must already be private and authorized.

exclusive_access=True asserts host-enforced writer exclusion, not consent.
Backup location is part of the authorization document alongside the entire plan.
On failure recovery_id identifies the retained private recovery batch, if made.
"""
    # Snapshot caller-owned mutable data before any callback or I/O.
    p = _copy(p)
    proposed = _validate(p, time.time())
    if target_ref != p['target_ref']:
        _fail('TARGET_MISMATCH')
    if exclusive_access is not True:
        _fail('EXCLUSIVE_ACCESS_REQUIRED')
    _backup_path_budget(backup_directory)
    _recovery_document_budget(p, backup_directory)
    authorization = {'plan': p, 'backup_directory': backup_directory}
    _authorize(authorize, 'apply', authorization, target_ref)
    batch = None
    try:
        with _parent(p['path']) as (fd, name), _directory(backup_directory) as backup_fd:
            s = os.fstat(backup_fd)
            if s.st_uid != os.geteuid() or stat.S_IMODE(s.st_mode) != 0o700:
                _fail('BACKUP_DIRECTORY_NOT_PRIVATE')
            if _identity(fd) != p['parent_identity']:
                _fail('PARENT_CHANGED')
            original, snapshot = _read(fd, name)
            if snapshot != p['before']:
                _fail('STALE_FILE')
            batch = uuid.uuid4().hex
            os.mkdir(batch, 0o700, dir_fd=backup_fd)
            os.fsync(backup_fd)
            batch_path = backup_directory + '/' + batch
            with _directory(batch_path) as recovery_fd:
                _write(recovery_fd, 'original.bin', original)
                backup_data, backup_snapshot = _read(recovery_fd, 'original.bin')
                if backup_data != original:
                    _fail('BACKUP_VERIFY_FAILED')
                recovery = {'schema_version': 'exact-file-recovery/2', 'plan': p,
                            'backup_directory': backup_directory, 'batch': batch,
                            'state': 'prepared', 'applied_snapshot': None,
                            'batch_identity': _identity(recovery_fd), 'replacement': None}
                prepared_snapshot = None
                def prepared(staging, staged):
                    nonlocal prepared_snapshot
                    recovery['replacement'] = {'name': staging, 'snapshot': staged}
                    _write(recovery_fd, 'prepared.json', _journal_bytes(recovery))
                    retained, prepared_snapshot = _document_file(recovery_fd, 'prepared.json')
                    if digest(retained) != digest(recovery):
                        _fail('RECEIPT_DIGEST_MISMATCH')
                def evidence_check():
                    with _directory(batch_path) as current_fd:
                        _private_batch(current_fd, recovery['batch_identity'])
                        retained, retained_snapshot = _document_file(current_fd, 'prepared.json')
                        if (digest(retained) != digest(recovery)
                                or retained_snapshot != prepared_snapshot):
                            _fail('RECEIPT_CHANGED')
                        if _read(current_fd, 'original.bin')[1] != backup_snapshot:
                            _fail('BACKUP_CHANGED')
                def confirm():
                    _validate(p, time.time())
                    _authorize(authorize, 'apply', authorization, target_ref)
                    _validate(p, time.time())
                    evidence_check()
                applied = _replace(fd, name, proposed, snapshot, p['path'],
                                   p['parent_identity'], confirm, prepared,
                                   lambda *_: evidence_check())
                recovery['state'] = 'applied'
                recovery['applied_snapshot'] = applied
                _write(recovery_fd, 'applied.json', _journal_bytes(recovery))
                return recovery
    except (OSError, TransactionError, KeyboardInterrupt) as exc:
        raise _context_error(exc, batch) from None


def verify(recovery):
    """Verify bytes and file identity only, never application/network behavior."""
    recovery = _copy(_recovery(recovery))
    p = recovery['plan']
    with _parent(p['path']) as (fd, name):
        actual, snapshot = _read(fd, name)
        matched = (_identity(fd) == p['parent_identity'] and
                   snapshot == recovery['applied_snapshot'] and
                   _hash(actual) == p['after_sha256'])
    return {'check_status': 'pass' if matched else 'fail',
            'verification_scope': 'exact_file_bytes_only',
            'application_effect': 'not_tested', 'network_effect': 'not_tested'}


def rollback(recovery, *, target_ref, authorize=None, exclusive_access=False):
    """Restore a strict applied receipt with separate, fresh rollback authority.

    A private restore witness is persisted before replacement. It remains usable
    for read-only reconciliation if the completion journal cannot be written.
    """
    recovery = _copy(_recovery(recovery))
    p = recovery['plan']
    if p['target_ref'] != target_ref:
        _fail('TARGET_MISMATCH')
    if exclusive_access is not True:
        _fail('EXCLUSIVE_ACCESS_REQUIRED')
    try:
        _backup_path_budget(recovery['backup_directory'])
        _recovery_document_budget(p, recovery['backup_directory'])
        _authorize(authorize, 'rollback', recovery, target_ref)
        return _restore(recovery, recovery['applied_snapshot'],
                        lambda: _authorize(authorize, 'rollback', recovery, target_ref))
    except (OSError, TransactionError, KeyboardInterrupt) as exc:
        raise _context_error(exc, recovery['batch']) from None


def _private_batch(fd, expected=None):
    info = os.fstat(fd)
    if info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o700:
        _fail('BACKUP_DIRECTORY_NOT_PRIVATE')
    if expected is not None and _identity(fd) != expected:
        _fail('BACKUP_DIRECTORY_CHANGED')


def _restore(recovery, expected, confirm, revalidate=None):
    p = recovery['plan']
    batch = recovery['batch']
    attempt = uuid.uuid4().hex
    batch_path = recovery['backup_directory'] + '/' + batch
    try:
        with _directory(batch_path) as bfd:
            _private_batch(bfd, recovery.get('batch_identity'))
            batch_identity = _identity(bfd)
            original, backup_snapshot = _read(bfd, 'original.bin')
            if _hash(original) != p['before']['sha256']:
                _fail('BACKUP_CORRUPT')
            with _parent(p['path']) as (fd, name):
                if _identity(fd) != p['parent_identity']:
                    _fail('PARENT_CHANGED')
                if _read(fd, name)[1] != expected:
                    _fail('ROLLBACK_CONFLICT')
                def prepared(staging, staged):
                    record = {'schema_version': 'exact-file-restore/1', 'plan': p,
                              'backup_directory': recovery['backup_directory'],
                              'batch': batch, 'batch_identity': batch_identity,
                              'attempt_id': attempt, 'state': 'restore_prepared',
                              'source_digest': digest(recovery), 'source_snapshot': expected,
                              'replacement': {'name': staging, 'snapshot': staged}}
                    record_name = 'restore-' + attempt + '.prepared.json'
                    _write(bfd, record_name, _journal_bytes(record))
                    retained, retained_snapshot = _document_file(bfd, record_name)
                    if digest(retained) != digest(record):
                        _fail('RECEIPT_DIGEST_MISMATCH')
                    evidence_check()
                    with _directory(batch_path) as current_bfd:
                        _private_batch(current_bfd, batch_identity)
                        fresh, fresh_snapshot = _document_file(current_bfd, record_name)
                        if digest(fresh) != digest(record) or fresh_snapshot != retained_snapshot:
                            _fail('RECEIPT_CHANGED')
                    if revalidate is not None:
                        revalidate()
                def evidence_check():
                    with _directory(batch_path) as current_bfd:
                        _private_batch(current_bfd, batch_identity)
                        if _read(current_bfd, 'original.bin')[1] != backup_snapshot:
                            _fail('BACKUP_CHANGED')
                def final_check():
                    confirm()
                    evidence_check()
                restored = _replace(fd, name, original, expected, p['path'],
                                    p['parent_identity'], final_check, on_committing=prepared)
                result = {'schema_version': 'exact-file-rollback/1', 'state': 'restored',
                          'recovery_digest': digest(recovery), 'restored_snapshot': restored,
                          'verification_scope': 'exact_file_bytes_only',
                          'application_effect': 'not_tested', 'network_effect': 'not_tested',
                          'recovery_id': batch, 'attempt_id': attempt}
                _write(bfd, 'rollback-' + attempt + '.json',
                       _journal_bytes(result))
                return result
    except (OSError, TransactionError, KeyboardInterrupt) as exc:
        raise _context_error(exc, batch, attempt) from None


def _restore_shape(document):
    _bounded_document(document)
    fields = {'schema_version', 'plan', 'backup_directory', 'batch', 'batch_identity',
              'attempt_id', 'state', 'source_digest', 'source_snapshot', 'replacement'}
    if (type(document) is not dict or set(document) != fields
            or document['schema_version'] != 'exact-file-restore/1'
            or document['state'] != 'restore_prepared'
            or not _hex(document['attempt_id'], 32) or not _hex(document['batch'], 32)
            or not _hex(document['source_digest'], 64)):
        _fail('INVALID_RECOVERY')
    proposed = _validate(document['plan'])
    _path(document['backup_directory'])
    _identity_value(document['batch_identity'])
    _snapshot(document['source_snapshot'])
    p = document['plan']
    _witness(document['replacement'], p['before']['sha256'], p['before']['size'], p['before'])
    if (document['source_snapshot']['sha256'] != p['after_sha256']
            or document['source_snapshot']['size'] != len(proposed)
            or any(document['source_snapshot'][k] != p['before'][k]
                   for k in ('mode', 'uid', 'gid', 'device'))):
        _fail('INVALID_RECOVERY')
    return document


def _document_file(fd, name):
    """Private bounded JSON journal read; its base64 payload may exceed MAX_BYTES."""
    file_fd = None
    primary = None
    try:
        file_fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        before = os.fstat(file_fd)
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or before.st_uid != os.geteuid() or before.st_gid != os.getegid()
                or stat.S_IMODE(before.st_mode) & 0o7077
                or before.st_size > MAX_DOCUMENT or _has_xattrs(file_fd)):
            _fail('UNSAFE_RECEIPT_FILE')
        data = bytearray()
        while len(data) <= MAX_DOCUMENT:
            block = os.read(file_fd, min(65536, MAX_DOCUMENT + 1 - len(data)))
            if not block:
                break
            data.extend(block)
        after = os.fstat(file_fd)
        if len(data) > MAX_DOCUMENT:
            _fail('INVALID_DOCUMENT')
        fields = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_uid', 'st_gid',
                  'st_size', 'st_mtime_ns', 'st_ctime_ns')
        if any(getattr(before, key) != getattr(after, key) for key in fields):
            _fail('RECEIPT_CHANGED')
        snapshot = {'sha256': _hash(data), 'size': len(data),
                    'device': before.st_dev, 'inode': before.st_ino,
                    'mode': stat.S_IMODE(before.st_mode), 'uid': before.st_uid,
                    'gid': before.st_gid, 'mtime_ns': before.st_mtime_ns,
                    'ctime_ns': before.st_ctime_ns}
    except BaseException as exc:
        primary = exc
        raise
    finally:
        if file_fd is not None:
            _close_preserving(file_fd, primary)
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                _fail('INVALID_RECEIPT_JSON')
            result[key] = value
        return result
    try:
        document = json.loads(data.decode('utf-8'), object_pairs_hook=unique,
                              parse_constant=lambda _: _fail('INVALID_RECEIPT_JSON'))
        digest(document)
        return document, snapshot
    except (ValueError, UnicodeError, RecursionError, OverflowError):
        _fail('INVALID_RECEIPT_JSON')


def reconcile(recovery, *, receipt_path, target_ref, target_path, backup_batch):
    """Observe one explicitly scoped retained record; no writes or historical success.

    The trusted host establishes source authenticity and authorizes the scoped
    reads. The deterministic private result contains identities/hashes, no bytes.
    A staging witness tolerates rename's ctime change only for initial candidate
    observation. It cannot establish uninterrupted edit history or exclude inode
    reuse under arbitrary interference. Host-enforced writer exclusion is still
    required for any later restore; the complete observation is then rechecked.
    """
    recovery = _copy(recovery)
    _path(receipt_path); _path(target_path); _path(backup_batch)
    if type(recovery) is not dict or type(recovery.get('plan')) is not dict:
        _fail('INVALID_RECOVERY')
    p = recovery['plan']
    if p.get('path') != target_path or p.get('target_ref') != target_ref:
        _fail('TARGET_MISMATCH')
    if (type(recovery.get('backup_directory')) is not str
            or not _hex(recovery.get('batch'), 32)
            or recovery['backup_directory'] + '/' + recovery['batch'] != backup_batch):
        _fail('BACKUP_SCOPE_MISMATCH')
    is_restore = recovery.get('schema_version') == 'exact-file-restore/1'
    if is_restore:
        _restore_shape(recovery)
        basename = 'restore-' + recovery['attempt_id'] + '.prepared.json'
    else:
        _recovery_shape(recovery)
        basename = 'prepared.json' if recovery['state'] == 'prepared' else 'applied.json'
    if receipt_path != backup_batch + '/' + basename:
        _fail('RECEIPT_PATH_MISMATCH')
    try:
        with _directory(backup_batch) as bfd:
            _private_batch(bfd, recovery.get('batch_identity'))
            document, receipt_snapshot = _document_file(bfd, basename)
            if digest(document) != digest(recovery):
                _fail('RECEIPT_DIGEST_MISMATCH')
            original, backup_snapshot = _read(bfd, 'original.bin')
            if backup_snapshot['mode'] != 0o600:
                _fail('BACKUP_NOT_PRIVATE')
            if _hash(original) != p['before']['sha256']:
                _fail('BACKUP_CORRUPT')
            batch_identity = _identity(bfd)
        with _parent(target_path) as (fd, name):
            if _identity(fd) != p['parent_identity']:
                _fail('PARENT_CHANGED')
            _, current = _read(fd, name)
            witness = recovery.get('replacement')
            stage_absent = True
            if witness:
                try:
                    os.stat(witness['name'], dir_fd=fd, follow_symlinks=False)
                    stage_absent = False
                except FileNotFoundError:
                    pass
            if is_restore:
                if current == recovery['source_snapshot']:
                    classification = 'restore_not_committed'
                elif stage_absent and _same_renamed_file(current, witness['snapshot']):
                    classification = 'restored_candidate_observed'
                else:
                    classification = 'conflict'
            elif recovery['state'] == 'applied':
                classification = ('applied_observed' if current == recovery['applied_snapshot'] else 'conflict')
            elif current == p['before']:
                classification = 'original_observed'
            elif recovery['schema_version'] == 'exact-file-recovery/1':
                classification = 'legacy_identity_unproven'
            elif stage_absent and _same_renamed_file(current, witness['snapshot']):
                classification = 'prepared_candidate_observed'
            else:
                classification = 'conflict'
        result = {'schema_version': 'exact-file-reconciliation/1',
                  'recovery_digest': digest(recovery), 'receipt_path': receipt_path,
                  'receipt_snapshot': receipt_snapshot, 'backup_snapshot': backup_snapshot,
                  'target_ref': target_ref, 'target_path': target_path,
                  'backup_batch': backup_batch, 'batch_identity': batch_identity,
                  'current_snapshot': current, 'classification': classification,
                  'restore_sha256': p['before']['sha256'], 'replace_sha256': p['after_sha256'],
                  'restore_mode': p['before']['mode'], 'verification_scope': 'exact_file_bytes_only',
                  'application_effect': 'not_tested', 'network_effect': 'not_tested'}
        digest(result)
        return result
    except (OSError, TransactionError, KeyboardInterrupt) as exc:
        raise _context_error(exc, recovery['batch'], recovery.get('attempt_id')) from None


def restore_prepared(recovery, observation, *, target_ref, authorize=None, exclusive_access=False):
    """Newly authorize restoration of an observed v2 candidate, never replay apply.

    Both approvals bind the complete private observation. Source journal, backup,
    batch and target are freshly rechecked after each approval. No legacy prepared
    record can enter this write path. Completion describes this restoration only.
    """
    recovery = _copy(recovery)
    observation = _copy(observation)
    _recovery_shape(recovery)
    if recovery['plan']['target_ref'] != target_ref:
        _fail('TARGET_MISMATCH')
    if recovery['schema_version'] != 'exact-file-recovery/2':
        _fail('LEGACY_RECOVERY_IDENTITY_UNPROVEN')
    if recovery['state'] != 'prepared':
        _fail('PREPARED_RECOVERY_REQUIRED')
    if exclusive_access is not True:
        _fail('EXCLUSIVE_ACCESS_REQUIRED')
    fields = {'receipt_path', 'target_ref', 'target_path', 'backup_batch'}
    if type(observation) is not dict or not fields <= set(observation):
        _fail('INVALID_RECONCILIATION')
    scope = {key: observation[key] for key in fields}
    def recheck():
        fresh = reconcile(recovery, **scope)
        if fresh != observation:
            _fail('RECONCILIATION_STALE')
        if fresh['classification'] != 'prepared_candidate_observed':
            _fail('RECOVERY_WITNESS_MISMATCH')
    authorization = {'recovery_digest': digest(recovery), 'observation': observation}
    try:
        _backup_path_budget(recovery['backup_directory'])
        _recovery_document_budget(recovery['plan'], recovery['backup_directory'])
        recheck()
        _authorize(authorize, 'restore_prepared', authorization, target_ref)
        recheck()
        def confirm():
            _authorize(authorize, 'restore_prepared', authorization, target_ref)
            recheck()
        return _restore(recovery, observation['current_snapshot'], confirm, recheck)
    except (OSError, TransactionError, KeyboardInterrupt) as exc:
        raise _context_error(exc, recovery['batch']) from None
