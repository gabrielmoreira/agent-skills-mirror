"""Offline, explicit-scope POSIX recovery for exact-file transactions only.

The invoking person is the trusted host: they must independently know the scope
and digest, exclude other writers, and approve on a real terminal. This is not a
security boundary against a malicious local caller or terminal controller.
"""
import argparse
import hashlib
import json
import os
import select
import secrets
import stat
import sys
import time

sys.dont_write_bytecode = True  # Inspection must not create import caches.
import transactions as tx


def fail(code):
    raise tx.TransactionError(code)


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail('INVALID_RECEIPT_JSON')
        result[key] = value
    return result


def load_receipt(path):
    """Read only an explicitly selected private regular file; never follow links.

    Byte bounds apply before JSON parsing. The existing engine also bounds parsed
    structure, depth and canonical document size. Filesystem reads may block in
    the kernel (for example a hung filesystem); no hard I/O deadline is claimed.
    """
    tx._support()
    with tx._parent(path) as (parent, name):
        directory = os.fstat(parent)
        if directory.st_uid != os.geteuid() or stat.S_IMODE(directory.st_mode) != 0o700:
            fail('RECEIPT_DIRECTORY_NOT_PRIVATE')
        fd = None
        try:
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
            before = os.fstat(fd)
            if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                    or before.st_uid != os.geteuid() or before.st_gid != os.getegid()
                    or stat.S_IMODE(before.st_mode) & 0o7077
                    or before.st_size > tx.MAX_DOCUMENT or tx._has_xattrs(fd)):
                fail('UNSAFE_RECEIPT_FILE')
            data = bytearray()
            while len(data) <= tx.MAX_DOCUMENT:
                block = os.read(fd, min(65536, tx.MAX_DOCUMENT + 1 - len(data)))
                if not block:
                    break
                data.extend(block)
            after = os.fstat(fd)
            if len(data) > tx.MAX_DOCUMENT:
                fail('RECEIPT_TOO_LARGE')
            if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                    after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                fail('RECEIPT_CHANGED')
        finally:
            if fd is not None:
                os.close(fd)
    try:
        result = json.loads(data.decode('utf-8'), object_pairs_hook=_unique,
                            parse_constant=lambda _: fail('INVALID_RECEIPT_JSON'))
        tx.digest(result)
        return result
    except (UnicodeError, ValueError, RecursionError, OverflowError):
        fail('INVALID_RECEIPT_JSON')


def bind_receipt(args):
    # Caller paths, not receipt fields, define the complete allowed read scope.
    tx._path(args.receipt)
    tx._path(args.target_path)
    tx._path(args.backup_batch)
    if not tx._hex(args.receipt_digest, 64):
        fail('INVALID_EXPECTED_DIGEST')
    receipt = load_receipt(args.receipt)
    if tx.digest(receipt) != args.receipt_digest:
        fail('RECEIPT_DIGEST_MISMATCH')
    if type(receipt) is not dict or type(receipt.get('plan')) is not dict:
        fail('INVALID_RECOVERY')
    plan = receipt['plan']
    if plan.get('path') != args.target_path or plan.get('target_ref') != args.target_ref:
        fail('TARGET_MISMATCH')
    backup = receipt.get('backup_directory')
    batch = receipt.get('batch')
    if (type(backup) is not str or not tx._hex(batch, 32)
            or backup + '/' + batch != args.backup_batch
            or args.receipt not in (args.backup_batch + '/applied.json',
                                    args.backup_batch + '/prepared.json')):
        fail('BACKUP_SCOPE_MISMATCH')
    tx._recovery(receipt)  # prepared-only records deliberately require reconciliation
    if args.receipt != args.backup_batch + '/applied.json':
        fail('RECEIPT_PATH_MISMATCH')
    return receipt


def preview(receipt, args):
    result = tx.verify(receipt)
    if result['check_status'] != 'pass':
        fail('ROLLBACK_CONFLICT')
    with tx._directory(args.backup_batch) as fd:
        info = os.fstat(fd)
        if info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o700:
            fail('BACKUP_DIRECTORY_NOT_PRIVATE')
        original, _ = tx._read(fd, 'original.bin')
    if hashlib.sha256(original).hexdigest() != receipt['plan']['before']['sha256']:
        fail('BACKUP_CORRUPT')
    return result


def bind_reconciliation(args):
    """Explicit caller scope is checked by reconcile before target/backup reads."""
    tx._path(args.receipt)
    tx._path(args.target_path)
    tx._path(args.backup_batch)
    if not tx._hex(args.receipt_digest, 64):
        fail('INVALID_EXPECTED_DIGEST')
    receipt = load_receipt(args.receipt)
    if tx.digest(receipt) != args.receipt_digest:
        fail('RECEIPT_DIGEST_MISMATCH')
    observation = tx.reconcile(receipt, receipt_path=args.receipt,
                               target_ref=args.target_ref, target_path=args.target_path,
                               backup_batch=args.backup_batch)
    bound = tx.digest({'recovery_digest': args.receipt_digest, 'observation': observation})
    return receipt, observation, bound


def reconcile_command(args):
    restoring = args.command == 'restore-prepared'
    if restoring and not args.reconciliation_digest:
        fail('EXPECTED_RECONCILIATION_REQUIRED')
    if args.reconciliation_digest is not None and not tx._hex(args.reconciliation_digest, 64):
        fail('INVALID_EXPECTED_DIGEST')
    receipt, observation, bound = bind_reconciliation(args)
    if args.reconciliation_digest is not None and args.reconciliation_digest != bound:
        fail('RECONCILIATION_STALE')
    summary = {key: observation[key] for key in (
        'classification', 'target_ref', 'target_path', 'backup_batch',
        'restore_sha256', 'replace_sha256', 'restore_mode', 'verification_scope',
        'application_effect', 'network_effect')}
    summary.update(status='observed', receipt=args.receipt,
                   receipt_digest=args.receipt_digest, reconciliation_digest=bound,
                   current_sha256=observation['current_snapshot']['sha256'],
                   restore_candidate=observation['classification'] == 'prepared_candidate_observed')
    print(json.dumps(summary, sort_keys=True), flush=True)
    if not restoring:
        return 0
    if receipt['schema_version'] == 'exact-file-recovery/1':
        fail('LEGACY_RECOVERY_IDENTITY_UNPROVEN')
    if receipt['schema_version'] != 'exact-file-recovery/2' or receipt['state'] != 'prepared':
        fail('PREPARED_RECOVERY_REQUIRED')
    if observation['classification'] != 'prepared_candidate_observed':
        fail('RECOVERY_WITNESS_MISMATCH')
    print('Separately restores the original bytes and mode of this observed candidate. '
          'It does not replay apply or establish a historical successful commit. '
          'Keep this private; hashes may be sensitive.\n'
          'HOST PREREQUISITE: save work and stop/exclude every writer for the '
          'entire operation, including GUI/services/sync. An advisory lock is '
          'insufficient. This tool cannot establish writer exclusion. If you '
          'cannot establish it, cancel. Receipt integrity is not consent.', flush=True)
    confirm('EXCLUSIVE ACCESS ESTABLISHED', args.approval_timeout)
    calls = 0
    def authorize(operation, value, target):
        nonlocal calls
        if (operation != 'restore_prepared' or value != bound or target != args.target_ref):
            fail('AUTHORIZATION_SCOPE_MISMATCH')
        def recheck():
            current_receipt, current_observation, current_bound = bind_reconciliation(args)
            if (current_receipt != receipt or current_observation != observation
                    or current_bound != bound):
                fail('RECONCILIATION_STALE')
        recheck()
        calls += 1
        print('Approval %d/2 for the exact reconciled scope above' % calls, flush=True)
        confirm('RESTORE_PREPARED ' + bound, args.approval_timeout)
        recheck()
        return True
    result = tx.restore_prepared(receipt, observation, target_ref=args.target_ref,
                                 authorize=authorize, exclusive_access=True)
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0


def confirm(phrase, timeout):
    """Fresh, bounded terminal input; stdin pipes are never approval."""
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        fail('INTERACTIVE_TERMINAL_REQUIRED')
    # Discard paste-ahead/type-ahead before opening this distinct approval.
    # A new unpredictable challenge also prevents queued future answers from
    # matching if they arrive just after the flush. This is a human workflow
    # boundary, not protection against a process controlling the terminal.
    import termios
    try:
        termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
    except termios.error:
        fail('TERMINAL_FLUSH_FAILED')
    phrase = phrase + ' ' + secrets.token_hex(8)
    print('Type exactly ' + json.dumps(phrase) + ' or cancel:', flush=True)
    deadline = time.monotonic() + timeout
    value = bytearray()
    while len(value) <= 256:
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not select.select([sys.stdin.fileno()], [], [], remaining)[0]:
            fail('APPROVAL_TIMEOUT')
        char = os.read(sys.stdin.fileno(), 1)
        if not char:
            fail('APPROVAL_CANCELLED')
        if char == b'\n':
            if bytes(value) != phrase.encode('ascii'):
                fail('APPROVAL_CANCELLED')
            return
        value.extend(char)
    fail('APPROVAL_CANCELLED')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('inspect', 'preview', 'rollback',
                                            'reconcile', 'restore-prepared'))
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--receipt-digest',
                        help='Canonical digest retained independently by the trusted host')
    parser.add_argument('--target-ref')
    parser.add_argument('--target-path')
    parser.add_argument('--backup-batch')
    parser.add_argument('--reconciliation-digest',
                        help='Exact restore operation digest from a separately reviewed reconcile result')
    parser.add_argument('--approval-timeout', type=int, default=60,
                        help='Seconds per terminal prompt (1..300); not an I/O deadline')
    args = parser.parse_args(argv)
    try:
        tx._support()
        if not 1 <= args.approval_timeout <= 300:
            fail('INVALID_APPROVAL_TIMEOUT')
        if args.command == 'inspect':
            candidate = load_receipt(args.receipt)
            print(json.dumps({'status': 'unverified_candidate',
                              'candidate_receipt_digest': tx.digest(candidate),
                              'scope': 'selected_receipt_only',
                              'note': 'No embedded paths read. Independently establish target '
                              'and backup scope before preview, rollback or reconcile; a digest is '
                              'integrity data, never authenticity or permission.'}, sort_keys=True))
            return 0
        if not all((args.receipt_digest, args.target_ref, args.target_path, args.backup_batch)):
            fail('EXPLICIT_SCOPE_REQUIRED')
        if args.command in ('reconcile', 'restore-prepared'):
            return reconcile_command(args)
        receipt = bind_receipt(args)
        summary = {'state': receipt['state'], 'receipt_digest': args.receipt_digest,
                   'receipt': args.receipt, 'target_ref': args.target_ref,
                   'target_path': args.target_path, 'backup_batch': args.backup_batch,
                   'restore_sha256': receipt['plan']['before']['sha256'],
                   'replace_sha256': receipt['plan']['after_sha256'],
                   'verification_scope': 'exact_file_bytes_only',
                   'application_effect': 'not_tested', 'network_effect': 'not_tested'}
        if args.command in ('preview', 'rollback'):
            summary.update(preview(receipt, args))
        # JSON escapes control sequences in user-supplied labels and paths.
        print(json.dumps(summary, sort_keys=True), flush=True)
        if args.command != 'rollback':
            return 0
        print('Restores the original bytes and mode to this exact existing file. '
              'No application is started. Keep this private; hashes may be sensitive.\n'
              'HOST PREREQUISITE: save work and stop/exclude every writer for the '
              'entire operation, including GUI/services/sync. An advisory lock is '
              'insufficient. This tool cannot establish writer exclusion. If you '
              'cannot establish it, cancel. Receipt integrity is not consent.', flush=True)
        confirm('EXCLUSIVE ACCESS ESTABLISHED', args.approval_timeout)
        calls = 0
        def authorize(operation, value, target):
            nonlocal calls
            if (operation != 'rollback' or value != args.receipt_digest
                    or target != args.target_ref):
                fail('AUTHORIZATION_SCOPE_MISMATCH')
            # Reopen the exact approved receipt on each authorization, detecting
            # changes during the human review instead of replaying a saved grant.
            bind_receipt(args)
            calls += 1
            print('Approval %d/2 for the exact scope above' % calls, flush=True)
            confirm('ROLLBACK ' + args.receipt_digest, args.approval_timeout)
            bind_receipt(args)
            return True
        result = tx.rollback(receipt, target_ref=args.target_ref,
                             authorize=authorize, exclusive_access=True)
        print(json.dumps(result, sort_keys=True), flush=True)
        return 0
    except tx.TransactionError as exc:
        error = {'status': 'blocked', 'code': exc.code,
                 'note': 'No automatic retry. On write-phase failure, inspect '
                 'the exact target and retained private batch before reconciliation.'}
        for key in ('recovery_id', 'attempt_id'):
            value = getattr(exc, key, None)
            if tx._hex(value, 32):
                error[key] = value
        cleanup = getattr(exc, 'cleanup_code', None)
        if cleanup in ('STAGING_RETAINED', 'STAGING_CLEANUP_FAILED', 'DESCRIPTOR_CLOSE_FAILED'):
            error['cleanup_code'] = cleanup
        print(json.dumps(error), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print('{"status":"blocked","code":"CANCELLED"}', file=sys.stderr)
        return 130
    except OSError:
        print('{"status":"blocked","code":"IO_FAILURE"}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
